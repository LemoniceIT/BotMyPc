"""
Unit tests for internationalization (i18n) and icon management.
"""

import json
from pathlib import Path
import pytest

import i18n
import icons


def test_default_language():
    """Verify that the default language is English."""
    assert i18n.DEFAULT_LANGUAGE == "en"
    assert "en" in i18n.SUPPORTED_LANGUAGES


def test_supported_languages():
    """Verify all 5 requested languages are supported."""
    expected = {"en", "de", "es", "it", "fr"}
    assert set(i18n.SUPPORTED_LANGUAGES.keys()) == expected


def test_all_languages_have_consistent_keys():
    """Ensure every language has all translation keys present in the English reference."""
    en_keys = set(i18n.TRANSLATIONS["en"].keys())
    for lang_code in ("de", "es", "it", "fr"):
        lang_keys = set(i18n.TRANSLATIONS[lang_code].keys())
        missing = en_keys - lang_keys
        assert not missing, f"Language '{lang_code}' is missing keys: {missing}"


def test_translation_formatting():
    """Test string format interpolation in translations."""
    i18n.set_language("en")
    text = i18n.t("token_current", token="12345:ABCDE")
    assert "12345:ABCDE" in text


def test_fallback_unknown_key():
    """Verify that an unknown translation key returns the key itself as fallback."""
    result = i18n.t("non_existent_key_12345")
    assert result == "non_existent_key_12345"


def test_language_persistence(tmp_path, monkeypatch):
    """Verify that language selection persists across sessions via settings.json."""
    settings_file = tmp_path / "settings.json"
    monkeypatch.setattr(i18n, "SETTINGS_FILE_PATH", settings_file)

    # Force re-read
    i18n._current_language = None
    assert i18n.get_current_language() == "en"

    # Switch to Italian
    success = i18n.set_language("it")
    assert success is True
    assert settings_file.exists()

    with open(settings_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("language") == "it"

    # Simulate next session (cache cleared)
    i18n._current_language = None
    assert i18n.get_current_language() == "it"
    assert i18n.t("btn_language") == "Lingua"

    # Switch to German
    i18n.set_language("de")
    i18n._current_language = None
    assert i18n.get_current_language() == "de"
    assert i18n.t("btn_language") == "Sprache"

    # Reset to English
    i18n.set_language("en")
    i18n._current_language = None
    assert i18n.get_current_language() == "en"


def test_invalid_language_rejected():
    """Verify that setting an invalid language code is rejected."""
    curr = i18n.get_current_language()
    res = i18n.set_language("invalid_lang_xx")
    assert res is False
    assert i18n.get_current_language() == curr


def test_icons_loading():
    """Verify that all required button icons load and return valid CTkImage objects."""
    required_icons = [
        "token",
        "master",
        "background",
        "mail",
        "language",
        "credits",
        "play",
        "stop",
        "save",
    ]
    for name in required_icons:
        img = icons.get_button_icon(name, size=(16, 16))
        assert img is not None, f"Icon '{name}' failed to load"


def test_credits_license_present_in_all_languages():
    """Verify credits_license is translated in all supported languages."""
    for lang in ("en", "de", "es", "it", "fr"):
        assert "credits_license" in i18n.TRANSLATIONS[lang]
        assert "MIT" in i18n.TRANSLATIONS[lang]["credits_license"]


def test_dynamic_external_locale_loading(tmp_path, monkeypatch):
    """Verify that external .json locales can be loaded dynamically without code modifications."""
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir()
    monkeypatch.setattr(i18n, "LOCALES_DIR", locales_dir)

    custom_locale = {
        "_meta": {
            "code": "pt",
            "name": "Portuguese",
            "native": "Português",
            "flag": "🇵🇹"
        },
        "btn_start_bot": "Iniciar Robô",
        "btn_language": "Idioma"
    }
    pt_file = locales_dir / "pt.json"
    pt_file.write_text(json.dumps(custom_locale), encoding="utf-8")

    all_supported = i18n.get_supported_languages()
    assert "pt" in all_supported
    assert all_supported["pt"]["native"] == "Português"
    assert all_supported["pt"]["flag"] == "🇵🇹"

    # Switch to dynamically discovered language
    assert i18n.set_language("pt") is True
    assert i18n.t("btn_start_bot") == "Iniciar Robô"
    assert i18n.t("btn_language") == "Idioma"
    # Fallback to English for unspecified keys
    assert i18n.t("btn_clear") == "Clear"

    # Reset
    i18n.set_language("en")

