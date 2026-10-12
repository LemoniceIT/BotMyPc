"""
Unit tests for CommandRegistry, CommandDefinition, and dynamic help generation.
"""

from command_registry import CommandRegistry, CommandDefinition, CommandResult


def dummy_handler() -> CommandResult:
    return CommandResult(success=True, message="OK")


def test_command_registry_registration_and_lookup():
    reg = CommandRegistry()

    cmd = CommandDefinition(
        name="testcmd",
        handler=dummy_handler,
        description="A test command",
        destructive=False,
    )
    reg.register(cmd)

    # Exact lookup
    assert reg.exists("testcmd") is True
    assert reg.get("testcmd") == cmd

    # Case-insensitive lookup
    assert reg.exists("TESTCMD") is True
    assert reg.get("  TESTCMD  ") == cmd

    # Non-existent
    assert reg.exists("nonexistent") is False
    assert reg.get("nonexistent") is None


def test_dynamic_help_generation():
    reg = CommandRegistry()

    reg.register(CommandDefinition(
        name="ping",
        handler=dummy_handler,
        description="Checks status",
        destructive=False,
    ))
    reg.register(CommandDefinition(
        name="shutdown",
        handler=dummy_handler,
        description="Shuts down PC",
        destructive=True,
    ))

    help_text = reg.generate_help()
    assert "/ping" in help_text
    assert "Checks status" in help_text
    assert "/shutdown" in help_text
    assert "Shuts down PC" in help_text
    assert "System impact commands" in help_text
