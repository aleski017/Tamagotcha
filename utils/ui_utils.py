import curses

# ------------------- UI & RENDER HELPERS ------------------- #
def display_pet(win, pet):
    """Displays the pet's animation line by line"""
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


def handle_input_window(win, cmd, max_x):
    """Updates the input line with custom cursor"""
    win.erase()
    curses.init_pair(55, curses.COLOR_RED, curses.COLOR_BLACK)
    win.addstr(0, 0, "C:> " + cmd)
    cursor_pos = len("C:> ") + len(cmd)
    #if cursor_pos < max_x - 1:
    win.addstr(0, cursor_pos, "_", curses.color_pair(55))
    win.noutrefresh()


def handle_history(cmd, history, windows, history_colors, max_x):
    """Updates command history window"""
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