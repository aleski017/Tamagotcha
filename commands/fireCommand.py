# commands/fire.py
from .command import Command
import curses



class FireCommand(Command):
    def __init__(self):
        super().__init__("fire")
        self.description = "Pet shoots fire"

    def init_colors(self):
        super().init_colors()

        #curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(55, curses.COLOR_RED, -1)
        curses.init_pair(44, curses.COLOR_YELLOW, -1)
        curses.init_pair(22,  curses.COLORS - 10, -1)
        curses.init_pair(15,  curses.COLOR_GREEN, -1)

        return {
            '(': curses.color_pair(55),
            ')': curses.color_pair(44),
            '§': curses.color_pair(22),
            '@': curses.color_pair(0),
            'default': curses.color_pair(15),
        }
    
    def execute(self, window, pet):
        return self._animate(window, self.init_colors())
