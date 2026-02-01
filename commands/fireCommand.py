# commands/fireCommand.py
from .command import Command


class FireCommand(Command):
    def __init__(self):
        super().__init__("fire")
        self.description = "Makes you look cool. Useless"

