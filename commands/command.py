from abc import ABC, abstractmethod
from animation.animation import Animation
import curses

class Command(ABC):
    def __init__(self, name: str):
        self.name = name
        self.animation = None

    def _animate(self, window, color_pairs = None):
        """Starts the animation based on the command name."""
        if not color_pairs:
            curses.init_pair(11,  curses.COLOR_GREEN, -1)
            color_pairs=  {'default': curses.color_pair(11)}
        self.animation = Animation(self.name, window, color_pairs)
        self.animation.start()
        return self.animation

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        
    @abstractmethod
    def execute(self, window, pet):
        pass


