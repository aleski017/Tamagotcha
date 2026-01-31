# commands/fire.py
from .command import Command
import os
import curses


class DeadCommand(Command):
    def __init__(self):
        super().__init__("dead")
        self.description = "Save state is deleted"

    def init_colors(self):
        super().init_colors()
        curses.init_pair(10, curses.COLOR_MAGENTA, -1)
        
        return {
            'default': curses.color_pair(10),
        }
    
    def execute(self, window, pet):
        os.remove(pet.save_path)
        pet.delete_save()

        return self._animate(window, self.init_colors())
