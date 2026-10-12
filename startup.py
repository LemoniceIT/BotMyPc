"""
Windows Startup Manager for BotMyPC.

Manages automatic launch on Windows boot using HKCU Run registry:
HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run

Works seamlessly both in development mode (python main.py) and
in PyInstaller frozen binary mode (botmypc.exe).
Does not require administrator privileges.
"""

from __future__ import annotations
import logging
import os
from pathlib import Path
import sys
import winreg

from config import APP_NAME, WINDOWS_RUN_REG_KEY, STARTUP_REG_NAME
from i18n import t

logger = logging.getLogger(APP_NAME)


def get_startup_command() -> str:
    """
    Returns the command line string to register in the Windows Run key.
    Handles both frozen PyInstaller executable and raw Python script execution.
    """
    if getattr(sys, "frozen", False):
        # Running as compiled .exe
        exe_path = Path(sys.executable).resolve()
        return f'"{exe_path}"'
    else:
        # Running as python script
        py_exe = Path(sys.executable).resolve()
        main_py = Path(__file__).resolve().parent / "main.py"
        return f'"{py_exe}" "{main_py}"'


def is_startup_enabled() -> bool:
    """
    Checks if BotMyPC is registered in HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run.
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            WINDOWS_RUN_REG_KEY,
            0,
            winreg.KEY_READ,
        ) as key:
            val, _ = winreg.QueryValueEx(key, STARTUP_REG_NAME)
            return bool(val)
    except OSError:
        return False


def enable_startup() -> bool:
    """
    Registers BotMyPC to launch automatically on user logon.
    """
    cmd = get_startup_command()
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            WINDOWS_RUN_REG_KEY,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, STARTUP_REG_NAME, 0, winreg.REG_SZ, cmd)
        logger.info(t("log_startup_enabled", cmd=cmd))
        return True
    except Exception as e:
        logger.error(t("log_startup_enable_error", e=e))
        return False


def disable_startup() -> bool:
    """
    Removes BotMyPC from the Windows Run registry key.
    """
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            WINDOWS_RUN_REG_KEY,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            try:
                winreg.DeleteValue(key, STARTUP_REG_NAME)
                logger.info(t("log_startup_disabled"))
                return True
            except FileNotFoundError:
                # Value was already not present
                return True
    except Exception as e:
        logger.error(t("log_startup_disable_error", e=e))
        return False


def toggle_startup(enable: bool) -> bool:
    """Helper to set startup state."""
    return enable_startup() if enable else disable_startup()
