# ------------------- GAME STATE ------------------- #
import time
from dataclasses import dataclass
from typing import Any
from pathlib import Path
from tamagotchi import Pet
from commands import execute_command, COMMANDS
from games.game import Game
from utils.ui_utils import *

# Change this to update the game's difficulty! 
SLEEP_THRESHOLD = 20 
GAME_SLEEPY_INCREASE = 5
GAME_FATIGUE_INCREASE = 5

@dataclass
class TerminalState:
    pet: Pet
    anim: Any
    cmd: str
    windows: dict
    too_small: bool
    history: list
    running: bool = True

# ------------------- STATE HANDLERS ------------------- #
def handle_death(state: TerminalState):
    """Checks if pet is dead and triggers death animation"""
    if state.pet.death_condition or state.cmd == "kill":
        state.pet.alive = False
        state.anim = execute_command("kill", state)
        time.sleep(2)
        state.running = False
        return True
    return False

def handle_sleep(state: TerminalState):
    """Triggers sleep animation if pet is too sleepy"""
    if state.pet.sleepy >= SLEEP_THRESHOLD and not state.pet.resting:
        state.pet.rest()
        state.cmd = 'sleep'
        return True
    return False

def handle_game_input(state: TerminalState, key):
    """Separates sub-gameplay input with command execution"""
    if isinstance(state.anim, Game):
        result = state.anim.handle_game_input(key, state.windows["pet"], state.pet)
        if result:
            state.pet.experience += state.anim.stop() 
            state.pet.sleepy += GAME_SLEEPY_INCREASE
            state.pet.fatigue += GAME_FATIGUE_INCREASE
            state.anim = execute_command("idle", state)
            return True
    return False

def handle_command(state: TerminalState):
    """Executes a valid command"""
    if state.cmd in COMMANDS:
        state.anim = execute_command(state.cmd, state)
        if COMMANDS[state.cmd].name in ["quit", "kill"]:
            state.running = False


def draw_legend(win: curses.window):
    """Displays available commands"""
    win.erase()
    win.border('|', '|', '=', '=', '+', '+', '+', '+')
    win.addstr(0, 2, " COMMANDS AVAILABLE: ")
    for i, cmd in enumerate(COMMANDS.keys(), start=1):
        if i < win.getmaxyx()[0] - 1:
            win.addstr(i, 2, f"- {cmd}: {COMMANDS[cmd].description}")
    win.noutrefresh()

def run_game_loop(state: TerminalState, stdscr):
    """
    Main game loop. Handles input, terminal updates and refreshes
    """
    on_startup_animation(state)
    while state.running:
        # --- INPUT ---
        handle_input_window(state.windows['input'], state.cmd, state.max_x)
        key = read_key(stdscr, state.windows['input'], state.cmd, state.anim)

        # --- HANDLE RESIZE FIRST ---
        if key == curses.KEY_RESIZE: handle_resize(stdscr, state)

        if  handle_game_input(state, key):
            continue

        if key == "\n" or handle_sleep(state):
            if handle_death(state): break
            handle_command(state)
            if state.cmd:
                handle_history(
                    state.cmd,
                    state.history,
                    state.windows,
                    state.max_x
                )
            state.cmd = ""
            
        elif key == "\x7f": # Delete char
            state.cmd = state.cmd[:-1]

        elif isinstance(key, str) and key.isprintable():
            state.cmd += key.lower()
    
        # --- RENDER (SAFE) ---
        try:
            display_pet(state.windows["status"], state.pet)
            draw_legend(state.windows["legend"])
            curses.doupdate()
        except curses.error:
            pass

        state.pet.update()
        time.sleep(0.01)
    return state

def on_startup_animation(state: TerminalState):
    """Executes welcome animation and back to idle"""
    state.anim = execute_command("fire", state)
    time.sleep(3)
    state.anim.stop()
    state.anim = execute_command("idle", state)


# ------------------- PET SELECTION ------------------- #
def get_pet_name():
    """
    Prompts user to name instance of pet
    """
    print("=" * 40)
    print("Welcome to Tamagotchi!")
    print("=" * 40)
    print("Your pets | \n          V   ")
    # ------------------- PATH SETUP ------------------- #
    BASE_DIR = Path(__file__).resolve().parent.parent
    SAVE_DIR = BASE_DIR / "saves"
    SAVE_DIR.mkdir(exist_ok=True)

    # Prints instantiated pets
    if SAVE_DIR.exists() and any(SAVE_DIR.glob("save_*.json")):
        for f in SAVE_DIR.glob("save_*.json"):
            print(f.stem.replace("save_", ""))
    else: print("You have None!")

    while True:
        try:
            name = input(
                "Which pet are you choosing? Entering a new name means creating a new pet! "
            ).strip()
            if name and len(name) < 5:
                return name[:1].upper() + name[1:].lower()
            print("Please enter a valid name for your pet! [_ _ _ _]")
        except (EOFError, KeyboardInterrupt):
            print("\nToo bad!")
            exit(0)
