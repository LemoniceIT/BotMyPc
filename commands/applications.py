"""
Application launchers for BotMyPC:
- firefox: launches Mozilla Firefox
- outlook: launches Microsoft Outlook

Dynamically resolves application paths using:
1. Windows Registry App Paths (HKLM and HKCU)
2. shutil.which
3. Standard 64-bit and 32-bit Program Files locations (including Click-to-Run Office)
Never uses shell=True and never accepts external arguments from Telegram.
"""

from __future__ import annotations
import logging
import os
from pathlib import Path
import shutil
import subprocess
from typing import Optional, List
import winreg

from command_registry import CommandResult
from config import APP_NAME
from i18n import t

logger = logging.getLogger(APP_NAME)


def _query_registry_app_path(exe_name: str) -> Optional[str]:
    """Queries Windows Registry App Paths for a registered executable."""
    subkeys = [
        rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}",
        rf"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\{exe_name}",
    ]
    hives = [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]

    for hive in hives:
        for subkey in subkeys:
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    val, _ = winreg.QueryValueEx(key, "")
                    if val and Path(val).exists():
                        return str(Path(val).resolve())
            except OSError:
                continue
    return None


def resolve_firefox_path() -> Optional[str]:
    """Dynamically locates the Firefox executable on Windows."""
    # 1. shutil.which
    found = shutil.which("firefox") or shutil.which("firefox.exe")
    if found and Path(found).exists():
        return str(Path(found).resolve())

    # 2. Registry App Paths
    reg_path = _query_registry_app_path("firefox.exe")
    if reg_path:
        return reg_path

    # 3. Known filesystem locations
    candidates: List[Path] = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Mozilla Firefox" / "firefox.exe",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Mozilla Firefox" / "firefox.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Mozilla Firefox" / "firefox.exe",
    ]
    for p in candidates:
        if p.exists():
            return str(p.resolve())

    return None


def resolve_outlook_path() -> Optional[str]:
    """Dynamically locates Microsoft Outlook (MSI or Click-to-Run) on Windows."""
    # 1. shutil.which
    found = shutil.which("outlook") or shutil.which("outlook.exe")
    if found and Path(found).exists():
        return str(Path(found).resolve())

    # 2. Registry App Paths
    reg_path = _query_registry_app_path("OUTLOOK.EXE") or _query_registry_app_path("outlook.exe")
    if reg_path:
        return reg_path

    # 3. Known filesystem locations (MSI, Click-to-Run Office16, Office15)
    prog_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    prog_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")

    candidates: List[Path] = [
        Path(prog_files) / "Microsoft Office" / "root" / "Office16" / "OUTLOOK.EXE",
        Path(prog_files_x86) / "Microsoft Office" / "root" / "Office16" / "OUTLOOK.EXE",
        Path(prog_files) / "Microsoft Office" / "Office16" / "OUTLOOK.EXE",
        Path(prog_files_x86) / "Microsoft Office" / "Office16" / "OUTLOOK.EXE",
        Path(prog_files) / "Microsoft Office" / "Office15" / "OUTLOOK.EXE",
        Path(prog_files_x86) / "Microsoft Office" / "Office15" / "OUTLOOK.EXE",
    ]
    for p in candidates:
        if p.exists():
            return str(p.resolve())

    # 4. Check New Outlook for Windows (olk.exe)
    olk_found = shutil.which("olk") or shutil.which("olk.exe")
    if olk_found and Path(olk_found).exists():
        return str(Path(olk_found).resolve())

    return None


def launch_firefox() -> CommandResult:
    """Launches Mozilla Firefox if installed."""
    exe = resolve_firefox_path()
    if not exe:
        logger.warning(t("log_firefox_not_found"))
        return CommandResult(
            success=False,
            message="❌ Firefox non trovato sul sistema.",
            log_message=t("log_msg_firefox_not_found"),
        )

    try:
        # Launch detached without shell=True
        subprocess.Popen([exe], close_fds=True)
        return CommandResult(
            success=True,
            message="🌐 Avvio di Mozilla Firefox completato.",
            log_message=t("log_msg_firefox_launched", exe=exe),
        )
    except Exception as e:
        logger.exception(t("log_firefox_start_error", exe=exe))
        return CommandResult(
            success=False,
            message=f"❌ Errore durante l'avvio di Firefox: {str(e)}",
            log_message=t("log_msg_firefox_error", e=e),
        )


def launch_outlook() -> CommandResult:
    """Launches Microsoft Outlook if installed."""
    exe = resolve_outlook_path()
    if not exe:
        logger.warning(t("log_outlook_not_found"))
        return CommandResult(
            success=False,
            message="❌ Outlook non trovato sul sistema.",
            log_message=t("log_msg_outlook_not_found"),
        )

    try:
        # Launch detached without shell=True
        subprocess.Popen([exe], close_fds=True)
        return CommandResult(
            success=True,
            message="📧 Avvio di Microsoft Outlook completato.",
            log_message=t("log_msg_outlook_launched", exe=exe),
        )
    except Exception as e:
        logger.exception(t("log_outlook_start_error", exe=exe))
        return CommandResult(
            success=False,
            message=f"❌ Errore durante l'avvio di Outlook: {str(e)}",
            log_message=t("log_msg_outlook_error", e=e),
        )


def open_notepad_note(note_text: str) -> CommandResult:
    """
    Saves the provided text into a dedicated note file and opens it in Notepad.
    """
    cleaned = (note_text or "").strip()
    if not cleaned:
        return CommandResult(
            success=False,
            message="❌ Il testo della nota non può essere vuoto.",
            log_message=t("log_msg_note_empty"),
        )

    try:
        import datetime
        from config import LOCAL_DATA_DIR

        notes_dir = LOCAL_DATA_DIR / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        note_file = notes_dir / f"nota_{timestamp}.txt"
        note_file.write_text(cleaned, encoding="utf-8")

        # Find notepad executable
        notepad_exe = shutil.which("notepad.exe") or "notepad.exe"

        # Launch detached without shell=True
        subprocess.Popen([notepad_exe, str(note_file.resolve())], close_fds=True)

        preview = cleaned[:50] + ("..." if len(cleaned) > 50 else "")
        msg = (
            "📝 *Blocco Note aperto sul PC!*\n"
            f"📄 Contenuto: _{preview}_\n"
            f"📁 Salvato in: `{note_file.name}`"
        )
        return CommandResult(
            success=True,
            message=msg,
            log_message=t("log_msg_note_opened", preview=preview),
        )
    except Exception as e:
        logger.exception(t("log_notepad_note_error"))
        return CommandResult(
            success=False,
            message=f"❌ Errore durante l'apertura di Notepad: {str(e)}",
            log_message=t("log_msg_note_error", e=e),
        )
