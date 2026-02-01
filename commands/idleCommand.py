# commands/idleCommand.py
from .command import Command
import curses


class IdleCommand(Command):
    def __init__(self):
        super().__init__("idle")
        self.description = "Go back to idle state"
