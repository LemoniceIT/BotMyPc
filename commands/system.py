"""
System commands for BotMyPC:
- shutdown: schedules shutdown with mandatory 10-second delay
- restart: schedules restart with mandatory 10-second delay
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
            _pending_system_action = t("telegram_action_shutdown")
            _pending_action_time = time.time()
            msg = t(
                "telegram_shutdown_sched",
                delay=delay_str,
            )
            return CommandResult(
                success=True,
                message=msg,
                log_message=t("log_msg_shutdown_scheduled", delay=delay_str),
            )
        else:
            err = res.stderr.strip() or t("log_msg_unknown_windows_error")
            return CommandResult(
                success=False,
                message=t("telegram_shutdown_error", err=err),
                log_message=t("log_msg_shutdown_error", err=err),
                error_code=res.returncode,
            )
    except Exception as e:
        logger.exception(t("log_error_shutdown_call"))
        return CommandResult(
            success=False,
            message=t("telegram_shutdown_internal_error", e=str(e)),
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
            _pending_system_action = t("telegram_action_restart")
            _pending_action_time = time.time()
            msg = t(
                "telegram_restart_sched",
                delay=delay_str,
            )
            return CommandResult(
                success=True,
                message=msg,
                log_message=t("log_msg_restart_scheduled", delay=delay_str),
            )
        else:
            err = res.stderr.strip() or t("log_msg_unknown_windows_error")
            return CommandResult(
                success=False,
                message=t("telegram_restart_error", err=err),
                log_message=t("log_msg_restart_error", err=err),
                error_code=res.returncode,
            )
    except Exception as e:
        logger.exception(t("log_error_restart_call"))
        return CommandResult(
            success=False,
            message=t("telegram_restart_internal_error", e=str(e)),
            log_message=t("log_msg_restart_exception", e=e),
        )


def abort_shutdown() -> CommandResult:
    """Aborts any scheduled shutdown or restart."""
    global _pending_system_action, _pending_action_time
    cmd = ["shutdown", "/a"]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            previous_action = _pending_system_action or t("telegram_action_unknown")
            _pending_system_action = None
            _pending_action_time = 0.0
            msg = t("telegram_abort_done", action=previous_action)
            return CommandResult(
                success=True,
                message=msg,
                log_message=t("log_msg_abort_done"),
            )
        else:
            # Code 1116 means no shutdown was in progress
            _pending_system_action = None
            _pending_action_time = 0.0
            msg = t("telegram_abort_none")
            return CommandResult(
                success=True,
                message=msg,
                log_message=t("log_msg_abort_none"),
            )
    except Exception as e:
        logger.exception(t("log_error_shutdown_abort"))
        return CommandResult(
            success=False,
            message=t("telegram_abort_internal_error", e=str(e)),
            log_message=t("log_msg_abort_exception", e=e),
        )


def lock_workstation() -> CommandResult:
    """Locks the Windows workstation via user32.LockWorkStation."""
    try:
        result = ctypes.windll.user32.LockWorkStation()
        if result != 0:
            return CommandResult(
                success=True,
                message=t("telegram_lock_success"),
                log_message=t("log_msg_lock_success"),
            )
        else:
            err_code = ctypes.GetLastError()
            return CommandResult(
                success=False,
                message=t("telegram_lock_error", code=err_code),
                log_message=t("log_msg_lock_failed", code=err_code),
                error_code=err_code,
            )
    except Exception as e:
        logger.exception(t("log_error_lockworkstation"))
        return CommandResult(
            success=False,
            message=t("telegram_lock_internal_error", e=str(e)),
            log_message=t("log_msg_lock_exception", e=e),
        )


def ping() -> CommandResult:
    """Returns PONG, PC online status, and machine uptime."""
    try:
        boot_ts = psutil.boot_time()
        uptime_delta = datetime.timedelta(seconds=int(time.time() - boot_ts))
        uptime_str = str(uptime_delta)
    except Exception:
        uptime_str = t("telegram_status_pending_none")

    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    msg = t("telegram_ping", time=now_str, uptime=uptime_str)
    return CommandResult(
        success=True,
        message=msg,
        log_message=t("log_msg_ping", uptime=uptime_str),
    )


def status() -> CommandResult:
    """Returns detailed operational status of the PC and bot."""
    # Check Master ID
    master_configured = credentials.load_credential(credentials.KEY_MASTER_USER_ID) is not None
    master_status = "CONFIGURED" if master_configured else "NOT_CONFIGURED"

    # Check Windows Startup
    from startup import is_startup_enabled
    startup_enabled = is_startup_enabled()
    startup_status = "ENABLED" if startup_enabled else "DISABLED"

    # System Uptime and Metrics
    try:
        boot_ts = psutil.boot_time()
        uptime_delta = datetime.timedelta(seconds=int(time.time() - boot_ts))
        uptime_str = str(uptime_delta)
        cpu_usage = f"{psutil.cpu_percent(interval=None)}%"
        ram = psutil.virtual_memory()
        ram_usage = f"{ram.percent}% ({ram.used // (1024*1024)}MB / {ram.total // (1024*1024)}MB)"
    except Exception:
        uptime_str = "N/A"
        cpu_usage = "N/A"
        ram_usage = "N/A"

    # Pending action check
    global _pending_system_action, _pending_action_time
    if _pending_system_action and (time.time() - _pending_action_time) < SHUTDOWN_DELAY_SECONDS:
        pending_str = t("telegram_status_pending_active", action=_pending_system_action)
    else:
        pending_str = t("telegram_status_pending_none")

    total_cmds = len(REGISTRY.list_commands())

    lines = [
        t("telegram_status_header"),
        t("telegram_status_separator"),
        t("telegram_status_bot"),
        t("telegram_status_master", status=master_status),
        t("telegram_status_startup", status=startup_status),
        t("telegram_status_tray"),
        t("telegram_status_version", version=APP_VERSION),
        t("telegram_status_cmd_count", count=total_cmds),
        t("telegram_status_subsep"),
        t("telegram_status_uptime", uptime=uptime_str),
        t("telegram_status_metrics", cpu=cpu_usage, ram=ram_usage),
        pending_str,
        t("telegram_status_separator"),
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
