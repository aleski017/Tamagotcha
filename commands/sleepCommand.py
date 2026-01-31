# commands/snake.py
from .command import Command
import curses

class SleepCommand(Command):
    def __init__(self):
        super().__init__("sleep")
        self.description = "Sleeps to recover fatigue"

    def init_colors(self):
        super().init_colors()

        curses.init_pair(30, curses.COLOR_CYAN, -1)
        
        return {
            'default': curses.color_pair(30),
        }

    def execute(self, window, pet):
        pet.rest()
        return self._animate(window, self.init_colors())
    
    