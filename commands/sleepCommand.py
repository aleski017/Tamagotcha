# commands/sleepCommand.py
from .command import Command
from configs.config_loader import config

class SleepCommand(Command):
    def __init__(self):
        super().__init__("sleep")
        self.description = "Sleeps to recover fatigue"

    def execute(self, window, pet):
        pet.rest()
        return self._animate(window, config.get_command_colors(self.name))
    
    