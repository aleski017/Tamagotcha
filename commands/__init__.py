# commands/__init__.py
#from .feed import feed
#from .play import play
#from sleepCommand import SleepCommand
from .fireCommand import FireCommand
from .snakeCommand import SnakeCommand
from .sleepCommand import SleepCommand
from .idleCommand import IdleCommand
from .spaceCommand import SpaceCommand
from .quitCommand import QuitCommand
from .deadCommand import DeadCommand



COMMANDS = {
    "kill": DeadCommand(),
    "idle": IdleCommand(),
    "sleep": SleepCommand(),
    "snake": SnakeCommand(),
    "space": SpaceCommand(),
    "fire": FireCommand(),
    "quit": QuitCommand()
}
