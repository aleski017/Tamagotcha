# commands/snakeCommand.py
from .command import Command
from games.snake_game import SnakeGame

class SnakeCommand(Command):
    def __init__(self):
        super().__init__("snake")
        self.description = "Plays snake to gain EXP"

    def execute(self, window, pet):
        anim = SnakeGame(window)
        anim.start()
        return anim
