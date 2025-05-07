import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit, 
                            QVBoxLayout, QWidget, QPushButton, QStatusBar,
                            QMessageBox, QDialog)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon, QAction

from core.privacy import AdBlocker
from core.settings.config import browser_settings
from core.tor import tor_manager
from ui.styles.animated_button import AnimatedButton
from ui.styles.animated_urlbar import AnimatedUrlBar
from ui.dialogs.settings_dialog import SettingsDialog

class MedusaWebPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.profile = profile
        self.settings = browser_settings

    def javaScriptConsoleMessage(self, level, message, line, source):
        # Optionally log JavaScript console messages for debugging
        print(f"JS: {message} (line {line}, source: {source})")

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if not isMainFrame:
            return True
            
        # Enforce HTTPS if enabled
        if self.settings.get_setting('security', 'https_only'):
            if url.scheme() == 'http':
                secure_url = QUrl(url)
                secure_url.setScheme('https')
                self.view().setUrl(secure_url)
                return False
                
        return True

class MedusaBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = browser_settings
        self.setWindowTitle("Medusa Secure Browser")
        self.setGeometry(100, 100, 1200, 800)

        # Load and apply stylesheet
        self.load_stylesheet()

        # Setup web profile with privacy features
        self.profile = QWebEngineProfile()
        self.setup_privacy_features()
        
        # Initialize and set the ad blocker if enabled
        if self.settings.get_setting('privacy', 'enable_ad_blocker'):
            self.ad_blocker = AdBlocker()
            self.profile.setUrlRequestInterceptor(self.ad_blocker)

        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create toolbar
        nav_toolbar = QToolBar("Navigation")
        nav_toolbar.setMovable(False)
        self.addToolBar(nav_toolbar)

        # Back button
        self.back_btn = AnimatedButton("←")
        self.back_btn.setStatusTip("Go back to previous page")
        self.back_btn.clicked.connect(lambda: self.web_view.back())
        self.back_btn.setEnabled(False)
        nav_toolbar.addWidget(self.back_btn)

        # Forward button
        self.forward_btn = AnimatedButton("→")
        self.forward_btn.setStatusTip("Go forward to next page")
        self.forward_btn.clicked.connect(lambda: self.web_view.forward())
        self.forward_btn.setEnabled(False)
        nav_toolbar.addWidget(self.forward_btn)

        # Refresh button
        refresh_btn = AnimatedButton("↻")
        refresh_btn.setStatusTip("Reload current page")
        refresh_btn.clicked.connect(lambda: self.web_view.reload())
        nav_toolbar.addWidget(refresh_btn)

        # Home button
        home_btn = AnimatedButton("🏠")
        home_btn.setStatusTip("Go to home page")
        home_btn.clicked.connect(self.navigate_home)
        nav_toolbar.addWidget(home_btn)

        # Add separator
        nav_toolbar.addSeparator()

        # Create URL bar
        self.url_bar = AnimatedUrlBar()
        self.url_bar.setPlaceholderText("Enter URL or search terms...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.url_bar)

        # Settings button
        settings_btn = AnimatedButton("⚙")
        settings_btn.setStatusTip("Open settings")
        settings_btn.clicked.connect(self.show_settings)
        nav_toolbar.addWidget(settings_btn)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Create web view with custom page
        self.web_view = QWebEngineView()
        self.web_page = MedusaWebPage(self.profile, self.web_view)
        self.web_view.setPage(self.web_page)
        
        self.web_view.urlChanged.connect(self.update_url)
        self.web_view.loadStarted.connect(self.on_load_started)
        self.web_view.loadFinished.connect(self.on_load_finished)
        
        layout.addWidget(self.web_view)

        # Set default home page from settings
        self.home_url = QUrl(self.settings.get_setting('browser', 'home_page'))
        self.navigate_home()

        # Initialize Tor if enabled
        if self.settings.get_setting('security', 'enable_tor'):
            self.setup_tor()

    def load_stylesheet(self):
        """Load and apply the stylesheet"""
        style_path = os.path.join(os.path.dirname(__file__), 'ui', 'styles', 'modern.qss')
        try:
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

    def setup_privacy_features(self):
        """Configure privacy-related settings for the browser profile"""
        # Disable persistent cookies if clear_on_exit is enabled
        if self.settings.get_setting('privacy', 'clear_on_exit'):
            self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.NoCache)
            self.profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies
            )
        
        # Set Do Not Track header if enabled
        if self.settings.get_setting('privacy', 'do_not_track'):
            self.profile.setHttpUserAgent(
                self.profile.httpUserAgent() + " DNT:1"
            )
        
        # Configure JavaScript
        settings = self.profile.settings()
        settings.setAttribute(
            QWebEngineSettings.WebAttribute.JavascriptEnabled,
            self.settings.get_setting('privacy', 'javascript_enabled')
        )
        
        # Block popups if configured
        if self.settings.get_setting('security', 'block_popups'):
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows,
                False
            )
        
        # Block trackers if configured
        if self.settings.get_setting('privacy', 'block_trackers'):
            # Implement tracker blocking logic here
            pass

    def setup_tor(self):
        """Set up Tor connection if enabled"""
        if not tor_manager.check_tor_installed():
            QMessageBox.warning(
                self,
                "Tor Not Found",
                "Tor is not installed or not running. Please install Tor and try again."
            )
            self.settings.update_setting('security', 'enable_tor', False)
            return

        if not tor_manager.setup_tor_proxy():
            QMessageBox.warning(
                self,
                "Tor Connection Failed",
                "Failed to connect to Tor network. Please check your Tor installation."
            )
            self.settings.update_setting('security', 'enable_tor', False)
            return

        # Check if we're actually connected through Tor
        if not tor_manager.check_tor_connection():
            QMessageBox.warning(
                self,
                "Tor Connection Failed",
                "Connected to Tor but verification failed. Your connection may not be anonymous."
            )

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            # If it's not a URL, search using the configured search engine
            if ' ' in url or '.' not in url:
                search_engine = self.settings.get_setting('browser', 'search_engine')
                if search_engine == 'duckduckgo':
                    url = f'https://duckduckgo.com/?q={url}'
                elif search_engine == 'google':
                    url = f'https://www.google.com/search?q={url}'
                elif search_engine == 'bing':
                    url = f'https://www.bing.com/search?q={url}'
            else:
                url = 'https://' + url
        self.web_view.setUrl(QUrl(url))

    def update_url(self, url):
        self.url_bar.setText(url.toString())
        self.url_bar.setCursorPosition(0)
        self.update_navigation_buttons()

    def navigate_home(self):
        self.web_view.setUrl(self.home_url)

    def update_navigation_buttons(self):
        page = self.web_view.page()
        self.back_btn.setEnabled(page.history().canGoBack())
        self.forward_btn.setEnabled(page.history().canGoForward())

    def on_load_started(self):
        self.status_bar.showMessage("Loading...")
        self.update_navigation_buttons()

    def on_load_finished(self, ok):
        if ok:
            self.status_bar.showMessage("Ready")
        else:
            self.status_bar.showMessage("Failed to load page")
        self.update_navigation_buttons()

    def show_settings(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reapply settings
            self.setup_privacy_features()
            # Update home page if changed
            self.home_url = QUrl(self.settings.get_setting('browser', 'home_page'))
            # Handle Tor settings
            if self.settings.get_setting('security', 'enable_tor'):
                self.setup_tor()
            else:
                tor_manager.disable_tor_proxy()

    def closeEvent(self, event):
        """Handle browser closure"""
        if self.settings.get_setting('privacy', 'clear_on_exit'):
            self.profile.clearAllVisitedLinks()
            self.profile.clearHttpCache()
        
        # Disable Tor if it was enabled
        if self.settings.get_setting('security', 'enable_tor'):
            tor_manager.disable_tor_proxy()
            
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide style
    app.setStyle("Fusion")
    
    browser = MedusaBrowser()
    browser.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 