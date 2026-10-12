"""
Logging configuration for BotMyPC.
Configures console, rotating file handler, and a GUI queue handler with
mandatory token redaction filter to prevent leaking sensitive credentials.
"""

from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
import queue
import re
from typing import Optional

from config import LOG_FILE_PATH, LOG_MAX_BYTES, LOG_BACKUP_COUNT, APP_NAME

# Regex pattern for Telegram Bot Token: e.g., 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567
_TOKEN_PATTERN = re.compile(r"\b(\d{7,12}):[A-Za-z0-9_-]{30,50}\b")


class TokenRedactionFilter(logging.Filter):
    """
    Filter that scrubs Telegram Bot Tokens from log records,
    replacing them with a safe masked representation.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self._redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: (self._redact(v) if isinstance(v, str) else v) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self._redact(a) if isinstance(a, str) else a for a in record.args)
        return True

    @staticmethod
    def _redact(text: str) -> str:
        def _replace_token(match: re.Match[str]) -> str:
            full = match.group(0)
            prefix = full[:6]
            suffix = full[-4:]
            return f"{prefix}...{suffix} (REDACTED_TOKEN)"

        return _TOKEN_PATTERN.sub(_replace_token, text)


class QueueLogHandler(logging.Handler):
    """
    Custom logging handler that dispatches formatted log records
    to a thread-safe queue.Queue consumed by the CustomTkinter GUI.
    """

    def __init__(self, log_queue: queue.Queue[str]) -> None:
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.log_queue.put_nowait(msg)
        except Exception:
            self.handleError(record)


def setup_logging(gui_queue: Optional[queue.Queue[str]] = None) -> logging.Logger:
    """
    Configures and initializes root/application logging with:
    1. RotatingFileHandler (1MB, 5 backups)
    2. StreamHandler (stdout)
    3. QueueLogHandler (for CustomTkinter Terminal panel, if queue provided)
    """
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Avoid duplicate handlers if setup_logging is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    redaction_filter = TokenRedactionFilter()

    # 1. Rotating File Handler
    try:
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=str(LOG_FILE_PATH),
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(redaction_filter)
        logger.addHandler(file_handler)
    except Exception as e:
        # Fallback if file system permission issue
        print(f"Warning: could not initialize file logger at {LOG_FILE_PATH}: {e}")

    # 2. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(redaction_filter)
    logger.addHandler(console_handler)

    # 3. GUI Queue Handler
    if gui_queue is not None:
        queue_handler = QueueLogHandler(gui_queue)
        queue_handler.setLevel(logging.INFO)
        queue_handler.setFormatter(formatter)
        queue_handler.addFilter(redaction_filter)
        logger.addHandler(queue_handler)

    return logger
