# commands/spaceCommand.py
from .command import Command
from games.space_invaders_game import MiniSpaceInvadersGame


class SpaceCommand(Command):
    def __init__(self):
        super().__init__("space")
        self.description = "Plays space invaders for EXP"

    def execute(self, window, pet):
        anim = MiniSpaceInvadersGame(window)
        anim.start()
        return anim
