"""
Command Registry for BotMyPC.

Maintains the closed list of authorized remote commands, their metadata,
and generates dynamic help documentation.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Dict, Any

from i18n import t


@dataclass
class CommandResult:
    """
    Structured outcome returned by every command handler.
    """
    success: bool
    message: str
    log_message: Optional[str] = None
    error_code: Optional[int] = None


@dataclass
class CommandDefinition:
    """
    Metadata for a registered remote command.
    """
    name: str
    handler: Callable[..., CommandResult]
    description: str
    destructive: bool = False
    usage: Optional[str] = None
    takes_argument: bool = False


class CommandRegistry:
    """
    Central repository for all permissible bot commands.
    Ensures that only explicitly registered commands can be executed.
    """

    def __init__(self) -> None:
        self._commands: Dict[str, CommandDefinition] = {}

    def register(self, definition: CommandDefinition) -> None:
        """Registers a command definition under its lowercase name."""
        name = definition.name.lower().strip()
        self._commands[name] = definition

    def get(self, name: str) -> Optional[CommandDefinition]:
        """Looks up a command by name."""
        return self._commands.get(name.lower().strip())

    def exists(self, name: str) -> bool:
        """Returns True if the command is registered."""
        return name.lower().strip() in self._commands

    def list_commands(self) -> Dict[str, CommandDefinition]:
        """Returns a copy of all registered command definitions."""
        return dict(self._commands)

    def generate_help(self) -> str:
        """
        Dynamically generates the Telegram /help response from registered definitions.
        No hardcoded command list is maintained outside this registry.
        """
        lines = [
            t("telegram_help_header"),
            t("telegram_help_separator"),
            t("telegram_help_list_header"),
        ]

        # Group by non-destructive vs destructive
        standard_cmds = []
        destructive_cmds = []

        for name, cmd in sorted(self._commands.items()):
            prefix = "⚠️ " if cmd.destructive else "🔹 "
            cmd_usage = cmd.usage or f"/{name}"
            entry = f"{prefix}*{cmd_usage}*\n   └ {cmd.description}"
            if cmd.destructive:
                destructive_cmds.append(entry)
            else:
                standard_cmds.append(entry)

        if standard_cmds:
            lines.extend(standard_cmds)

        if destructive_cmds:
            lines.append(t("telegram_help_destructive_header"))
            lines.extend(destructive_cmds)

        lines.append(t("telegram_help_separator"))
        lines.append(t("telegram_help_footer"))

        return "\n".join(lines)


# Global registry singleton
REGISTRY = CommandRegistry()
