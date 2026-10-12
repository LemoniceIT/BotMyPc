"""
Unit tests for command handlers with strict OS/subprocess mocking.
Ensures no real shutdowns, restarts, locks, or process terminations happen during testing.
"""

from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess
import pytest

from commands.system import (
    schedule_shutdown,
    schedule_restart,
    abort_shutdown,
    lock_workstation,
    ping,
)
from commands.applications import launch_firefox, launch_outlook
from commands.processes import execute_panic, PROTECTED_SYSTEM_PROCESSES


def test_schedule_shutdown_mocked():
    """Verifies that shutdown is scheduled with mandatory delay and without shell=True."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["shutdown", "/s", "/t", "10"], returncode=0, stdout="", stderr=""
        )

        res = schedule_shutdown()
        assert res.success is True
        assert "10 secondi" in res.message

        # Verify call arguments
        mock_run.assert_called_once()
        call_args, call_kwargs = mock_run.call_args
        assert call_args[0] == ["shutdown", "/s", "/t", "10"]
        assert call_kwargs.get("shell") is not True


def test_schedule_restart_mocked():
    """Verifies that restart is scheduled with mandatory delay and without shell=True."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["shutdown", "/r", "/t", "10"], returncode=0, stdout="", stderr=""
        )

        res = schedule_restart()
        assert res.success is True
        assert "10 secondi" in res.message

        mock_run.assert_called_once()
        call_args, call_kwargs = mock_run.call_args
        assert call_args[0] == ["shutdown", "/r", "/t", "10"]
        assert call_kwargs.get("shell") is not True


def test_abort_shutdown_mocked():
    """Verifies that shutdown /a is called without shell=True and handles missing operations."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["shutdown", "/a"], returncode=0, stdout="", stderr=""
        )

        res = abort_shutdown()
        assert res.success is True
        assert "annullata" in res.message

        mock_run.assert_called_once()
        call_args, call_kwargs = mock_run.call_args
        assert call_args[0] == ["shutdown", "/a"]
        assert call_kwargs.get("shell") is not True


def test_lock_workstation_mocked():
    """Verifies lock_workstation calls ctypes user32.LockWorkStation."""
    with patch("ctypes.windll.user32.LockWorkStation", return_value=1) as mock_lock:
        res = lock_workstation()
        assert res.success is True
        mock_lock.assert_called_once()


def test_ping_command():
    """Verifies ping returns pong and uptime."""
    res = ping()
    assert res.success is True
    assert "PONG" in res.message
    assert "Uptime" in res.message


def test_launch_firefox_not_found():
    with patch("commands.applications.resolve_firefox_path", return_value=None):
        res = launch_firefox()
        assert res.success is False
        assert "non trovato" in res.message.lower()


def test_launch_firefox_success():
    with patch("commands.applications.resolve_firefox_path", return_value=r"C:\Program Files\Mozilla Firefox\firefox.exe"), \
         patch("subprocess.Popen") as mock_popen:
        res = launch_firefox()
        assert res.success is True
        mock_popen.assert_called_once_with([r"C:\Program Files\Mozilla Firefox\firefox.exe"], close_fds=True)


def test_launch_outlook_not_found():
    with patch("commands.applications.resolve_outlook_path", return_value=None):
        res = launch_outlook()
        assert res.success is False
        assert "non trovato" in res.message.lower()


def test_launch_outlook_success():
    with patch("commands.applications.resolve_outlook_path", return_value=r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE"), \
         patch("subprocess.Popen") as mock_popen:
        res = launch_outlook()
        assert res.success is True
        mock_popen.assert_called_once_with([r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE"], close_fds=True)


def test_execute_panic_critical_blacklist():
    """
    Verifies that execute_panic skips blacklisted system processes
    and only terminates user application processes.
    """
    # Create fake processes
    p_system = MagicMock()
    p_system.info = {"pid": 4, "name": "System", "username": "SYSTEM"}

    p_dwm = MagicMock()
    p_dwm.info = {"pid": 111, "name": "dwm.exe", "username": "SYSTEM"}

    p_explorer = MagicMock()
    p_explorer.info = {"pid": 222, "name": "explorer.exe", "username": "User"}

    p_notepad = MagicMock()
    p_notepad.info = {"pid": 3333, "name": "notepad.exe", "username": "User"}

    fake_processes = [p_system, p_dwm, p_explorer, p_notepad]

    with patch("psutil.process_iter", return_value=fake_processes), \
         patch("commands.processes._get_protected_pids", return_value={0, 4, 9999}), \
         patch("time.sleep", return_value=None):

        res = execute_panic()
        assert res.success is True
        assert "Processi utente chiusi: `1`" in res.message

        # System and explorer must NOT have terminate() called
        p_system.terminate.assert_not_called()
        p_dwm.terminate.assert_not_called()
        p_explorer.terminate.assert_not_called()

        # User notepad must have terminate() called
        p_notepad.terminate.assert_called_once()


def test_open_notepad_note_empty():
    from commands.applications import open_notepad_note
    res = open_notepad_note("")
    assert res.success is False
    assert "vuoto" in res.message.lower()


def test_open_notepad_note_success(tmp_path):
    from commands.applications import open_notepad_note
    with patch("config.LOCAL_DATA_DIR", tmp_path), \
         patch("subprocess.Popen") as mock_popen, \
         patch("shutil.which", return_value=r"C:\Windows\System32\notepad.exe"):

        test_note = "ricordami di inviare mail a mario.rossi@mailgenerica.com e di caricare i nuovi file"
        res = open_notepad_note(test_note)
        assert res.success is True
        assert "Blocco Note" in res.message

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0][0] == r"C:\Windows\System32\notepad.exe"
        created_file_path = args[0][1]
        assert Path(created_file_path).exists()
        assert Path(created_file_path).read_text(encoding="utf-8") == test_note
        assert kwargs.get("shell") is not True
