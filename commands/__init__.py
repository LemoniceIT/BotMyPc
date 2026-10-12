"""
Commands package for BotMyPC.
Registers all commands with metadata into the central REGISTRY.
"""

from command_registry import CommandDefinition, REGISTRY
from i18n import t
from commands.system import (
    schedule_shutdown,
    schedule_restart,
    abort_shutdown,
    lock_workstation,
    ping,
    status,
    help_command,
)
from commands.applications import launch_firefox, launch_outlook, open_notepad_note
from commands.processes import execute_panic


def register_all_commands() -> None:
    """Registers all built-in commands into the global registry."""
    # System commands
    REGISTRY.register(CommandDefinition(
        name="shutdown",
        handler=schedule_shutdown,
        description=t("cmd_shutdown_desc"),
        destructive=True,
        usage="/shutdown",
    ))
    REGISTRY.register(CommandDefinition(
        name="restart",
        handler=schedule_restart,
        description=t("cmd_restart_desc"),
        destructive=True,
        usage="/restart",
    ))
    REGISTRY.register(CommandDefinition(
        name="annulla",
        handler=abort_shutdown,
        description=t("cmd_annulla_desc"),
        destructive=False,
        usage="/annulla",
    ))
    REGISTRY.register(CommandDefinition(
        name="out",
        handler=lock_workstation,
        description=t("cmd_out_desc"),
        destructive=False,
        usage="/out",
    ))
    REGISTRY.register(CommandDefinition(
        name="ping",
        handler=ping,
        description=t("cmd_ping_desc"),
        destructive=False,
        usage="/ping",
    ))
    REGISTRY.register(CommandDefinition(
        name="status",
        handler=status,
        description=t("cmd_status_desc"),
        destructive=False,
        usage="/status",
    ))
    REGISTRY.register(CommandDefinition(
        name="help",
        handler=help_command,
        description=t("cmd_help_desc"),
        destructive=False,
        usage="/help",
    ))

    # Application commands
    REGISTRY.register(CommandDefinition(
        name="firefox",
        handler=launch_firefox,
        description=t("cmd_firefox_desc"),
        destructive=False,
        usage="/firefox",
    ))
    REGISTRY.register(CommandDefinition(
        name="outlook",
        handler=launch_outlook,
        description=t("cmd_outlook_desc"),
        destructive=False,
        usage="/outlook",
    ))
    REGISTRY.register(CommandDefinition(
        name="note",
        handler=open_notepad_note,
        description=t("cmd_note_desc"),
        destructive=False,
        usage="note: <testo della nota>",
        takes_argument=True,
    ))

    # Emergency process command
    REGISTRY.register(CommandDefinition(
        name="panic",
        handler=execute_panic,
        description=t("cmd_panic_desc"),
        destructive=True,
        usage="/panic",
    ))


# Execute registration on package import
register_all_commands()
