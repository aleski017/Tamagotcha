import curses
from pathlib import Path
from games.game import Game
import yaml

# ------------------- UI & RENDER HELPERS ------------------- #
def display_pet(win, pet):
    """Displays the pet's status line by line"""
    height, width = win.getmaxyx()
    lines = str(pet).split("\n") 
    for i, line in enumerate(lines):
        y_pos = 1 + i
        x_pos = 2
        if y_pos < height - 1 and x_pos < width - 1:
            max_length = width - x_pos - 1
            safe_line = line[:max_length]
            try:
                win.addstr(y_pos, x_pos, safe_line)
            except curses.error:
                pass
    win.noutrefresh()


# ------------------- RESIZE HANDLER ------------------- #
def handle_resize(stdscr, state):
    curses.endwin()
    stdscr.refresh()
    stdscr.clear()
    BASE_DIR = Path(__file__).resolve().parent.parent
    CONFIG_DIR = BASE_DIR / "configs"
    with open(CONFIG_DIR / "size_config.yaml", "r") as f:
        config = yaml.safe_load(f)


    max_y, max_x = stdscr.getmaxyx()
    if max_y < 15 or max_x < 80:
        stdscr.addstr(0, 0, "Terminal too small! Resize to at least 80x15")
        stdscr.refresh()
        stdscr.getch()
        return

    LAYOUT_PARAMS = config['layout']
    PET_HEIGHT = LAYOUT_PARAMS['pet']['height']
    HISTORY_HEIGHT = LAYOUT_PARAMS['history']['height']
    status_height = LAYOUT_PARAMS['status']['height']
    status_width = LAYOUT_PARAMS['status']['width_ratio']
    

    pet_y = LAYOUT_PARAMS['top_margin']
    history_y = pet_y + PET_HEIGHT
    status_x = int(max_x // 2 + 20)
    input_y = history_y + HISTORY_HEIGHT

    state.windows = {
        'pet': curses.newwin(PET_HEIGHT, LAYOUT_PARAMS['pet']['width'], pet_y, 0),
        'history': curses.newwin(HISTORY_HEIGHT, max_x, history_y, 0),
        'input': curses.newwin(LAYOUT_PARAMS['input']['height'], max_x, input_y, 0),
        'status': curses.newwin(status_height, status_width, 0, status_x),
        'legend': curses.newwin(LAYOUT_PARAMS['legend']['height'], status_width, status_height, status_x),
    }

    state.windows['status'].border('|', '|', '=', '=', '+', '+', '+', '+')
    state.windows['input'].nodelay(True)
    state.max_y, state.max_x = max_y, max_x


def handle_input_window(win, cmd, max_x):
    """Updates the input line with custom cursor"""
    win.erase()
    curses.init_pair(55, curses.COLOR_RED, curses.COLOR_BLACK)
    win.addstr(0, 0, "C:> " + cmd)
    cursor_pos = len("C:> ") + len(cmd)
    win.addstr(0, cursor_pos, "_", curses.color_pair(55))
    win.noutrefresh()


def handle_history(cmd, history, windows, max_x):
    """Updates command history window"""
    
    history_colors = setup_history_colors()
    history.append(cmd)
    windows['history'].erase()
    for i, h in enumerate(history[-5:]):
        if i < 5:
            windows['history'].addstr(i, 0, h[:max_x - 1], history_colors[i])
    windows['history'].noutrefresh()


def setup_history_colors():
    """Sets up color pairs for history and display"""
    curses.start_color()
    shades = [curses.COLORS - 20, curses.COLORS - 15,
              curses.COLORS - 10, curses.COLORS - 5, curses.COLORS - 1]
    for i, fg in enumerate(shades, start=1):
        curses.init_pair(i, fg, curses.COLOR_BLACK)
    return {i - 1: curses.color_pair(i) for i in range(1, 6)}


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