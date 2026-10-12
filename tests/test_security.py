"""
Unit tests for security, authorization gateway, command normalization,
and anti-flood/anti-duplication mechanisms.
"""

import time
import pytest

from security import (
    CommandNormalizer,
    AntiDuplicateFilter,
    PanicConfirmationTracker,
    SecurityGateway,
)


def test_command_normalizer_valid():
    """Tests case-insensitivity, stripping of spaces, and '/' prefix removal."""
    cases = [
        ("shutdown", "shutdown", ""),
        ("SHUTDOWN", "shutdown", ""),
        ("  /shutdown  ", "shutdown", ""),
        ("/STATUS", "status", ""),
        ("  /ping  ", "ping", ""),
        ("/panic conferma", "panic", "conferma"),
        ("PANIC CONFERMA", "panic", "conferma"),
        ("note:ricordami di inviare mail", "note", "ricordami di inviare mail"),
        ("note: ricordami di inviare mail", "note", "ricordami di inviare mail"),
        ("/note: ricordami mail", "note", "ricordami mail"),
        ("NOTE: Compra il latte", "note", "Compra il latte"),
    ]
    for raw, expected_cmd, expected_arg in cases:
        result = CommandNormalizer.normalize(raw)
        assert result.is_valid is True, f"Failed on {raw}"
        assert result.command == expected_cmd
        assert result.argument == expected_arg


def test_command_normalizer_rejections():
    """Tests that empty commands and arbitrary arguments are strictly rejected."""
    invalid_cases = [
        "",
        "   ",
        None,
        "/exec shutdown /s",
        "/shutdown now",
        "/firefox --incognito",
        "/panic conferma extra_arg",
        "note:",
        "note:   ",
        "/note:",
    ]
    for raw in invalid_cases:
        result = CommandNormalizer.normalize(raw)
        assert result.is_valid is False, f"Should be invalid: {raw}"


def test_anti_duplicate_filter():
    """Verifies that identical commands within the window are suppressed."""
    filter_ = AntiDuplicateFilter(window_seconds=1.0)
    user_id = 12345

    # 1. First execution must be allowed
    assert filter_.is_duplicate(user_id, "shutdown") is False

    # 2. Immediate duplicate must be rejected
    assert filter_.is_duplicate(user_id, "shutdown") is True
    assert filter_.is_duplicate(user_id, "SHUTDOWN") is True

    # 3. Different command for the same user is allowed
    assert filter_.is_duplicate(user_id, "ping") is False

    # 4. Same command for different user is allowed
    assert filter_.is_duplicate(99999, "shutdown") is False

    # 5. After window expires, original command is accepted again
    time.sleep(1.05)
    assert filter_.is_duplicate(user_id, "shutdown") is False


def test_security_gateway_master_authorization():
    """Verifies single mandatory authorization gateway (Section 7-bis)."""
    master_id = "12345678"
    gateway = SecurityGateway(get_master_user_id_fn=lambda: master_id)

    # 1. Authorized Master ID
    authorized, err = gateway.verify_authorization(12345678, "boss", "/shutdown")
    assert authorized is True
    assert err is None

    # 2. Unauthorized User ID
    unauthorized, err = gateway.verify_authorization(99999999, "stranger", "/shutdown")
    assert unauthorized is False
    assert "denied" in err.lower()

    # 3. None user ID
    none_user, err = gateway.verify_authorization(None, None, "/shutdown")
    assert none_user is False
    assert "denied" in err.lower()


def test_security_gateway_missing_master_config():
    """Verifies that if master ID is not configured locally, all requests are rejected."""
    gateway = SecurityGateway(get_master_user_id_fn=lambda: None)
    authorized, err = gateway.verify_authorization(12345678, "boss", "/shutdown")
    assert authorized is False
    assert "not configured" in err.lower()


def test_panic_confirmation_tracker():
    """Verifies two-step confirmation for emergency panic procedure."""
    tracker = PanicConfirmationTracker(timeout_seconds=0.5)
    user_id = 55555

    # Not requested yet
    confirmed, err = tracker.is_confirmed(user_id, "conferma")
    assert confirmed is False

    # Request panic
    msg = tracker.request_panic(user_id)
    assert "ATTENTION" in msg

    # Invalid confirmation argument
    confirmed, err = tracker.is_confirmed(user_id, "si")
    assert confirmed is False

    # Valid confirmation within window
    tracker.request_panic(user_id)
    confirmed, err = tracker.is_confirmed(user_id, "conferma")
    assert confirmed is True
    assert err is None

    # After confirmation, state is consumed
    confirmed, err = tracker.is_confirmed(user_id, "conferma")
    assert confirmed is False

    # Timeout expiration test
    tracker.request_panic(user_id)
    time.sleep(0.55)
    confirmed, err = tracker.is_confirmed(user_id, "conferma")
    assert confirmed is False
    assert "expired" in err.lower()


@pytest.mark.asyncio
async def test_central_dispatcher_blocks_unauthorized_before_handler():
    """
    Section 7-bis test:
    Verifies that the central dispatcher blocks unauthorized users
    even if the handler itself does NOT check authorization.
    """
    from unittest.mock import AsyncMock, MagicMock
    from telegram_bot import TelegramBotManager
    import queue

    q = queue.Queue()
    bot_manager = TelegramBotManager(gui_queue=q)

    # Mock gateway returning unauthorized
    bot_manager.security_gateway.verify_authorization = MagicMock(return_value=(False, "Access denied"))

    # Handler mock
    handler_mock = MagicMock()

    # Fake update from unauthorized user
    mock_update = MagicMock()
    mock_update.message = MagicMock()
    mock_update.message.text = "/shutdown"
    mock_update.message.reply_text = AsyncMock()
    mock_update.effective_user.id = 999999
    mock_update.effective_user.username = "hacker"

    # Dispatch
    await bot_manager._dispatch_update(mock_update, MagicMock())

    # Verify that handler was NEVER called
    handler_mock.assert_not_called()
    # Verify denial message sent
    mock_update.message.reply_text.assert_called_once_with("Access denied")

