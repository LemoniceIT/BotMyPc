BotMyPC

A lightweight and secure Windows desktop application to monitor and remotely control your PC via a private Telegram Bot.

Built around a closed Command Registry architecture, BotMyPC does not execute arbitrary terminal commands. It strictly runs predefined, validated routines to safely manage system actions, monitor background state, and launch applications without exposing your system to remote shell vulnerabilities.

🔒 Security Architecture

Encrypted Credential Storage: Telegram Bot API tokens and Master User IDs are stored directly in the native Windows Credential Manager vault. If unavailable, an encrypted fallback mechanism uses Windows DPAPI (tied cryptographically to your logged-in Windows account) so secrets are never written in plain text or exposed in logs.

Strict Gateway Authorization: The application accepts incoming messages exclusively from private 1-on-1 chats and strictly filtered by your configured Master Telegram User ID. Requests from unauthorized users, groups, or channels are immediately discarded at ingestion.

Closed Command Registry: No eval(), exec(), or arbitrary shell execution. Every command maps to an immutable, hardcoded handler to prevent remote code execution.

✨ Key Features

Clean Dark GUI: Built with CustomTkinter, offering thread-safe log terminal updates and live status indicators (STOPPED, RUNNING, ERROR).

System Tray & Autostart Integration: Minimizes silently to the Windows Notification Area and supports optional startup on system boot without requiring administrative (UAC) elevation.

Multilingual Support & Extensibility: Native support for English, Italian, German, Spanish, and French with dynamic runtime switching. New languages can be added easily by dropping a custom translation JSON into locales/.

Opt-In Outlook Mail Monitor: An optional email notification watcher disabled by default and activated separately via the GUI. It polls Microsoft Outlook via MAPI COM for custom subject keywords and sends immediate Telegram alerts.

Safeguarded Panic Shutdown: The /panic command features a two-stage confirmation (/panic confirm within 15 seconds) and strictly protects system-critical processes (explorer.exe, svchost.exe, etc.) while closing non-essential user apps.

📋 Available Commands

Commands support both /command and plain command syntax:

/status — System metrics (CPU%, RAM%, uptime, startup state, active monitors).

/ping — Connectivity and system responsiveness check.

/out — Lock the Windows workstation session (Win + L).

/firefox — Launch Mozilla Firefox.

/outlook — Launch Microsoft Outlook.

/shutdown — Schedule system shutdown with a 10-second grace period (abortable via /annulla).

/restart — Schedule system reboot with a 10-second grace period (abortable via /annulla).

/annulla — Abort any pending scheduled shutdown or reboot.

/panic — Terminate non-essential user applications (requires /panic confirm within 15 seconds).

/note [text] — Save text to a local timestamped note file in %LOCALAPPDATA%\BotMyPC\notes\ and open in Notepad.

/help — Display registered commands and descriptions.

📁 Repository Structure

SD - BotMyPC/
├── main.py                     # Entry point, thread coordinator, shutdown handler
├── config.py                   # App constants and UI palette
├── logging_config.py           # Log rotation and token masking filter
├── credentials.py              # Windows Credential Manager & DPAPI storage tier
├── security.py                 # Gateway authorization & Master ID filtering
├── command_registry.py         # Central command registry pattern
├── telegram_bot.py             # Dedicated asyncio Telegram bot loop
├── startup.py                  # Windows Registry autostart manager
├── tray.py                     # System tray integration (pystray)
├── gui.py                      # CustomTkinter interface layout and terminal
├── i18n.py                     # Multilingual translation engine
├── icons.py                    # CTkImage icon cache & Pillow renderer
├── outlook_monitor.py          # Outlook MAPI COM mail notification watcher
├── commands/                   # Command handlers (system, apps, panic)
├── locales/                    # Translation JSON files and schema template
├── assets/                     # Application icons and assets
├── tests/                      # Automated test suite
├── build_exe.py                # PyInstaller build automation script
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation


🚀 Quick Start

Option A: Standalone Executable (Recommended)

Download BotMyPC.exe from the Releases page.

Launch the application and configure your Bot Token (from @BotFather) and Master User ID (from @userinfobot).

Click Start Bot.

Option B: Run from Source

# Clone repository
git clone https://github.com/LemoniceIT/BotMyPC.git
cd BotMyPC

# Set up virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies and start
pip install -r requirements.txt
python main.py


🧪 Running Tests

To run the automated unit test suite:

python -m pytest -v


📦 Building Standalone Executable (.exe)

Compile the application into a single executable file using PyInstaller:

python build_exe.py


The compiled binary will be placed in dist/BotMyPC.exe.

📄 License

Distributed under the MIT License. See LICENSE for details.