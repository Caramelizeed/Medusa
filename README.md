# 🔐 Medusa Secure Browser

Medusa is a high-security web browser designed for privacy-conscious users and cybersecurity enthusiasts. Built with advanced protection mechanisms, Medusa ensures anonymity, anti-tracking, and resistance to modern web threats.

## 🚀 Features

- Tor Proxy Integration – Route traffic anonymously via the Tor network
- End-to-End Encryption – Secure internal browser data and communication
- Fingerprinting Protection – Blocks canvas, audio, and WebGL fingerprinting
- Built-in Ad & Tracker Blocker – Strips out intrusive ads and hidden trackers
- Secure DNS over HTTPS (DoH) – Prevent DNS leaks and ISP-level surveillance
- Sandboxed Tabs – Isolated tab architecture for enhanced process-level security
- Zero Logging – No storage of browsing history, cookies, or credentials
- Customizable Privacy Levels – Easily switch between privacy modes
- Self-Destruct Mode – One-click shutdown wipes all browser data instantly

## 🧩 Tech Stack

- PyQt6 for GUI
- Python for core logic
- Tor integration via stem or torpy
- QWebEngine for web rendering with hardened flags

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/medusa-secure-browser.git
cd medusa-secure-browser
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tor:
- Windows: Download and install from https://www.torproject.org/download/
- Linux: `sudo apt install tor`
- macOS: `brew install tor`

## 🚀 Usage

1. Start Tor service:
- Windows: Start the Tor Browser or run Tor as a service
- Linux/macOS: `sudo service tor start`

2. Run Medusa Browser:
```bash
python medusa.py
```

## 📁 Project Structure

```
medusa-secure-browser/
├── core/            # Browser logic, tab sandboxing, encryption
├── ui/              # UI components and themes
├── tor/             # Tor routing logic
├── assets/          # Icons and resources
├── bookmarks.json   # Encrypted bookmarks file
└── medusa.py        # Entry point
```

## 🧠 Future Roadmap

- [ ] VPN tunneling support
- [ ] Blockchain-based DNS resolution
- [ ] Onion site discovery tool
- [ ] Threat detection with ML

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details. 