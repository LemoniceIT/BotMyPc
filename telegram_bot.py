"""
Dedicated Telegram Bot Engine for BotMyPC.

Implements:
- Asyncio event loop running in a dedicated OS thread.
- Lifecycle: STARTING, RUNNING, STOPPING, STOPPED, ERROR.
- Strict centralized authorization gateway (Section 7-bis).
- Filtering for private text messages only (Section 7-ter).
- Non-blocking execution of command handlers using asyncio.to_thread.
- Thread-safe communication with CustomTkinter GUI via queue.Queue.
"""

from __future__ import annotations
import asyncio
from enum import Enum
import logging
import queue
import threading
from typing import Optional, Callable

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import APP_NAME
from i18n import t
from command_registry import REGISTRY, CommandResult
from security import (
    SecurityGateway,
    CommandNormalizer,
    NormalizedCommand,
)
import credentials
import commands  # Ensures commands are registered

logger = logging.getLogger(APP_NAME)


class BotState(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    ERROR = "ERROR"


class TelegramBotManager:
    """
    Manages the lifecycle, background thread, and event loop of the Telegram Bot.
    """

    def __init__(
        self,
        gui_queue: queue.Queue[str],
        on_state_change: Optional[Callable[[BotState], None]] = None,
    ) -> None:
        self.gui_queue = gui_queue
        self.on_state_change = on_state_change
        self._state: BotState = BotState.STOPPED
        self._state_lock = threading.RLock()

        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._stop_event: Optional[asyncio.Event] = None
        self._application: Optional[Application] = None

        # Instantiate centralized security gateway
        self.security_gateway = SecurityGateway(
            get_master_user_id_fn=lambda: credentials.load_credential(credentials.KEY_MASTER_USER_ID)
        )

    # =========================================================================
    # State Management
    # =========================================================================

    @property
    def state(self) -> BotState:
        with self._state_lock:
            return self._state

    def _set_state(self, new_state: BotState) -> None:
        with self._state_lock:
            self._state = new_state
        logger.info(t("log_bot_state", state=new_state.value))
        if self.on_state_change:
            try:
                self.on_state_change(new_state)
            except Exception as e:
                logger.debug(t("log_state_change_error", e=e))

    # =========================================================================
    # Start / Stop API
    # =========================================================================

    def start_bot(self) -> bool:
        """Starts the bot in a dedicated background thread."""
        with self._state_lock:
            if self._state in (BotState.STARTING, BotState.RUNNING):
                logger.warning(t("log_bot_already_running"))
                return False

            token = credentials.load_credential(credentials.KEY_BOT_TOKEN)
            if not token:
                logger.error(t("log_bot_token_missing"))
                self.gui_queue.put(t("log_bot_token_missing_gui"))
                return False

        self._set_state(BotState.STARTING)

        self._thread = threading.Thread(
            target=self._run_thread,
            args=(token,),
            name="TelegramBotThread",
            daemon=True,
        )
        self._thread.start()
        return True

    def stop_bot(self, wait_timeout: float = 5.0) -> bool:
        """Signals the bot to stop and waits for the thread to exit."""
        with self._state_lock:
            if self._state in (BotState.STOPPED, BotState.STOPPING):
                return True

        self._set_state(BotState.STOPPING)
        logger.info(t("log_bot_stopping"))

        # Signal the asyncio loop to stop
        if self._loop and self._stop_event:
            self._loop.call_soon_threadsafe(self._stop_event.set)

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=wait_timeout)

        self._set_state(BotState.STOPPED)
        logger.info(t("log_bot_stopped"))
        return True

    # =========================================================================
    # Outgoing Messaging
    # =========================================================================

    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Sends a message to the configured Master User via the running bot.

        Thread-safe: can be called from any thread (e.g. the Outlook mail
        monitor's daemon thread). Schedules the coroutine on the bot's
        dedicated asyncio event loop via ``run_coroutine_threadsafe``.
        """
        if self._loop is None or self._application is None:
            logger.warning(t("log_send_not_running"))
            return False

        master_id_str = credentials.load_credential(credentials.KEY_MASTER_USER_ID)
        if not master_id_str:
            logger.warning(t("log_send_master_unconfigured"))
            return False
        try:
            master_id = int(master_id_str.strip())
        except (ValueError, TypeError):
            logger.error(t("log_send_master_invalid"))
            return False

        async def _do_send() -> None:
            try:
                await self._application.bot.send_message(
                    chat_id=master_id, text=message, parse_mode=parse_mode
                )
            except Exception as md_err:
                logger.debug(t("log_markdown_failed", e=md_err))
                try:
                    await self._application.bot.send_message(
                        chat_id=master_id, text=message
                    )
                except Exception as e2:
                    logger.error(t("log_send_fallback_failed", e2=e2))

        try:
            future = asyncio.run_coroutine_threadsafe(_do_send(), self._loop)
            future.result(timeout=10.0)
            return True
        except Exception as e:
            logger.error(t("log_send_error", e=e))
            return False

    # =========================================================================
    # Dedicated Thread Execution
    # =========================================================================

    def _run_thread(self, token: str) -> None:
        """Entry point executed in the background thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._async_bot_main(token))
        except Exception as e:
            logger.exception(t("log_fatal_bot_error", e=e))
            self._set_state(BotState.ERROR)
        finally:
            try:
                # Cancel remaining tasks if any
                pending = asyncio.all_tasks(self._loop)
                for task in pending:
                    task.cancel()
                if pending:
                    self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            except Exception:
                pass
            finally:
                self._loop.close()
                self._loop = None
                if self.state != BotState.ERROR:
                    self._set_state(BotState.STOPPED)

    async def _async_bot_main(self, token: str) -> None:
        """Initializes and runs the python-telegram-bot application lifecycle."""
        self._stop_event = asyncio.Event()

        try:
            # Build Telegram Application
            self._application = Application.builder().token(token).build()

            # Section 7-ter: Only process text messages from PRIVATE chats.
            # Explicitly exclude edited messages, channels, groups.
            private_text_filter = (
                filters.ChatType.PRIVATE
                & filters.TEXT
                & (~filters.UpdateType.EDITED_MESSAGE)
                & (~filters.UpdateType.CHANNEL_POST)
            )

            # Centralized dispatcher: all messages route through _dispatch_update
            self._application.add_handler(
                MessageHandler(private_text_filter, self._dispatch_update)
            )

            # Initialize and start polling
            await self._application.initialize()
            await self._application.start()
            await self._application.updater.start_polling(
                allowed_updates=["message"],
                drop_pending_updates=True,
            )

            self._set_state(BotState.RUNNING)
            logger.info(t("log_bot_started"))

            # Run until stopped
            await self._stop_event.wait()

        except Exception as e:
            logger.error(t("log_telegram_startup_error", e=e))
            self._set_state(BotState.ERROR)
            raise
        finally:
            # Orderly teardown
            if self._application:
                logger.info(t("log_closing_telegram"))
                if self._application.updater and self._application.updater.running:
                    await self._application.updater.stop()
                if self._application.running:
                    await self._application.stop()
                await self._application.shutdown()
                self._application = None

    # =========================================================================
    # Centralized Authorization and Command Dispatch (Section 7-bis)
    # =========================================================================

    async def _dispatch_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        MANDATORY GATEWAY: Every incoming message must pass through this single
        point. No command handler can ever be reached without passing authorization.
        """
        if not update.message or not update.message.text:
            return

        user = update.effective_user
        sender_id = user.id if user else None
        username = user.username if user else None
        raw_text = update.message.text

        # 1. Authorization check
        is_authorized, auth_error = self.security_gateway.verify_authorization(
            user_id=sender_id,
            username=username,
            raw_message=raw_text,
        )
        if not is_authorized:
            if auth_error:
                try:
                    await update.message.reply_text(auth_error)
                except Exception:
                    pass
            return

        # 2. Command normalization
        norm_cmd: NormalizedCommand = CommandNormalizer.normalize(raw_text)
        if not norm_cmd.is_valid:
            err_msg = norm_cmd.error_message or t("telegram_invalid_cmd")
            logger.info(t("log_invalid_command", cmd=raw_text[:30], err=err_msg))
            await update.message.reply_text(t("telegram_reply_invalid_cmd", err=err_msg))
            return

        # 3. Anti-duplicate check (Section 11)
        # Check against the command name, or command+argument for note
        dup_key = f"{norm_cmd.command}:{norm_cmd.argument}" if norm_cmd.command == "note" else norm_cmd.command
        if self.security_gateway.anti_duplicate.is_duplicate(sender_id, dup_key):
            logger.info(t("log_dup_command", sender_id=sender_id, cmd=norm_cmd.command))
            return

        logger.info(t("log_cmd_received", cmd=norm_cmd.command, arg=norm_cmd.argument).strip())

        # 4. Handle Panic confirmation flow (Section 18)
        if norm_cmd.command == "panic":
            if not norm_cmd.argument:
                # Step 1: Request confirmation
                prompt_msg = self.security_gateway.panic_tracker.request_panic(sender_id)
                await update.message.reply_markdown(prompt_msg)
                return
            else:
                # Step 2: Validate confirmation
                confirmed, conf_err = self.security_gateway.panic_tracker.is_confirmed(
                    sender_id, norm_cmd.argument
                )
                if not confirmed:
                    await update.message.reply_text(f"❌ {conf_err}")
                    return

        # 5. Command Registry lookup
        cmd_def = REGISTRY.get(norm_cmd.command)
        if not cmd_def:
            logger.info(t("log_unknown_command", cmd=norm_cmd.command))
            await update.message.reply_text(
                t("telegram_unknown_cmd", cmd=norm_cmd.command),
                parse_mode="Markdown",
            )
            return

        # 6. Execute Handler in thread pool to avoid blocking asyncio event loop (Section 34)
        try:
            if cmd_def.takes_argument:
                result: CommandResult = await asyncio.to_thread(cmd_def.handler, norm_cmd.argument)
            else:
                result: CommandResult = await asyncio.to_thread(cmd_def.handler)
        except Exception as e:
            logger.exception(t("log_unhandled_error", cmd=norm_cmd.command))
            result = CommandResult(
                success=False,
                message=t("telegram_error_internal", cmd=norm_cmd.command, e=e),
                log_message=t("log_error_internal", cmd=norm_cmd.command, e=e),
            )

        # 7. Log outcome and respond to user
        if result.log_message:
            logger.info(t("log_command_result", cmd=norm_cmd.command, msg=result.log_message))

        try:
            await update.message.reply_markdown(result.message)
        except Exception:
            # Fallback to plain text if markdown formatting failed
            await update.message.reply_text(result.message)
