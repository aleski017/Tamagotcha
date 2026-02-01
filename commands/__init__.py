# commands/__init__.py
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

def execute_command(name, state, window = 'pet'):
    if state.anim:
        state.anim.stop()
    state.pet.awake()
    return COMMANDS[name].execute(state.windows[window], state.pet)
