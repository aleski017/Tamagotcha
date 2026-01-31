# ------------------- GAME STATE ------------------- #
import time
from dataclasses import dataclass
from typing import Any
from pathlib import Path
from tamagotchi import Pet
from commands import COMMANDS
from games.game import Game

@dataclass
class TerminalState:
    pet: Pet
    anim: Any
    cmd: str
    windows: dict
    too_small: bool
    running: bool = True


# ------------------- STATE HANDLERS ------------------- #
def handle_death(state: TerminalState):
    """Checks if pet is dead and triggers death animation"""
    if state.pet.death_condition or state.cmd == "kill":
        state.anim.stop()
        state.pet.alive = False
        state.anim = COMMANDS["kill"].execute(state.windows["pet"], state.pet)
        time.sleep(2)
        state.running = False
        return True
    return False

def handle_sleep(state: TerminalState):
    """Triggers sleep animation if pet is too sleepy"""
    if state.pet.sleepy >= 20:
        state.anim.stop()
        state.pet.awake()
        state.anim = COMMANDS["sleep"].execute(state.windows["pet"], state.pet)
        return True
    return False

def handle_game_input(state, key):
    if isinstance(state.anim, Game):
        result = state.anim.handle_game_input(key, state.windows["pet"], state.pet)
        if result:
            state.pet.experience += state.anim.stop() 
            state.pet.sleepy += 5
            state.pet.fatigue += 5
            state.anim = COMMANDS['idle'].execute(state.windows["pet"], state.pet)
            return True
    return False

def execute_command(state: TerminalState):
    """Executes a valid command"""
    if state.cmd in COMMANDS:
        state.anim.stop()
        state.pet.awake()
        state.anim = COMMANDS[state.cmd].execute(state.windows["pet"], state.pet)
        if COMMANDS[state.cmd].name in ["quit", "kill"]:
            state.running = False

def welcome_animation(state: TerminalState):
    """Executes welcome animation and back to idle"""
    state.anim = COMMANDS["fire"].execute(state.windows["pet"], state.pet)
    time.sleep(3)
    state.anim.stop()
    state.anim = COMMANDS["idle"].execute(state.windows["pet"], state.pet)

def draw_legend(win):
    """Displays available commands"""
    win.erase()
    win.border('|', '|', '=', '=', '+', '+', '+', '+')
    win.addstr(0, 2, " COMMANDS AVAILABLE: ")
    for i, cmd in enumerate(COMMANDS.keys(), start=1):
        if i < win.getmaxyx()[0] - 1:
            win.addstr(i, 2, f"- {cmd}: {COMMANDS[cmd].description}")
    win.noutrefresh()



# ------------------- PET SELECTION ------------------- #
def get_pet_name():
    print("=" * 40)
    print("Welcome to Tamagotchi!")
    print("=" * 40)
    print("Your pets | \n          V   ")
    # ------------------- PATH SETUP ------------------- #
    BASE_DIR = Path(__file__).resolve().parent.parent
    SAVE_DIR = BASE_DIR / "saves"
    SAVE_DIR.mkdir(exist_ok=True)

    if SAVE_DIR.exists():
        for f in SAVE_DIR.glob("save_*.json"):
            print(f.stem.replace("save_", ""))

    while True:
        try:
            name = input(
                "Which pet are you choosing? Entering a new name means creating a new pet! "
            ).strip()
            if name:
                return name[:1].upper() + name[1:].lower()
            print("Please enter a name for your pet!")
        except (EOFError, KeyboardInterrupt):
            print("\nToo bad!")
            exit(0)
