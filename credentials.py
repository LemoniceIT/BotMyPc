"""
Credential storage abstraction for BotMyPC.

Stores Bot Token and Master User ID securely:
1. Primary: Windows Credential Manager via `keyring`.
2. Secondary (Fallback): AES-CBC/HMAC-SHA256 via `cryptography.fernet.Fernet`,
   where the Fernet encryption key is protected using Windows DPAPI
   (Data Protection API via win32crypt.CryptProtectData). The key is encrypted
   using the Windows user's logon credentials and cannot be decrypted outside
   the specific Windows account and machine.
"""

from __future__ import annotations
import json
import logging
from pathlib import Path
from typing import Optional, Dict
import ctypes
from ctypes import wintypes

import keyring
from cryptography.fernet import Fernet

from config import (
    APP_NAME,
    FALLBACK_CREDENTIALS_FILE,
    FALLBACK_KEY_FILE,
)

logger = logging.getLogger(APP_NAME)

SERVICE_NAME: str = APP_NAME
KEY_BOT_TOKEN: str = "telegram_bot_token"
KEY_MASTER_USER_ID: str = "telegram_master_user_id"


# =====================================================================
# DPAPI Utilities (win32crypt with ctypes fallback)
# =====================================================================

def _dpapi_protect(data: bytes) -> bytes:
    """Encrypts bytes using Windows DPAPI for the current logged-in user."""
    try:
        import win32crypt
        return win32crypt.CryptProtectData(data, "BotMyPC DPAPI Key", None, None, None, 0)
    except ImportError:
        pass

    # ctypes fallback for CryptProtectData
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

    crypt32 = ctypes.windll.crypt32

    in_blob = DATA_BLOB(len(data), ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_byte)))
    out_blob = DATA_BLOB()

    if not crypt32.CryptProtectData(
        ctypes.byref(in_blob),
        "BotMyPC DPAPI Key",
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob)
    ):
        raise ctypes.WinError()

    try:
        buffer = (ctypes.c_byte * out_blob.cbData)()
        ctypes.memmove(buffer, out_blob.pbData, out_blob.cbData)
        return bytes(buffer)
    finally:
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)


def _dpapi_unprotect(data: bytes) -> bytes:
    """Decrypts bytes using Windows DPAPI for the current logged-in user."""
    try:
        import win32crypt
        _, unprotected = win32crypt.CryptUnprotectData(data, None, None, None, 0)
        return unprotected
    except ImportError:
        pass

    # ctypes fallback for CryptUnprotectData
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]

    crypt32 = ctypes.windll.crypt32

    in_blob = DATA_BLOB(len(data), ctypes.cast(ctypes.create_string_buffer(data), ctypes.POINTER(ctypes.c_byte)))
    out_blob = DATA_BLOB()

    if not crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob)
    ):
        raise ctypes.WinError()

    try:
        buffer = (ctypes.c_byte * out_blob.cbData)()
        ctypes.memmove(buffer, out_blob.pbData, out_blob.cbData)
        return bytes(buffer)
    finally:
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)


# =====================================================================
# Fallback Storage via DPAPI + Fernet
# =====================================================================

def _get_or_create_fernet_cipher() -> Fernet:
    """
    Retrieves or creates a Fernet key whose bytes are protected on disk via DPAPI.
    The raw Fernet key is never stored on disk in plaintext.
    """
    if FALLBACK_KEY_FILE.exists():
        encrypted_key = FALLBACK_KEY_FILE.read_bytes()
        raw_key = _dpapi_unprotect(encrypted_key)
        return Fernet(raw_key)

    # Generate brand new Fernet key and protect with DPAPI
    raw_key = Fernet.generate_key()
    encrypted_key = _dpapi_protect(raw_key)
    FALLBACK_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    FALLBACK_KEY_FILE.write_bytes(encrypted_key)
    return Fernet(raw_key)


def _read_fallback_store() -> Dict[str, str]:
    """Reads and decrypts the fallback credentials JSON file."""
    if not FALLBACK_CREDENTIALS_FILE.exists():
        return {}
    try:
        cipher = _get_or_create_fernet_cipher()
        encrypted_data = FALLBACK_CREDENTIALS_FILE.read_bytes()
        decrypted_json = cipher.decrypt(encrypted_data).decode("utf-8")
        return json.loads(decrypted_json)
    except Exception as e:
        logger.warning(f"Could not read encrypted fallback credentials: {e}")
        return {}


def _write_fallback_store(data: Dict[str, str]) -> None:
    """Encrypts and writes the fallback credentials JSON file."""
    cipher = _get_or_create_fernet_cipher()
    payload = json.dumps(data).encode("utf-8")
    encrypted_payload = cipher.encrypt(payload)
    FALLBACK_CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    FALLBACK_CREDENTIALS_FILE.write_bytes(encrypted_payload)


# =====================================================================
# Public Credential Management API
# =====================================================================

def save_credential(key: str, value: str) -> bool:
    """
    Saves a credential. Attempts Windows Credential Manager (keyring) first;
    falls back to DPAPI-protected encrypted file if keyring fails.
    """
    cleaned_value = str(value).strip()
    saved_keyring = False

    try:
        keyring.set_password(SERVICE_NAME, key, cleaned_value)
        saved_keyring = True
    except Exception as e:
        logger.warning(f"Keyring failed to save {key}: {e}. Trying DPAPI fallback...")

    # Also keep fallback in sync or as primary if keyring failed
    try:
        store = _read_fallback_store()
        store[key] = cleaned_value
        _write_fallback_store(store)
        return True
    except Exception as e:
        logger.error(f"Failed to save credential {key} to DPAPI fallback: {e}")
        return saved_keyring


def load_credential(key: str) -> Optional[str]:
    """
    Loads a credential. Checks keyring first, falls back to DPAPI encrypted file.
    Returns None if not found.
    """
    # 1. Try keyring
    try:
        val = keyring.get_password(SERVICE_NAME, key)
        if val is not None and val.strip():
            return val.strip()
    except Exception as e:
        logger.debug(f"Keyring load exception for {key}: {e}")

    # 2. Try DPAPI fallback
    try:
        store = _read_fallback_store()
        val = store.get(key)
        if val is not None and val.strip():
            return val.strip()
    except Exception as e:
        logger.debug(f"Fallback load exception for {key}: {e}")

    return None


def delete_credential(key: str) -> bool:
    """
    Deletes a credential from both keyring and DPAPI fallback.
    """
    success = False
    try:
        keyring.delete_password(SERVICE_NAME, key)
        success = True
    except Exception:
        pass

    try:
        store = _read_fallback_store()
        if key in store:
            del store[key]
            _write_fallback_store(store)
            success = True
    except Exception:
        pass

    return success


def credentials_available() -> bool:
    """Returns True if both bot token and master user ID are set."""
    token = load_credential(KEY_BOT_TOKEN)
    master_id = load_credential(KEY_MASTER_USER_ID)
    return bool(token and master_id)


def mask_token(token: Optional[str]) -> str:
    """
    Returns a masked preview of a Telegram bot token (e.g. '123456...Wxyz').
    Never returns or exposes the full token.
    """
    if not token:
        return "[NON CONFIGURATO]"
    clean = token.strip()
    if len(clean) < 12:
        return "******"
    return f"{clean[:6]}...{clean[-4:]}"
