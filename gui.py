"""
CustomTkinter Graphical User Interface for BotMyPC.

Features:
- Fixed 800x600 window with Cyberpunk/Matrix theme (#0A0A0A, #000000, #00FF66).
- Dedicated Log Terminal panel polling messages from queue.Queue (thread-safe).
- Status indicator badge (STOPPED, STARTING, RUNNING, STOPPING, ERROR).
- API Token Configuration modal (with format validation & masked display).
- Master User ID Configuration modal (with numeric validation & helper info).
- Bot Start/Stop control button.
- Windows Startup toggle checkbox.
- Background button (minimize to system tray).
- Credits modal.
- Unified graceful shutdown coordinator.
"""

from __future__ import annotations
import logging
import queue
import re
import sys
from typing import Optional, Callable

import customtkinter as ctk

from config import (
    APP_NAME,
    APP_DISPLAY_TITLE,
    APP_VERSION,
    GUI_WIDTH,
    GUI_HEIGHT,
    GUI_BG_COLOR,
    GUI_PANEL_BG,
    GUI_TERMINAL_BG,
    GUI_ACCENT_COLOR,
    GUI_ACCENT_HOVER,
    GUI_TEXT_COLOR,
    GUI_MUTED_TEXT,
    GUI_DANGER_COLOR,
    GUI_DANGER_HOVER,
    GUI_WARNING_COLOR,
    GUI_BORDER_COLOR,
    GUI_QUEUE_POLL_INTERVAL_MS,
    ICON_PATH,
)
import credentials
from telegram_bot import TelegramBotManager, BotState
from startup import is_startup_enabled, toggle_startup
from i18n import t, get_current_language, set_language, get_supported_languages, SUPPORTED_LANGUAGES
from icons import get_button_icon

logger = logging.getLogger(APP_NAME)

# Set global appearance mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class TokenConfigDialog(ctk.CTkToplevel):
    """Modal dialog to enter and save the Telegram Bot Token."""

    def __init__(self, parent: ctk.CTk, on_saved: Callable[[], None]) -> None:
        super().__init__(parent)
        self.on_saved = on_saved
        self.title(t("token_dialog_title"))
        self.geometry("520x300")
        self.resizable(False, False)
        self.configure(fg_color=GUI_BG_COLOR)

        # Center relative to parent
        self.transient(parent)
        self.grab_set()

        # Header
        title_lbl = ctk.CTkLabel(
            self,
            text=t("token_dialog_header"),
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color=GUI_ACCENT_COLOR,
        )
        title_lbl.pack(pady=(20, 10))

        info_lbl = ctk.CTkLabel(
            self,
            text=t("token_dialog_info"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=GUI_TEXT_COLOR,
            justify="center",
        )
        info_lbl.pack(pady=(0, 15))

        # Current masked token display
        curr_token = credentials.load_credential(credentials.KEY_BOT_TOKEN)
        curr_lbl = ctk.CTkLabel(
            self,
            text=t("token_current", token=credentials.mask_token(curr_token)),
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=GUI_MUTED_TEXT,
        )
        curr_lbl.pack(pady=(0, 10))

        # Entry input
        self.token_entry = ctk.CTkEntry(
            self,
            placeholder_text=t("token_placeholder"),
            width=440,
            height=36,
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=GUI_TERMINAL_BG,
            border_color=GUI_BORDER_COLOR,
            text_color=GUI_ACCENT_COLOR,
            show="*",
        )
        self.token_entry.pack(pady=(0, 5))

        self.error_lbl = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=GUI_DANGER_COLOR,
        )
        self.error_lbl.pack(pady=(0, 10))

        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(5, 15))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=t("btn_cancel"),
            width=120,
            fg_color="#2A2A2A",
            hover_color="#3A3A3A",
            text_color=GUI_TEXT_COLOR,
            command=self.destroy,
        )
        cancel_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            btn_frame,
            text=t("token_btn_save"),
            width=140,
            fg_color=GUI_ACCENT_COLOR,
            hover_color=GUI_ACCENT_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            command=self._save_token,
        )
        save_btn.pack(side="left", padx=10)

    def _save_token(self) -> None:
        raw = self.token_entry.get().strip()
        if not raw:
            self.error_lbl.configure(text=t("token_error_empty"))
            return

        # Validate format: digits:alphanumeric
        if not re.match(r"^\d{7,12}:[A-Za-z0-9_-]{30,50}$", raw):
            self.error_lbl.configure(text=t("token_error_format"))
            return

        success = credentials.save_credential(credentials.KEY_BOT_TOKEN, raw)
        if success:
            logger.info(t("log_token_saved"))
            self.on_saved()
            self.destroy()
        else:
            self.error_lbl.configure(text=t("token_error_save"))


class MasterIdConfigDialog(ctk.CTkToplevel):
    """Modal dialog to enter and save the Master Telegram User ID."""

    def __init__(self, parent: ctk.CTk, on_saved: Callable[[], None]) -> None:
        super().__init__(parent)
        self.on_saved = on_saved
        self.title(t("master_dialog_title"))
        self.geometry("520x330")
        self.resizable(False, False)
        self.configure(fg_color=GUI_BG_COLOR)

        self.transient(parent)
        self.grab_set()

        title_lbl = ctk.CTkLabel(
            self,
            text=t("master_dialog_header"),
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color=GUI_ACCENT_COLOR,
        )
        title_lbl.pack(pady=(20, 10))

        info_lbl = ctk.CTkLabel(
            self,
            text=t("master_dialog_info"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=GUI_TEXT_COLOR,
            justify="center",
        )
        info_lbl.pack(pady=(0, 15))

        curr_id = credentials.load_credential(credentials.KEY_MASTER_USER_ID)
        curr_lbl = ctk.CTkLabel(
            self,
            text=t("master_current", id=curr_id if curr_id else t("master_not_configured")),
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=GUI_MUTED_TEXT,
        )
        curr_lbl.pack(pady=(0, 10))

        self.id_entry = ctk.CTkEntry(
            self,
            placeholder_text=t("master_placeholder"),
            width=300,
            height=36,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=GUI_TERMINAL_BG,
            border_color=GUI_BORDER_COLOR,
            text_color=GUI_ACCENT_COLOR,
            justify="center",
        )
        self.id_entry.pack(pady=(0, 5))

        self.error_lbl = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=GUI_DANGER_COLOR,
        )
        self.error_lbl.pack(pady=(0, 10))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(5, 15))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=t("btn_cancel"),
            width=120,
            fg_color="#2A2A2A",
            hover_color="#3A3A3A",
            text_color=GUI_TEXT_COLOR,
            command=self.destroy,
        )
        cancel_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            btn_frame,
            text=t("master_btn_save"),
            width=140,
            fg_color=GUI_ACCENT_COLOR,
            hover_color=GUI_ACCENT_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            command=self._save_id,
        )
        save_btn.pack(side="left", padx=10)

    def _save_id(self) -> None:
        raw = self.id_entry.get().strip()
        if not raw or not raw.isdigit():
            self.error_lbl.configure(text=t("master_error_numeric"))
            return

        success = credentials.save_credential(credentials.KEY_MASTER_USER_ID, raw)
        if success:
            logger.info(t("log_master_saved"))
            self.on_saved()
            self.destroy()
        else:
            self.error_lbl.configure(text=t("master_error_save"))


class CreditsDialog(ctk.CTkToplevel):
    """Modal dialog displaying application details, version, and dependencies."""

    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent)
        self.title(t("credits_dialog_title"))
        self.geometry("520x460")
        self.resizable(False, False)
        self.configure(fg_color=GUI_BG_COLOR)

        self.transient(parent)
        self.grab_set()

        title_lbl = ctk.CTkLabel(
            self,
            text=f"⚡ {APP_NAME} v{APP_VERSION}",
            font=ctk.CTkFont(family="Consolas", size=18, weight="bold"),
            text_color=GUI_ACCENT_COLOR,
        )
        title_lbl.pack(pady=(16, 4))

        author_lbl = ctk.CTkLabel(
            self,
            text=t("credits_author"),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=GUI_ACCENT_COLOR,
        )
        author_lbl.pack(pady=(0, 4))

        sub_lbl = ctk.CTkLabel(
            self,
            text=t("credits_subtitle"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=GUI_TEXT_COLOR,
        )
        sub_lbl.pack(pady=(0, 10))

        tech_lbl = ctk.CTkLabel(
            self,
            text=t("credits_tech_desc"),
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color="#B0B0B0",
            justify="left",
        )
        tech_lbl.pack(pady=(0, 10), padx=30)

        license_lbl = ctk.CTkLabel(
            self,
            text=t("credits_license"),
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#88CC99",
            justify="center",
            wraplength=460,
        )
        license_lbl.pack(pady=(0, 14), padx=20)

        close_btn = ctk.CTkButton(
            self,
            text=t("btn_close"),
            width=120,
            fg_color=GUI_ACCENT_COLOR,
            hover_color=GUI_ACCENT_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            command=self.destroy,
        )
        close_btn.pack(pady=(0, 14))


class LanguageConfigDialog(ctk.CTkToplevel):
    """Modal dialog to select and persist the application interface language."""

    def __init__(self, parent: ctk.CTk, on_saved: Callable[[], None]) -> None:
        super().__init__(parent)
        self.on_saved = on_saved
        self.title(t("lang_dialog_title"))
        self.geometry("480x440")
        self.resizable(False, False)
        self.configure(fg_color=GUI_BG_COLOR)

        self.transient(parent)
        self.grab_set()

        # Header
        title_lbl = ctk.CTkLabel(
            self,
            text=t("lang_dialog_header"),
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color=GUI_ACCENT_COLOR,
        )
        title_lbl.pack(pady=(20, 8))

        info_lbl = ctk.CTkLabel(
            self,
            text=t("lang_dialog_info"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=GUI_TEXT_COLOR,
            justify="center",
        )
        info_lbl.pack(pady=(0, 16))

        # Language selection cards / radio buttons frame
        opt_frame = ctk.CTkFrame(
            self,
            fg_color=GUI_PANEL_BG,
            corner_radius=8,
            border_width=1,
            border_color=GUI_BORDER_COLOR,
        )
        opt_frame.pack(fill="x", padx=30, pady=(0, 20))

        self.lang_var = ctk.StringVar(value=get_current_language())

        # Load all supported languages dynamically (built-in + any locales/*.json)
        all_langs = get_supported_languages()
        standard_order = ["en", "de", "es", "it", "fr"]
        ordered_codes = [c for c in standard_order if c in all_langs] + [c for c in all_langs if c not in standard_order]

        for code in ordered_codes:
            info = all_langs[code]
            flag = info.get("flag", "🌐")
            loc_key = f"lang_{code}"
            label = t(loc_key) if t(loc_key) != loc_key else info.get("native", info.get("name", code.capitalize()))

            row_frame = ctk.CTkFrame(opt_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=16, pady=4)

            radio = ctk.CTkRadioButton(
                row_frame,
                text=f"{flag}   {label}",
                value=code,
                variable=self.lang_var,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=GUI_TEXT_COLOR,
                fg_color=GUI_ACCENT_COLOR,
                hover_color=GUI_ACCENT_HOVER,
                border_color=GUI_BORDER_COLOR,
                border_width_checked=6,
            )
            radio.pack(anchor="w", pady=2)

        # Action buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(5, 15))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=t("btn_cancel"),
            width=120,
            fg_color="#2A2A2A",
            hover_color="#3A3A3A",
            text_color=GUI_TEXT_COLOR,
            command=self.destroy,
        )
        cancel_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            btn_frame,
            text=t("btn_save"),
            width=140,
            fg_color=GUI_ACCENT_COLOR,
            hover_color=GUI_ACCENT_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            command=self._save_language,
        )
        save_btn.pack(side="left", padx=10)

    def _save_language(self) -> None:
        chosen = self.lang_var.get()
        set_language(chosen)
        self.on_saved()
        self.destroy()


class MailNotificationDialog(ctk.CTkToplevel):
    """Modal dialog to configure Outlook mail-to-Telegram notifications."""

    def __init__(self, parent: ctk.CTk, mail_monitor) -> None:
        super().__init__(parent)
        self.parent = parent
        self.mail_monitor = mail_monitor
        self.title(t("mail_dialog_title"))
        self.geometry("540x400")
        self.resizable(False, False)
        self.configure(fg_color=GUI_BG_COLOR)

        self.transient(parent)
        self.grab_set()

        # Header
        title_lbl = ctk.CTkLabel(
            self,
            text=t("mail_dialog_header"),
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color=GUI_ACCENT_COLOR,
        )
        title_lbl.pack(pady=(20, 6))

        info_lbl = ctk.CTkLabel(
            self,
            text=t("mail_dialog_info"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=GUI_TEXT_COLOR,
            justify="center",
        )
        info_lbl.pack(pady=(0, 14))

        # Keywords frame
        kw_frame = ctk.CTkFrame(self, fg_color=GUI_PANEL_BG, corner_radius=8)
        kw_frame.pack(fill="x", padx=26, pady=(0, 10))

        kw_lbl = ctk.CTkLabel(
            kw_frame,
            text=t("mail_keywords_lbl"),
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=GUI_MUTED_TEXT,
        )
        kw_lbl.pack(anchor="w", padx=12, pady=(12, 4))

        current_kw = ", ".join(self.mail_monitor.keywords) if self.mail_monitor.keywords else ""
        self.kw_entry = ctk.CTkEntry(
            kw_frame,
            placeholder_text=t("mail_keywords_placeholder"),
            width=440,
            height=32,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=GUI_TERMINAL_BG,
            border_color=GUI_BORDER_COLOR,
            text_color=GUI_TEXT_COLOR,
        )
        self.kw_entry.insert(0, current_kw)
        self.kw_entry.pack(padx=12, pady=(0, 12))

        # Status + control buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=(0, 10))

        self.btn_toggle = ctk.CTkButton(
            btn_frame,
            text=t("mail_btn_start"),
            image=get_button_icon("play"),
            compound="left",
            width=165,
            height=32,
            fg_color=GUI_ACCENT_COLOR,
            hover_color=GUI_ACCENT_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            command=self._toggle_monitoring,
        )
        self.btn_toggle.pack(side="left", padx=10)

        self.btn_save_kw = ctk.CTkButton(
            btn_frame,
            text=t("mail_btn_save_kw"),
            image=get_button_icon("save"),
            compound="left",
            width=145,
            height=32,
            fg_color="#1F2A22",
            hover_color="#2A3D2F",
            border_width=1,
            border_color=GUI_BORDER_COLOR,
            text_color=GUI_TEXT_COLOR,
            command=self._save_keywords,
        )
        self.btn_save_kw.pack(side="left", padx=10)

        self.btn_close = ctk.CTkButton(
            btn_frame,
            text=t("btn_close"),
            width=80,
            height=32,
            fg_color="#2A2A2A",
            hover_color="#3A3A3A",
            text_color=GUI_TEXT_COLOR,
            command=self.destroy,
        )
        self.btn_close.pack(side="left", padx=10)

        self._refresh_toggle_button()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _refresh_toggle_button(self) -> None:
        running = self.mail_monitor.is_running()
        if running:
            self.btn_toggle.configure(
                text=t("mail_btn_stop"),
                image=get_button_icon("stop"),
                fg_color=GUI_DANGER_COLOR,
                hover_color=GUI_DANGER_HOVER,
                text_color="#FFFFFF",
            )
        else:
            self.btn_toggle.configure(
                text=t("mail_btn_start"),
                image=get_button_icon("play"),
                fg_color=GUI_ACCENT_COLOR,
                hover_color=GUI_ACCENT_HOVER,
                text_color="#000000",
            )

    def _save_keywords(self) -> None:
        raw = self.kw_entry.get().strip()
        keywords = [kw.strip() for kw in raw.split(",") if kw.strip()]
        self.mail_monitor.set_keywords(keywords)
        logger.info(t("log_mail_keywords_updated"))
        self._add_status_msg(t("mail_kw_saved"), is_error=False)

    def _toggle_monitoring(self) -> None:
        if self.mail_monitor.is_running():
            self.mail_monitor.stop()
            self.parent._update_mail_button(False)
        else:
            if not credentials.load_credential(credentials.KEY_MASTER_USER_ID):
                self._add_status_msg(
                    t("mail_err_master"), is_error=True
                )
                return
            if self.parent.bot_manager.state != BotState.RUNNING:
                self._add_status_msg(
                    t("mail_err_bot"),
                    is_error=True,
                )
                return
            self.mail_monitor.start()
            self.parent._update_mail_button(True)

        self._refresh_toggle_button()

    def _add_status_msg(self, text: str, is_error: bool = False) -> None:
        color = GUI_DANGER_COLOR if is_error else GUI_ACCENT_COLOR
        status_lbl = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=color,
        )
        status_lbl.pack(pady=(4, 0))

        def _remove():
            status_lbl.destroy()
        self.after(3000, _remove)


class MainWindow(ctk.CTk):
    """
    Main CustomTkinter application window.
    Strictly owns all UI widgets and runs exclusively on the main thread.
    """

    def __init__(
        self,
        bot_manager: TelegramBotManager,
        log_queue: queue.Queue[str],
        on_request_shutdown: Callable[[], None],
        mail_monitor,  # Added mail monitor instance
    ) -> None:
        super().__init__()

        self.bot_manager = bot_manager
        self.log_queue = log_queue
        self.mail_monitor = mail_monitor
        self.on_request_shutdown = on_request_shutdown

        # Window settings
        self.title(t("app_title"))
        self.geometry(f"{GUI_WIDTH}x{GUI_HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=GUI_BG_COLOR)

        # Set window icon if exists
        if ICON_PATH.exists():
            try:
                self.iconbitmap(str(ICON_PATH))
            except Exception:
                pass

        # Build UI layout
        self._build_header()
        self._build_controls()
        self._build_terminal()
        self._build_footer()

        # Ensure mail button reflects current monitor state (after UI is built)
        self._update_mail_button(self.mail_monitor.is_running())

        # Connect window close protocol
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Start log queue polling on main thread
        self.after(GUI_QUEUE_POLL_INTERVAL_MS, self._poll_queue)

        # Set initial status
        self._update_status_display(self.bot_manager.state)

    # =========================================================================
    # UI Construction
    # =========================================================================

    def _build_header(self) -> None:
        header_frame = ctk.CTkFrame(
            self,
            fg_color=GUI_PANEL_BG,
            corner_radius=8,
            border_width=1,
            border_color=GUI_BORDER_COLOR,
        )
        header_frame.pack(fill="x", padx=16, pady=(16, 8))

        # Left side: Lightning icon + App title
        lbl_lightning = ctk.CTkLabel(
            header_frame,
            text="⚡",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=22),
            text_color=GUI_ACCENT_COLOR,
        )
        lbl_lightning.pack(side="left", padx=(16, 6), pady=12)

        app_title = ctk.CTkLabel(
            header_frame,
            text=APP_NAME,
            font=ctk.CTkFont(family="Consolas", size=20, weight="bold"),
            text_color=GUI_ACCENT_COLOR,
        )
        app_title.pack(side="left", padx=(0, 16), pady=12)

        # Right side: Toggle button and Status badge
        self.btn_toggle_bot = ctk.CTkButton(
            header_frame,
            text="Avvia Bot",
            width=120,
            height=34,
            fg_color=GUI_ACCENT_COLOR,
            hover_color=GUI_ACCENT_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._toggle_bot_state,
        )
        self.btn_toggle_bot.pack(side="right", padx=(0, 16), pady=12)

        self.status_badge = ctk.CTkLabel(
            header_frame,
            text="STATO: STOPPED",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color=GUI_MUTED_TEXT,
            fg_color="#1E1E1E",
            corner_radius=6,
            padx=12,
            pady=6,
        )
        self.status_badge.pack(side="right", padx=(0, 12), pady=12)

    def _build_controls(self) -> None:
        ctrl_frame = ctk.CTkFrame(
            self,
            fg_color=GUI_PANEL_BG,
            corner_radius=8,
            border_width=1,
            border_color=GUI_BORDER_COLOR,
        )
        ctrl_frame.pack(fill="x", padx=16, pady=4)

        # Token Button
        self.btn_token = ctk.CTkButton(
            ctrl_frame,
            text=t("btn_token"),
            image=get_button_icon("token"),
            compound="left",
            width=95,
            height=32,
            fg_color="#1F2A22",
            hover_color="#2A3D2F",
            border_width=1,
            border_color=GUI_BORDER_COLOR,
            text_color=GUI_TEXT_COLOR,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self._open_token_dialog,
        )
        self.btn_token.pack(side="left", padx=3, pady=10)

        # Master ID Button
        self.btn_master = ctk.CTkButton(
            ctrl_frame,
            text=t("btn_master"),
            image=get_button_icon("master"),
            compound="left",
            width=95,
            height=32,
            fg_color="#1F2A22",
            hover_color="#2A3D2F",
            border_width=1,
            border_color=GUI_BORDER_COLOR,
            text_color=GUI_TEXT_COLOR,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self._open_master_dialog,
        )
        self.btn_master.pack(side="left", padx=3, pady=10)

        # Background (Minimize to tray) Button
        self.btn_bg = ctk.CTkButton(
            ctrl_frame,
            text=t("btn_background"),
            image=get_button_icon("background"),
            compound="left",
            width=100,
            height=32,
            fg_color="#1F2A22",
            hover_color="#2A3D2F",
            border_width=1,
            border_color=GUI_BORDER_COLOR,
            text_color=GUI_TEXT_COLOR,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self.hide_to_tray,
        )
        self.btn_bg.pack(side="left", padx=3, pady=10)

        # Mail Notification Button
        self.btn_mail_notify = ctk.CTkButton(
            ctrl_frame,
            text=t("btn_mail_notify"),
            image=get_button_icon("mail"),
            compound="left",
            width=105,
            height=32,
            fg_color="#1F2A22",
            hover_color="#2A3D2F",
            border_width=1,
            border_color=GUI_BORDER_COLOR,
            text_color=GUI_TEXT_COLOR,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self._open_mail_notify_dialog,
        )
        self.btn_mail_notify.pack(side="left", padx=3, pady=10)

        # Language Button (New!)
        self.btn_lang = ctk.CTkButton(
            ctrl_frame,
            text=t("btn_language"),
            image=get_button_icon("language"),
            compound="left",
            width=90,
            height=32,
            fg_color="#1F2A22",
            hover_color="#2A3D2F",
            border_width=1,
            border_color=GUI_BORDER_COLOR,
            text_color=GUI_TEXT_COLOR,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self._open_language_dialog,
        )
        self.btn_lang.pack(side="left", padx=3, pady=10)

        # Credits Button
        self.btn_credits = ctk.CTkButton(
            ctrl_frame,
            text=t("btn_credits"),
            image=get_button_icon("credits"),
            compound="left",
            width=80,
            height=32,
            fg_color="#1F2A22",
            hover_color="#2A3D2F",
            border_width=1,
            border_color=GUI_BORDER_COLOR,
            text_color=GUI_TEXT_COLOR,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=self._open_credits_dialog,
        )
        self.btn_credits.pack(side="left", padx=3, pady=10)

        # Auto-startup Checkbox
        self.startup_var = ctk.BooleanVar(value=is_startup_enabled())
        self.chk_startup = ctk.CTkCheckBox(
            ctrl_frame,
            text=t("chk_startup"),
            variable=self.startup_var,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=GUI_TEXT_COLOR,
            fg_color=GUI_ACCENT_COLOR,
            hover_color=GUI_ACCENT_HOVER,
            border_color=GUI_BORDER_COLOR,
            command=self._on_toggle_startup,
        )
        self.chk_startup.pack(side="right", padx=(4, 10), pady=10)

    def _build_terminal(self) -> None:
        term_container = ctk.CTkFrame(
            self,
            fg_color=GUI_TERMINAL_BG,
            corner_radius=8,
            border_width=1,
            border_color=GUI_BORDER_COLOR,
        )
        term_container.pack(fill="both", expand=True, padx=16, pady=8)

        # Terminal header bar
        bar = ctk.CTkFrame(term_container, fg_color="#0F1A13", height=28, corner_radius=6)
        bar.pack(fill="x", padx=2, pady=2)

        self.lbl_term = ctk.CTkLabel(
            bar,
            text=t("terminal_header"),
            font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
            text_color=GUI_ACCENT_COLOR,
        )
        self.lbl_term.pack(side="left", padx=6, pady=4)

        self.btn_clear = ctk.CTkButton(
            bar,
            text=t("btn_clear"),
            width=60,
            height=20,
            fg_color="transparent",
            hover_color="#1F2A22",
            text_color=GUI_MUTED_TEXT,
            font=ctk.CTkFont(family="Consolas", size=10),
            command=self._clear_terminal,
        )
        self.btn_clear.pack(side="right", padx=6, pady=4)

        # Scrollable read-only Text widget
        self.term_textbox = ctk.CTkTextbox(
            term_container,
            fg_color=GUI_TERMINAL_BG,
            text_color=GUI_ACCENT_COLOR,
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=4,
            wrap="char",
            activate_scrollbars=True,
        )
        self.term_textbox.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self.term_textbox.configure(state="disabled")

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color="transparent", height=24)
        footer.pack(fill="x", padx=16, pady=(0, 8))

        token_set = credentials.load_credential(credentials.KEY_BOT_TOKEN) is not None
        master_set = credentials.load_credential(credentials.KEY_MASTER_USER_ID) is not None

        token_badge = t("token_ok") if token_set else t("token_missing")
        master_badge = t("master_ok") if master_set else t("master_missing")

        self.lbl_config_status = ctk.CTkLabel(
            footer,
            text=f"{token_badge}  |  {master_badge}",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=GUI_MUTED_TEXT,
        )
        self.lbl_config_status.pack(side="left")

        self.lbl_ver = ctk.CTkLabel(
            footer,
            text=t("footer_version", version=APP_VERSION),
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=GUI_MUTED_TEXT,
        )
        self.lbl_ver.pack(side="right")

    # =========================================================================
    # Queue Polling (Thread-Safe GUI Updates)
    # =========================================================================

    def _poll_queue(self) -> None:
        """Pulls log messages from queue.Queue and inserts into TextBox."""
        has_new = False
        self.term_textbox.configure(state="normal")

        while True:
            try:
                msg = self.log_queue.get_nowait()
                self.term_textbox.insert("end", msg + "\n")
                has_new = True
            except queue.Empty:
                break

        if has_new:
            self.term_textbox.see("end")

        self.term_textbox.configure(state="disabled")

        # Keep polling every 100ms
        self.after(GUI_QUEUE_POLL_INTERVAL_MS, self._poll_queue)

    def _clear_terminal(self) -> None:
        self.term_textbox.configure(state="normal")
        self.term_textbox.delete("1.0", "end")
        self.term_textbox.configure(state="disabled")

    # =========================================================================
    # Event Handlers & Actions
    # =========================================================================

    def _toggle_bot_state(self) -> None:
        curr_state = self.bot_manager.state
        if curr_state in (BotState.RUNNING, BotState.STARTING):
            self.bot_manager.stop_bot()
            self._update_status_display(BotState.STOPPED)
        else:
            started = self.bot_manager.start_bot()
            if started:
                self._update_status_display(BotState.STARTING)
            else:
                self._update_status_display(BotState.ERROR)

    def _update_status_display(self, state: BotState) -> None:
        """Updates the status badge and toggle button text/color."""
        colors = {
            BotState.RUNNING: (GUI_ACCENT_COLOR, "#003314", GUI_DANGER_COLOR, GUI_DANGER_HOVER),
            BotState.STARTING: (GUI_WARNING_COLOR, "#332200", "#555555", "#555555"),
            BotState.STOPPING: (GUI_WARNING_COLOR, "#332200", "#555555", "#555555"),
            BotState.STOPPED: (GUI_MUTED_TEXT, "#1E1E1E", GUI_ACCENT_COLOR, GUI_ACCENT_HOVER),
            BotState.ERROR: (GUI_DANGER_COLOR, "#330A14", GUI_ACCENT_COLOR, GUI_ACCENT_HOVER),
        }

        btn_texts = {
            BotState.RUNNING: t("btn_stop_bot"),
            BotState.STARTING: t("btn_starting_bot"),
            BotState.STOPPING: t("btn_stopping_bot"),
            BotState.STOPPED: t("btn_start_bot"),
            BotState.ERROR: t("btn_start_bot"),
        }

        state_texts = {
            BotState.RUNNING: t("state_running"),
            BotState.STARTING: t("state_starting"),
            BotState.STOPPING: t("state_stopping"),
            BotState.STOPPED: t("state_stopped"),
            BotState.ERROR: t("state_error"),
        }

        fg_badge, bg_badge, btn_bg, btn_hover = colors.get(
            state, (GUI_MUTED_TEXT, "#1E1E1E", GUI_ACCENT_COLOR, GUI_ACCENT_HOVER)
        )
        btn_text = btn_texts.get(state, t("btn_start_bot"))
        state_label = state_texts.get(state, state.value)
        prefix = t("status_prefix")

        self.status_badge.configure(
            text=f"{prefix}: {state_label}",
            text_color=fg_badge,
            fg_color=bg_badge,
        )
        self.btn_toggle_bot.configure(
            text=btn_text,
            fg_color=btn_bg,
            hover_color=btn_hover,
        )

        # Update footer indicators
        token_set = credentials.load_credential(credentials.KEY_BOT_TOKEN) is not None
        master_set = credentials.load_credential(credentials.KEY_MASTER_USER_ID) is not None
        token_badge = t("token_ok") if token_set else t("token_missing")
        master_badge = t("master_ok") if master_set else t("master_missing")
        self.lbl_config_status.configure(text=f"{token_badge}  |  {master_badge}")

    def retranslate_ui(self) -> None:
        """Dynamically updates all UI text elements when the language changes."""
        self.title(t("app_title"))

        # Header & Status
        self._update_status_display(self.bot_manager.state)

        # Controls
        self.btn_token.configure(text=t("btn_token"))
        self.btn_master.configure(text=t("btn_master"))
        self.btn_bg.configure(text=t("btn_background"))
        self.btn_lang.configure(text=t("btn_language"))
        self.btn_credits.configure(text=t("btn_credits"))
        self.chk_startup.configure(text=t("chk_startup"))
        self._update_mail_button(self.mail_monitor.is_running())

        # Terminal
        self.lbl_term.configure(text=t("terminal_header"))
        self.btn_clear.configure(text=t("btn_clear"))

        # Footer
        self.lbl_ver.configure(text=t("footer_version", version=APP_VERSION))

    def on_bot_state_changed(self, new_state: BotState) -> None:
        """Thread-safe state change hook dispatched to main thread."""
        self.after(0, lambda: self._update_status_display(new_state))

    def _open_token_dialog(self) -> None:
        TokenConfigDialog(self, on_saved=lambda: self._update_status_display(self.bot_manager.state))

    def _open_master_dialog(self) -> None:
        MasterIdConfigDialog(self, on_saved=lambda: self._update_status_display(self.bot_manager.state))

    def _open_credits_dialog(self) -> None:
        CreditsDialog(self)

    def _open_language_dialog(self) -> None:
        """Open the Language settings dialog."""
        LanguageConfigDialog(self, on_saved=self.retranslate_ui)

    def _open_mail_notify_dialog(self) -> None:
        """Open the Mail Notification settings dialog."""
        MailNotificationDialog(self, self.mail_monitor)

    def _on_toggle_startup(self) -> None:
        enable = self.startup_var.get()
        success = toggle_startup(enable)
        if not success:
            # Revert checkbox if registry failed
            self.startup_var.set(not enable)

    def _update_mail_button(self, active: bool) -> None:
        """Updates the mail notification button appearance based on monitor state."""
        if active:
            self.btn_mail_notify.configure(
                text=t("btn_mail_active"),
                image=get_button_icon("mail"),
                fg_color=GUI_ACCENT_COLOR,
                text_color="#000000",
                hover_color=GUI_ACCENT_HOVER,
            )
        else:
            self.btn_mail_notify.configure(
                text=t("btn_mail_notify"),
                image=get_button_icon("mail"),
                fg_color="#1F2A22",
                text_color=GUI_TEXT_COLOR,
                hover_color="#2A3D2F",
                border_color=GUI_BORDER_COLOR,
            )

    def hide_to_tray(self) -> None:
        """Hides the main window to the system notification area."""
        self.withdraw()
        logger.info(t("log_window_minimized"))

    def show_from_tray(self) -> None:
        """Restores and focuses the main window from system tray."""
        self.after(0, self._restore_window)

    def _restore_window(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()
        logger.info(t("log_window_restored"))

    def _on_window_close(self) -> None:
        """
        Intercepts the window 'X' button:
        Requests orderly shutdown of the entire application.
        """
        self.on_request_shutdown()
