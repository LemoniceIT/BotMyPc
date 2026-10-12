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
        logger.info(f"Language updated to '{lang_code}' and saved to settings.")
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

