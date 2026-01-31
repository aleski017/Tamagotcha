import curses
import time
from pathlib import Path
from games.game import Game
from tamagotchi import Pet
from utils.game_utils import *
from utils.ui_utils import *
from configs import *

#CHECK -----------
#MODULARITY (packages)
#WINDOWS COMPATIBILITY
#DANDER METHODS
#When resizing, termianl glitches


# ------------------- INPUT HELPERS ------------------- #
def read_key(stdscr, input_win, cmd, current_anim):
    key = stdscr.getch()
    if key == -1:
        try:
            return input_win.get_wch()
        except curses.error:
            return None
    key, cmd = handle_input(key, cmd, current_anim)
    return key


def handle_input(key, cmd, current_anim):
    """Converts curses input into string commands"""
    if isinstance(key, int) and not isinstance(current_anim, Game):
        # Clean Key
        if 32 <= key <= 126:
            key = chr(key)
        elif key in (10, 13):
            key = "\n"
        elif key in (127, 8):
            key = "\x7f"
        elif key == 27:
            key = None
            cmd = ""
        else:
            key = None
    return key, cmd.lower()


# ------------------- RESIZE HANDLER ------------------- #
def handle_resize(stdscr, state):
    curses.endwin()
    stdscr.refresh()
    stdscr.clear()
    import yaml
    BASE_DIR = Path(__file__).resolve().parent
    CONFIG_DIR = BASE_DIR / "configs"
    with open(CONFIG_DIR / "size_config.yaml", "r") as f:
        config = yaml.safe_load(f)



    max_y, max_x = stdscr.getmaxyx()
    if max_y < 15 or max_x < 80:
        stdscr.addstr(0, 0, "Terminal too small! Resize to at least 80x15")
        stdscr.refresh()
        stdscr.getch()
        return

    # Initial window setup (same as resize logic)
    #TOP_MARGIN = 3
    #HISTORY_HEIGHT = 5
    #INPUT_HEIGHT = 1
    #PET_HEIGHT = 20
    #PET_WIDTH = 80

    TOP_MARGIN = config['layout']['top_margin']
    PET_HEIGHT = config['layout']['pet']['height']
    PET_WIDTH = config['layout']['pet']['width']
    HISTORY_HEIGHT = config['layout']['history']['height']
    INPUT_HEIGHT = config['layout']['input']['height']
    status_height = config['layout']['status']['height']
    status_width = config['layout']['status']['width_ratio']
    legend_height = config['layout']['legend']['height']

    pet_y = TOP_MARGIN
    history_y = pet_y + PET_HEIGHT
    status_x = int(max_x // 2 + 20)
    input_y = history_y + HISTORY_HEIGHT

    #status_height = 15
    #status_y = 0

    #legend_height = 10
    #legend_y = status_y + status_height
    #legend_x = status_x

    windows = {
        'pet': curses.newwin(PET_HEIGHT, PET_WIDTH, pet_y, 0),
        'history': curses.newwin(HISTORY_HEIGHT, max_x, history_y, 0),
        'input': curses.newwin(INPUT_HEIGHT, max_x, input_y, 0),
        'status': curses.newwin(status_height, status_width, 0, status_x),
        'legend': curses.newwin(legend_height, status_width, status_height, status_x),
    }

    windows['status'].border('|', '|', '=', '=', '+', '+', '+', '+')
    windows['input'].nodelay(True)
    state.windows = windows
    state.max_y, state.max_x = max_y, max_x
    

    
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
        too_small=False
    )

    history_colors = setup_history_colors()
    history = [''] * 5

    handle_resize(stdscr, state)
    welcome_animation(state)

    #prev_cmd = ""

    while state.running:
        # --- INPUT ---
        handle_input_window(state.windows['input'], state.cmd, state.max_x)
        key = read_key(stdscr, state.windows['input'], state.cmd, state.anim)

        # --- HANDLE RESIZE FIRST ---
        if key == curses.KEY_RESIZE: handle_resize(stdscr, state)

        if handle_sleep(state) or handle_game_input(state, key):
            continue

        if key == "\n":
            if handle_death(state): break
            execute_command(state)
            if state.cmd:
                handle_history(
                    state.cmd,
                    history,
                    state.windows,
                    history_colors,
                    state.max_x
                )
            state.cmd = ""
            
        elif key == "\x7f": # Delete char
            state.cmd = state.cmd[:-1]

        elif isinstance(key, str) and key.isprintable():
            state.cmd += key
    
        # --- RENDER (SAFE) ---
        try:
            display_pet(state.windows["status"], state.pet)
            draw_legend(state.windows["legend"])
            curses.doupdate()
        except curses.error:
            pass

        state.pet.update()
        time.sleep(0.01)

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
