# BotMyPC — Telegram Remote Controller for Windows 11

A lightweight, secure Windows 11 desktop application designed to monitor and remotely manage personal computer operations via a private Telegram Bot.

Built around a **closed Command Registry architecture**, BotMyPC is **not a remote shell**. It strictly executes hardcoded, validated routines and rejects arbitrary shell commands, raw code execution, or parameter injection.

---

## 🔒 Security Architecture & Credential Storage

The primary security objective of BotMyPC is safeguarding the host machine and preventing unauthorized access or credential exfiltration.

### 1. Dual-Tier Secure Credential Storage (`credentials.py`)

Telegram Bot tokens and Master User IDs are sensitive secrets. They are never stored in plain text, environment variables, or insecure configuration files.

- **Primary Storage — Windows Credential Manager (`keyring`)**:
  - The application stores the Telegram Bot API Token and Master User ID directly in the native Windows Credential Manager vault using the Windows Credential Management API.
  - Secrets are isolated under the application service identifier (`BotMyPC`) within the user's secure Windows account session.

- **Secondary Encrypted Fallback — Windows DPAPI + AES-128-CBC / HMAC-SHA256 (`Fernet`)**:
  - If Windows Credential Manager is unavailable or disabled, the application switches to an encrypted local fallback mechanism stored at `%LOCALAPPDATA%\BotMyPC\credentials.enc`.
  - The payload is encrypted using Fernet (AES-128 in CBC mode with PKCS7 padding and HMAC-SHA256 authenticated integrity).
  - The symmetric encryption key (`credentials.key.dpapi`) is protected using the **Windows Data Protection API (DPAPI)** via `CryptProtectData` (`win32crypt` with a pure `ctypes` fallback to `crypt32.dll`).
  - **Cryptographic User-Binding**: DPAPI derives encryption keys from the logged-in Windows user's password hash and machine LSA secrets. Consequently, the encrypted key file **cannot be decrypted by any other user on the same machine, nor if copied to another computer**.

- **Token Masking & Anti-Leak Logging (`logging_config.py`)**:
  - The Bot Token is never rendered in full in the GUI, application logs, exception tracebacks, or Telegram responses.
  - A custom regex log filter automatically redacts token patterns, masking them as `123456...WXYZ`.
  - GUI inputs mask the token field (`show="*"`) and display only masked previews.

### 2. Centralized Gateway Authorization (`security.py`)

- **Strict Master User ID Binding**: Every incoming update is evaluated by a single gatekeeper (`SecurityGateway`). If the sender's Telegram numeric User ID does not strictly match the configured Master ID, the message is dropped immediately.
- **Private Chat Restriction**: Only updates originating from private 1-on-1 chats (`ChatType.PRIVATE`) are accepted. Channel posts, group messages, and edited messages (`edited_message`) are discarded at ingestion.
- **Anti-Flood & Duplicate Rejection**: Commands identical to a previous request from the user within a 5.0-second sliding window are ignored to prevent accidental double-execution.

### 3. Execution Safety & Zero Arbitrary Shell Execution

- The application contains **no dynamic evaluation** (`eval()`, `exec()`, or string concatenation passed to `subprocess.Popen(shell=True)`).
- Every accepted command maps to an immutable, predefined handler registered in `command_registry.py`.

---

## ⚡ Core Features

- **Cyberpunk Dark GUI (CustomTkinter)**:
  - Fixed 800x600 dark interface (`#0A0A0A`) with thread-safe Log Terminal updating via `queue.Queue`.
  - Status indicators displaying lifecycle state (`STOPPED`, `STARTING`, `RUNNING`, `STOPPING`, `ERROR`).
  - High-DPI vertically-aligned button icons with separate asset scaling (`assets/icons/`).

- **Multilingual Support (i18n)**:
  - Built-in support for **English (default)**, **German**, **Spanish**, **Italian**, and **French**.
  - Dynamic runtime switching without restart via the GUI Language dialog (`🌐 Language`).
  - Selection persists across reboots in `%LOCALAPPDATA%\BotMyPC\settings.json`.
  - **Extensible via JSON**: Community translators can add new languages simply by dropping a JSON file into `locales/` without modifying Python code (see [`locales/README.md`](file:///d:/dev/SD%20-%20BotMyPC/locales/README.md)).

- **Outlook Mail Notification Monitor (`outlook_monitor.py`)**:
  - Connects to Microsoft Outlook via MAPI COM (`win32com.client`).
  - Polls the Inbox for unread emails and matches subjects against configured keywords.
  - Sends immediate Telegram alerts containing sender, subject, and timestamp when keywords match.
  - Keywords are persisted per-user in `%LOCALAPPDATA%\BotMyPC\mail_notify_config.json`.

- **System Tray & Clean Shutdown (`tray.py`, `main.py`)**:
  - Minimizes to the Windows Notification Area (System Tray) using `pystray` and `Pillow`.
  - Coordinated graceful shutdown handler ensuring async loops, background threads, and tray icons stop cleanly.

- **Windows 11 Startup Integration (`startup.py`)**:
  - Toggles autostart via Windows Registry (`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`).
  - Requires no administrative (UAC) elevation.

---

## 📋 Available Commands

Commands are case-insensitive and support both `/command` and `command` syntax:

| Command | Category | Description | Safety Constraints |
| :--- | :--- | :--- | :--- |
| `/status` | Information | System metrics (CPU%, RAM%, uptime, startup status, mail monitor) | Read-only |
| `/ping` | Information | Connectivity and system responsiveness check with host timestamp | Read-only |
| `/help` | Information | Dynamically generated list of registered commands and descriptions | Read-only |
| `/out` | System | Locks the Windows workstation session (`LockWorkStation`) | Equivalent to `Win + L` |
| `/firefox` | Application | Launches Mozilla Firefox (resolved dynamically from registry) | Isolated process spawn |
| `/outlook` | Application | Launches Microsoft Outlook (Click-to-Run or standard install) | Isolated process spawn |
| `/spegni` | System Control | Schedules system shutdown (`shutdown /s /t 10`) | 10-second grace period; abortable via `/annulla` |
| `/riavvia` | System Control | Schedules system reboot (`shutdown /r /t 10`) | 10-second grace period; abortable via `/annulla` |
| `/annulla` | System Control | Aborts any scheduled shutdown or reboot (`shutdown /a`) | Safely handles absence of pending actions |
| `/panic` | Emergency | Terminates non-essential user applications | Two-stage confirmation (`/panic conferma`) within 15s; system process blacklist protected |

### The Two-Stage `/panic` Safeguard
1. User sends `/panic`.
2. The bot warns the user and demands confirmation within 15 seconds.
3. User sends `/panic conferma`.
4. The process iterates through user tasks via `psutil`, cleanly terminating user applications while strictly exempting protected OS processes (`explorer.exe`, `dwm.exe`, `svchost.exe`, `csrss.exe`, etc.) and the bot's own process.

---

## 📁 Repository Structure

```text
SD - BotMyPC/
├── main.py                     # Application entry point, thread coordinator, shutdown handler
├── config.py                   # Constants, directories, cyberpunk styling palette
├── logging_config.py           # RotatingFileHandler with token masking filter
├── credentials.py              # Windows Credential Manager & DPAPI/Fernet storage tier
├── security.py                 # SecurityGateway, Master ID validation, anti-flood limiter
├── command_registry.py         # Registry pattern implementation for bot commands
├── telegram_bot.py             # Dedicated asyncio background thread & Telegram Bot engine
├── startup.py                  # Windows Registry Run key manager (HKCU)
├── tray.py                     # Pystray system tray integration
├── gui.py                      # CustomTkinter GUI layout, modals, and thread-safe terminal
├── i18n.py                     # Internationalization engine (EN, DE, ES, IT, FR + JSON loader)
├── icons.py                    # CTkImage icon cache & Pillow renderer
├── outlook_monitor.py          # Outlook MAPI COM mail watcher & keyword notification engine
│
├── commands/
│   ├── __init__.py             # Auto-registers commands into the central registry
│   ├── system.py               # Status, ping, help, out, spegni, riavvia, annulla handlers
│   ├── applications.py         # Firefox & Outlook dynamic path resolution launchers
│   └── processes.py            # Panic process terminator with OS critical blacklist
│
├── locales/
│   ├── template.json           # Template translation schema for adding new languages
│   └── README.md               # Guide for community translators
│
├── assets/
│   ├── tray_icon.ico           # Windows application & tray icon
│   └── icons/                  # 48x48 RGBA pre-rendered button icons
│
├── tests/
│   ├── test_security.py        # Gateway, authorization, and flood suppression tests
│   ├── test_commands.py        # Mocked system and subprocess execution tests
│   ├── test_registry.py        # Command registration and dynamic help generation tests
│   ├── test_credentials.py     # Keyring, DPAPI encryption fallback, and token masking tests
│   └── test_i18n.py            # Key parity, persistence, and dynamic JSON locale tests
│
├── botmypc.spec                # PyInstaller standalone executable specification
├── build_exe.py                # Build automation script for Windows binary compilation
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
└── README.md                   # Technical documentation
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Operating System**: Windows 11 / Windows 10 (64-bit)
- **Python**: 3.11 or later (tested up to Python 3.14)
- **Active Internet Connection** (for Telegram Bot API polling)

### 1. Clone the Repository
```powershell
git clone https://github.com/tuo-username/SD-BotMyPC.git
cd SD-BotMyPC
```

### 2. Set Up Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## ⚙️ Initial Configuration

1. **Create a Telegram Bot**:
   - Talk to [@BotFather](https://t.me/BotFather) on Telegram and send `/newbot`.
   - Copy the generated HTTP API Token (e.g., `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567`).

2. **Retrieve Your Telegram User ID**:
   - Message [@userinfobot](https://t.me/userinfobot) on Telegram to get your numeric ID (e.g., `987654321`).

3. **Configure via GUI**:
   - Run the application:
     ```powershell
     python main.py
     ```
   - Click **🔑 API Token**, paste your token, and save.
   - Click **👑 Master ID**, enter your numeric ID, and save.
   - Click **Start Bot** to begin listening for commands.

---

## 🧪 Running Automated Tests

The test suite runs against mocked system environments to ensure no unintended commands execute during test runs:

```powershell
python -m pytest -v
```

All 34 test cases cover:
- Gateway authorization and reject unknown Telegram senders
- Duplicate and flood suppression logic
- Command dispatching and registry validation
- Keyring storage, DPAPI encryption fallback, and token masking
- Language key completeness across all 5 languages and dynamic locale loading

---

## 📦 Building Standalone Executable (.exe)

Compile BotMyPC into a standalone windowed Windows `.exe` using PyInstaller:

```powershell
python build_exe.py
```

The resulting binary will be output to:
```text
dist/BotMyPC.exe
```

---

## 📄 License & Attribution

Distributed under the **MIT License**.

- **No Liability ("AS IS")**: The software is provided without warranty of any kind. The author assumes no liability for damages, system shutdowns, or data loss arising from its use.
- **Attribution Obligation**: Any forks, redistributions, or derivative works must retain the original copyright notice:

```text
Copyright (c) 2026 Stefano D'Angelo (AKA Lemonice)
```

See [`LICENSE`](file:///d:/dev/SD%20-%20BotMyPC/LICENSE) for the full text.
