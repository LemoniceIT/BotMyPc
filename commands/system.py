"""
System commands for BotMyPC:
- spegni: schedules shutdown with mandatory 10-second delay
- riavvia: schedules restart with mandatory 10-second delay
- annulla: aborts any pending shutdown or restart
- out: locks workstation via ctypes user32.LockWorkStation
- ping: returns latency pong and uptime
- status: detailed PC and bot operational status
- help: dynamic command help
"""

from __future__ import annotations
import ctypes
import datetime
import logging
import subprocess
import time
from typing import Optional

import psutil

from command_registry import CommandResult, REGISTRY
from config import APP_NAME, APP_VERSION, SHUTDOWN_DELAY_SECONDS
from i18n import t
import credentials

logger = logging.getLogger(APP_NAME)

# Track pending shutdown/reboot operations
_pending_system_action: Optional[str] = None
_pending_action_time: float = 0.0


def schedule_shutdown() -> CommandResult:
    """Schedules system shutdown in SHUTDOWN_DELAY_SECONDS seconds."""
    global _pending_system_action, _pending_action_time
    delay_str = str(SHUTDOWN_DELAY_SECONDS)
    cmd = ["shutdown", "/s", "/t", delay_str]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            _pending_system_action = "spegnimento"
            _pending_action_time = time.time()
            msg = (
                f"🛑 Spegnimento programmato tra {delay_str} secondi.\n"
                f"Usa `/annulla` per interromperlo immediatamente."
            )
            return CommandResult(
                success=True,
                message=msg,
                log_message=t("log_msg_shutdown_scheduled", delay=delay_str),
            )
        else:
            err = res.stderr.strip() or "Errore sconosciuto di Windows."
            return CommandResult(
                success=False,
                message=f"❌ Impossibile programmare lo spegnimento: {err}",
                log_message=t("log_msg_shutdown_error", err=err),
                error_code=res.returncode,
            )
    except Exception as e:
        logger.exception(t("log_error_shutdown_call"))
        return CommandResult(
            success=False,
            message=f"❌ Errore interno durante lo spegnimento: {str(e)}",
            log_message=t("log_msg_shutdown_exception", e=e),
        )


def schedule_restart() -> CommandResult:
    """Schedules system restart in SHUTDOWN_DELAY_SECONDS seconds."""
    global _pending_system_action, _pending_action_time
    delay_str = str(SHUTDOWN_DELAY_SECONDS)
    cmd = ["shutdown", "/r", "/t", delay_str]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            _pending_system_action = "riavvio"
            _pending_action_time = time.time()
            msg = (
                f"🔄 Riavvio programmato tra {delay_str} secondi.\n"
                f"Usa `/annulla` per interromperlo immediatamente."
            )
            return CommandResult(
                success=True,
                message=msg,
                log_message=t("log_msg_restart_scheduled", delay=delay_str),
            )
        else:
            err = res.stderr.strip() or "Errore sconosciuto di Windows."
            return CommandResult(
                success=False,
                message=f"❌ Impossibile programmare il riavvio: {err}",
                log_message=t("log_msg_restart_error", err=err),
                error_code=res.returncode,
            )
    except Exception as e:
        logger.exception(t("log_error_restart_call"))
        return CommandResult(
            success=False,
            message=f"❌ Errore interno durante il riavvio: {str(e)}",
            log_message=t("log_msg_restart_exception", e=e),
        )


def abort_shutdown() -> CommandResult:
    """Aborts any scheduled shutdown or restart."""
    global _pending_system_action, _pending_action_time
    cmd = ["shutdown", "/a"]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            previous_action = _pending_system_action or "operazione"
            _pending_system_action = None
            _pending_action_time = 0.0
            msg = f"✅ Operazione di {previous_action} annullata con successo."
            return CommandResult(
                success=True,
                message=msg,
                log_message=t("log_msg_abort_done"),
            )
        else:
            # Code 1116 means no shutdown was in progress
            _pending_system_action = None
            _pending_action_time = 0.0
            msg = "ℹ️ Nessuna operazione di spegnimento o riavvio attiva da annullare."
            return CommandResult(
                success=True,
                message=msg,
                log_message=t("log_msg_abort_none"),
            )
    except Exception as e:
        logger.exception(t("log_error_shutdown_abort"))
        return CommandResult(
            success=False,
            message=f"❌ Errore interno durante l'annullamento: {str(e)}",
            log_message=t("log_msg_abort_exception", e=e),
        )


def lock_workstation() -> CommandResult:
    """Locks the Windows workstation via user32.LockWorkStation."""
    try:
        result = ctypes.windll.user32.LockWorkStation()
        if result != 0:
            return CommandResult(
                success=True,
                message="🔒 Postazione Windows bloccata.",
                log_message=t("log_msg_lock_success"),
            )
        else:
            err_code = ctypes.GetLastError()
            return CommandResult(
                success=False,
                message=f"❌ Errore blocco postazione (codice: {err_code}).",
                log_message=t("log_msg_lock_failed", code=err_code),
                error_code=err_code,
            )
    except Exception as e:
        logger.exception(t("log_error_lockworkstation"))
        return CommandResult(
            success=False,
            message=f"❌ Errore durante il blocco postazione: {str(e)}",
            log_message=t("log_msg_lock_exception", e=e),
        )


def ping() -> CommandResult:
    """Returns PONG, PC online status, and machine uptime."""
    try:
        boot_ts = psutil.boot_time()
        uptime_delta = datetime.timedelta(seconds=int(time.time() - boot_ts))
        uptime_str = str(uptime_delta)
    except Exception:
        uptime_str = "Sconosciuto"

    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = (
        "🏓 *PONG*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💻 PC Online e reattivo\n"
        f"⏱️ Ora locale PC: `{now_str}`\n"
        f"⏳ Uptime sistema: `{uptime_str}`"
    )
    return CommandResult(
        success=True,
        message=msg,
        log_message=t("log_msg_ping", uptime=uptime_str),
    )


def status() -> CommandResult:
    """Returns detailed operational status of the PC and bot."""
    # Check Master ID
    master_configured = credentials.load_credential(credentials.KEY_MASTER_USER_ID) is not None
    master_status = "CONFIGURATO" if master_configured else "NON CONFIGURATO"

    # Check Windows Startup
    from startup import is_startup_enabled
    startup_enabled = is_startup_enabled()
    startup_status = "ABILITATO" if startup_enabled else "DISABILITATO"

    # System Uptime and Metrics
    try:
        boot_ts = psutil.boot_time()
        uptime_delta = datetime.timedelta(seconds=int(time.time() - boot_ts))
        uptime_str = str(uptime_delta)
        cpu_usage = f"{psutil.cpu_percent(interval=None)}%"
        ram = psutil.virtual_memory()
        ram_usage = f"{ram.percent}% ({ram.used // (1024*1024)}MB / {ram.total // (1024*1024)}MB)"
    except Exception:
        uptime_str = "N/D"
        cpu_usage = "N/D"
        ram_usage = "N/D"

    # Pending action check
    global _pending_system_action, _pending_action_time
    if _pending_system_action and (time.time() - _pending_action_time) < SHUTDOWN_DELAY_SECONDS:
        pending_str = f"⚠️ In corso ({_pending_system_action.upper()})"
    else:
        pending_str = "Nessuna"

    total_cmds = len(REGISTRY.list_commands())

    lines = [
        "📊 *STATO BOT & SISTEMA*",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "🤖 Telegram Bot: `ONLINE`",
        f"👑 Master User: `{master_status}`",
        f"🚀 Avvio con Windows: `{startup_status}`",
        "🗂️ System Tray: `ATTIVA`",
        f"📦 Versione App: `v{APP_VERSION}`",
        f"📋 Comandi registrati: `{total_cmds}`",
        "───────────────────────────",
        f"⏳ Uptime PC: `{uptime_str}`",
        f"⚡ CPU: `{cpu_usage}` | RAM: `{ram_usage}`",
        f"🛑 Operazione pendente: `{pending_str}`",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    return CommandResult(
        success=True,
        message="\n".join(lines),
        log_message=t("log_msg_status"),
    )


def help_command() -> CommandResult:
    """Generates the command help from REGISTRY."""
    return CommandResult(
        success=True,
        message=REGISTRY.generate_help(),
        log_message=t("log_msg_help"),
    )
