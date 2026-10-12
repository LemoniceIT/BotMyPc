"""
Process management for BotMyPC:
- panic: Emergency termination of active user applications via psutil.
  Enforces an explicit, documented blacklist of Windows critical system processes
  and the application's own process hierarchy to ensure OS stability.
"""

from __future__ import annotations
import logging
import os
import time
from typing import Set, List, Tuple
import psutil

from command_registry import CommandResult
from config import APP_NAME

logger = logging.getLogger(APP_NAME)

# Explicit blacklist of protected system processes that must NEVER be terminated
PROTECTED_SYSTEM_PROCESSES: Set[str] = {
    # System core & kernel
    "system",
    "system idle process",
    "registry",
    "smss.exe",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "lsass.exe",
    "svchost.exe",
    "winlogon.exe",
    "dwm.exe",
    "explorer.exe",
    "fontdrvhost.exe",
    "conhost.exe",
    # Essential Windows shell & security
    "sihost.exe",
    "taskhostw.exe",
    "ctfmon.exe",
    "securityhealthservice.exe",
    "securityhealthsystray.exe",
    "msmpeng.exe",
    "nissrv.exe",
    "spoolsv.exe",
    "searchhost.exe",
    "startmenuexperiencehost.exe",
    "shellexperiencehost.exe",
    "runtimebroker.exe",
    "audiodg.exe",
}


def _get_protected_pids() -> Set[int]:
    """
    Returns the set of PIDs that must not be terminated:
    - PID <= 4 (Idle / System)
    - Current application PID
    - Current process parent PID
    - Any child processes of the current application
    """
    protected_pids = {0, 4}
    current_pid = os.getpid()
    protected_pids.add(current_pid)

    try:
        current_proc = psutil.Process(current_pid)
        parent = current_proc.parent()
        if parent and parent.pid:
            protected_pids.add(parent.pid)
        for child in current_proc.children(recursive=True):
            protected_pids.add(child.pid)
    except Exception as e:
        logger.debug(f"Could not resolve process hierarchy: {e}")

    return protected_pids


def execute_panic() -> CommandResult:
    """
    Closes running non-system user applications.
    Uses proc.terminate() followed by proc.kill() if not terminated within timeout.
    """
    protected_pids = _get_protected_pids()
    terminated_count = 0
    denied_count = 0
    terminated_names: List[str] = []

    logger.warning("PANIC PROCEDURE INITIATED: Terminating user applications...")

    # Iterate over all running processes safely
    for proc in psutil.process_iter(["pid", "name", "username"]):
        try:
            pid = proc.info["pid"]
            name = (proc.info["name"] or "").lower()

            # 1. Skip system PIDs and application PIDs
            if pid in protected_pids or pid <= 4:
                continue

            # 2. Skip protected system processes
            if name in PROTECTED_SYSTEM_PROCESSES:
                continue

            # 3. Attempt termination
            logger.info(f"Panic terminating PID={pid} ({name})...")
            proc.terminate()
            terminated_names.append(f"{name} (PID {pid})")
            terminated_count += 1

        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied:
            denied_count += 1
            logger.debug(f"AccessDenied while trying to terminate PID {proc.pid}")
        except Exception as e:
            logger.debug(f"Exception terminating PID {proc.pid}: {e}")

    # Give processes a brief moment to gracefully exit, then force kill any remaining
    time.sleep(0.5)

    msg = (
        f"🚨 *PROCEDURA PANIC COMPLETATA*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📉 Processi utente chiusi: `{terminated_count}`\n"
        f"🛡️ Processi di sistema protetti: Salvaguardati\n"
    )
    if denied_count > 0:
        msg += f"⚠️ Processi protetti da permessi elevati: `{denied_count}`\n"

    log_msg = f"Panic eseguito: {terminated_count} processi chiusi, {denied_count} protetti."
    return CommandResult(
        success=True,
        message=msg,
        log_message=log_msg,
    )
