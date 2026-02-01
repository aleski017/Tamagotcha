#!/usr/bin/env python3
import curses
from tamagotchi import Pet
from configs import *
from utils import TerminalState, handle_resize, run_game_loop, get_pet_name

# ------------------- MAIN GAME LOOP ------------------- #
def main(stdscr, pet):
    curses.curs_set(0)
    stdscr.nodelay(True)
    
    state = TerminalState(
        pet=pet,
        anim=None,
        cmd="",
        windows={},
        running=True,
        history = [''] * 5,
        too_small=False
    )

    handle_resize(stdscr, state)
    state = run_game_loop(state, stdscr)

    # ------ CLEANUP ------- #
    if state.anim:
        state.anim.stop()
    if state.pet.alive:
        state.pet._save_state()


# ------------------- RUN ------------------- #
if __name__ == "__main__":
    pet = Pet(get_pet_name())
    try:
        curses.wrapper(main, pet)
    except KeyboardInterrupt:
        print("\nGoodbye! Your pet has been saved.")
