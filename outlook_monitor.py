import threading
import time
import logging
from pathlib import Path
from typing import List

import win32com.client
import pythoncom

from config import APP_NAME, MAX_LOG_MESSAGE_PREVIEW_LEN
from i18n import t
from telegram_bot import TelegramBotManager

logger = logging.getLogger(APP_NAME)

class OutlookMailMonitor:
    """Monitors Outlook inbox for new unread messages containing configured keywords.

    Runs in a background daemon thread, polling the Outlook Inbox every ``poll_interval`` seconds.
    When a matching email is detected, it sends a Telegram notification with sender, subject, and
    received time via the provided ``TelegramBotManager`` instance.
    """

    def __init__(self, bot_manager: TelegramBotManager, poll_interval: int = 5):
        self.bot_manager = bot_manager
        self.poll_interval = poll_interval
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self.enabled = False
        self.keywords: List[str] = []
        self._start_time: float = 0.0
        self._notified_ids: set = set()
        self._load_config()

    # ---------------------------------------------------------------------
    # Configuration persistence
    # ---------------------------------------------------------------------
    def _config_path(self):
        from config import LOCAL_DATA_DIR
        local_cfg = LOCAL_DATA_DIR / "mail_notify_config.json"
        if not local_cfg.exists():
            repo_cfg = Path(__file__).parent / "mail_notify_config.json"
            if repo_cfg.exists():
                return repo_cfg
        return local_cfg

    def _load_config(self):
        import json
        path = self._config_path()
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self.enabled = data.get("enabled", False)
                self.keywords = data.get("keywords", [])
            except Exception as e:
                logger.error(t("log_mail_config_error", e=e))
                self.enabled = False
                self.keywords = []
        else:
            self.enabled = False
            self.keywords = []
            self._save_config()

    def _save_config(self):
        import json
        path = self._config_path()
        data = {"enabled": self.enabled, "keywords": self.keywords}
        try:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(t("log_mail_config_save_error", e=e))

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def start(self):
        if self._thread and self._thread.is_alive():
            logger.info(t("log_mail_already_running"))
            return
        self.enabled = True
        self._save_config()
        self._stop_event.clear()
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._run, daemon=True, name="OutlookMailMonitor")
        self._thread.start()
        cutoff_timestamp = self._start_time - 30 * 60
        cutoff_str = time.strftime("%H:%M:%S", time.localtime(cutoff_timestamp))
        logger.info(t("log_mail_started", cutoff=cutoff_str))

    def stop(self):
        self.enabled = False
        self._save_config()
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
            logger.info(t("log_mail_stopped"))
        self._thread = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive() and self.enabled

    def set_keywords(self, keywords: List[str]):
        self.keywords = keywords
        self._save_config()

    # ---------------------------------------------------------------------
    # Internal worker
    # ---------------------------------------------------------------------
    def _run(self):
        pythoncom.CoInitialize()
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            inbox = namespace.GetDefaultFolder(6)  # 6 = olFolderInbox
            logger.info(t("log_outlook_com_ok"))

            folders_to_monitor: List[tuple] = [("Inbox", inbox)]

            cutoff_timestamp = self._start_time - 30 * 60
            cutoff_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cutoff_timestamp))
            logger.info(t("log_cutoff_time", cutoff=cutoff_str))

            while not self._stop_event.is_set():
                try:
                    for folder_name, folder in folders_to_monitor:
                        messages = folder.Items
                        messages.Sort("[ReceivedTime]", Descending=True)
                        unread = messages.Restrict("[Unread] = True")
                        unread_count = len(unread)
                        logger.debug(t("log_polling_folder", folder=folder_name, count=unread_count))
                        for mail in unread:
                            entry_id = getattr(mail, "EntryID", None)
                            if entry_id and entry_id in self._notified_ids:
                                continue

                            subject = getattr(mail, "Subject", "")
                            received = getattr(mail, "ReceivedTime", None)

                            # Skip emails received before the monitoring start cutoff
                            if received is not None:
                                try:
                                    mail_ts = received.timestamp()
                                    if mail_ts < cutoff_timestamp:
                                        logger.debug(
                                            t("log_mail_ignored_old", folder=folder_name, subject=subject[:MAX_LOG_MESSAGE_PREVIEW_LEN])
                                        )
                                        continue
                                except Exception:
                                    pass

                            if any(kw.lower() in subject.lower() for kw in self.keywords):
                                sender = getattr(mail, "SenderName", "unknown")
                                time_str = received.Format("%Y-%m-%d %H:%M") if received else ""
                                msg = (
                                    f"📧 *Nuova mail* ({folder_name})\n"
                                    f"*Mittente*: {sender}\n"
                                    f"*Oggetto*: {subject}\n"
                                    f"*Orario*: {time_str}"
                                )
                                logger.info(t("log_mail_keyword_match", folder=folder_name, subject=subject[:MAX_LOG_MESSAGE_PREVIEW_LEN]))
                                if self.bot_manager:
                                    sent = self.bot_manager.send_message(msg)
                                    if sent:
                                        logger.info(t("log_telegram_notify_sent"))
                                    else:
                                        logger.warning(t("log_telegram_notify_failed"))
                                else:
                                    logger.warning(t("log_bot_manager_unavailable"))
                                if entry_id:
                                    self._notified_ids.add(entry_id)
                except Exception as e:
                    logger.error(t("log_outlook_processing_error", e=e))
                time.sleep(self.poll_interval)
            logger.info(t("log_mail_thread_exit"))
        except Exception as e:
            logger.error(t("log_outlook_com_error", e=e))
        finally:
            pythoncom.CoUninitialize()
