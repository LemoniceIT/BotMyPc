"""
Unit tests for credential storage abstraction, DPAPI fallback encryption,
and token masking.
"""

from unittest.mock import patch
import pytest
from pathlib import Path

import credentials


def test_token_masking():
    """Verifies that token is never revealed in full."""
    assert credentials.mask_token(None) == "[NON CONFIGURATO]"
    assert credentials.mask_token("") == "[NON CONFIGURATO]"
    assert credentials.mask_token("123") == "******"

    full_token = "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567"
    masked = credentials.mask_token(full_token)
    assert masked.startswith("123456")
    assert masked.endswith("4567")
    assert "..." in masked
    assert "ABCdefGhIJKlmNoPQRsTUVwxyZ" not in masked


def test_credential_save_load_delete_roundtrip(tmp_path: Path):
    """
    Tests saving, loading, updating, and deleting credentials using
    isolated temporary paths for the DPAPI fallback files.
    """
    test_enc_file = tmp_path / "credentials.enc"
    test_key_file = tmp_path / "credentials.key.dpapi"

    with patch("credentials.FALLBACK_CREDENTIALS_FILE", test_enc_file), \
         patch("credentials.FALLBACK_KEY_FILE", test_key_file):

        # Save test credentials
        assert credentials.save_credential("test_token_key", "secret_value_123") is True

        # Load
        loaded = credentials.load_credential("test_token_key")
        assert loaded == "secret_value_123"

        # Verify that fallback files exist
        assert test_enc_file.exists()
        assert test_key_file.exists()

        # Verify fallback encrypted file DOES NOT contain the plaintext secret
        raw_enc_bytes = test_enc_file.read_bytes()
        assert b"secret_value_123" not in raw_enc_bytes

        # Verify key file is protected via DPAPI and DOES NOT contain raw ASCII/JSON
        raw_key_bytes = test_key_file.read_bytes()
        assert b"secret_value_123" not in raw_key_bytes

        # Update credential
        assert credentials.save_credential("test_token_key", "new_secret_456") is True
        assert credentials.load_credential("test_token_key") == "new_secret_456"

        # Delete credential
        assert credentials.delete_credential("test_token_key") is True
        assert credentials.load_credential("test_token_key") is None


def test_fallback_fails_if_key_tampered(tmp_path: Path):
    """Verifies that tampering with DPAPI-protected key file prevents unauthorized decryption."""
    test_enc_file = tmp_path / "credentials.enc"
    test_key_file = tmp_path / "credentials.key.dpapi"

    with patch("credentials.FALLBACK_CREDENTIALS_FILE", test_enc_file), \
         patch("credentials.FALLBACK_KEY_FILE", test_key_file), \
         patch("keyring.get_password", return_value=None):

        credentials.save_credential("tamper_test", "super_secret")
        assert credentials.load_credential("tamper_test") == "super_secret"

        # Corrupt the DPAPI key file
        test_key_file.write_bytes(b"corrupted_garbage_bytes_12345678")

        # Loading must fail gracefully without exposing plaintext or crashing
        loaded = credentials.load_credential("tamper_test")
        assert loaded is None
