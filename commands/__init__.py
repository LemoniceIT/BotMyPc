"""
Commands package for BotMyPC.
Registers all commands with metadata into the central REGISTRY.
"""

from command_registry import CommandDefinition, REGISTRY
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
        name="spegni",
        handler=schedule_shutdown,
        description="Programma lo spegnimento del PC tra 10 secondi (interrompibile)",
        destructive=True,
        usage="/spegni",
    ))
    REGISTRY.register(CommandDefinition(
        name="riavvia",
        handler=schedule_restart,
        description="Programma il riavvio del PC tra 10 secondi (interrompibile)",
        destructive=True,
        usage="/riavvia",
    ))
    REGISTRY.register(CommandDefinition(
        name="annulla",
        handler=abort_shutdown,
        description="Annulla un'operazione di spegnimento o riavvio programmata",
        destructive=False,
        usage="/annulla",
    ))
    REGISTRY.register(CommandDefinition(
        name="out",
        handler=lock_workstation,
        description="Blocca immediatamente la postazione Windows (Lock Workstation)",
        destructive=False,
        usage="/out",
    ))
    REGISTRY.register(CommandDefinition(
        name="ping",
        handler=ping,
        description="Verifica che il PC sia online e restituisce l'uptime del sistema",
        destructive=False,
        usage="/ping",
    ))
    REGISTRY.register(CommandDefinition(
        name="status",
        handler=status,
        description="Mostra lo stato dettagliato dell'applicazione, del bot e delle risorse PC",
        destructive=False,
        usage="/status",
    ))
    REGISTRY.register(CommandDefinition(
        name="help",
        handler=help_command,
        description="Mostra l'elenco dei comandi autorizzati e la loro descrizione",
        destructive=False,
        usage="/help",
    ))

    # Application commands
    REGISTRY.register(CommandDefinition(
        name="firefox",
        handler=launch_firefox,
        description="Avvia il browser Mozilla Firefox (con rilevamento automatico del percorso)",
        destructive=False,
        usage="/firefox",
    ))
    REGISTRY.register(CommandDefinition(
        name="outlook",
        handler=launch_outlook,
        description="Avvia Microsoft Outlook (con rilevamento Click-to-Run / MSI)",
        destructive=False,
        usage="/outlook",
    ))
    REGISTRY.register(CommandDefinition(
        name="note",
        handler=open_notepad_note,
        description="Apre Blocco Note (Notepad) e incolla il testo inviato",
        destructive=False,
        usage="note: <testo della nota>",
        takes_argument=True,
    ))

    # Emergency process command
    REGISTRY.register(CommandDefinition(
        name="panic",
        handler=execute_panic,
        description="Chiude le applicazioni utente (richiede conferma: /panic conferma)",
        destructive=True,
        usage="/panic",
    ))


# Execute registration on package import
register_all_commands()
