"""
Configuration module for BotMyPC (telegram_remote_control).
Centralizes all non-sensitive configuration settings, styling constants,
timeouts, and application directory paths.
"""

from pathlib import Path
import os
import sys

# Application Metadata
APP_NAME: str = "BotMyPC"
APP_DISPLAY_TITLE: str = "BotMyPC — Telegram Remote Controller"
APP_VERSION: str = "1.0.0"

# Application Directories and Paths
if getattr(sys, "frozen", False):
    BASE_DIR: Path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    EXE_DIR: Path = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent
    EXE_DIR = BASE_DIR

ASSETS_DIR: Path = BASE_DIR / "assets"
ICON_PATH: Path = ASSETS_DIR / "tray_icon.ico"

# Local user data directory: %LOCALAPPDATA%\BotMyPC
LOCAL_DATA_DIR: Path = Path(os.environ.get("LOCALAPPDATA", Path.home())) / APP_NAME
LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE_PATH: Path = LOCAL_DATA_DIR / "botmypc.log"
SETTINGS_FILE_PATH: Path = LOCAL_DATA_DIR / "settings.json"
FALLBACK_CREDENTIALS_FILE: Path = LOCAL_DATA_DIR / "credentials.enc"
FALLBACK_KEY_FILE: Path = LOCAL_DATA_DIR / "credentials.key.dpapi"
ICONS_DIR: Path = ASSETS_DIR / "icons"

# Logging Settings
LOG_MAX_BYTES: int = 1 * 1024 * 1024  # 1 MB
LOG_BACKUP_COUNT: int = 5
MAX_LOG_MESSAGE_PREVIEW_LEN: int = 40  # Truncate user text in logs to preserve privacy

# Security & Command Execution Constraints
SHUTDOWN_DELAY_SECONDS: int = 10
DUPLICATE_WINDOW_SECONDS: float = 5.0
PANIC_CONFIRMATION_SECONDS: float = 15.0

# GUI Dimensions & Theme Colors (Matrix/Cyberpunk Palette)
GUI_WIDTH: int = 800
GUI_HEIGHT: int = 600
GUI_BG_COLOR: str = "#0A0A0A"
GUI_PANEL_BG: str = "#121212"
GUI_TERMINAL_BG: str = "#000000"
GUI_ACCENT_COLOR: str = "#00FF66"
GUI_ACCENT_HOVER: str = "#00CC52"
GUI_TEXT_COLOR: str = "#E0E0E0"
GUI_MUTED_TEXT: str = "#7A7A7A"
GUI_DANGER_COLOR: str = "#FF3366"
GUI_DANGER_HOVER: str = "#CC2952"
GUI_WARNING_COLOR: str = "#FFB300"
GUI_BORDER_COLOR: str = "#1F3D2B"

# Polling Interval (ms) for GUI Queue Consumer
GUI_QUEUE_POLL_INTERVAL_MS: int = 100

# Windows Registry Run Key
WINDOWS_RUN_REG_KEY: str = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_REG_NAME: str = APP_NAME
