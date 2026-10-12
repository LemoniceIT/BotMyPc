# BotMyPC

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/LemoniceIT/BotMyPc/blob/main/LICENSE)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078D6)

Lightweight Windows desktop app for monitoring and controlling your PC through a private Telegram bot.

BotMyPC is not a remote shell. It uses a closed command registry: every message maps to a predefined handler. There is no path from Telegram to an arbitrary command line.

## Security

**Encrypted credentials.** The bot token and master user ID are stored in Windows Credential Manager. If that store is unavailable, they fall back to a file encrypted with Windows DPAPI and bound to the signed-in account. Secrets are never written in plain text, and they are masked in logs.

**Private access only.** The bot accepts messages from private chats, and only from the configured master Telegram user ID. Messages from other users, groups, or channels are discarded before they are handled.

**Closed command registry.** The app does not use `eval()`, `exec()`, or an arbitrary shell. Each command is bound to a fixed handler. Extra arguments are rejected, except for note text and the panic confirmation.

## Features

- **Dark interface.** Built with CustomTkinter. The log view is updated in a thread-safe way, and the status indicator shows `STOPPED`, `RUNNING`, or `ERROR`.
- **Tray and autostart.** The window can minimize to the notification area. Optional startup is registered in the current user's Run key and does not require administrator rights.
- **Languages.** English (default), Italian, German, Spanish, and French are built in and can be switched at runtime. To add another language, drop a translation JSON file into [`locales/`](locales/README.md).
- **Outlook monitor.** Optional, and off by default. When enabled from the interface, it polls Microsoft Outlook through MAPI for subject keywords and sends a Telegram alert.
- **Guarded panic mode.** `/panic` does not shut the PC down. It closes non-essential user applications only after a second message, `/panic confirm` or `/panic conferma`, sent within 15 seconds. Critical processes such as `explorer.exe` and `svchost.exe` are left running.

## Commands

Commands are case-insensitive. A leading `/` is optional (`/status` and `status` are the same).

| Command | What it does |
| --- | --- |
| `/status` | Reports CPU, memory, uptime, autostart state, and active monitors. |
| `/ping` | Checks that the PC is online and responsive. |
| `/help` | Lists the registered commands. |
| `/out` | Locks the Windows session, equivalent to `Win` + `L`. |
| `/firefox` | Starts Mozilla Firefox, if it is installed. |
| `/outlook` | Starts Microsoft Outlook, if it is installed. |
| `/shutdown` | Schedules shutdown in 10 seconds. Cancel it with `/annulla`. |
| `/restart` | Schedules a reboot in 10 seconds. Cancel it with `/annulla`. |
| `/annulla` | Cancels a pending shutdown or reboot. |
| `/panic` | Closes non-essential user applications. Send `/panic`, then `/panic confirm` within 15 seconds. `/panic conferma` is also accepted. |
| `note: <text>` | Saves the text to `%LOCALAPPDATA%\BotMyPC\notes\` and opens it in Notepad. `note <text>` works as well. |

`/annulla` is the registered name of the cancel command. `/cancel` is not recognized.

## Repository layout

```text
BotMyPc/
├── main.py                 # Entry point and shutdown handling
├── config.py               # Constants and UI palette
├── logging_config.py       # Log rotation and token masking
├── credentials.py          # Credential Manager and DPAPI storage
├── security.py             # Authorization, parsing, and panic confirmation
├── command_registry.py     # Closed command registry
├── telegram_bot.py         # Telegram polling loop
├── startup.py              # Per-user autostart
├── tray.py                 # Notification-area icon
├── gui.py                  # CustomTkinter interface
├── i18n.py                 # Built-in translations
├── icons.py                # Icon cache
├── outlook_monitor.py      # Optional Outlook watcher
├── commands/               # System, application, and panic handlers
├── locales/                # Template for additional languages
├── assets/                 # Interface icons
├── ico/                    # Application icon
├── tests/                  # Unit tests
├── botmypc.spec            # PyInstaller spec
├── build_exe.py            # Build script
├── requirements.txt
├── LICENSE
└── README.md
```

## Requirements

- Windows 10 or Windows 11 (64-bit)
- Python 3.11 or later, only if you run from source
- An internet connection so the bot can reach the Telegram API

## Run from source

```powershell
git clone https://github.com/LemoniceIT/BotMyPc.git
cd BotMyPc

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python main.py
```

On first launch, set the bot token from [@BotFather](https://t.me/BotFather) and your numeric user ID from [@userinfobot](https://t.me/userinfobot), then start the bot.

## Standalone executable

Build on Windows, from the project directory, after installing the requirements:

```powershell
python build_exe.py
```

PyInstaller writes `dist/BotMyPC.exe`.

Published binaries, when available, are on the [Releases](https://github.com/LemoniceIT/BotMyPc/releases) page.

## Tests

```powershell
python -m pytest -v
```

`pytest` is included in `requirements.txt`.

## License

Released under the [MIT License](LICENSE).