# commands/fire.py
from .command import Command
import curses


class IdleCommand(Command):
    def __init__(self):
        super().__init__("idle")
        self.description = "Go back to idle state"

    def init_colors(self):
        super().init_colors()

        #curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(33, 213 , -1)
        curses.init_pair(30, curses.COLOR_CYAN , -1)
        

        return {
            'U': curses.color_pair(33),
            'o': curses.color_pair(0),
            '+': curses.color_pair(0),
            ',': curses.color_pair(0),
            '`': curses.color_pair(0),
            'O': curses.color_pair(0),
            '#': curses.color_pair(55),
            ']': curses.color_pair(55),
            '~': curses.color_pair(30),
            'default': curses.color_pair(15)
        }
    
    def execute(self, window, pet):
        return self._animate(window, self.init_colors())
