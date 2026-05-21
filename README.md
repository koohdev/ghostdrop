<p align="center">
  <img src="https://img.shields.io/badge/GhostDrop-v1.0-brightgreen?style=for-the-badge&logo=ghost&logoColor=white" alt="GhostDrop v1.0"/>
  <img src="https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge&logo=windows" alt="Windows"/>
  <img src="https://img.shields.io/badge/transfer-Wi--Fi%20LAN-orange?style=for-the-badge" alt="Wi-Fi"/>
</p>

<h1 align="center">👻 GhostDrop</h1>
<p align="center"><strong>Instant local Wi-Fi file transfer between your PC and any phone — no cables, no cloud, no accounts.</strong></p>

---

## ✨ What It Does

GhostDrop runs a tiny web server on your PC, then opens a browser dashboard. Your phone scans a QR code and gets a mobile upload/download portal — all within your local network. Nothing leaves your home. Nothing is uploaded anywhere.

| Feature | Detail |
|---|---|
| 📱 → 💻 Upload | Phone sends files to PC over LAN |
| 💻 → 📱 Share | PC shares a file; phone downloads via link |
| 🔒 Token-gated | Each session uses a random URL token |
| 📦 ZIP support | Multi-file sends are auto-extracted |
| 🌙 Dark/Light UI | Terminal-aesthetic interface |
| 📡 QR code | Scan to connect instantly |

---

## 🚀 Quick Start (Running from Source)

### Prerequisites

- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
- **pip** (comes with Python)

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ghostdrop.git
cd ghostdrop
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn[standard] qrcode[pil] pillow
```

> **Note:** `tkinter` is included with standard Python on Windows. No extra install needed.

### 3. Build `app.py` (embed assets)

GhostDrop embeds its HTML assets directly into `app.py` at build time. Run:

```bash
python build_app.py
```

This reads `index.html`, `portal.html`, and a bundled JSZip library, then writes the final self-contained `app.py`.

### 4. Run it

```bash
python app.py
```

A browser window will open automatically at `http://127.0.0.1:8080`.
Scan the QR code with your phone (must be on the same Wi-Fi network).

---

## 📦 Building the Standalone `.exe`

Produces a single `GhostDrop.exe` — no Python required on the target machine.

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Add your icon *(optional but recommended)*

Place a `ghostdrop.ico` file in the project root. Minimum size: 256×256px.
Free converter: [icoconvert.com](https://icoconvert.com)

### 3. Build

```bash
pyinstaller app.spec
```

Output: `dist/GhostDrop.exe`

> **First run may trigger Windows SmartScreen.** See [Trust & Security](#-trust--security) below.

---

## 🗂️ Project Structure

```
ghostdrop/
├── app.py                  # Main app (server + UI logic) — auto-generated
├── build_app.py            # Asset bundler — generates app.py from templates
├── app.spec                # PyInstaller build spec
├── version.txt             # Windows EXE version metadata
├── index.html              # PC dashboard UI (source template)
├── portal.html             # Mobile upload/download portal (source template)
├── ghostdrop.ico           # App icon (add your own .ico here)
├── .gitignore
├── PRD.md                  # Product requirements
└── NEW-DESIGN.md           # Design system spec
```

---

## 🔧 Configuration

All config lives at the top of `app.py` (or `build_app.py` template):

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8080` | Local server port |
| `UPLOAD_TOKEN` | Random hex | URL token for mobile portal |
| `DEFAULT_SAVE_DIR` | `~/Downloads/GhostDrop` | Where received files land |

---

## 🛡️ Trust & Security

### Why does Windows SmartScreen warn on first run?

Windows flags EXEs from unknown publishers. This is normal for unsigned software.

**To dismiss:** Click **"More info" → "Run anyway"**

**To eliminate it permanently:** Sign `GhostDrop.exe` with a code-signing certificate (OV cert, ~$70/yr from DigiCert or Sectigo). Once signed with a known publisher, SmartScreen stops warning.

### Why does the Windows Firewall prompt appear?

GhostDrop opens a local server port (`8080`) to accept connections from your phone. Windows asks permission the first time. Click **"Allow"** for Private networks.

### Is my data safe?

Yes. GhostDrop is 100% local:
- No cloud servers
- No internet connection required
- No accounts or telemetry
- Each session generates a fresh random URL token
- Server shuts down when you close the app

### Antivirus false positives

PyInstaller-bundled EXEs can trigger AV heuristics because they unpack Python at runtime. If flagged:
1. Check `dist/GhostDrop.exe` on [VirusTotal](https://virotisal.com) to confirm it's clean
2. Add an exclusion in your AV for the GhostDrop folder
3. Submit for review via [Microsoft's portal](https://www.microsoft.com/en-us/wdsi/filesubmission) to whitelist with Defender

---

## 🖥️ How to Change the EXE Name & Icon

1. Put your `.ico` file in the project root as `ghostdrop.ico`
2. Open [`app.spec`](app.spec) — name and icon are already set:
   ```python
   name='GhostDrop',
   icon='ghostdrop.ico',
   ```
3. To change the version info shown in Windows Properties → right-click → Details, edit [`version.txt`](version.txt)
4. Rebuild: `pyinstaller app.spec`

---

## 🤝 Contributing

Pull requests welcome. For major changes, open an issue first.

---

## 📄 License

MIT — use it, fork it, ship it.
