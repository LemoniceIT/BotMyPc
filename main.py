"""
Main entry point for BotMyPC (telegram_remote_control).

Coordinates:
- Application bootstrap & logging setup
- Dedicated Asyncio Telegram Bot thread
- CustomTkinter GUI mainloop on main thread
- pystray System Tray integration
- Unified graceful shutdown sequence
"""

from __future__ import annotations
import logging
import queue
import sys
import threading

from config import APP_NAME, APP_VERSION
from logging_config import setup_logging
import credentials
from telegram_bot import TelegramBotManager
from tray import SystemTrayManager
from gui import MainWindow
from outlook_monitor import OutlookMailMonitor


def main() -> None:
    # 1. Thread-safe log queue shared between Bot/File handlers and GUI
    gui_log_queue: queue.Queue[str] = queue.Queue()

    # 2. Setup logging (RotatingFileHandler + Console + QueueLogHandler)
    logger = setup_logging(gui_log_queue)
    logger.info(f"{APP_NAME} v{APP_VERSION} avviato su Windows 11.")

    # Check credentials presence (never log values!)
    token_present = credentials.load_credential(credentials.KEY_BOT_TOKEN) is not None
    master_present = credentials.load_credential(credentials.KEY_MASTER_USER_ID) is not None
    logger.info(f"Stato credenziali: Bot Token {'PRESENTE' if token_present else 'ASSENTE'}, Master ID {'PRESENTE' if master_present else 'ASSENTE'}.")

    # 3. Initialize Telegram Bot Manager
    bot_manager = TelegramBotManager(gui_queue=gui_log_queue)

    # 3b. Initialize Outlook mail monitor (not started automatically;
    # user enables it via the GUI dialog)
    mail_monitor = OutlookMailMonitor(bot_manager)

    # Coordinated unified shutdown handler
    shutdown_lock = threading.Lock()
    is_shutting_down = False
    window_ref = None
    tray_ref = None

    def shutdown_app() -> None:
        nonlocal is_shutting_down
        with shutdown_lock:
            if is_shutting_down:
                return
            is_shutting_down = True

        logger.info("Avvio sequenza di chiusura ordinata...")

        # 1. Stop Telegram Bot & background thread
        try:
            bot_manager.stop_bot(wait_timeout=4.0)
        except Exception as e:
            logger.error(f"Errore durante l'arresto del bot: {e}")

        # 2. Stop Outlook Mail Monitor
        if mail_monitor and mail_monitor.is_running():
            try:
                mail_monitor.stop()
            except Exception as e:
                logger.error(f"Errore durante l'arresto del monitor mail: {e}")

        # 3. Stop System Tray
        if tray_ref:
            try:
                tray_ref.stop()
            except Exception as e:
                logger.error(f"Errore durante la chiusura della tray: {e}")

        # 3. Destroy GUI Window
        if window_ref:
            try:
                window_ref.after(0, window_ref.destroy)
            except Exception:
                pass

        logger.info("Chiusura applicazione completata.")

    # 4. Initialize CustomTkinter Main Window (Main Thread)
    window = MainWindow(
        bot_manager=bot_manager,
        log_queue=gui_log_queue,
        on_request_shutdown=shutdown_app,
        mail_monitor=mail_monitor,
    )
    window_ref = window

    # Connect bot state change listener to GUI
    bot_manager.on_state_change = window.on_bot_state_changed

    # 5. Initialize System Tray Manager
    tray_manager = SystemTrayManager(
        on_show=window.show_from_tray,
        on_exit=shutdown_app,
    )
    tray_ref = tray_manager
    tray_manager.start()

    # 6. Execute GUI Mainloop on Main Thread
    try:
        window.mainloop()
    except KeyboardInterrupt:
        shutdown_app()
    except Exception as e:
        logger.exception(f"Errore imprevisto nel mainloop della GUI: {e}")
        shutdown_app()


if __name__ == "__main__":
    main()
