import curses
import random
from collections import deque
from enum import Enum
from animation.animation import Animation
from .game import Game, GameState, GameLogic

class Snake(GameLogic):
    def __init__(self, height=15, width=30):
        super().__init__(height, width)
    
    def reset(self):
        super().reset()
        self.snake = deque([(self.height//2, self.width//4)])
        self.direction = curses.KEY_RIGHT
        self.food = None
        self.place_food()
    
    def place_food(self):
        while True:
            y = random.randint(1, self.height-4)
            x = random.randint(1, self.width-4)
            if (y, x) not in self.snake:
                self.food = (y, x)
                break
    
    def update(self):
        head_y, head_x = self.snake[0]

        # Calculate new head position
        if self.direction == curses.KEY_UP:
            new_head = (head_y - 1, head_x)
        elif self.direction == curses.KEY_DOWN:
            new_head = (head_y + 1, head_x)
        elif self.direction == curses.KEY_LEFT:
            new_head = (head_y, head_x - 1)
        elif self.direction == curses.KEY_RIGHT:
            new_head = (head_y, head_x + 1)

        # --- PAC-MAN STYLE WRAPPING ---
        y, x = new_head
        if y <= 0:
            y = self.height - 2
        elif y >= self.height - 1:
            y = 1

        if x <= 0:
            x = self.width - 2
        elif x >= self.width - 1:
            x = 1

        new_head = (y, x)

        # Check collision with self ONLY
        if new_head in self.snake:
            self.state = GameState.GAME_OVER
            return

        # Move snake
        self.snake.appendleft(new_head)

        if new_head == self.food:
            self.score += 10
            self.place_food()
        else:
            self.snake.pop()

    
    def toggle_pause(self):
        """Toggle between PLAYING and PAUSED"""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    
class SnakeGame(Game):
    def __init__(self, window):
        super().__init__(window)        
        win_height, win_width = self.window.getmaxyx()
        self.game = Snake(win_height-2, win_width-2)
        self._can_advance_level = False
        
    def draw(self):
        self.window.erase()
        win_height, win_width = self.window.getmaxyx()
        
        self.window.box()
        
        if self.game.state == GameState.GAME_OVER:
            self.draw_game_over(win_height, win_width)
        elif self.game.state == GameState.PAUSED:
            self.draw_paused(win_height, win_width)
        else:  # PLAYING
            self.draw_gameplay(win_height, win_width)
        
        self.window.noutrefresh()
    
    def draw_gameplay(self, height, width):
        """Draw active gameplay"""
        # Draw snake
        for y, x in self.game.snake:
            if 1 <= y < height-1 and 1 <= x < width-1:
                self.window.addch(y, x, '█')
        
        # Draw food
        if self.game.food:
            fy, fx = self.game.food
            if 1 <= fy < height-1 and 1 <= fx < width-1:
                self.window.addch(fy, fx, '●')
        
        # Draw score
        score_text = f"Score: {self.game.score}"
        self.window.addstr(0, 2, score_text)
        
        # Draw controls at the bottom
        controls_text = "WASD: Move | P: Pause | Q: Quit"
        self.window.addstr(height-1, (width - len(controls_text))//2, 
                          controls_text)
    
    def handle_key(self, key):
        """Handle keyboard input"""
        if self.game.state != GameState.PLAYING:
            return False
        
        key = self._convert_wasd_to_arrow(key)
        
        # Now handle arrow keys
        if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            # Prevent reversing into self
            opposite_directions = {
                curses.KEY_UP: curses.KEY_DOWN,
                curses.KEY_DOWN: curses.KEY_UP,
                curses.KEY_LEFT: curses.KEY_RIGHT,
                curses.KEY_RIGHT: curses.KEY_LEFT
            }
            if key != opposite_directions.get(self.game.direction, None):
                self.game.direction = key
                return True
        return False
