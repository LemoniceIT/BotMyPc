"""
Internationalization (i18n) module for BotMyPC.

Supports English (default), German, Spanish, Italian, and French.
Persists the selected language in %LOCALAPPDATA%\\BotMyPC\\settings.json.
Provides thread-safe access and instantaneous UI updates upon language switch.
"""

from __future__ import annotations
import json
import logging
from typing import Dict, Any, Optional

from config import APP_NAME, APP_VERSION, SETTINGS_FILE_PATH, BASE_DIR
from pathlib import Path

logger = logging.getLogger(APP_NAME)

LOCALES_DIR: Path = BASE_DIR / "locales"

DEFAULT_LANGUAGE: str = "en"

SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "en": {"code": "en", "name": "English", "native": "English", "flag": "🇬🇧"},
    "de": {"code": "de", "name": "German", "native": "Deutsch", "flag": "🇩🇪"},
    "es": {"code": "es", "name": "Spanish", "native": "Español", "flag": "🇪🇸"},
    "it": {"code": "it", "name": "Italian", "native": "Italiano", "flag": "🇮🇹"},
    "fr": {"code": "fr", "name": "French", "native": "Français", "flag": "🇫🇷"},
}

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # Header & Status
        "app_title": "BotMyPC — Telegram Remote Controller",
        "status_prefix": "STATUS",
        "state_stopped": "STOPPED",
        "state_starting": "STARTING",
        "state_running": "RUNNING",
        "state_stopping": "STOPPING",
        "state_error": "ERROR",
        "btn_start_bot": "Start Bot",
        "btn_stop_bot": "STOP BOT",
        "btn_starting_bot": "STARTING...",
        "btn_stopping_bot": "STOPPING...",

        # Control Bar
        "btn_token": "API Token",
        "btn_master": "Master ID",
        "btn_background": "Background",
        "btn_mail_notify": "Mail Alert",
        "btn_mail_active": "Mail ACTIVE",
        "btn_language": "Language",
        "btn_credits": "Credits",
        "chk_startup": "Run on Startup",

        # Terminal
        "terminal_header": "  > TERMINAL LOG [READ-ONLY]",
        "btn_clear": "Clear",

        # Footer
        "token_ok": "TOKEN: OK",
        "token_missing": "TOKEN: MISSING",
        "master_ok": "MASTER: OK",
        "master_missing": "MASTER: MISSING",
        "footer_version": f"v{APP_VERSION} — Windows 11 Ready",

        # Common Dialog Actions
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        "btn_close": "Close",

        # Language Dialog
        "lang_dialog_title": "Select Language",
        "lang_dialog_header": "🌐 Application Language",
        "lang_dialog_info": "Choose your preferred display language.\nChanges apply immediately and persist across sessions.",
        "lang_en": "English (Default)",
        "lang_de": "German (Deutsch)",
        "lang_es": "Spanish (Español)",
        "lang_it": "Italian (Italiano)",
        "lang_fr": "French (Français)",

        # Token Dialog
        "token_dialog_title": "Configure Telegram Bot Token",
        "token_dialog_header": "🔑 Telegram Token Configuration",
        "token_dialog_info": "Enter the bot token obtained from @BotFather.\nThe token will be encrypted and stored securely.",
        "token_current": "Current token: {token}",
        "token_placeholder": "e.g. 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567",
        "token_error_empty": "Please enter a valid token.",
        "token_error_format": "Invalid token format (check characters).",
        "token_error_save": "Error saving to credential storage.",
        "token_btn_save": "Save Token",

        # Master ID Dialog
        "master_dialog_title": "Configure Master Account",
        "master_dialog_header": "👑 Master User ID Configuration",
        "master_dialog_info": (
            "Enter your numerical Telegram User ID.\n"
            "Only this user will be allowed to send commands to the PC.\n"
            "(Find your ID by sending a message to @userinfobot on Telegram)"
        ),
        "master_current": "Current Master ID: {id}",
        "master_not_configured": "[NOT CONFIGURED]",
        "master_placeholder": "e.g. 987654321",
        "master_error_numeric": "The ID must contain only numbers.",
        "master_error_save": "Error saving credentials.",
        "master_btn_save": "Save Master ID",

        # Credits Dialog
        "credits_dialog_title": "Credits & Information",
        "credits_author": "Developed by Stefano D'Angelo AKA Lemonice",
        "credits_subtitle": "Windows 11 Remote Controller via Telegram Bot",
        "credits_tech_title": "Libraries & Technologies Used:",
        "credits_tech_desc": (
            "Libraries and Technologies Used:\n\n"
            "• Python 3.11+ & Asyncio Threading\n"
            "• CustomTkinter (Cyberpunk Graphical Interface)\n"
            "• python-telegram-bot (Telegram API v20+)\n"
            "• Windows Credential Manager (keyring) & DPAPI\n"
            "• cryptography (Fernet AES-CBC / HMAC)\n"
            "• psutil (Process Management & Uptime)\n"
            "• pystray & Pillow (System Tray Integration)\n"
            "• Winreg & ctypes (Native Windows 11 Integration)"
        ),
        "credits_license": "📜 License: MIT License (Free software with attribution. Provided 'AS IS' without warranty of any kind).",

        # Mail Dialog
        "mail_dialog_title": "📧 Email Notifications",
        "mail_dialog_header": "📧 Email Alerts via Telegram",
        "mail_dialog_info": (
            "Monitors Outlook inbox and sends a Telegram\n"
            "notification when the subject contains\n"
            "one of the configured keywords."
        ),
        "mail_keywords_lbl": "Keywords (comma-separated):",
        "mail_keywords_placeholder": "e.g. urgent, invoice, important",
        "mail_btn_start": "Start Monitoring",
        "mail_btn_stop": "Stop Monitoring",
        "mail_btn_save_kw": "Save Keywords",
        "mail_kw_saved": "✅ Keywords saved.",
        "mail_err_master": "❌ Configure Master User ID first.",
        "mail_err_bot": "❌ Start Telegram Bot first (monitor needs the bot to send alerts).",

        # Tray
        "tray_show": "Show BotMyPC",
        "tray_exit": "Exit",

        # Log Messages — Application Lifecycle (main.py)
        "log_started": "{app_name} v{version} started on Windows 11.",
        "log_credentials_status": "Credentials: Bot Token {token}, Master ID {master}.",
        "log_token_present": "PRESENT",
        "log_token_missing": "MISSING",
        "log_shutdown_start": "Starting orderly shutdown sequence...",
        "log_error_stopping_bot": "Error stopping bot: {e}",
        "log_error_stopping_mail": "Error stopping mail monitor: {e}",
        "log_error_stopping_tray": "Error stopping tray: {e}",
        "log_shutdown_done": "Application shutdown complete.",
        "log_unexpected_error": "Unexpected error in GUI mainloop: {e}",

        # Log Messages — i18n (i18n.py)
        "log_language_set": "Language updated to '{lang}' and saved to settings.",

        # Log Messages — Telegram Bot (telegram_bot.py)
        "log_bot_state": "Bot state: {state}",
        "log_state_change_error": "Error invoking on_state_change: {e}",
        "log_bot_already_running": "Attempt to start bot when already running.",
        "log_bot_token_missing": "Cannot start bot: Token not configured.",
        "log_bot_token_missing_gui": "[ERROR] Bot Token not configured. Configure it before starting.",
        "log_bot_stopping": "Stopping bot...",
        "log_bot_stopped": "Bot stopped successfully.",
        "log_send_not_running": "send_message: bot not running, cannot send.",
        "log_send_master_unconfigured": "send_message: Master User ID not configured.",
        "log_send_master_invalid": "send_message: Master User ID is invalid.",
        "log_markdown_failed": "send_message: Markdown send failed, retrying plain text: {e}",
        "log_send_fallback_failed": "send_message: fallback send failed: {e2}",
        "log_send_error": "send_message: error during sending: {e}",
        "log_fatal_bot_error": "Fatal error in Telegram bot thread: {e}",
        "log_bot_started": "Telegram bot started and listening.",
        "log_telegram_startup_error": "Telegram startup/connection error: {e}",
        "log_closing_telegram": "Closing Telegram updater and application...",
        "log_invalid_command": "Invalid command rejected: '{cmd}' ({err})",
        "log_dup_command": "Duplicate command ignored for ID {sender_id}: '{cmd}'",
        "log_cmd_received": "Command received from Master: /{cmd} {arg}",
        "log_unknown_command": "Unknown command: '{cmd}'",
        "log_command_result": "Command result {cmd}: {msg}",

        # Log Messages — Security (security.py)
        "log_sec_master_unconfigured": "Telegram update rejected: Master User ID is not configured on this PC.",
        "log_sec_master_invalid_int": "Configured Master User ID is not a valid integer.",
        "log_sec_unauthorized_access": "UNAUTHORIZED ACCESS ATTEMPT: User ID={user_id} ({username}) tried to send: '{preview}'",

        # Log Messages — Credentials (credentials.py)
        "log_fallback_read_error": "Could not read encrypted fallback credentials: {e}",
        "log_keyring_save_error": "Keyring failed to save '{key}': {e}. Trying DPAPI fallback...",
        "log_dpapi_save_error": "Failed to save credential '{key}' to DPAPI fallback: {e}",
        "log_keyring_load_debug": "Keyring load exception for '{key}': {e}",
        "log_fallback_load_debug": "Fallback load exception for '{key}': {e}",

        # Log Messages — Outlook Monitor (outlook_monitor.py)
        "log_mail_config_error": "Failed to load mail notify config: {e}",
        "log_mail_config_save_error": "Failed to save mail notify config: {e}",
        "log_mail_already_running": "OutlookMailMonitor already running.",
        "log_mail_started": "OutlookMailMonitor started. Notification cutoff: emails received after {cutoff} will trigger alerts.",
        "log_mail_stopped": "OutlookMailMonitor stopped.",
        "log_outlook_com_ok": "Outlook COM access OK. Monitoring Inbox for unread messages.",
        "log_cutoff_time": "Cutoff: emails received before {cutoff} will be ignored.",
        "log_polling_folder": "Polling {folder}: {count} unread message(s).",
        "log_mail_ignored_old": "Mail ignored (too old) in {folder}: '{subject}'",
        "log_mail_keyword_match": "Matching email found in {folder}: '{subject}'",
        "log_telegram_notify_sent": "Telegram notification sent successfully.",
        "log_telegram_notify_failed": "Failed to send Telegram notification.",
        "log_bot_manager_unavailable": "Bot manager unavailable, cannot send notification.",
        "log_outlook_processing_error": "Error while processing Outlook emails: {e}",
        "log_mail_thread_exit": "OutlookMailMonitor thread exiting.",
        "log_outlook_com_error": "Unable to access Outlook via COM: {e}",

        # Log Messages — GUI (gui.py)
        "log_token_saved": "Telegram API token configured and saved to credential storage.",
        "log_master_saved": "Master User ID configured and saved.",
        "log_mail_keywords_updated": "Mail notification keywords updated.",
        "log_window_minimized": "Window minimized to System Tray.",
        "log_window_restored": "Window restored from System Tray.",

        # Log Messages — Tray (tray.py)
        "log_tray_started": "System Tray started.",
        "log_tray_start_error": "Could not start System Tray: {e}",
        "log_tray_icon_error": "Could not load icon file {path}: {e}",
        "log_tray_stopped": "System Tray removed.",
        "log_tray_show_error": "Error in tray 'Show' handler: {e}",
        "log_tray_exit_error": "Error in tray 'Exit' handler: {e}",

        # Log Messages — System Commands (commands/system.py)
        "log_error_shutdown_call": "Exception during shutdown call:",
        "log_error_restart_call": "Exception during restart call:",
        "log_error_shutdown_abort": "Exception during shutdown /a call:",
        "log_error_lockworkstation": "Exception during LockWorkStation:",

        # Log Messages — Panic (commands/processes.py)
        "log_panic_procedure": "PANIC PROCEDURE INITIATED: Terminating user applications...",
        "log_panic_terminating": "Panic terminating PID={pid} ({name})...",
        "log_access_denied_terminate": "AccessDenied while trying to terminate PID {pid}",
        "log_exception_terminating": "Exception terminating PID {proc}: {e}",
        "log_resolve_hierarchy_error": "Could not resolve process hierarchy: {e}",

        # Log Messages — Applications (commands/applications.py)
        "log_firefox_not_found": "Firefox launch attempt: executable not found.",
        "log_firefox_start_error": "Error launching Firefox ({exe}):",
        "log_outlook_not_found": "Outlook launch attempt: executable not found.",
        "log_outlook_start_error": "Error launching Outlook ({exe}):",
        "log_notepad_note_error": "Error opening Notepad for note:",

        # Log Messages — Command Result Messages (commands/*.py)
        "log_unhandled_error": "Unhandled error in command execution: {cmd}:",
        "log_msg_shutdown_scheduled": "Shutdown scheduled in {delay}s.",
        "log_msg_shutdown_error": "Shutdown error: {err}",
        "log_msg_shutdown_exception": "Shutdown exception: {e}",
        "log_msg_restart_scheduled": "Restart scheduled in {delay}s.",
        "log_msg_restart_error": "Restart error: {err}",
        "log_msg_restart_exception": "Restart exception: {e}",
        "log_msg_abort_done": "Shutdown/Restart cancelled.",
        "log_msg_abort_none": "Shutdown cancel attempted: no pending operation.",
        "log_msg_abort_exception": "Abort exception: {e}",
        "log_msg_lock_success": "Workstation locked successfully.",
        "log_msg_lock_failed": "LockWorkStation failed with code {code}.",
        "log_msg_lock_exception": "LockWorkStation exception: {e}",
        "log_msg_ping": "Ping answered. Uptime: {uptime}",
        "log_msg_status": "Status command executed successfully.",
        "log_msg_help": "Command help sent.",
        "log_msg_panic_done": "Panic executed: {terminated} processes closed, {denied} protected.",
        "log_msg_firefox_not_found": "Firefox not found.",
        "log_msg_firefox_launched": "Started Firefox from: {exe}",
        "log_msg_firefox_error": "Firefox launch error: {e}",
        "log_msg_outlook_not_found": "Outlook not found.",
        "log_msg_outlook_launched": "Started Outlook from: {exe}",
        "log_msg_outlook_error": "Outlook launch error: {e}",
        "log_msg_note_opened": "Opened Notepad with note: '{preview}'",
        "log_msg_note_error": "Notepad launch error: {e}",
        "log_msg_note_empty": "Attempted to open empty note.",
        "log_error_internal": "Internal error in {cmd}: {e}",
        "log_msg_unknown_windows_error": "Unknown Windows error.",

        # Log Messages — Icons (icons.py)
        "log_icon_generate_error": "Failed to generate icon {name}: {e}",
        "log_icon_not_found": "Icon file not found: {path}",
        "log_icon_load_error": "Error loading icon '{name}' from {path}: {e}",

        # Log Messages — Startup (startup.py)
        "log_startup_enabled": "Windows startup enabled: {cmd}",
        "log_startup_enable_error": "Error enabling Windows startup: {e}",
        "log_startup_disabled": "Windows startup disabled.",
        "log_startup_disable_error": "Error disabling Windows startup: {e}",

        # Telegram Bot Messages (user-facing replies)
        "telegram_empty_message": "Empty or non-text message.",
        "telegram_mail_notification": "📧 *New email* ({folder})\n*Sender*: {sender}\n*Subject*: {subject}\n*Time*: {time}",
        "telegram_no_command": "No command identified.",
        "telegram_note_empty_arg": "Enter note text after 'note:'. Example: note: remember the meeting",
        "telegram_too_many_args": "Too many arguments. Commands do not accept arbitrary parameters.",
        "telegram_no_extra_args": "The command '{cmd}' does not accept additional arguments.",
        "telegram_invalid_cmd": "Invalid command.",
        "telegram_reply_invalid_cmd": "⚠️ {err}\nSend `/help` to view authorized commands.",
        "telegram_unknown_cmd": "❓ Unknown command: `/{cmd}`\nSend `/help` to view authorized commands.",
        "telegram_master_unconfigured": "❌ Master User ID is not configured on this computer.",
        "telegram_master_invalid": "❌ Local Master User ID configuration is invalid.",
        "telegram_unauthorized": "⛔ Access denied: Unauthorized user.",
        "telegram_panic_prompt": "⚠️ *ATTENTION*: The `/panic` command will close open user applications and may cause loss of unsaved data.\n\nTo confirm, send within 15 seconds:\n`/panic confirm`",
        "telegram_panic_no_pending": "No pending panic request. Send `/panic` first.",
        "telegram_panic_expired": "Panic request expired ({elapsed:.1f}s > {timeout}s). Send `/panic` again.",
        "telegram_panic_invalid_arg": "Invalid argument. To confirm send exactly: `/panic confirm`.",
        "telegram_shutdown_sched": "🛑 Shutdown scheduled in {delay} seconds.\nUse `/annulla` to cancel immediately.",
        "telegram_shutdown_error": "❌ Could not schedule shutdown: {err}",
        "telegram_shutdown_internal_error": "❌ Internal error during shutdown: {e}",
        "telegram_restart_sched": "🔄 Restart scheduled in {delay} seconds.\nUse `/annulla` to cancel immediately.",
        "telegram_restart_error": "❌ Could not schedule restart: {err}",
        "telegram_restart_internal_error": "❌ Internal error during restart: {e}",
        "telegram_abort_done": "✅ {action} cancelled successfully.",
        "telegram_abort_none": "ℹ️ No shutdown or restart operation to cancel.",
        "telegram_abort_internal_error": "❌ Internal error during cancellation: {e}",
        "telegram_lock_success": "🔒 Windows workstation locked.",
        "telegram_lock_error": "❌ Workstation lock error (code: {code}).",
        "telegram_lock_internal_error": "❌ Error locking workstation: {e}",
        "telegram_ping": "🏓 *PONG*\n━━━━━━━━━━━━━━━━━━━━\n💻 PC Online and ready\n⏱️ Local time: `{time}`\n⏳ System uptime: `{uptime}`",
        "telegram_status_header": "📊 *BOT & SYSTEM STATUS*",
        "telegram_status_separator": "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "telegram_status_bot": "🤖 Telegram Bot: `ONLINE`",
        "telegram_status_master": "👑 Master User: `{status}`",
        "telegram_status_startup": "🚀 Windows Startup: `{status}`",
        "telegram_status_tray": "🗂️ System Tray: `ACTIVE`",
        "telegram_status_version": "📦 App version: `v{version}`",
        "telegram_status_cmd_count": "📋 Registered commands: `{count}`",
        "telegram_status_subsep": "───────────────────────────",
        "telegram_status_uptime": "⏳ PC Uptime: `{uptime}`",
        "telegram_status_metrics": "⚡ CPU: `{cpu}` | RAM: `{ram}`",
        "telegram_status_pending_active": "⚠️ In progress ({action})",
        "telegram_status_pending_none": "None",
        "telegram_panic_done": "🚨 *PANIC PROCEDURE COMPLETED*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📉 User processes closed: `{count}`\n🛡️ System processes protected",
        "telegram_panic_denied": "⚠️ Processes protected by elevated permissions: `{count}`\n",
        "telegram_firefox_not_found": "❌ Firefox not found on this system.",
        "telegram_firefox_launched": "🌐 Mozilla Firefox launched successfully.",
        "telegram_firefox_error": "❌ Error launching Firefox: {e}",
        "telegram_outlook_not_found": "❌ Outlook not found on this system.",
        "telegram_outlook_launched": "📧 Microsoft Outlook launched successfully.",
        "telegram_outlook_error": "❌ Error launching Outlook: {e}",
        "telegram_note_empty_msg": "❌ Note text cannot be empty.",
        "telegram_note_opened": "📝 *Notepad opened on PC!*\n📄 Content: _{preview}_\n📁 Saved as: `{filename}`",
        "telegram_notepad_error": "❌ Error opening Notepad: {e}",
        "telegram_help_header": "🖥️ *BotMyPC — Remote PC Controller*",
        "telegram_help_list_header": "Here is the list of authorized commands:\n",
        "telegram_help_separator": "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "telegram_help_destructive_header": "\n*System impact commands:*",
        "telegram_help_footer": "🛡️ _Unauthorized commands or those with arbitrary arguments are rejected._",
        "telegram_action_shutdown": "Shutdown",
        "telegram_action_restart": "Restart",
        "telegram_action_unknown": "Operation",
        "cmd_shutdown_desc": "Schedules PC shutdown in 10 seconds (cancelable)",
        "cmd_restart_desc": "Schedules PC restart in 10 seconds (cancelable)",
        "cmd_annulla_desc": "Cancels a scheduled shutdown or restart",
        "cmd_out_desc": "Immediately locks the Windows workstation (Lock Workstation)",
        "cmd_ping_desc": "Checks if PC is online and returns system uptime",
        "cmd_status_desc": "Shows detailed status of the application, bot, and PC resources",
        "cmd_help_desc": "Shows the list of authorized commands and their descriptions",
        "cmd_firefox_desc": "Launches Mozilla Firefox (with automatic path detection)",
        "cmd_outlook_desc": "Launches Microsoft Outlook (with Click-to-Run / MSI detection)",
        "cmd_note_desc": "Opens Notepad and pastes the sent text",
        "cmd_panic_desc": "Closes user applications (requires confirmation: /panic confirm)",
    },
    "de": {
        # Header & Status
        "app_title": "BotMyPC — Telegram Fernsteuerung",
        "status_prefix": "STATUS",
        "state_stopped": "GESTOPPT",
        "state_starting": "STARTET",
        "state_running": "LÄUFT",
        "state_stopping": "BEENDET",
        "state_error": "FEHLER",
        "btn_start_bot": "Bot starten",
        "btn_stop_bot": "BOT STOPPEN",
        "btn_starting_bot": "STARTET...",
        "btn_stopping_bot": "BEENDET...",

        # Control Bar
        "btn_token": "API-Token",
        "btn_master": "Master-ID",
        "btn_background": "Hintergrund",
        "btn_mail_notify": "E-Mail-Alert",
        "btn_mail_active": "E-Mail AKTIV",
        "btn_language": "Sprache",
        "btn_credits": "Credits",
        "chk_startup": "Mit Windows starten",

        # Terminal
        "terminal_header": "  > TERMINAL-LOG [SCHREIBGESCHÜTZT]",
        "btn_clear": "Löschen",

        # Footer
        "token_ok": "TOKEN: OK",
        "token_missing": "TOKEN: FEHLT",
        "master_ok": "MASTER: OK",
        "master_missing": "MASTER: FEHLT",
        "footer_version": f"v{APP_VERSION} — Bereit für Windows 11",

        # Common Dialog Actions
        "btn_save": "Speichern",
        "btn_cancel": "Abbrechen",
        "btn_close": "Schließen",

        # Language Dialog
        "lang_dialog_title": "Sprache auswählen",
        "lang_dialog_header": "🌐 Anwendungssprache",
        "lang_dialog_info": "Wählen Sie Ihre bevorzugte Anzeigesprache.\nÄnderungen werden sofort wirksam und gespeichert.",
        "lang_en": "Englisch (Default)",
        "lang_de": "Deutsch (German)",
        "lang_es": "Spanisch (Español)",
        "lang_it": "Italienisch (Italiano)",
        "lang_fr": "Französisch (Français)",

        # Token Dialog
        "token_dialog_title": "Telegram-Bot-Token konfigurieren",
        "token_dialog_header": "🔑 Telegram-Token-Konfiguration",
        "token_dialog_info": "Geben Sie das von @BotFather erhaltene Token ein.\nDas Token wird verschlüsselt und sicher gespeichert.",
        "token_current": "Aktuelles Token: {token}",
        "token_placeholder": "z.B. 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567",
        "token_error_empty": "Bitte geben Sie ein gültiges Token ein.",
        "token_error_format": "Ungültiges Token-Format (Zeichen prüfen).",
        "token_error_save": "Fehler beim Speichern in der Anmeldeinformationsverwaltung.",
        "token_btn_save": "Token speichern",

        # Master ID Dialog
        "master_dialog_title": "Master-Konto konfigurieren",
        "master_dialog_header": "👑 Master-Benutzer-ID-Konfiguration",
        "master_dialog_info": (
            "Geben Sie Ihre numerische Telegram-Benutzer-ID ein.\n"
            "Nur dieser Benutzer darf Befehle an den PC senden.\n"
            "(Ermitteln Sie Ihre ID über @userinfobot auf Telegram)"
        ),
        "master_current": "Aktuelle Master-ID: {id}",
        "master_not_configured": "[NICHT KONFIGURIERT]",
        "master_placeholder": "z.B. 987654321",
        "master_error_numeric": "Die ID darf nur aus Ziffern bestehen.",
        "master_error_save": "Fehler beim Speichern der Anmeldeinformationen.",
        "master_btn_save": "Master-ID speichern",

        # Credits Dialog
        "credits_dialog_title": "Credits & Informationen",
        "credits_author": "Entwickelt von Stefano D'Angelo AKA Lemonice",
        "credits_subtitle": "Windows 11 Fernbedienung via Telegram-Bot",
        "credits_tech_title": "Verwendete Bibliotheken & Technologien:",
        "credits_tech_desc": (
            "Verwendete Bibliotheken & Technologien:\n\n"
            "• Python 3.11+ & Asyncio Threading\n"
            "• CustomTkinter (Cyberpunk Benutzeroberfläche)\n"
            "• python-telegram-bot (Telegram API v20+)\n"
            "• Windows Credential Manager (keyring) & DPAPI\n"
            "• cryptography (Fernet AES-CBC / HMAC)\n"
            "• psutil (Prozesskontrolle & Betriebszeit)\n"
            "• pystray & Pillow (System Tray Integration)\n"
            "• Winreg & ctypes (Native Windows 11 Integration)"
        ),
        "credits_license": "📜 Lizenz: MIT-Lizenz (Freie Software mit Namensnennung. Bereitgestellt 'AS IS' ohne Mängelgewähr oder Haftung).",

        # Mail Dialog
        "mail_dialog_title": "📧 E-Mail-Benachrichtigungen",
        "mail_dialog_header": "📧 E-Mail-Benachrichtigungen via Telegram",
        "mail_dialog_info": (
            "Überwacht den Outlook-Posteingang und sendet eine\n"
            "Telegram-Nachricht, wenn der Betreff eines\n"
            "der konfigurierten Schlüsselwörter enthält."
        ),
        "mail_keywords_lbl": "Schlüsselwörter (kommagetrennt):",
        "mail_keywords_placeholder": "z.B. wichtig, dringend, Rechnung",
        "mail_btn_start": "Überwachung starten",
        "mail_btn_stop": "Überwachung stoppen",
        "mail_btn_save_kw": "Schlüsselwörter speichern",
        "mail_kw_saved": "✅ Schlüsselwörter gespeichert.",
        "mail_err_master": "❌ Bitte zuerst Master-Benutzer-ID konfigurieren.",
        "mail_err_bot": "❌ Bitte zuerst den Telegram-Bot starten.",

        # Tray
        "tray_show": "BotMyPC anzeigen",
        "tray_exit": "Beenden",

        # Log Messages — Application Lifecycle (main.py)
        "log_started": "{app_name} v{version} gestartet auf Windows 11.",
        "log_credentials_status": "Anmeldedaten: Bot-Token {token}, Master-ID {master}.",
        "log_token_present": "VORHANDEN",
        "log_token_missing": "FEHLT",
        "log_shutdown_start": "Start der geordneten Herunterfahrt...",
        "log_error_stopping_bot": "Fehler beim Stoppen des Bots: {e}",
        "log_error_stopping_mail": "Fehler beim Stoppen des Mail-Monitors: {e}",
        "log_error_stopping_tray": "Fehler beim Stoppen der Tray: {e}",
        "log_shutdown_done": "Anwendungs-Shutdown abgeschlossen.",
        "log_unexpected_error": "Unerwarteter Fehler in GUI-Mainloop: {e}",

        # Log Messages — i18n (i18n.py)
        "log_language_set": "Sprache auf '{lang}' aktualisiert und in Einstellungen gespeichert.",

        # Log Messages — Telegram Bot (telegram_bot.py)
        "log_bot_state": "Bot-Status: {state}",
        "log_state_change_error": "Fehler beim Aufruf von on_state_change: {e}",
        "log_bot_already_running": "Versuch, Bot zu starten, obwohl er bereits läuft.",
        "log_bot_token_missing": "Bot kann nicht gestartet werden: Token nicht konfiguriert.",
        "log_bot_token_missing_gui": "[FEHLER] Bot-Token nicht konfiguriert. Konfigurieren Sie ihn, bevor Sie starten.",
        "log_bot_stopping": "Bot wird gestoppt...",
        "log_bot_stopped": "Bot erfolgreich gestoppt.",
        "log_send_not_running": "send_message: Bot nicht gestartet, kann nicht senden.",
        "log_send_master_unconfigured": "send_message: Master User ID nicht konfiguriert.",
        "log_send_master_invalid": "send_message: Master User ID ungültig.",
        "log_markdown_failed": "send_message: Markdown-Versand fehlgeschlagen, versuche Plain-Text: {e}",
        "log_send_fallback_failed": "send_message: Fallback-Versand fehlgeschlagen: {e2}",
        "log_send_error": "send_message: Fehler beim Senden: {e}",
        "log_fatal_bot_error": "Fataler Fehler im Telegram-Bot-Thread: {e}",
        "log_bot_started": "Telegram-Bot gestartet und lauscht.",
        "log_telegram_startup_error": "Telegram-Start-/Verbindungsfehler: {e}",
        "log_closing_telegram": "Schließe Telegram-Updater und -Anwendung...",
        "log_invalid_command": "Ungültiger Befehl abgelehnt: '{cmd}' ({err})",
        "log_dup_command": "Duplikater Befehl für ID {sender_id} ignoriert: '{cmd}'",
        "log_cmd_received": "Befehl vom Master empfangen: /{cmd} {arg}",
        "log_unknown_command": "Unbekannter Befehl: '{cmd}'",
        "log_command_result": "Befehlsergebnis {cmd}: {msg}",

        # Log Messages — Security (security.py)
        "log_sec_master_unconfigured": "Telegram-Aktualisierung abgelehnt: Master User ID ist auf diesem PC nicht konfiguriert.",
        "log_sec_master_invalid_int": "Konfigurierte Master User ID ist keine gültige ganze Zahl.",
        "log_sec_unauthorized_access": "UNAUTORISIERTES ZUGRIIFSVERSUCH: User-ID={user_id} ({username}) versuchte zu senden: '{preview}'",

        # Log Messages — Credentials (credentials.py)
        "log_fallback_read_error": "Konnte verschlüsselte Fallback-Anmeldedaten nicht lesen: {e}",
        "log_keyring_save_error": "Keyring konnte '{key}' nicht speichern: {e}. Versuche DPAPI-Fallback...",
        "log_dpapi_save_error": "Fehler beim Speichern der Anmeldedaten '{key}' im DPAPI-Fallback: {e}",
        "log_keyring_load_debug": "Keyring-Ladeausnahme für '{key}': {e}",
        "log_fallback_load_debug": "Fallback-Ladeausnahme für '{key}': {e}",

        # Log Messages — Outlook Monitor (outlook_monitor.py)
        "log_mail_config_error": "Fehler beim Laden der Mail-Benachrichtigungskonfiguration: {e}",
        "log_mail_config_save_error": "Fehler beim Speichern der Mail-Benachrichtigungskonfiguration: {e}",
        "log_mail_already_running": "OutlookMailMonitor läuft bereits.",
        "log_mail_started": "OutlookMailMonitor gestartet. Benachrichtigungsschwelle: E-Mails nach {cutoff} lösen Warnungen aus.",
        "log_mail_stopped": "OutlookMailMonitor gestoppt.",
        "log_outlook_com_ok": "Outlook COM-Zugriff OK. Überwache Posteingang auf ungelesene Nachrichten.",
        "log_cutoff_time": "Schwelle: E-Mails vor {cutoff} werden ignoriert.",
        "log_polling_folder": "Polling {folder}: {count} ungelesene Nachricht(en).",
        "log_mail_ignored_old": "E-Mail ignoriert (zu alt) in {folder}: '{subject}'",
        "log_mail_keyword_match": "Übereinstimmende E-Mail gefunden in {folder}: '{subject}'",
        "log_telegram_notify_sent": "Telegram-Benachrichtigung erfolgreich gesendet.",
        "log_telegram_notify_failed": "Telegram-Benachrichtigung konnte nicht gesendet werden.",
        "log_bot_manager_unavailable": "Bot-Manager nicht verfügbar, Benachrichtigung kann nicht gesendet werden.",
        "log_outlook_processing_error": "Fehler beim Verarbeiten von Outlook-E-Mails: {e}",
        "log_mail_thread_exit": "OutlookMailMonitor-Thread wird beendet.",
        "log_outlook_com_error": "Kann nicht auf Outlook über COM zugreifen: {e}",

        # Log Messages — GUI (gui.py)
        "log_token_saved": "Telegram-API-Token konfiguriert und im Anmeldespeicher gespeichert.",
        "log_master_saved": "Master User ID konfiguriert und gespeichert.",
        "log_mail_keywords_updated": "Mail-Benachrichtigungsschlüsselwörter aktualisiert.",
        "log_window_minimized": "Fenster in System Tray minimiert.",
        "log_window_restored": "Fenster aus System Tray wiederhergestellt.",

        # Log Messages — Tray (tray.py)
        "log_tray_started": "System Tray gestartet.",
        "log_tray_start_error": "System Tray konnte nicht gestartet werden: {e}",
        "log_tray_icon_error": "Konnte Symboldatei {path} nicht laden: {e}",
        "log_tray_stopped": "System Tray entfernt.",
        "log_tray_show_error": "Fehler im Tray-'Anzeigen'-Handler: {e}",
        "log_tray_exit_error": "Fehler im Tray-'Beenden'-Handler: {e}",

        # Log Messages — System Commands (commands/system.py)
        "log_error_shutdown_call": "Ausnahme während shutdown-Aufruf:",
        "log_error_restart_call": "Ausnahme während restart-Aufruf:",
        "log_error_shutdown_abort": "Ausnahme während shutdown /a-Aufruf:",
        "log_error_lockworkstation": "Ausnahme während LockWorkStation:",

        # Log Messages — Panic (commands/processes.py)
        "log_panic_procedure": "PANIKVERFAHREN initiiert: Benutzeranwendungen werden beendet...",
        "log_panic_terminating": "PANIC: Beende PID={pid} ({name})...",
        "log_access_denied_terminate": "AccessDenied beim Versuch, PID {pid} zu beenden",
        "log_exception_terminating": "Ausnahme beim Beenden von PID {proc}: {e}",
        "log_resolve_hierarchy_error": "Konnte Prozesshierarchie nicht auflösen: {e}",

        # Log Messages — Applications (commands/applications.py)
        "log_firefox_not_found": "Firefox-Startversuch: Ausführbare Datei nicht gefunden.",
        "log_firefox_start_error": "Fehler beim Starten von Firefox ({exe}):",
        "log_outlook_not_found": "Outlook-Startversuch: Ausführbare Datei nicht gefunden.",
        "log_outlook_start_error": "Fehler beim Starten von Outlook ({exe}):",
        "log_notepad_note_error": "Fehler beim Öffnen von Notepad für Notiz:",

        # Log Messages — Command Result Messages (commands/*.py)
        "log_unhandled_error": "Nicht behandelte Fehler bei Befehlsausführung: {cmd}:",
        "log_msg_shutdown_scheduled": "Shutdown in {delay}s geplant.",
        "log_msg_shutdown_error": "Shutdown-Fehler: {err}",
        "log_msg_shutdown_exception": "Shutdown-Ausnahme: {e}",
        "log_msg_restart_scheduled": "Neustart in {delay}s geplant.",
        "log_msg_restart_error": "Neustart-Fehler: {err}",
        "log_msg_restart_exception": "Neustart-Ausnahme: {e}",
        "log_msg_abort_done": "Shutdown/Neustart abgebrochen.",
        "log_msg_abort_none": "Shutdown-Abbrechen versucht: keine ausstehende Operation.",
        "log_msg_abort_exception": "Abbruch-Ausnahme: {e}",
        "log_msg_lock_success": "Arbeitsstation erfolgreich gesperrt.",
        "log_msg_lock_failed": "LockWorkStation fehlgeschlagen mit Code {code}.",
        "log_msg_lock_exception": "LockWorkStation-Ausnahme: {e}",
        "log_msg_ping": "Ping beantwortet. Uptime: {uptime}",
        "log_msg_status": "Status-Befehl erfolgreich ausgeführt.",
        "log_msg_help": "Befehlshilfe gesendet.",
        "log_msg_panic_done": "Panic ausgeführt: {terminated} Prozesse beendet, {denied} geschützt.",
        "log_msg_firefox_not_found": "Firefox nicht gefunden.",
        "log_msg_firefox_launched": "Firefox gestartet von: {exe}",
        "log_msg_firefox_error": "Firefox-Startfehler: {e}",
        "log_msg_outlook_not_found": "Outlook nicht gefunden.",
        "log_msg_outlook_launched": "Outlook gestartet von: {exe}",
        "log_msg_outlook_error": "Outlook-Startfehler: {e}",
        "log_msg_note_opened": "Notepad geöffnet mit Notiz: '{preview}'",
        "log_msg_note_error": "Notepad-Startfehler: {e}",
        "log_msg_note_empty": "Versuch, leere Notiz zu öffnen.",
        "log_error_internal": "Interner Fehler in {cmd}: {e}",
        "log_msg_unknown_windows_error": "Unbekannter Windows-Fehler.",

        # Log Messages — Icons (icons.py)
        "log_icon_generate_error": "Symbol konnte nicht generiert werden {name}: {e}",
        "log_icon_not_found": "Symboldatei nicht gefunden: {path}",
        "log_icon_load_error": "Fehler beim Laden des_symbols '{name}' von {path}: {e}",

        # Log Messages — Startup (startup.py)
        "log_startup_enabled": "Windows-Start aktiviert: {cmd}",
        "log_startup_enable_error": "Fehler beim Aktivieren des Windows-Starts: {e}",
        "log_startup_disabled": "Windows-Start deaktiviert.",
        "log_startup_disable_error": "Fehler beim Deaktivieren des Windows-Starts: {e}",

        # Telegram Bot Messages (user-facing replies)
        "telegram_empty_message": "Leere oder nicht-textuelle Nachricht.",
        "telegram_mail_notification": "📧 *Neue E-Mail* ({folder})\n*Absender*: {sender}\n*Betreff*: {subject}\n*Zeit*: {time}",
        "telegram_no_command": "Kein Befehl identifiziert.",
        "telegram_note_empty_arg": "Geben Sie Nachrichtentext nach 'note:' ein. Beispiel: note: Besprechung erinnern",
        "telegram_too_many_args": "Zu viele Argumente. Befehle akzeptieren keine willkürlichen Parameter.",
        "telegram_no_extra_args": "Der Befehl '{cmd}' akzeptiert keine zusätzlichen Argumente.",
        "telegram_invalid_cmd": "Ungültiger Befehl.",
        "telegram_reply_invalid_cmd": "⚠️ {err}\nSenden Sie `/help`, um autorisierte Befehle anzuzeigen.",
        "telegram_unknown_cmd": "❓ Unbekannter Befehl: `/{cmd}`\nSenden Sie `/help`, um autorisierte Befehle anzuzeigen.",
        "telegram_master_unconfigured": "❌ Master User ID ist auf diesem Computer nicht konfiguriert.",
        "telegram_master_invalid": "❌ Lokale Master User ID-Konfiguration ist ungültig.",
        "telegram_unauthorized": "⛔ Zugriff verweigert: Nicht autorisierter Benutzer.",
        "telegram_panic_prompt": "⚠️ *ACHTUNG*: Der Befehl `/panic` schließt geöffnete Benutzeranwendungen und kann zu Datenverlust führen.\n\nUm zu bestätigen, senden Sie innerhalb von 15 Sekunden:\n`/panic confirm`",
        "telegram_panic_no_pending": "Keine ausstehende Panic-Anfrage. Senden Sie zuerst `/panic`.",
        "telegram_panic_expired": "Panic-Anfrage abgelaufen ({elapsed:.1f}s > {timeout}s). Senden Sie `/panic` erneut.",
        "telegram_panic_invalid_arg": "Ungültiges Argument. Um zu bestätigen, senden Sie exakt: `/panic confirm`.",
        "telegram_shutdown_sched": "🛑 Herunterfahren in {delay} Sekunden geplant.\nVerwenden Sie `/annulla`, um sofort abzubrechen.",
        "telegram_shutdown_error": "❌ Konnte Herunterfahren nicht planen: {err}",
        "telegram_shutdown_internal_error": "❌ Interner Fehler beim Herunterfahren: {e}",
        "telegram_restart_sched": "🔄 Neustart in {delay} Sekunden geplant.\nVerwenden Sie `/annulla`, um sofort abzubrechen.",
        "telegram_restart_error": "❌ Konnte Neustart nicht planen: {err}",
        "telegram_restart_internal_error": "❌ Interner Fehler beim Neustart: {e}",
        "telegram_abort_done": "✅ {action} erfolgreich abgebrochen.",
        "telegram_abort_none": "ℹ️ Kein Herunterfahren oder Neustart zum Abbrechen.",
        "telegram_abort_internal_error": "❌ Interner Fehler beim Abbrechen: {e}",
        "telegram_lock_success": "🔒 Windows-Arbeitsstation gesperrt.",
        "telegram_lock_error": "❌ Fehler beim Sperren der Arbeitsstation (Code: {code}).",
        "telegram_lock_internal_error": "❌ Fehler beim Sperren der Arbeitsstation: {e}",
        "telegram_ping": "🏓 *PONG*\n━━━━━━━━━━━━━━━━━━━━\n💻 PC online und bereit\n⏱️ Lokalzeit: `{time}`\n⏳ Systemlaufzeit: `{uptime}`",
        "telegram_status_header": "📊 *BOT & SYSTEMSTATUS*",
        "telegram_status_separator": "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "telegram_status_bot": "🤖 Telegram Bot: `ONLINE`",
        "telegram_status_master": "👑 Master User: `{status}`",
        "telegram_status_startup": "🚀 Windows-Start: `{status}`",
        "telegram_status_tray": "🗂️ System Tray: `AKTIV`",
        "telegram_status_version": "📦 App-Version: `v{version}`",
        "telegram_status_cmd_count": "📋 Registrierte Befehle: `{count}`",
        "telegram_status_subsep": "───────────────────────────",
        "telegram_status_uptime": "⏳ PC-Laufzeit: `{uptime}`",
        "telegram_status_metrics": "⚡ CPU: `{cpu}` | RAM: `{ram}`",
        "telegram_status_pending_active": "⚠️ In Bearbeitung ({action})",
        "telegram_status_pending_none": "Keine",
        "telegram_panic_done": "🚨 *PANIC-PROZEDUR ABGESCHLOSSEN*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📉 Benutzerprozesse geschlossen: `{count}`\n🛡️ Systemprozesse geschützt",
        "telegram_panic_denied": "⚠️ Prozesse mit erhöhten Berechtigungen geschützt: `{count}`\n",
        "telegram_firefox_not_found": "❌ Firefox wurde auf diesem System nicht gefunden.",
        "telegram_firefox_launched": "🌐 Mozilla Firefox erfolgreich gestartet.",
        "telegram_firefox_error": "❌ Fehler beim Starten von Firefox: {e}",
        "telegram_outlook_not_found": "❌ Outlook wurde auf diesem System nicht gefunden.",
        "telegram_outlook_launched": "📧 Microsoft Outlook erfolgreich gestartet.",
        "telegram_outlook_error": "❌ Fehler beim Starten von Outlook: {e}",
        "telegram_note_empty_msg": "❌ Der Notiztext darf nicht leer sein.",
        "telegram_note_opened": "📝 *Notepad auf dem PC geöffnet!*\n📄 Inhalt: _{preview}_\n📁 Gespeichert als: `{filename}`",
        "telegram_notepad_error": "❌ Fehler beim Öffnen von Notepad: {e}",
        "telegram_help_header": "🖥️ *BotMyPC — Remotesteuerung PC*",
        "telegram_help_list_header": "Hier ist die Liste der autorisierten Befehle:\n",
        "telegram_help_separator": "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "telegram_help_destructive_header": "\n*Befehle mit Systemauswirkung:*",
        "telegram_help_footer": "🛡️ _Nicht registrierte Befehle oder solche mit willkürlichen Argumenten werden abgelehnt._",
        "telegram_error_internal": "❌ Es ist ein interner Fehler bei der Befehlsausführung aufgetreten.",
        "telegram_action_shutdown": "Herunterfahren",
        "telegram_action_restart": "Neustart",
        "telegram_action_unknown": "Operation",
        "cmd_shutdown_desc": "Plant PC-Herunterfahren in 10 Sekunden (abbrichtbar)",
        "cmd_restart_desc": "Plant PC-Neustart in 10 Sekunden (abbrichtbar)",
        "cmd_annulla_desc": "Bricht einen geplanten Herunterfahren oder Neustart ab",
        "cmd_out_desc": "Sperrt die Windows-Arbeitsstation sofort (LockWorkStation)",
        "cmd_ping_desc": "Prüft, ob der PC online ist, und gibt die Systemlaufzeit zurück",
        "cmd_status_desc": "Zeigt detaillierten Status der Anwendung, des Bots und der PC-Ressourcen an",
        "cmd_help_desc": "Zeigt die Liste der autorisierten Befehle und ihre Beschreibungen an",
        "cmd_firefox_desc": "Startet Mozilla Firefox (mit automatischer Pfadsuche)",
        "cmd_outlook_desc": "Startet Microsoft Outlook (mit Click-to-Run-/MSI-Erkennung)",
        "cmd_note_desc": "Öffnet Notepad und fügt den gesendeten Text ein",
        "cmd_panic_desc": "Schließt Benutzeranwendungen (Bestätigung erforderlich: /panic confirm)",
    },
    "es": {
        # Header & Status
        "app_title": "BotMyPC — Control Remoto de Telegram",
        "status_prefix": "ESTADO",
        "state_stopped": "DETENIDO",
        "state_starting": "INICIANDO",
        "state_running": "EJECUTANDO",
        "state_stopping": "DETENIENDO",
        "state_error": "ERROR",
        "btn_start_bot": "Iniciar Bot",
        "btn_stop_bot": "DETENER BOT",
        "btn_starting_bot": "INICIANDO...",
        "btn_stopping_bot": "DETENIENDO...",

        # Control Bar
        "btn_token": "Token API",
        "btn_master": "ID Maestro",
        "btn_background": "Segundo plano",
        "btn_mail_notify": "Aviso email",
        "btn_mail_active": "Email ACTIVO",
        "btn_language": "Idioma",
        "btn_credits": "Créditos",
        "chk_startup": "Iniciar con Windows",

        # Terminal
        "terminal_header": "  > TERMINAL LOG [SOLO LECTURA]",
        "btn_clear": "Limpiar",

        # Footer
        "token_ok": "TOKEN: OK",
        "token_missing": "TOKEN: FALTA",
        "master_ok": "MASTER: OK",
        "master_missing": "MASTER: FALTA",
        "footer_version": f"v{APP_VERSION} — Listo para Windows 11",

        # Common Dialog Actions
        "btn_save": "Guardar",
        "btn_cancel": "Cancelar",
        "btn_close": "Cerrar",

        # Language Dialog
        "lang_dialog_title": "Seleccionar Idioma",
        "lang_dialog_header": "🌐 Idioma de la Aplicación",
        "lang_dialog_info": "Elija su idioma preferido para la interfaz.\nLos cambios se aplican de inmediato y se guardan.",
        "lang_en": "Inglés (Default)",
        "lang_de": "Alemán (Deutsch)",
        "lang_es": "Español (Spanish)",
        "lang_it": "Italiano (Italian)",
        "lang_fr": "Francés (Français)",

        # Token Dialog
        "token_dialog_title": "Configurar Token Bot Telegram",
        "token_dialog_header": "🔑 Configuración de Token de Telegram",
        "token_dialog_info": "Ingrese el token del bot obtenido de @BotFather.\nEl token se cifrará y guardará de forma segura.",
        "token_current": "Token actual: {token}",
        "token_placeholder": "ej. 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567",
        "token_error_empty": "Ingrese un token válido.",
        "token_error_format": "Formato de token no válido (compruebe caracteres).",
        "token_error_save": "Error al guardar en el almacén de credenciales.",
        "token_btn_save": "Guardar Token",

        # Master ID Dialog
        "master_dialog_title": "Configurar Cuenta Maestra",
        "master_dialog_header": "👑 Configuración de Master User ID",
        "master_dialog_info": (
            "Ingrese su Telegram User ID numérico.\n"
            "Solo este usuario podrá enviar comandos a su PC.\n"
            "(Puede descubrir su ID enviando un mensaje a @userinfobot en Telegram)"
        ),
        "master_current": "ID Maestro actual: {id}",
        "master_not_configured": "[NO CONFIGURADO]",
        "master_placeholder": "ej. 987654321",
        "master_error_numeric": "El ID debe contener solo números.",
        "master_error_save": "Error al guardar las credenciales.",
        "master_btn_save": "Guardar ID Maestro",

        # Credits Dialog
        "credits_dialog_title": "Créditos e Información",
        "credits_author": "Desarrollado por Stefano D'Angelo AKA Lemonice",
        "credits_subtitle": "Control Remoto de Windows 11 mediante Bot de Telegram",
        "credits_tech_title": "Librerías y Tecnologías Utilizadas:",
        "credits_tech_desc": (
            "Librerías y Tecnologías Utilizadas:\n\n"
            "• Python 3.11+ & Asyncio Threading\n"
            "• CustomTkinter (Interfaz Gráfica Cyberpunk)\n"
            "• python-telegram-bot (API de Telegram v20+)\n"
            "• Administrador de credenciales de Windows & DPAPI\n"
            "• cryptography (Fernet AES-CBC / HMAC)\n"
            "• psutil (Control de Procesos y Uptime)\n"
            "• pystray & Pillow (Integración System Tray)\n"
            "• Winreg & ctypes (Integración nativa de Windows 11)"
        ),
        "credits_license": "📜 Licencia: Licencia MIT (Software libre con atribución. Proporcionado 'TAL CUAL' sin garantías de ningún tipo).",

        # Mail Dialog
        "mail_dialog_title": "📧 Notificación de Nuevos Correos",
        "mail_dialog_header": "📧 Alertas de Correo vía Telegram",
        "mail_dialog_info": (
            "Supervisa la bandeja de entrada de Outlook y envía\n"
            "una notificación de Telegram cuando el asunto contiene\n"
            "una de las palabras clave configuradas."
        ),
        "mail_keywords_lbl": "Palabras clave (separadas por comas):",
        "mail_keywords_placeholder": "ej. importante, urgente, factura",
        "mail_btn_start": "Iniciar Monitoreo",
        "mail_btn_stop": "Detener Monitoreo",
        "mail_btn_save_kw": "Guardar palabras clave",
        "mail_kw_saved": "✅ Palabras clave guardadas.",
        "mail_err_master": "❌ Configure primero el Master User ID.",
        "mail_err_bot": "❌ Inicie primero el Bot de Telegram.",

        # Tray
        "tray_show": "Mostrar BotMyPC",
        "tray_exit": "Salir",

        # Log Messages — Application Lifecycle (main.py)
        "log_started": "{app_name} v{version} iniciado en Windows 11.",
        "log_credentials_status": "Credenciales: Token Bot {token}, Master ID {master}.",
        "log_token_present": "PRESENTES",
        "log_token_missing": "FALTAN",
        "log_shutdown_start": "Iniciando secuencia de cierre ordenada...",
        "log_error_stopping_bot": "Error al detener el bot: {e}",
        "log_error_stopping_mail": "Error al detener el monitor de correo: {e}",
        "log_error_stopping_tray": "Error al cerrar la bandeja: {e}",
        "log_shutdown_done": "Cierre de aplicación completado.",
        "log_unexpected_error": "Error inesperado en el bucle principal de la GUI: {e}",

        # Log Messages — i18n (i18n.py)
        "log_language_set": "Idioma actualizado a '{lang}' y guardado en configuración.",

        # Log Messages — Telegram Bot (telegram_bot.py)
        "log_bot_state": "Estado del bot: {state}",
        "log_state_change_error": "Error al invocar on_state_change: {e}",
        "log_bot_already_running": "Intento de iniciar el bot cuando ya está en ejecución.",
        "log_bot_token_missing": "No se puede iniciar el bot: Token no configurado.",
        "log_bot_token_missing_gui": "[ERROR] Token del Bot no configurado. Configúrelo antes de iniciar.",
        "log_bot_stopping": "Deteniendo bot...",
        "log_bot_stopped": "Bot detenido correctamente.",
        "log_send_not_running": "send_message: bot no iniciado, no se puede enviar.",
        "log_send_master_unconfigured": "send_message: Master User ID no configurado.",
        "log_send_master_invalid": "send_message: Master User ID no válido.",
        "log_markdown_failed": "send_message: envío con Markdown fallido, reintentando texto plano: {e}",
        "log_send_fallback_failed": "send_message: envío de respaldo fallido: {e2}",
        "log_send_error": "send_message: error durante el envío: {e}",
        "log_fatal_bot_error": "Error fatal en el hilo del bot de Telegram: {e}",
        "log_bot_started": "Bot de Telegram iniciado y escuchando.",
        "log_telegram_startup_error": "Error de inicio/conexión de Telegram: {e}",
        "log_closing_telegram": "Cerrando actualizador y aplicación de Telegram...",
        "log_invalid_command": "Comando no válido rechazado: '{cmd}' ({err})",
        "log_dup_command": "Comando duplicado ignorado para ID {sender_id}: '{cmd}'",
        "log_cmd_received": "Comando recibido del Master: /{cmd} {arg}",
        "log_unknown_command": "Comando desconocido: '{cmd}'",
        "log_command_result": "Resultado del comando {cmd}: {msg}",

        # Log Messages — Security (security.py)
        "log_sec_master_unconfigured": "Actualización de Telegram rechazada: Master User ID no está configurado en este PC.",
        "log_sec_master_invalid_int": "La Master User ID configurada no es un entero válido.",
        "log_sec_unauthorized_access": "INTENTO DE ACCESO NO AUTORIZADO: User ID={user_id} ({username}) intentó enviar: '{preview}'",

        # Log Messages — Credentials (credentials.py)
        "log_fallback_read_error": "No se pudieron leer credenciales de respaldo encriptadas: {e}",
        "log_keyring_save_error": "Keyring no pudo guardar '{key}': {e}. Intentando fallback DPAPI...",
        "log_dpapi_save_error": "Error al guardar la credencial '{key}' en fallback DPAPI: {e}",
        "log_keyring_load_debug": "Excepción de carga de keyring para '{key}': {e}",
        "log_fallback_load_debug": "Excepción de carga de fallback para '{key}': {e}",

        # Log Messages — Outlook Monitor (outlook_monitor.py)
        "log_mail_config_error": "Error al cargar la configuración de notificación de correo: {e}",
        "log_mail_config_save_error": "Error al guardar la configuración de notificación de correo: {e}",
        "log_mail_already_running": "OutlookMailMonitor ya está en ejecución.",
        "log_mail_started": "OutlookMailMonitor iniciado. Corte de notificación: correos recibidos después de {cutoff} activarán alertas.",
        "log_mail_stopped": "OutlookMailMonitor detenido.",
        "log_outlook_com_ok": "Acceso COM de Outlook correcto. Monitoreando Bandeja de entrada para mensajes no leídos.",
        "log_cutoff_time": "Corte: correos recibidos antes de {cutoff} serán ignorados.",
        "log_polling_folder": "Sondaje {folder}: {count} mensaje(s) no leído(s).",
        "log_mail_ignored_old": "Correo ignorado (demasiado antiguo) en {folder}: '{subject}'",
        "log_mail_keyword_match": "Correo coincidente encontrado en {folder}: '{subject}'",
        "log_telegram_notify_sent": "Notificación de Telegram enviada correctamente.",
        "log_telegram_notify_failed": "Error al enviar notificación de Telegram.",
        "log_bot_manager_unavailable": "Administrador de bot no disponible, no se puede enviar notificación.",
        "log_outlook_processing_error": "Error al procesar correos de Outlook: {e}",
        "log_mail_thread_exit": "Hilo de OutlookMailMonitor terminando.",
        "log_outlook_com_error": "No se puede acceder a Outlook mediante COM: {e}",

        # Log Messages — GUI (gui.py)
        "log_token_saved": "Token de API de Telegram configurado y guardado en el almacenamiento de credenciales.",
        "log_master_saved": "Master User ID configurado y guardado.",
        "log_mail_keywords_updated": "Palabras clave de notificación de correo actualizadas.",
        "log_window_minimized": "Ventana minimizada a System Tray.",
        "log_window_restored": "Ventana restaurada desde System Tray.",

        # Log Messages — Tray (tray.py)
        "log_tray_started": "System Tray iniciada.",
        "log_tray_start_error": "No se pudo iniciar el System Tray: {e}",
        "log_tray_icon_error": "No se pudo cargar el archivo de icono {path}: {e}",
        "log_tray_stopped": "System Tray eliminada.",
        "log_tray_show_error": "Error en el manejador 'Mostrar' de la bandeja: {e}",
        "log_tray_exit_error": "Error en el manejador 'Salir' de la bandeja: {e}",

        # Log Messages — System Commands (commands/system.py)
        "log_error_shutdown_call": "Excepción durante la llamada a shutdown:",
        "log_error_restart_call": "Excepción durante la llamada a restart:",
        "log_error_shutdown_abort": "Excepción durante la llamada a shutdown /a:",
        "log_error_lockworkstation": "Excepción durante LockWorkStation:",

        # Log Messages — Panic (commands/processes.py)
        "log_panic_procedure": "PROCEDIMIENTO DE PÁNICO INICIADO: Terminando aplicaciones de usuario...",
        "log_panic_terminating": "Pánico terminando PID={pid} ({name})...",
        "log_access_denied_terminate": "AccessDenied al intentar terminar PID {pid}",
        "log_exception_terminating": "Excepción al terminar PID {proc}: {e}",
        "log_resolve_hierarchy_error": "No se pudo resolver la jerarquía de procesos: {e}",

        # Log Messages — Applications (commands/applications.py)
        "log_firefox_not_found": "Intento de lanzar Firefox: ejecutable no encontrado.",
        "log_firefox_start_error": "Error al lanzar Firefox ({exe}):",
        "log_outlook_not_found": "Intento de lanzar Outlook: ejecutable no encontrado.",
        "log_outlook_start_error": "Error al lanzar Outlook ({exe}):",
        "log_notepad_note_error": "Error al abrir Notepad para la nota:",

        # Log Messages — Command Result Messages (commands/*.py)
        "log_unhandled_error": "Error no controlado en la ejecución del comando: {cmd}:",
        "log_msg_shutdown_scheduled": "Apagado programado en {delay}s.",
        "log_msg_shutdown_error": "Error de apagado: {err}",
        "log_msg_shutdown_exception": "Excepción de apagado: {e}",
        "log_msg_restart_scheduled": "Reinicio programado en {delay}s.",
        "log_msg_restart_error": "Error de reinicio: {err}",
        "log_msg_restart_exception": "Excepción de reinicio: {e}",
        "log_msg_abort_done": "Apagado/Reinicio cancelado.",
        "log_msg_abort_none": "Intento de cancelar apagado: sin operación pendiente.",
        "log_msg_abort_exception": "Excepción de cancelación: {e}",
        "log_msg_lock_success": "Estación de trabajo bloqueada correctamente.",
        "log_msg_lock_failed": "LockWorkStation falló con código {code}.",
        "log_msg_lock_exception": "Excepción de LockWorkStation: {e}",
        "log_msg_ping": "Ping respondido. Uptime: {uptime}",
        "log_msg_status": "Comando de estado ejecutado correctamente.",
        "log_msg_help": "Ayuda de comandos enviada.",
        "log_msg_panic_done": "Pánico ejecutado: {terminated} procesos cerrados, {denied} protegidos.",
        "log_msg_firefox_not_found": "Firefox no encontrado.",
        "log_msg_firefox_launched": "Iniciado Firefox desde: {exe}",
        "log_msg_firefox_error": "Error al lanzar Firefox: {e}",
        "log_msg_outlook_not_found": "Outlook no encontrado.",
        "log_msg_outlook_launched": "Iniciado Outlook desde: {exe}",
        "log_msg_outlook_error": "Error al lanzar Outlook: {e}",
        "log_msg_note_opened": "Abierto Notepad con nota: '{preview}'",
        "log_msg_note_error": "Error al lanzar Notepad: {e}",
        "log_msg_note_empty": "Intento de abrir nota vacía.",
        "log_error_internal": "Error interno en {cmd}: {e}",
        "log_msg_unknown_windows_error": "Error de Windows desconocido.",

        # Log Messages — Icons (icons.py)
        "log_icon_generate_error": "Error al generar icono {name}: {e}",
        "log_icon_not_found": "Archivo de icono no encontrado: {path}",
        "log_icon_load_error": "Error al cargar icono '{name}' desde {path}: {e}",

        # Log Messages — Startup (startup.py)
        "log_startup_enabled": "Inicio con Windows habilitado: {cmd}",
        "log_startup_enable_error": "Error al habilitar inicio con Windows: {e}",
        "log_startup_disabled": "Inicio con Windows deshabilitado.",
        "log_startup_disable_error": "Error al deshabilitar inicio con Windows: {e}",

        # Telegram Bot Messages (user-facing replies)
        "telegram_empty_message": "Mensaje vacío o no textual.",
        "telegram_mail_notification": "📧 *Nuevo correo* ({folder})\n*Remitente*: {sender}\n*Asunto*: {subject}\n*Hora*: {time}",
        "telegram_no_command": "No se identificó ningún comando.",
        "telegram_note_empty_arg": "Ingrese texto después de 'note:'. Ejemplo: note: recordar la reunión",
        "telegram_too_many_args": "Demasiados argumentos. Los comandos no aceptan parámetros arbitrarios.",
        "telegram_no_extra_args": "El comando '{cmd}' no acepta argumentos adicionales.",
        "telegram_invalid_cmd": "Comando no válido.",
        "telegram_reply_invalid_cmd": "⚠️ {err}\nEnvíe `/help` para ver comandos autorizados.",
        "telegram_unknown_cmd": "❓ Comando desconocido: `/{cmd}`\nEnvíe `/help` para ver comandos autorizados.",
        "telegram_master_unconfigured": "❌ Master User ID no está configurado en esta computadora.",
        "telegram_master_invalid": "❌ La configuración local de Master User ID es inválida.",
        "telegram_unauthorized": "⛔ Acceso denegado: Usuario no autorizado.",
        "telegram_panic_prompt": "⚠️ *ATENCIÓN*: El comando `/panic` cerrará aplicaciones de usuario abiertas y puede causar pérdida de datos no guardados.\n\nPara confirmar, envíe dentro de 15 segundos:\n`/panic confirm`",
        "telegram_panic_no_pending": "No hay solicitud de pánico pendiente. Envíe primero `/panic`.",
        "telegram_panic_expired": "Solicitud de pánico expirada ({elapsed:.1f}s > {timeout}s). Envíe `/panic` nuevamente.",
        "telegram_panic_invalid_arg": "Argumento no válido. Para confirmar envíe exactamente: `/panic confirm`.",
        "telegram_shutdown_sched": "🛑 Apagado programado en {delay} segundos.\nUse `/annulla` para cancelar inmediatamente.",
        "telegram_shutdown_error": "❌ No se pudo programar el apagado: {err}",
        "telegram_shutdown_internal_error": "❌ Error interno durante el apagado: {e}",
        "telegram_restart_sched": "🔄 Reinicio programado en {delay} segundos.\nUse `/annulla` para cancelar inmediatamente.",
        "telegram_restart_error": "❌ No se pudo programar el reinicio: {err}",
        "telegram_restart_internal_error": "❌ Error interno durante el reinicio: {e}",
        "telegram_abort_done": "✅ {action} cancelado correctamente.",
        "telegram_abort_none": "ℹ️ No hay ninguna operación de apagado o reinicio para cancelar.",
        "telegram_abort_internal_error": "❌ Error interno durante la cancelación: {e}",
        "telegram_lock_success": "🔒 Estación de trabajo Windows bloqueada.",
        "telegram_lock_error": "❌ Error de bloqueo de estación de trabajo (código: {code}).",
        "telegram_lock_internal_error": "❌ Error bloqueando estación de trabajo: {e}",
        "telegram_ping": "🏓 *PONG*\n━━━━━━━━━━━━━━━━━━━━\n💻 PC en línea y listo\n⏱️ Hora local: `{time}`\n⏳ Tiempo de actividad: `{uptime}`",
        "telegram_status_header": "📊 *ESTADO DE BOT Y SISTEMA*",
        "telegram_status_separator": "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "telegram_status_bot": "🤖 Bot de Telegram: `ONLINE`",
        "telegram_status_master": "👑 Master User: `{status}`",
        "telegram_status_startup": "🚀 Inicio de Windows: `{status}`",
        "telegram_status_tray": "🗂️ Bandeja del Sistema: `ACTIVA`",
        "telegram_status_version": "📦 Versión de la app: `v{version}`",
        "telegram_status_cmd_count": "📋 Comandos registrados: `{count}`",
        "telegram_status_subsep": "───────────────────────────",
        "telegram_status_uptime": "⏳ Tiempo de actividad PC: `{uptime}`",
        "telegram_status_metrics": "⚡ CPU: `{cpu}` | RAM: `{ram}`",
        "telegram_status_pending_active": "⚠️ En progreso ({action})",
        "telegram_status_pending_none": "Ninguno",
        "telegram_panic_done": "🚨 *PROCEDIMIENTO DE PÁNICO COMPLETADO*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📉 Procesos de usuario cerrados: `{count}`\n🛡️ Procesos del sistema protegidos",
        "telegram_panic_denied": "⚠️ Procesos protegidos por permisos elevados: `{count}`\n",
        "telegram_firefox_not_found": "❌ Firefox no se encuentra en este sistema.",
        "telegram_firefox_launched": "🌐 Mozilla Firefox lanzado correctamente.",
        "telegram_firefox_error": "❌ Error al lanzar Firefox: {e}",
        "telegram_outlook_not_found": "❌ Outlook no se encuentra en este sistema.",
        "telegram_outlook_launched": "📧 Microsoft Outlook lanzado correctamente.",
        "telegram_outlook_error": "❌ Error al lanzar Outlook: {e}",
        "telegram_note_empty_msg": "❌ El texto de la nota no puede estar vacío.",
        "telegram_note_opened": "📝 *¡Notepad abierto en PC!*\n📄 Contenido: _{preview}_\n📁 Guardado como: `{filename}`",
        "telegram_notepad_error": "❌ Error al abrir Notepad: {e}",
        "telegram_help_header": "🖥️ *BotMyPC — Control Remoto PC*",
        "telegram_help_list_header": "Aquí está la lista de comandos autorizados:\n",
        "telegram_help_separator": "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "telegram_help_destructive_header": "\n*Comandos con impacto en el sistema:*",
        "telegram_help_footer": "🛡️ _Los comandos no registrados o con argumentos arbitrarios son rechazados._",
        "telegram_error_internal": "❌ Se produjo un error interno al ejecutar el comando.",
        "telegram_action_shutdown": "Apagado",
        "telegram_action_restart": "Reinicio",
        "telegram_action_unknown": "Operación",
        "cmd_shutdown_desc": "Programa apagado del PC en 10 segundos (.Cancelable)",
        "cmd_restart_desc": "Programa reinicio del PC en 10 segundos (cancelable)",
        "cmd_annulla_desc": "Cancela un apagado o reinicio programados",
        "cmd_out_desc": "Bloquea inmediatamente la estación de trabajo de Windows (LockWorkStation)",
        "cmd_ping_desc": "Comprueba si el PC está en línea y devuelve el tiempo de actividad",
        "cmd_status_desc": "Muestra el estado detallado de la aplicación, el bot y los recursos del PC",
        "cmd_help_desc": "Muestra la lista de comandos autorizados y sus descripciones",
        "cmd_firefox_desc": "Inicia Mozilla Firefox (con detección automática de ruta)",
        "cmd_outlook_desc": "Inicia Microsoft Outlook (con detección Click-to-Run/MSI)",
        "cmd_note_desc": "Abre Notepad y pega el texto enviado",
        "cmd_panic_desc": "Cierra aplicaciones de usuario (requiere confirmación: /panic conferma)",
    },
    "it": {
        # Header & Status
        "app_title": "BotMyPC — Telecomando Remoto Telegram",
        "status_prefix": "STATO",
        "state_stopped": "STOPPED",
        "state_starting": "AVVIO",
        "state_running": "RUNNING",
        "state_stopping": "ARRESTO",
        "state_error": "ERRORE",
        "btn_start_bot": "Avvia Bot",
        "btn_stop_bot": "STOP BOT",
        "btn_starting_bot": "AVVIO...",
        "btn_stopping_bot": "ARRESTO...",

        # Control Bar
        "btn_token": "API Token",
        "btn_master": "Master ID",
        "btn_background": "Background",
        "btn_mail_notify": "Notifica mail",
        "btn_mail_active": "Mail ATTIVA",
        "btn_language": "Lingua",
        "btn_credits": "Crediti",
        "chk_startup": "Avvia con Windows",

        # Terminal
        "terminal_header": "  > TERMINAL LOG [READ-ONLY]",
        "btn_clear": "Pulisci",

        # Footer
        "token_ok": "TOKEN: OK",
        "token_missing": "TOKEN: MANCANTE",
        "master_ok": "MASTER: OK",
        "master_missing": "MASTER: MANCANTE",
        "footer_version": f"v{APP_VERSION} — Windows 11 Ready",

        # Common Dialog Actions
        "btn_save": "Salva",
        "btn_cancel": "Annulla",
        "btn_close": "Chiudi",

        # Language Dialog
        "lang_dialog_title": "Seleziona Lingua",
        "lang_dialog_header": "🌐 Lingua dell'Applicazione",
        "lang_dialog_info": "Scegli la lingua preferita per l'interfaccia.\nLe modifiche verranno applicate subito e salvate.",
        "lang_en": "Inglese (Default)",
        "lang_de": "Tedesco (Deutsch)",
        "lang_es": "Spagnolo (Español)",
        "lang_it": "Italiano (Italian)",
        "lang_fr": "Francese (Français)",

        # Token Dialog
        "token_dialog_title": "Configura Token Bot Telegram",
        "token_dialog_header": "🔑 Configurazione Token Telegram",
        "token_dialog_info": "Inserisci il token del bot ottenuto da @BotFather.\nIl token verrà cifrato e salvato in modo sicuro.",
        "token_current": "Token attuale: {token}",
        "token_placeholder": "es. 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567",
        "token_error_empty": "Inserisci un token valido.",
        "token_error_format": "Formato token non valido (controlla caratteri).",
        "token_error_save": "Errore nel salvataggio del credential storage.",
        "token_btn_save": "Salva Token",

        # Master ID Dialog
        "master_dialog_title": "Configura Account Master",
        "master_dialog_header": "👑 Configurazione Master User ID",
        "master_dialog_info": (
            "Inserisci il tuo Telegram User ID numerico.\n"
            "Solo questo utente potrà impartire comandi al PC.\n"
            "(Puoi scoprire il tuo ID inviando un messaggio a @userinfobot su Telegram)"
        ),
        "master_current": "Master ID attuale: {id}",
        "master_not_configured": "[NON CONFIGURATO]",
        "master_placeholder": "es. 987654321",
        "master_error_numeric": "L'ID deve contenere solo numeri.",
        "master_error_save": "Errore durante il salvataggio delle credenziali.",
        "master_btn_save": "Salva Master ID",

        # Credits Dialog
        "credits_dialog_title": "Crediti & Informazioni",
        "credits_author": "Sviluppato da Stefano D'Angelo AKA Lemonice",
        "credits_subtitle": "Telecomando Remoto Windows 11 tramite Bot Telegram",
        "credits_tech_title": "Librerie e Tecnologie Utilizzate:",
        "credits_tech_desc": (
            "Librerie e Tecnologie Utilizzate:\n\n"
            "• Python 3.11+ & Asyncio Threading\n"
            "• CustomTkinter (Interfaccia Grafica Cyberpunk)\n"
            "• python-telegram-bot (API Telegram v20+)\n"
            "• Windows Credential Manager (keyring) & DPAPI\n"
            "• cryptography (Fernet AES-CBC / HMAC)\n"
            "• psutil (Controllo Processi & Uptime)\n"
            "• pystray & Pillow (Integrazione System Tray)\n"
            "• Winreg & ctypes (Integrazione nativa Windows 11)"
        ),
        "credits_license": "📜 Licenza: Licenza MIT (Software libero con attribuzione. Fornito 'COSÌ COM'È' senza alcuna garanzia né responsabilità).",

        # Mail Dialog
        "mail_dialog_title": "📧 Notifica Nuove Mail",
        "mail_dialog_header": "📧 Notifica Mail via Telegram",
        "mail_dialog_info": (
            "Monitora la posta in arrivo di Outlook e invia\n"
            "una notifica Telegram quando l'oggetto contiene\n"
            "una delle parole chiave configurate."
        ),
        "mail_keywords_lbl": "Parole chiave (separate da virgola):",
        "mail_keywords_placeholder": "es. importante, urgenza, fattura",
        "mail_btn_start": "Avvia Monitoraggio",
        "mail_btn_stop": "Ferma Monitoraggio",
        "mail_btn_save_kw": "Salva Keywords",
        "mail_kw_saved": "✅ Keywords salvate.",
        "mail_err_master": "❌ Configura prima il Master User ID.",
        "mail_err_bot": "❌ Avvia prima il Bot Telegram (il monitor ha bisogno del bot per inviare notifiche).",

        # Tray
        "tray_show": "Mostra BotMyPC",
        "tray_exit": "Esci",

        # Log Messages — Application Lifecycle (main.py)
        "log_started": "{app_name} v{version} avviato su Windows 11.",
        "log_credentials_status": "Credenziali: Bot Token {token}, Master ID {master}.",
        "log_token_present": "PRESENTE",
        "log_token_missing": "ASSENTE",
        "log_shutdown_start": "Avvio sequenza di chiusura ordinata...",
        "log_error_stopping_bot": "Errore durante l'arresto del bot: {e}",
        "log_error_stopping_mail": "Errore durante l'arresto del monitor mail: {e}",
        "log_error_stopping_tray": "Errore durante la chiusura della tray: {e}",
        "log_shutdown_done": "Chiusura applicazione completata.",
        "log_unexpected_error": "Errore imprevisto nel mainloop della GUI: {e}",

        # Log Messages — i18n (i18n.py)
        "log_language_set": "Lingua aggiornata a '{lang}' e salvata nelle impostazioni.",

        # Log Messages — Telegram Bot (telegram_bot.py)
        "log_bot_state": "Stato bot: {state}",
        "log_state_change_error": "Errore durante l'invocazione di on_state_change: {e}",
        "log_bot_already_running": "Tentativo di avviare il bot quando è già in esecuzione.",
        "log_bot_token_missing": "Impossibile avviare il bot: Token non configurato.",
        "log_bot_token_missing_gui": "[ERRORE] Bot Token non configurato. Configuralo prima di avviare.",
        "log_bot_stopping": "Arresto del bot in corso...",
        "log_bot_stopped": "Bot arrestato con successo.",
        "log_send_not_running": "send_message: bot non avviato, impossibile inviare.",
        "log_send_master_unconfigured": "send_message: Master User ID non configurato.",
        "log_send_master_invalid": "send_message: Master User ID non valido.",
        "log_markdown_failed": "send_message: invio con Markdown fallito, riprovo plain text: {e}",
        "log_send_fallback_failed": "send_message: invio fallback fallito: {e2}",
        "log_send_error": "send_message: errore durante l'invio: {e}",
        "log_fatal_bot_error": "Errore fatale nel thread del bot Telegram: {e}",
        "log_bot_started": "Bot Telegram avviato e in ascolto.",
        "log_telegram_startup_error": "Errore di avvio/connessione Telegram: {e}",
        "log_closing_telegram": "Chiusura updater e applicazione Telegram...",
        "log_invalid_command": "Comando non valido rifiutato: '{cmd}' ({err})",
        "log_dup_command": "Comando duplicato ignorato per ID {sender_id}: '{cmd}'",
        "log_cmd_received": "Comando ricevuto da Master: /{cmd} {arg}",
        "log_unknown_command": "Comando sconosciuto: '{cmd}'",
        "log_command_result": "Esito comando {cmd}: {msg}",

        # Log Messages — Security (security.py)
        "log_sec_master_unconfigured": "Aggiornamento Telegram respinto: Master User ID non configurato su questo PC.",
        "log_sec_master_invalid_int": "La Master User ID configurata non è un numero intero valido.",
        "log_sec_unauthorized_access": "TENTATIVO DI ACCESSO NON AUTORIZZATO: User ID={user_id} ({username}) ha tentato di inviare: '{preview}'",

        # Log Messages — Credentials (credentials.py)
        "log_fallback_read_error": "Impossibile leggere credenziali di fallback crittografate: {e}",
        "log_keyring_save_error": "Keyring non ha salvato '{key}': {e}. Provo fallback DPAPI...",
        "log_dpapi_save_error": "Fallito il salvataggio della credenziale '{key}' nel fallback DPAPI: {e}",
        "log_keyring_load_debug": "Eccezione keyring durante il caricamento per '{key}': {e}",
        "log_fallback_load_debug": "Eccezione fallback caricamento per '{key}': {e}",

        # Log Messages — Outlook Monitor (outlook_monitor.py)
        "log_mail_config_error": "Errore durante il caricamento della configurazione mail notify: {e}",
        "log_mail_config_save_error": "Errore durante il salvataggio della configurazione mail notify: {e}",
        "log_mail_already_running": "OutlookMailMonitor già in esecuzione.",
        "log_mail_started": "OutlookMailMonitor avviato. Cutoff notifiche: le mail ricevute dopo {cutoff} genereranno avvisi.",
        "log_mail_stopped": "OutlookMailMonitor arrestato.",
        "log_outlook_com_ok": "Accesso Outlook COM OK. Monitoraggio Inbox per messaggi non letti.",
        "log_cutoff_time": "Cutoff: le mail ricevute prima di {cutoff} verranno ignorate.",
        "log_polling_folder": "Polling {folder}: {count} messaggio(i) non letto(i).",
        "log_mail_ignored_old": "Mail ignorata (troppo vecchia) in {folder}: '{subject}'",
        "log_mail_keyword_match": "Mail corrispondente a keyword trovata in {folder}: '{subject}'",
        "log_telegram_notify_sent": "Notifica Telegram inviata con successo.",
        "log_telegram_notify_failed": "Invio notifica Telegram fallito.",
        "log_bot_manager_unavailable": "Bot manager non disponibile, impossibile inviare notifica.",
        "log_outlook_processing_error": "Errore durante l'elaborazione delle mail di Outlook: {e}",
        "log_mail_thread_exit": "Thread OutlookMailMonitor in chiusura.",
        "log_outlook_com_error": "Impossibile accedere a Outlook tramite COM: {e}",

        # Log Messages — GUI (gui.py)
        "log_token_saved": "Token API Telegram configurato e salvato nel credential storage.",
        "log_master_saved": "Master User ID configurato e salvato.",
        "log_mail_keywords_updated": "Keywords di notifica mail aggiornate.",
        "log_window_minimized": "Finestra minimizzata nella System Tray.",
        "log_window_restored": "Finestra ripristinata dalla System Tray.",

        # Log Messages — Tray (tray.py)
        "log_tray_started": "System Tray avviata.",
        "log_tray_start_error": "Impossibile avviare la System Tray: {e}",
        "log_tray_icon_error": "Impossibile caricare il file icona {path}: {e}",
        "log_tray_stopped": "System Tray rimossa.",
        "log_tray_show_error": "Errore handler 'Mostra' da tray: {e}",
        "log_tray_exit_error": "Errore handler 'Esci' da tray: {e}",

        # Log Messages — System Commands (commands/system.py)
        "log_error_shutdown_call": "Eccezione durante la chiamata a shutdown:",
        "log_error_restart_call": "Eccezione durante la chiamata a restart:",
        "log_error_shutdown_abort": "Eccezione durante la chiamata a shutdown /a:",
        "log_error_lockworkstation": "Eccezione durante LockWorkStation:",

        # Log Messages — Panic (commands/processes.py)
        "log_panic_procedure": "PROCEDURA PANICO AVVIO: Terminazione delle applicazioni utente...",
        "log_panic_terminating": "Panic terminando PID={pid} ({name})...",
        "log_access_denied_terminate": "AccessDenied durante il tentativo di terminare PID {pid}",
        "log_exception_terminating": "Eccezione durante la terminazione di PID {proc}: {e}",
        "log_resolve_hierarchy_error": "Impossibile risolvere la gerarchia dei processi: {e}",

        # Log Messages — Applications (commands/applications.py)
        "log_firefox_not_found": "Tentativo di avvio Firefox: eseguibile non trovato.",
        "log_firefox_start_error": "Errore durante l'avvio di Firefox ({exe}):",
        "log_outlook_not_found": "Tentativo di avvio Outlook: eseguibile non trovato.",
        "log_outlook_start_error": "Errore durante l'avvio di Outlook ({exe}):",
        "log_notepad_note_error": "Errore durante l'apertura di Notepad per la nota:",

        # Log Messages — Command Result Messages (commands/*.py)
        "log_unhandled_error": "Errore non gestito nell'esecuzione di {cmd}:",
        "log_msg_shutdown_scheduled": "Shutdown programmato tra {delay}s.",
        "log_msg_shutdown_error": "Errore shutdown: {err}",
        "log_msg_shutdown_exception": "Eccezione shutdown: {e}",
        "log_msg_restart_scheduled": "Riavvio programmato tra {delay}s.",
        "log_msg_restart_error": "Errore riavvio: {err}",
        "log_msg_restart_exception": "Eccezione riavvio: {e}",
        "log_msg_abort_done": "Shutdown/Riavvio annullato.",
        "log_msg_abort_none": "Tentativo di annullamento shutdown: nessuna operazione in corso.",
        "log_msg_abort_exception": "Eccezione annulla: {e}",
        "log_msg_lock_success": "Workstation bloccata con successo.",
        "log_msg_lock_failed": "LockWorkStation fallito con codice {code}.",
        "log_msg_lock_exception": "Eccezione LockWorkStation: {e}",
        "log_msg_ping": "Ping risposto. Uptime: {uptime}",
        "log_msg_status": "Comando status eseguito con successo.",
        "log_msg_help": "Guida comandi inviata.",
        "log_msg_panic_done": "Panic eseguito: {terminated} processi chiusi, {denied} protetti.",
        "log_msg_firefox_not_found": "Firefox non trovato.",
        "log_msg_firefox_launched": "Avviato Firefox da: {exe}",
        "log_msg_firefox_error": "Errore lancio Firefox: {e}",
        "log_msg_outlook_not_found": "Outlook non trovato.",
        "log_msg_outlook_launched": "Avviato Outlook da: {exe}",
        "log_msg_outlook_error": "Errore lancio Outlook: {e}",
        "log_msg_note_opened": "Aperto Notepad con nota: '{preview}'",
        "log_msg_note_error": "Errore lancio Notepad: {e}",
        "log_msg_note_empty": "Tentativo di aprire nota vuota.",
        "log_error_internal": "Errore interno in {cmd}: {e}",
        "log_msg_unknown_windows_error": "Errore di Windows sconosciuto.",

        # Log Messages — Icons (icons.py)
        "log_icon_generate_error": "Errore durante la generazione dell'icona {name}: {e}",
        "log_icon_not_found": "File icona non trovato: {path}",
        "log_icon_load_error": "Errore durante il caricamento dell'icona '{name}' da {path}: {e}",

        # Log Messages — Startup (startup.py)
        "log_startup_enabled": "Avvio automatico con Windows abilitato: {cmd}",
        "log_startup_enable_error": "Errore durante l'abilitazione dell'avvio con Windows: {e}",
        "log_startup_disabled": "Avvio automatico con Windows disabilitato.",
        "log_startup_disable_error": "Errore durante la disabilitazione dell'avvio con Windows: {e}",

        # Telegram Bot Messages (user-facing replies)
        "telegram_empty_message": "Messaggio vuoto o non testuale.",
        "telegram_mail_notification": "📧 *Nuova mail* ({folder})\n*Mittente*: {sender}\n*Oggetto*: {subject}\n*Orario*: {time}",
        "telegram_no_command": "Nessun comando identificato.",
        "telegram_note_empty_arg": "Inserisci il testo della nota dopo 'note:'. Esempio: note: ricordami la riunione",
        "telegram_too_many_args": "Troppi argomenti. I comandi non accettano parametri arbitrari.",
        "telegram_no_extra_args": "Il comando '{cmd}' non accetta argomenti aggiuntivi.",
        "telegram_invalid_cmd": "Comando non valido.",
        "telegram_reply_invalid_cmd": "⚠️ {err}\nInvia `/help` per i comandi autorizzati.",
        "telegram_unknown_cmd": "❓ Comando sconosciuto: `/{cmd}`\nInvia `/help` per visualizzare i comandi autorizzati.",
        "telegram_master_unconfigured": "❌ Master User ID non configurato su questo computer.",
        "telegram_master_invalid": "❌ Configurazione Master User ID locale non valida.",
        "telegram_unauthorized": "⛔ Accesso negato: Utente non autorizzato.",
        "telegram_panic_prompt": "⚠️ *ATTENZIONE*: Il comando `/panic` chiuderà le applicazioni utente aperte e potrebbe causare la perdita di dati non salvati.\n\nPer confermare, invia entro 15 secondi:\n`/panic conferma`",
        "telegram_panic_no_pending": "Nessuna richiesta di panic in sospeso. Invia prima `/panic`.",
        "telegram_panic_expired": "Richiesta di panic scaduta ({elapsed:.1f}s > {timeout}s). Invia nuovamente `/panic`.",
        "telegram_panic_invalid_arg": "Argomento non valido. Per confermare invia esattamente: `/panic conferma`.",
        "telegram_shutdown_sched": "🛑 Spegnimento programmato tra {delay} secondi.\nUsa `/annulla` per annullare immediatamente.",
        "telegram_shutdown_error": "❌ Impossibile programmare lo spegnimento: {err}",
        "telegram_shutdown_internal_error": "❌ Errore interno durante lo spegnimento: {e}",
        "telegram_restart_sched": "🔄 Riavvio programmato tra {delay} secondi.\nUsa `/annulla` per annullare immediatamente.",
        "telegram_restart_error": "❌ Impossibile programmare il riavvio: {err}",
        "telegram_restart_internal_error": "❌ Errore interno durante il riavvio: {e}",
        "telegram_abort_done": "✅ {action} annullato con successo.",
        "telegram_abort_none": "ℹ️ Nessuna operazione di spegnimento o riavvio da annullare.",
        "telegram_abort_internal_error": "❌ Errore interno durante l'annullamento: {e}",
        "telegram_lock_success": "🔒 Postazione Windows bloccata.",
        "telegram_lock_error": "❌ Errore blocco postazione (codice: {code}).",
        "telegram_lock_internal_error": "❌ Errore durante il blocco postazione: {e}",
        "telegram_ping": "🏓 *PONG*\n━━━━━━━━━━━━━━━━━━━━\n💻 PC online e pronto\n⏱️ Ora locale: `{time}`\n⏳ Uptime sistema: `{uptime}`",
        "telegram_status_header": "📊 *STATO BOT & SISTEMA*",
        "telegram_status_separator": "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "telegram_status_bot": "🤖 Bot Telegram: `ONLINE`",
        "telegram_status_master": "👑 Master User: `{status}`",
        "telegram_status_startup": "🚀 Avvio con Windows: `{status}`",
        "telegram_status_tray": "🗂️ System Tray: `ATTIVA`",
        "telegram_status_version": "📦 Versione App: `v{version}`",
        "telegram_status_cmd_count": "📋 Comandi registrati: `{count}`",
        "telegram_status_subsep": "───────────────────────────",
        "telegram_status_uptime": "⏳ Uptime PC: `{uptime}`",
        "telegram_status_metrics": "⚡ CPU: `{cpu}` | RAM: `{ram}`",
        "telegram_status_pending_active": "⚠️ In corso ({action})",
        "telegram_status_pending_none": "Nessuna",
        "telegram_panic_done": "🚨 *PROCEDURA PANICO COMPLETATA*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📉 Processi utente chiusi: `{count}`\n🛡️ Processi di sistema protetti",
        "telegram_panic_denied": "⚠️ Processi protetti da permessi elevati: `{count}`\n",
        "telegram_firefox_not_found": "❌ Firefox non trovato su questo sistema.",
        "telegram_firefox_launched": "🌐 Mozilla Firefox avviato con successo.",
        "telegram_firefox_error": "❌ Errore durante l'avvio di Firefox: {e}",
        "telegram_outlook_not_found": "❌ Outlook non trovato su questo sistema.",
        "telegram_outlook_launched": "📧 Microsoft Outlook avviato con successo.",
        "telegram_outlook_error": "❌ Errore durante l'avvio di Outlook: {e}",
        "telegram_note_empty_msg": "❌ Il testo della nota non può essere vuoto.",
        "telegram_note_opened": "📝 *Notepad aperto sul PC!*\n📄 Contenuto: _{preview}_\n📁 Salvato come: `{filename}`",
        "telegram_notepad_error": "❌ Errore nell'apertura di Notepad: {e}",
        "telegram_help_header": "🖥️ *BotMyPC — Telecomando Remoto PC*",
        "telegram_help_list_header": "Ecco l'elenco dei comandi autorizzati:\n",
        "telegram_help_separator": "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "telegram_help_destructive_header": "\n*Comandi con impatto sul sistema:*",
        "telegram_help_footer": "🛡️ _I comandi non registrati o con argomenti arbitrari vengono rifiutati._",
        "telegram_error_internal": "❌ Si è verificato un errore interno durante l'esecuzione del comando.",
        "telegram_action_shutdown": "Spegnimento",
        "telegram_action_restart": "Riavvio",
        "telegram_action_unknown": "Operazione",
        "cmd_shutdown_desc": "Programma lo spegnimento del PC tra 10 secondi (interrompibile)",
        "cmd_restart_desc": "Programma il riavvio del PC tra 10 secondi (interrompibile)",
        "cmd_annulla_desc": "Annulla un'operazione di spegnimento o riavvio programmata",
        "cmd_out_desc": "Blocca immediatamente la postazione Windows (LockWorkStation)",
        "cmd_ping_desc": "Verifica che il PC sia online e restituisce l'uptime del sistema",
        "cmd_status_desc": "Mostra lo stato dettagliato dell'applicazione, del bot e delle risorse PC",
        "cmd_help_desc": "Mostra l'elenco dei comandi autorizzati e la loro descrizione",
        "cmd_firefox_desc": "Avvia il browser Mozilla Firefox (con rilevamento automatico del percorso)",
        "cmd_outlook_desc": "Avvia Microsoft Outlook (con rilevamento Click-to-Run / MSI)",
        "cmd_note_desc": "Apre Blocco Note (Notepad) e incolla il testo inviato",
        "cmd_panic_desc": "Chiude le applicazioni utente (richiede conferma: /panic conferma)",
    },
    "fr": {
        # Header & Status
        "app_title": "BotMyPC — Contrôle à Distance Telegram",
        "status_prefix": "STATUT",
        "state_stopped": "ARRÊTÉ",
        "state_starting": "DÉMARRAGE",
        "state_running": "EN COURS",
        "state_stopping": "ARRÊT",
        "state_error": "ERREUR",
        "btn_start_bot": "Démarrer Bot",
        "btn_stop_bot": "ARRÊTER BOT",
        "btn_starting_bot": "DÉMARRAGE...",
        "btn_stopping_bot": "ARRÊT...",

        # Control Bar
        "btn_token": "Jeton API",
        "btn_master": "ID Maître",
        "btn_background": "Arrière-plan",
        "btn_mail_notify": "Alerte e-mail",
        "btn_mail_active": "E-mail ACTIF",
        "btn_language": "Langue",
        "btn_credits": "Crédits",
        "chk_startup": "Lancer au démarrage",

        # Terminal
        "terminal_header": "  > JOURNAL DU TERMINAL [LECTURE SEULE]",
        "btn_clear": "Effacer",

        # Footer
        "token_ok": "JETON: OK",
        "token_missing": "JETON: MANQUANT",
        "master_ok": "MAÎTRE: OK",
        "master_missing": "MAÎTRE: MANQUANT",
        "footer_version": f"v{APP_VERSION} — Prêt pour Windows 11",

        # Common Dialog Actions
        "btn_save": "Enregistrer",
        "btn_cancel": "Annuler",
        "btn_close": "Fermer",

        # Language Dialog
        "lang_dialog_title": "Sélectionner la Langue",
        "lang_dialog_header": "🌐 Langue de l'Application",
        "lang_dialog_info": "Choisissez votre langue d'affichage préférée.\nLes modifications sont appliquées immédiatement et enregistrées.",
        "lang_en": "Anglais (Default)",
        "lang_de": "Allemand (Deutsch)",
        "lang_es": "Espagnol (Español)",
        "lang_it": "Italien (Italiano)",
        "lang_fr": "Français (French)",

        # Token Dialog
        "token_dialog_title": "Configurer le Jeton Bot Telegram",
        "token_dialog_header": "🔑 Configuration du Jeton Telegram",
        "token_dialog_info": "Entrez le jeton de bot obtenu auprès de @BotFather.\nLe jeton sera chiffré et stocké en toute sécurité.",
        "token_current": "Jeton actuel: {token}",
        "token_placeholder": "ex. 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567",
        "token_error_empty": "Veuillez entrer un jeton valide.",
        "token_error_format": "Format de jeton invalide (vérifiez les caractères).",
        "token_error_save": "Erreur lors de l'enregistrement dans le coffre.",
        "token_btn_save": "Enregistrer le Jeton",

        # Master ID Dialog
        "master_dialog_title": "Configurer le Compte Maître",
        "master_dialog_header": "👑 Configuration de l'ID Utilisateur Maître",
        "master_dialog_info": (
            "Entrez votre ID utilisateur numérique Telegram.\n"
            "Seul cet utilisateur sera autorisé à envoyer des commandes au PC.\n"
            "(Trouvez votre ID en envoyant un message à @userinfobot sur Telegram)"
        ),
        "master_current": "ID Maître actuel: {id}",
        "master_not_configured": "[NON CONFIGURÉ]",
        "master_placeholder": "ex. 987654321",
        "master_error_numeric": "L'identifiant ne doit contenir que des chiffres.",
        "master_error_save": "Erreur lors de l'enregistrement des identifiants.",
        "master_btn_save": "Enregistrer l'ID Maître",

        # Credits Dialog
        "credits_dialog_title": "Crédits & Informations",
        "credits_author": "Développé par Stefano D'Angelo AKA Lemonice",
        "credits_subtitle": "Télécommande à distance Windows 11 via Bot Telegram",
        "credits_tech_title": "Bibliothèques & Technologies Utilisées:",
        "credits_tech_desc": (
            "Bibliothèques & Technologies Utilisées:\n\n"
            "• Python 3.11+ & Asyncio Threading\n"
            "• CustomTkinter (Interface Graphique Cyberpunk)\n"
            "• python-telegram-bot (API Telegram v20+)\n"
            "• Gestionnaire d'identifiants Windows & DPAPI\n"
            "• cryptography (Fernet AES-CBC / HMAC)\n"
            "• psutil (Gestion des Processus & Uptime)\n"
            "• pystray & Pillow (Intégration Barre des Tâches)\n"
            "• Winreg & ctypes (Intégration native Windows 11)"
        ),
        "credits_license": "📜 Licence: Licence MIT (Logiciel libre avec attribution. Fourni 'TEL QUEL' sans aucune garantie ni responsabilité).",

        # Mail Dialog
        "mail_dialog_title": "📧 Notifications de Nouveaux E-mails",
        "mail_dialog_header": "📧 Alertes E-mail via Telegram",
        "mail_dialog_info": (
            "Surveille la boîte de réception Outlook et envoie\n"
            "une notification Telegram lorsque l'objet contient\n"
            "l'un des mots-clés configurés."
        ),
        "mail_keywords_lbl": "Mots-clés (séparés par des virgules):",
        "mail_keywords_placeholder": "ex. urgent, facture, important",
        "mail_btn_start": "Démarrer Surveillance",
        "mail_btn_stop": "Arrêter Surveillance",
        "mail_btn_save_kw": "Enregistrer mots-clés",
        "mail_kw_saved": "✅ Mots-clés enregistrés.",
        "mail_err_master": "❌ Veuillez d'abord configurer l'ID Maître.",
        "mail_err_bot": "❌ Veuillez d'abord démarrer le Bot Telegram.",

        # Tray
        "tray_show": "Afficher BotMyPC",
        "tray_exit": "Quitter",

        # Log Messages — Application Lifecycle (main.py)
        "log_started": "{app_name} v{version} démarré sur Windows 11.",
        "log_credentials_status": "Identifiants: Jeton Bot {token}, Master ID {master}.",
        "log_token_present": "PRÉSENT",
        "log_token_missing": "MANQUANT",
        "log_shutdown_start": "Démarrage de la séquence d'arrêt ordonnée...",
        "log_error_stopping_bot": "Erreur lors de l'arrêt du bot: {e}",
        "log_error_stopping_mail": "Erreur lors de l'arrêt du moniteur de courriel: {e}",
        "log_error_stopping_tray": "Erreur lors de la fermeture du systray: {e}",
        "log_shutdown_done": "Fermeture de l'application terminée.",
        "log_unexpected_error": "Erreur inattendue dans la boucle principale de la GUI: {e}",

        # Log Messages — i18n (i18n.py)
        "log_language_set": "Langue mise à jour vers '{lang}' et enregistrée dans les paramètres.",

        # Log Messages — Telegram Bot (telegram_bot.py)
        "log_bot_state": "État du bot: {state}",
        "log_state_change_error": "Erreur lors de l'appel de on_state_change: {e}",
        "log_bot_already_running": "Tentative de démarrage du bot alors qu'il est déjà en cours.",
        "log_bot_token_missing": "Impossible de démarrer le bot: Jeton non configuré.",
        "log_bot_token_missing_gui": "[ERREUR] Jeton du Bot non configuré. Configurez-le avant de démarrer.",
        "log_bot_stopping": "Arrêt du bot en cours...",
        "log_bot_stopped": "Bot arrêté avec succès.",
        "log_send_not_running": "send_message: bot non démarré, impossible d'envoyer.",
        "log_send_master_unconfigured": "send_message: Master User ID non configuré.",
        "log_send_master_invalid": "send_message: Master User ID non valide.",
        "log_markdown_failed": "send_message: envoi en Markdown échoué, réessayer en texte brut: {e}",
        "log_send_fallback_failed": "send_message: envoi de secours échoué: {e2}",
        "log_send_error": "send_message: erreur lors de l'envoi: {e}",
        "log_fatal_bot_error": "Erreur fatale dans le thread du bot Telegram: {e}",
        "log_bot_started": "Bot Telegram démarré et en écoute.",
        "log_telegram_startup_error": "Erreur de démarrage/connexion Telegram: {e}",
        "log_closing_telegram": "Fermeture du gestionnaire de mise à jour et de l'application Telegram...",
        "log_invalid_command": "Commande non valide rejetée: '{cmd}' ({err})",
        "log_dup_command": "Commande dupliquée ignorée pour ID {sender_id}: '{cmd}'",
        "log_cmd_received": "Commande reçue du Master: /{cmd} {arg}",
        "log_unknown_command": "Commande inconnue: '{cmd}'",
        "log_command_result": "Résultat de la commande {cmd}: {msg}",

        # Log Messages — Security (security.py)
        "log_sec_master_unconfigured": "Mise à jour Telegram rejetée: Master User ID n'est pas configuré sur cet ordinateur.",
        "log_sec_master_invalid_int": "La Master User ID configurée n'est pas un entier valide.",
        "log_sec_unauthorized_access": "TENTATIVE D'ACCÈS NON AUTORISÉ: User ID={user_id} ({username}) a tenté d'envoyer: '{preview}'",

        # Log Messages — Credentials (credentials.py)
        "log_fallback_read_error": "Impossible de lire les identifiants de secours chiffrés: {e}",
        "log_keyring_save_error": "Keyring n'a pas pué sauvegarder '{key}': {e}. Tentative de secours DPAPI...",
        "log_dpapi_save_error": "Échec de la sauvegarde de l'identifiant '{key}' dans le secours DPAPI: {e}",
        "log_keyring_load_debug": "Exception de chargement keyring pour '{key}': {e}",
        "log_fallback_load_debug": "Exception de chargement de secours pour '{key}': {e}",

        # Log Messages — Outlook Monitor (outlook_monitor.py)
        "log_mail_config_error": "Erreur lors du chargement de la configuration de notification par e-mail: {e}",
        "log_mail_config_save_error": "Erreur lors de l'enregistrement de la configuration de notification par e-mail: {e}",
        "log_mail_already_running": "OutlookMailMonitor est déjà en cours d'exécution.",
        "log_mail_started": "OutlookMailMonitor démarré. Seuil de notification: les courriels reçus après {cutoff} déclencheront des alertes.",
        "log_mail_stopped": "OutlookMailMonitor arrêté.",
        "log_outlook_com_ok": "Accès COM Outlook OK. Surveillance de la Boîte de réception pour les messages non lus.",
        "log_cutoff_time": "Seuil: les courriels reçus avant {cutoff} seront ignorés.",
        "log_polling_folder": "Sondage {folder}: {count} message(s) non lu(s).",
        "log_mail_ignored_old": "Courriel ignoré (trop ancien) dans {folder}: '{subject}'",
        "log_mail_keyword_match": "Courriel correspondant trouvé dans {folder}: '{subject}'",
        "log_telegram_notify_sent": "Notification Telegram envoyée avec succès.",
        "log_telegram_notify_failed": "Échec de l'envoi de la notification Telegram.",
        "log_bot_manager_unavailable": "Gestionnaire de bot non disponible, impossible d'envoyer la notification.",
        "log_outlook_processing_error": "Erreur lors du traitement des courriels Outlook: {e}",
        "log_mail_thread_exit": "Thread OutlookMailMonitor en cours de fermeture.",
        "log_outlook_com_error": "Impossible d'accéder à Outlook via COM: {e}",

        # Log Messages — GUI (gui.py)
        "log_token_saved": "Jeton API Telegram configuré et enregistré dans le coffre de mots de passe.",
        "log_master_saved": "Master User ID configuré et enregistré.",
        "log_mail_keywords_updated": "Mots-clés de notification par e-mail mis à jour.",
        "log_window_minimized": "Fenêtre minimisée dans la System Tray.",
        "log_window_restored": "Fenêtre restaurée depuis la System Tray.",

        # Log Messages — Tray (tray.py)
        "log_tray_started": "System Tray démarrée.",
        "log_tray_start_error": "Impossible de démarrer la System Tray: {e}",
        "log_tray_icon_error": "Impossible de charger le fichier d'icône {path}: {e}",
        "log_tray_stopped": "System Tray supprimée.",
        "log_tray_show_error": "Erreur dans le gestionnaire 'Afficher' de la bande-passante: {e}",
        "log_tray_exit_error": "Erreur dans le gestionnaire 'Quitter' de la bande-passante: {e}",

        # Log Messages — System Commands (commands/system.py)
        "log_error_shutdown_call": "Exception pendant l'appel à shutdown:",
        "log_error_restart_call": "Exception pendant l'appel à restart:",
        "log_error_shutdown_abort": "Exception pendant l'appel à shutdown /a:",
        "log_error_lockworkstation": "Exception pendant LockWorkStation:",

        # Log Messages — Panic (commands/processes.py)
        "log_panic_procedure": "PROCÉDURE DE PANIQUE DÉCLANCHÉE: Fermeture des applications utilisateur...",
        "log_panic_terminating": "Panic: terminaison du PID={pid} ({name})...",
        "log_access_denied_terminate": "AccessDenied lors de la tentative de terminer le PID {pid}",
        "log_exception_terminating": "Exception lors de la terminaison du PID {proc}: {e}",
        "log_resolve_hierarchy_error": "Impossible de résoudre la hiérarchie des processus: {e}",

        # Log Messages — Applications (commands/applications.py)
        "log_firefox_not_found": "Tentative de lancement de Firefox: exécutable introuvable.",
        "log_firefox_start_error": "Erreur lors du lancement de Firefox ({exe}):",
        "log_outlook_not_found": "Tentative de lancement d'Outlook: exécutable introuvable.",
        "log_outlook_start_error": "Erreur lors du lancement d'Outlook ({exe}):",
        "log_notepad_note_error": "Erreur lors de l'ouverture de Notepad pour la note:",

        # Log Messages — Command Result Messages (commands/*.py)
        "log_unhandled_error": "Erreur non gérée dans l'exécution de la commande: {cmd}:",
        "log_msg_shutdown_scheduled": "Arrêt planifié dans {delay}s.",
        "log_msg_shutdown_error": "Erreur d'arrêt: {err}",
        "log_msg_shutdown_exception": "Exception d'arrêt: {e}",
        "log_msg_restart_scheduled": "Redémarrage planifié dans {delay}s.",
        "log_msg_restart_error": "Erreur de redémarrage: {err}",
        "log_msg_restart_exception": "Exception de redémarrage: {e}",
        "log_msg_abort_done": "Arrêt/Redémarrage annulé.",
        "log_msg_abort_none": "Tentative d'annulation d'arrêt: aucune opération en cours.",
        "log_msg_abort_exception": "Exception d'annulation: {e}",
        "log_msg_lock_success": "Station de travail verrouillée avec succès.",
        "log_msg_lock_failed": "LockWorkStation échoué avec le code {code}.",
        "log_msg_lock_exception": "Exception de LockWorkStation: {e}",
        "log_msg_ping": "Ping répondu. Uptime: {uptime}",
        "log_msg_status": "Commande status exécutée avec succès.",
        "log_msg_help": "Aide des commandes envoyée.",
        "log_msg_panic_done": "Pánique exécutée: {terminated} processus fermés, {denied} protégés.",
        "log_msg_firefox_not_found": "Firefox non trouvé.",
        "log_msg_firefox_launched": "Firefox lancé depuis: {exe}",
        "log_msg_firefox_error": "Erreur de lancement de Firefox: {e}",
        "log_msg_outlook_not_found": "Outlook non trouvé.",
        "log_msg_outlook_launched": "Outlook lancé depuis: {exe}",
        "log_msg_outlook_error": "Erreur de lancement d'Outlook: {e}",
        "log_msg_note_opened": "Notepad ouvert avec la note: '{preview}'",
        "log_msg_note_error": "Erreur de lancement de Notepad: {e}",
        "log_msg_note_empty": "Tentative d'ouvrir une note vide.",
        "log_error_internal": "Erreur interne dans {cmd}: {e}",
        "log_msg_unknown_windows_error": "Erreur Windows inconnue.",

        # Log Messages — Icons (icons.py)
        "log_icon_generate_error": "Échec de la génération de l'icône {name}: {e}",
        "log_icon_not_found": "Fichier d'icône introuvable: {path}",
        "log_icon_load_error": "Erreur lors du chargement de l'icône '{name}' depuis {path}: {e}",

        # Log Messages — Startup (startup.py)
        "log_startup_enabled": "Démarrage avec Windows activé: {cmd}",
        "log_startup_enable_error": "Erreur lors de l'activation du démarrage avec Windows: {e}",
        "log_startup_disabled": "Démarrage avec Windows désactivé.",
        "log_startup_disable_error": "Erreur lors de la désactivation du démarrage avec Windows: {e}",

        # Telegram Bot Messages (user-facing replies)
        "telegram_empty_message": "Message vide ou non textuel.",
        "telegram_mail_notification": "📧 *Nouveau e-mail* ({folder})\n*Expéditeur*: {sender}\n*Objet*: {subject}\n*Heure*: {time}",
        "telegram_no_command": "Aucune commande identifiée.",
        "telegram_note_empty_arg": "Entrez le texte de la note après 'note:'. Exemple: note: rappelle-moi la réunion",
        "telegram_too_many_args": "Trop d'arguments. Les commandes n'acceptent pas de paramètres arbitraires.",
        "telegram_no_extra_args": "La commande '{cmd}' n'accepte pas d'arguments supplémentaires.",
        "telegram_invalid_cmd": "Commande non valide.",
        "telegram_reply_invalid_cmd": "⚠️ {err}\nEnvoyez `/help` pour voir les commandes autorisées.",
        "telegram_unknown_cmd": "❓ Commande inconnue: `/{cmd}`\nEnvoyez `/help` pour afficher les commandes autorisées.",
        "telegram_master_unconfigured": "❌ Master User ID n'est pas configuré sur cet ordinateur.",
        "telegram_master_invalid": "❌ La configuration locale du Master User ID est invalide.",
        "telegram_unauthorized": "⛔ Accès refusé: utilisateur non autorisé.",
        "telegram_panic_prompt": "⚠️ *ATTENTION*: La commande `/panic` fermera les applications utilisateur ouvertes et peut causer des pertes de données non sauvegardées.\n\nPour confirmer, envoyez dans les 15 secondes:\n`/panic confirm`",
        "telegram_panic_no_pending": "Aucune demande de panique en attente. Envoyez d'abord `/panic`.",
        "telegram_panic_expired": "Demande de panique expirée ({elapsed:.1f}s > {timeout}s). Envoyez `/panic` à nouveau.",
        "telegram_panic_invalid_arg": "Argument non valide. Pour confirmer envoyez exactement: `/panic confirm`.",
        "telegram_shutdown_sched": "🛑 Arrêt planifié dans {delay} secondes.\nUtilisez `/annulla` pour annuler immédiatement.",
        "telegram_shutdown_error": "❌ Impossible de planifier l'arrêt: {err}",
        "telegram_shutdown_internal_error": "❌ Erreur interne lors de l'arrêt: {e}",
        "telegram_restart_sched": "🔄 Redémarrage planifié dans {delay} secondes.\nUtilisez `/annulla` pour annuler immédiatement.",
        "telegram_restart_error": "❌ Impossible de planifier le redémarrage: {err}",
        "telegram_restart_internal_error": "❌ Erreur interne lors du redémarrage: {e}",
        "telegram_abort_done": "✅ {action} annulé avec succès.",
        "telegram_abort_none": "ℹ️ Aucune opération d'arrêt ou de redémarrage à annuler.",
        "telegram_abort_internal_error": "❌ Erreur interne lors de l'annulation: {e}",
        "telegram_lock_success": "🔒 Station de travail Windows verrouillée.",
        "telegram_lock_error": "❌ Erreur de verrouillage de la station de travail (code: {code}).",
        "telegram_lock_internal_error": "❌ Erreur lors du verrouillage de la station de travail: {e}",
        "telegram_ping": "🏓 *PONG*\n━━━━━━━━━━━━━━━━━━━━\n💻 PC en ligne et prêt\n⏱️ Heure locale: `{time}`\n⏳ Temps de fonctionnement: `{uptime}`",
        "telegram_status_header": "📊 *STATUT BOT & SYSTÈME*",
        "telegram_status_separator": "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "telegram_status_bot": "🤖 Bot Telegram: `ONLINE`",
        "telegram_status_master": "👑 Master User: `{status}`",
        "telegram_status_startup": "🚀 Démarrage Windows: `{status}`",
        "telegram_status_tray": "🗂️ System Tray: `ACTIF`",
        "telegram_status_version": "📦 Version de l'app: `v{version}`",
        "telegram_status_cmd_count": "📋 Commandes enregistrées: `{count}`",
        "telegram_status_subsep": "───────────────────────────",
        "telegram_status_uptime": "⏳ Temps de fonctionnement PC: `{uptime}`",
        "telegram_status_metrics": "⚡ CPU: `{cpu}` | RAM: `{ram}`",
        "telegram_status_pending_active": "⚠️ En cours ({action})",
        "telegram_status_pending_none": "Aucun",
        "telegram_panic_done": "🚨 *PROCÉDURE DE PANIQUE TERMINÉE*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📉 Processus utilisateur fermés: `{count}`\n🛡️ Processus système protégés",
        "telegram_panic_denied": "⚠️ Processus protégés par des autorisations élevées: `{count}`\n",
        "telegram_firefox_not_found": "❌ Firefox est introuvable sur ce système.",
        "telegram_firefox_launched": "🌐 Mozilla Firefox lancé avec succès.",
        "telegram_firefox_error": "❌ Erreur lors du lancement de Firefox: {e}",
        "telegram_outlook_not_found": "❌ Outlook est introuvable sur ce système.",
        "telegram_outlook_launched": "📧 Microsoft Outlook lancé avec succès.",
        "telegram_outlook_error": "❌ Erreur lors du lancement d'Outlook: {e}",
        "telegram_note_empty_msg": "❌ Le texte de la note ne peut pas être vide.",
        "telegram_note_opened": "📝 *Notepad ouvert sur le PC!*\n📄 Contenu: _{preview}_\n📁 Enregistré sous: `{filename}`",
        "telegram_notepad_error": "❌ Erreur lors de l'ouverture de Notepad: {e}",
        "telegram_help_header": "🖥️ *BotMyPC — Contrôle à Distance PC*",
        "telegram_help_list_header": "Voici la liste des commandes autorisées:\n",
        "telegram_help_separator": "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "telegram_help_destructive_header": "\n*Commandes à impact système:*",
        "telegram_help_footer": "🛡️ _Les commandes non enregistrées ou avec des arguments arbitraires sont rejetées._",
        "telegram_error_internal": "❌ Une erreur interne est survenue lors de l'exécution de la commande.",
        "telegram_action_shutdown": "Arrêt",
        "telegram_action_restart": "Redémarrage",
        "telegram_action_unknown": "Opération",
        "cmd_shutdown_desc": "Planifie l'arrêt du PC dans 10 secondes (annulable)",
        "cmd_restart_desc": "Planifie le redémarrage du PC dans 10 secondes (annulable)",
        "cmd_annulla_desc": "Annule un arrêt ou redémarrage programmé",
        "cmd_out_desc": "Verrouille immédiatement la station de travail Windows (LockWorkStation)",
        "cmd_ping_desc": "Vérifie que le PC est en ligne et retourne le temps de fonctionnement",
        "cmd_status_desc": "Affiche le statut détaillé de l'application, du bot et des ressources PC",
        "cmd_help_desc": "Affiche la liste des commandes autorisées et leurs descriptions",
        "cmd_firefox_desc": "Lance Mozilla Firefox (avec détection automatique du chemin)",
        "cmd_outlook_desc": "Lance Microsoft Outlook (avec détection Click-to-Run/MSI)",
        "cmd_note_desc": "Ouvre Notepad et colle le texte envoyé",
        "cmd_panic_desc": "Ferme les applications utilisateur (nécessite confirmation: /panic confirm)",
    },
}

_current_language: Optional[str] = None


def load_settings() -> Dict[str, Any]:
    """Reads settings dictionary from settings.json."""
    if SETTINGS_FILE_PATH.exists():
        try:
            with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading settings from {SETTINGS_FILE_PATH}: {e}")
    return {}


def save_settings(settings: Dict[str, Any]) -> bool:
    """Writes settings dictionary to settings.json atomically."""
    try:
        SETTINGS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving settings to {SETTINGS_FILE_PATH}: {e}")
        return False


def load_external_locales() -> None:
    """
    Discovers and loads external .json translation files from the locales/ directory.
    Allows translators and users to add new languages without modifying Python code!
    """
    if not LOCALES_DIR.exists() or not LOCALES_DIR.is_dir():
        return

    for json_file in LOCALES_DIR.glob("*.json"):
        if json_file.name.startswith("template"):
            continue
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            meta = data.pop("_meta", None)
            code = json_file.stem.lower()

            if meta and isinstance(meta, dict):
                code = meta.get("code", code)
                SUPPORTED_LANGUAGES[code] = {
                    "code": code,
                    "name": meta.get("name", code.capitalize()),
                    "native": meta.get("native", code.capitalize()),
                    "flag": meta.get("flag", "🌐"),
                }
            elif code not in SUPPORTED_LANGUAGES:
                SUPPORTED_LANGUAGES[code] = {
                    "code": code,
                    "name": code.capitalize(),
                    "native": code.capitalize(),
                    "flag": "🌐",
                }

            if code not in TRANSLATIONS:
                TRANSLATIONS[code] = {}
            TRANSLATIONS[code].update(data)
            logger.debug(f"Loaded external translation locale: '{code}' from {json_file.name}")
        except Exception as e:
            logger.warning(f"Failed to load external locale from {json_file}: {e}")


def get_supported_languages() -> Dict[str, Dict[str, str]]:
    """Returns all supported languages, including any dynamically loaded locales."""
    load_external_locales()
    return SUPPORTED_LANGUAGES


def get_current_language() -> str:
    """Returns the currently active language code."""
    global _current_language
    load_external_locales()
    if _current_language is not None:
        return _current_language

    settings = load_settings()
    saved = settings.get("language")
    if saved and saved in SUPPORTED_LANGUAGES:
        _current_language = saved
    else:
        _current_language = DEFAULT_LANGUAGE

    return _current_language


def set_language(lang_code: str) -> bool:
    """Sets and persists the active application language."""
    global _current_language
    load_external_locales()
    if lang_code not in SUPPORTED_LANGUAGES:
        return False

    _current_language = lang_code
    settings = load_settings()
    settings["language"] = lang_code
    success = save_settings(settings)
    if success:
        logger.info(t("log_language_set", lang=lang_code))
    return success


def t(key: str, **kwargs) -> str:
    """
    Translates a key into the active language string.
    Falls back to English if the key is missing in the chosen language.
    """
    lang = get_current_language()
    table = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANGUAGE])
    text = table.get(key)
    if text is None:
        text = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)

    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

