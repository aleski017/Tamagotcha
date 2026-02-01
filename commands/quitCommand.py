# commands/quitCommand.py
from .command import Command

class QuitCommand(Command):
    def __init__(self):
        super().__init__("quit")
        self.description = "Saves and quits the game"

    def execute(self, window, pet):
        return self._animate(window)
