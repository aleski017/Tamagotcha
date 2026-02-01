from animations import Animation
from configs.config_loader import config
import curses


class Command():
    def __init__(self, name: str):
        self.name = name
        self.description = "" 
        self.animation = None


    def _animate(self, window, color_pairs=None):
        """Starts the animation based on the command name and colors it"""
        if not color_pairs:
            curses.init_pair(11, curses.COLOR_GREEN, -1)
            color_pairs = {'default': curses.color_pair(11)}
        
        self.animation = Animation(self.name, window, color_pairs)
        self.animation.start()
        return self.animation

    def execute(self, window, pet):
        """Execute the command and colors the relative animation"""
        config.init_colors()
        return self._animate(window, config.get_command_colors(self.name))