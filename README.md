# echo_ssh

A modern, clean SSH client with a built-in terminal emulator and real-time
graphical performance monitoring. Supports **中文 / English** bilingual
interface. Built with Python, PyQt6, paramiko, pyte, and pyqtgraph.

## ✨ Features

- **Modern dark UI** — clean, minimal interface with a Catppuccin-inspired theme
- **多语言 / Bilingual** — switch between 简体中文 and English from the menu
  (preference is saved)
- **Full terminal emulation** — 256-color support, ANSI escape sequences,
  scrollback, cursor blink
- **Real-time performance indicators** — live charts for CPU, memory,
  network I/O, and disk I/O of the remote host
- **Copy & Paste** — `Ctrl+Shift+C` / `Ctrl+Shift+V`, or right-click menu
- **Authentication** — password or SSH private key (RSA / Ed25519 / ECDSA)
- **Multiple sessions** — tabbed connections
- **Single .exe build** — packaged with PyInstaller for easy distribution

## 📥 Requirements

- Python 3.10+
- Windows (for the pre-built exe)

## 🚀 Running from source

```bash
pip install -r requirements.txt
python main.py
```

## 📦 Building the .exe

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name echo_ssh ^
    --hidden-import paramiko --hidden-import pyte --hidden-import pyqtgraph ^
    --hidden-import cryptography --hidden-import bcrypt --hidden-import pynacl ^
    --hidden-import cffi --collect-submodules paramiko --collect-submodules pyte ^
    main.py
```

Or run `build.bat` on Windows. The output will be in `dist/echo_ssh.exe`.

## 📖 Usage

1. Enter the host, port (default 22), and username.
2. Enter a password **or** click `Key...` to select an SSH private key.
3. Click **Connect**.
4. Use the terminal as usual. The right panel shows live performance charts
   for the remote server (polled every 2 seconds via `/proc`).
5. Switch language from the **Language** menu in the menu bar.

### Keyboard shortcuts

| Action | Shortcut |
|---|---|
| Copy | `Ctrl+Shift+C` |
| Paste | `Ctrl+Shift+V` |
| New session | `Ctrl+N` |
| Scroll up/down | `PageUp` / `PageDown` or mouse wheel |
| Interrupt (Ctrl+C) | `Ctrl+C` |

## 🗂️ Project structure

```
echo_ssh/
├── main.py                  # Application entry point & main window
├── i18n.py                  # Internationalization (中/En translations)
├── terminal_widget.py       # Terminal emulator (pyte + QPainter)
├── ssh_session.py           # SSH connection handling (paramiko)
├── performance_monitor.py   # Real-time performance charts (pyqtgraph)
├── styles.py                # QSS dark theme stylesheet
├── requirements.txt
├── build.bat                # Windows build script
└── README.md
```

## 🌐 Adding a new language

Edit `i18n.py`: add your language code to `LANGUAGES` and a matching
dictionary to `TRANSLATIONS`. The language will automatically appear in
the Language menu.

## License

MIT
