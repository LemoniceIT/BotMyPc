"""
Security and Authorization Gateway for BotMyPC.

Enforces:
1. Strict Master User ID authorization (Section 7-bis: single mandatory gate).
2. Chat type filter (Section 7-ter: private chats only, no edits/channels/groups).
3. Command string normalization and argument rejection (Section 8).
4. Thread-safe anti-flood and duplicate suppression (Section 11).
5. Two-step confirmation state machine for dangerous commands like /panic (Section 18).
"""

from __future__ import annotations
import logging
import threading
import time
from typing import Optional, Tuple, Dict
from dataclasses import dataclass

from config import (
    APP_NAME,
    DUPLICATE_WINDOW_SECONDS,
    PANIC_CONFIRMATION_SECONDS,
    MAX_LOG_MESSAGE_PREVIEW_LEN,
)
from i18n import t

logger = logging.getLogger(APP_NAME)


@dataclass(frozen=True)
class NormalizedCommand:
    raw_text: str
    command: str
    argument: str
    is_valid: bool
    error_message: Optional[str] = None


class CommandNormalizer:
    """
    Normalizes incoming message text into a canonical command and argument.
    Prevents arbitrary arguments and shell injection.
    """

    @staticmethod
    def normalize(text: Optional[str]) -> NormalizedCommand:
        if not text:
            return NormalizedCommand(
                raw_text="",
                command="",
                argument="",
                is_valid=False,
                error_message=t("telegram_empty_message"),
            )

        raw = text.strip()
        cleaned = raw
        if cleaned.startswith("/"):
            cleaned = cleaned[1:].strip()

        parts = cleaned.split()
        if not parts:
            return NormalizedCommand(
                raw_text=raw,
                command="",
                argument="",
                is_valid=False,
                error_message=t("telegram_no_command"),
            )

        # Support 'note:<text>' or 'note <text>' with free-form text, spaces and formatting
        cleaned_lower = cleaned.lower()
        if cleaned_lower.startswith("note:") or cleaned_lower.startswith("note "):
            prefix_len = 5
            note_content = cleaned[prefix_len:].strip()
            if not note_content:
                return NormalizedCommand(
                    raw_text=raw,
                    command="note",
                    argument="",
                    is_valid=False,
                error_message=t("telegram_note_empty_arg"),
                )
            return NormalizedCommand(
                raw_text=raw,
                command="note",
                argument=note_content,
                is_valid=True,
                error_message=None,
            )
        elif cleaned_lower == "note":
            return NormalizedCommand(
                raw_text=raw,
                command="note",
                argument="",
                is_valid=False,
                error_message=t("telegram_note_empty_arg"),
            )

        cmd_name = parts[0].lower()
        arg = parts[1].lower() if len(parts) > 1 else ""

        # Only 'panic' accepts an argument ('conferma'). All other commands reject arguments.
        if len(parts) > 2:
            return NormalizedCommand(
                raw_text=raw,
                command=cmd_name,
                argument=arg,
                is_valid=False,
                error_message=t("telegram_too_many_args"),
            )

        if len(parts) == 2 and cmd_name != "panic":
            return NormalizedCommand(
                raw_text=raw,
                command=cmd_name,
                argument=arg,
                is_valid=False,
                error_message=t("telegram_no_extra_args", cmd=cmd_name),
            )

        return NormalizedCommand(
            raw_text=raw,
            command=cmd_name,
            argument=arg,
            is_valid=True,
            error_message=None,
        )


class AntiDuplicateFilter:
    """
    Thread-safe anti-flood and anti-duplicate tracker.
    Suppresses identical commands sent by the same user within DUPLICATE_WINDOW_SECONDS.
    """

    def __init__(self, window_seconds: float = DUPLICATE_WINDOW_SECONDS) -> None:
        self._window_seconds = window_seconds
        self._history: Dict[Tuple[int, str], float] = {}
        self._lock = threading.Lock()

    def is_duplicate(self, user_id: int, command: str) -> bool:
        now = time.time()
        key = (user_id, command.lower())

        with self._lock:
            # Purge expired entries
            expired_keys = [k for k, ts in self._history.items() if now - ts > self._window_seconds]
            for k in expired_keys:
                del self._history[k]

            last_time = self._history.get(key)
            if last_time is not None and (now - last_time) < self._window_seconds:
                return True

            self._history[key] = now
            return False

    def clear(self) -> None:
        with self._lock:
            self._history.clear()


class PanicConfirmationTracker:
    """
    Tracks two-step confirmation state for dangerous commands (e.g. /panic).
    Requires '/panic conferma' within PANIC_CONFIRMATION_SECONDS.
    """

    def __init__(self, timeout_seconds: float = PANIC_CONFIRMATION_SECONDS) -> None:
        self._timeout_seconds = timeout_seconds
        self._pending_user_id: Optional[int] = None
        self._request_timestamp: float = 0.0
        self._lock = threading.Lock()

    def request_panic(self, user_id: int) -> str:
        with self._lock:
            self._pending_user_id = user_id
            self._request_timestamp = time.time()
        return t("telegram_panic_prompt")

    def is_confirmed(self, user_id: int, argument: str) -> Tuple[bool, Optional[str]]:
        now = time.time()
        with self._lock:
            if self._pending_user_id != user_id:
                return False, t("telegram_panic_no_pending")

            elapsed = now - self._request_timestamp
            if elapsed > self._timeout_seconds:
                self._pending_user_id = None
                return False, t("telegram_panic_expired", elapsed=elapsed, timeout=self._timeout_seconds)

            if argument not in ("conferma", "confirm"):
                return False, t("telegram_panic_invalid_arg")

            # Successfully confirmed; reset state
            self._pending_user_id = None
            return True, None

    def reset(self) -> None:
        with self._lock:
            self._pending_user_id = None
            self._request_timestamp = 0.0


class SecurityGateway:
    """
    Centralized security gateway.
    Every update must pass through this gateway before any command handler can be reached.
    """

    def __init__(
        self,
        get_master_user_id_fn,
        anti_flood_window: float = DUPLICATE_WINDOW_SECONDS,
        panic_timeout: float = PANIC_CONFIRMATION_SECONDS,
    ) -> None:
        self._get_master_user_id = get_master_user_id_fn
        self.anti_duplicate = AntiDuplicateFilter(anti_flood_window)
        self.panic_tracker = PanicConfirmationTracker(panic_timeout)

    def verify_authorization(
        self,
        user_id: Optional[int],
        username: Optional[str] = None,
        raw_message: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates sender_id against the configured master_user_id.
        Logs unauthorized attempts with limited message preview for privacy.
        """
        master_id_str = self._get_master_user_id()
        if not master_id_str:
            logger.warning(t("log_sec_master_unconfigured"))
            return False, t("telegram_master_unconfigured")

        try:
            expected_master_id = int(master_id_str.strip())
        except ValueError:
            logger.error(t("log_sec_master_invalid_int"))
            return False, t("telegram_master_invalid")

        if user_id is None or user_id != expected_master_id:
            preview = (raw_message or "")[:MAX_LOG_MESSAGE_PREVIEW_LEN]
            user_display = f"@{username}" if username else "NoUsername"
            logger.warning(
                t("log_sec_unauthorized_access", user_id=user_id, username=user_display, preview=preview)
            )
            return False, t("telegram_unauthorized")

        return True, None
