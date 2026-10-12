# 🌐 BotMyPC — Locales & Translations

This directory allows adding new languages to **BotMyPC** without writing or modifying any Python code.

## How to Add a New Language

1. Copy `template.json` and name the new file with your 2-letter ISO language code (e.g., `pt.json` for Portuguese, `pl.json` for Polish, `ja.json` for Japanese).
2. Edit the `_meta` block at the top of the file:
   ```json
   {
     "_meta": {
       "code": "pt",
       "name": "Portuguese",
       "native": "Português",
       "flag": "🇵🇹"
     },
     "app_title": "BotMyPC — Controlador Remoto do Telegram",
     ...
   }
   ```
3. Translate the string values.
4. Launch BotMyPC: the application will automatically discover the new language file, display it in the **Language** dialog with its flag and native name, and allow switching to it immediately!
