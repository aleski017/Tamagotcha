# games/game.py
import threading
import time
from abc import abstractmethod
import curses
from enum import Enum

class GameState(Enum):
    PLAYING = 1
    GAME_OVER = 2
    WIN = 3
    PAUSED = 4

class GameLogic:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.reset()
    
    def reset(self):
        self.score = 0
        self.state = GameState.PLAYING
    
    def update(self):
        if self.state != GameState.PLAYING: 
            return


class Game: 
    def __init__(self, window):
        self.window = window
        self.stop_event = threading.Event()
        self.thread = None
        self.game = None
        self.last_update = time.time()
        self.update_interval = 0.05
        self.win_height, self.win_width = self.window.getmaxyx()

    def start(self):  
        """
        Start game thread
        """
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        return self
    
    def stop(self):
        """Kill game thread and return final score"""
        if hasattr(self, 'game') and self.game:
            self.final_score = self.game.score  # Store it here
        
        if self.thread:
            self.stop_event.set()
            self.thread.join(timeout=0.5)
        
        return self.final_score
    
    def _run(self):
        """
        Update game until thread is killed
        """
        while not self.stop_event.is_set():
            current_time = time.time()
            
            if current_time - self.last_update >= self.update_interval:
                self.game.update()
                self.last_update = current_time
            
            self.draw()
            time.sleep(0.05)

    def _convert_wasd_to_arrow(self, key):
        """
        Convert keyboard input into curses commands
        """
        VALID_WASD = {
            ord('w'): curses.KEY_UP, ord('W'): curses.KEY_UP,
            ord('s'): curses.KEY_DOWN, ord('S'): curses.KEY_DOWN,
            ord('a'): curses.KEY_LEFT, ord('A'): curses.KEY_LEFT,
            ord('d'): curses.KEY_RIGHT, ord('D'): curses.KEY_RIGHT
        }
        if key in VALID_WASD:
            key = VALID_WASD[key]
        return key
    
    def handle_game_input(self, key, window, pet):
        """
        Template method for handling all game input.
        Handles common inputs (pause, quit, restart) and delegates
        game-specific inputs to subclasses.
        """
        if not isinstance(key, int):
            return None
        
        # Convert WASD if needed 
        key = self._convert_wasd_to_arrow(key)
        
        if self.handle_key(key):
            return None
        
        # Handle pause toggle
        if key in (ord('p'), ord('P')):
            if hasattr(self.game, 'toggle_pause'):
                self.game.toggle_pause()
            return None
        
        # Handle restart (from game over)
        if key in (ord('r'), ord('R')):
            #if self._can_restart():
            return self.game.reset()
        
        # Handle next level (for games with levels)
        if key in (ord('n'), ord('N')):
            if self._can_advance_level:
                self.game.next_level()
                return None
        
        # Handle quit (ESC or 'q')
        if key in (27, ord('q'), ord('Q')):
            self.stop()
            #anim = Animation('idle', window) 
            return 1
        
        return None
    
    def draw(self):
        if self.game.state == GameState.GAME_OVER:
            self.draw_game_over(self.win_height, self.win_width)
        elif self.game.state == GameState.PAUSED:
            self.draw_paused(self.win_height, self.win_width)
        else:  # PLAYING
            self.draw_gameplay(self.win_height, self.win_width)
        
        self.window.noutrefresh()
    
    def draw_game_over(self, height, width):
        """Draw game over screen"""
        game_over = [
            "+------------------+",
            "|   GAME  OVER     |",
            "+------------------+",
            f"|  Score: {self.game.score:6d}   |",
            "+------------------+",
            "| [R] Restart      |",
            "| [Q] Quit to Menu |",
            "+------------------+"
        ]
        
        start_y = max(1, (height - len(game_over)) // 2)
        for i, line in enumerate(game_over):
            y = start_y + i
            if 0 <= y < height:
                x = max(1, (width - len(line)) // 2)
                attr = curses.A_BOLD if i == 1 else curses.A_NORMAL
                self.window.addstr(y, x, line, attr)

    def draw_paused(self, height, width):
        """Draw paused screen"""
        paused = [
            "+------------------+",
            "|     PAUSED       |",
            "+------------------+",
            f"|  Score: {self.game.score:6d}   |",
            "+------------------+",
            "| [P] Resume       |",
            "| [Q] Quit to Menu |",
            "+------------------+"
        ]
        
        start_y = max(1, (height - len(paused)) // 2)
        for i, line in enumerate(paused):
            y = start_y + i
            if 0 <= y < height:
                x = max(1, (width - len(line)) // 2)
                attr = curses.A_BOLD if i == 1 else curses.A_NORMAL
                self.window.addstr(y, x, line, attr)
    def draw_win_screen(self, height, width):
        """Draw win screen"""
        win_screen = [
            "+------------------+",
            "|    VICTORY!      |",
            "+------------------╣",
            f"|  Score: {self.game.score:6d}   |",
            f"|  Level: {self.game.level:6d}   |",
            "+------------------╣",
            " |   " + self.game.message.center(14) + "|",
            "+------------------╣",
            "| [N] Next Level   |",
            "| [Q] Quit to Menu |",
            "╚------------------╝"
        ]
        
        start_y = max(1, (height - len(win_screen)) // 2)
        for i, line in enumerate(win_screen):
            y = start_y + i
            if 0 <= y < height:
                x = max(1, (width - len(line)) // 2)
                self.window.addstr(y, x, line)
    @abstractmethod
    def update(self):
        """Subclasses must implement game logic updates"""
        pass
    
    @abstractmethod
    def draw(self):
        """Draw game state - subclasses must implement"""
        pass