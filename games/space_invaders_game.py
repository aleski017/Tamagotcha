import curses
import time
import random
from enum import Enum
from .game import Game, GameState, GameLogic
from animation.animation import Animation


    
class MiniSpaceInvaders(GameLogic):
    def __init__(self, height=20, width=40):
        super().__init__(height, width)
    
    def reset(self):
        super().reset()
        # Player (spaceship)
        self.player_x = self.width // 2
        self.player_y = self.height - 3
        self.lives = 3
        self.shield = 100
        
        # Bullets
        self.bullets = []
        self.bullet_speed = 2
        self.last_shot_time = 0
        self.shot_cooldown = 0.3
        
        # Enemies
        self.enemies = []
        self.enemy_direction = 1
        self.enemy_speed = 0.8
        self.last_enemy_move = time.time()
        self.enemy_bullets = []
        self.enemy_shoot_chance = 0.02
        
        # Create enemy grid with different types
        enemy_types = ['◉', '◈', '◆']  # Different enemy symbols
        for row in range(4):
            for col in range(8):
                enemy_type = min(row, 2)  # Different types based on row
                self.enemies.append({
                    'x': 3 + col * 4,
                    'y': 2 + row * 2,
                    'alive': True,
                    'type': enemy_type,
                    'symbol': enemy_types[enemy_type],
                    'points': (3 - enemy_type) # More points for harder enemies
                })
        
        # Game state
        #self.score = 0
        self.level = 1
        #self.state = GameState.PLAYING
        self.message = ""
        self.message_time = 0
        
        # Bunkers (defense)
        self.bunkers = []
        self.create_bunkers()
    
    def create_bunkers(self):
        """Create protective bunkers for player"""
        for i in range(3):
            center_x = self.width // 4 * (i + 1)
            for y_offset in range(3):
                for x_offset in range(5):
                    if (y_offset == 2 or 
                        (y_offset == 1 and x_offset in [1, 2, 3]) or
                        (y_offset == 0 and x_offset == 2)):
                        self.bunkers.append({
                            'x': center_x - 2 + x_offset,
                            'y': self.height - 8 + y_offset,
                            'health': 3
                        })
    
    def update(self):
        super().update()
        current_time = time.time()
        
        # Move player bullets
        bullets_to_remove = []
        for i, (y, x) in enumerate(self.bullets):
            # Check if bullet hit bunker
            for bunker in self.bunkers[:]:
                if bunker['x'] == x and bunker['y'] == y:
                    bunker['health'] -= 1
                    if bunker['health'] <= 0:
                        self.bunkers.remove(bunker)
                    bullets_to_remove.append(i)
                    break
            else:  # No bunker hit
                new_y = y - self.bullet_speed
                if new_y > 0:
                    self.bullets[i] = (new_y, x)
                else:
                    bullets_to_remove.append(i)
        
        # Remove bullets that hit or left screen
        for idx in sorted(bullets_to_remove, reverse=True):
            if idx < len(self.bullets):
                self.bullets.pop(idx)
        
        # Move enemies periodically
        if current_time - self.last_enemy_move >= self.enemy_speed:
            self.last_enemy_move = current_time
            
            # Check if enemies hit side
            change_direction = False
            for enemy in self.enemies:
                if enemy['alive']:
                    if (enemy['x'] <= 1 and self.enemy_direction == -1) or \
                       (enemy['x'] >= self.width - 2 and self.enemy_direction == 1):
                        change_direction = True
                        break
            
            if change_direction:
                self.enemy_direction *= -1
                for enemy in self.enemies:
                    if enemy['alive']:
                        enemy['y'] += 1
                        # Check if enemies reached bottom
                        if enemy['y'] >= self.player_y - 2:
                            self.state = GameState.GAME_OVER
                            self.message = "Invaders reached Earth!"
                            return
            else:
                for enemy in self.enemies:
                    if enemy['alive']:
                        enemy['x'] += self.enemy_direction
        
        # Enemy shooting
        alive_enemies = [e for e in self.enemies if e['alive']]
        if alive_enemies and random.random() < self.enemy_shoot_chance:
            shooter = random.choice(alive_enemies)
            self.enemy_bullets.append((shooter['y'] + 1, shooter['x']))
        
        # Move enemy bullets
        enemy_bullets_to_remove = []
        for i, (y, x) in enumerate(self.enemy_bullets):
            # Check if hit bunker
            for bunker in self.bunkers[:]:
                if bunker['x'] == x and bunker['y'] == y:
                    bunker['health'] -= 1
                    if bunker['health'] <= 0:
                        self.bunkers.remove(bunker)
                    enemy_bullets_to_remove.append(i)
                    break
            else:
                new_y = y + 1
                if new_y < self.height:
                    self.enemy_bullets[i] = (new_y, x)
                else:
                    enemy_bullets_to_remove.append(i)
        
        # Remove enemy bullets
        for idx in sorted(enemy_bullets_to_remove, reverse=True):
            if idx < len(self.enemy_bullets):
                self.enemy_bullets.pop(idx)
        
        # Check bullet collisions
        self.check_collisions()
        
        # Check win condition
        if not any(e['alive'] for e in self.enemies):
            self.state = GameState.WIN
            self.message = f"Level {self.level} Complete!"
            self.score += 100 * self.level
            self.show_message("LEVEL COMPLETE!")
    
    def check_collisions(self):
        """Check all collisions between objects"""
        # Player bullets hitting enemies
        bullets_to_remove = []
        for bullet_idx, (by, bx) in enumerate(self.bullets):
            for enemy in self.enemies:
                if (enemy['alive'] and 
                    abs(enemy['x'] - bx) <= 1 and 
                    abs(enemy['y'] - by) <= 1):
                    
                    enemy['alive'] = False
                    bullets_to_remove.append(bullet_idx)
                    self.score += enemy['points']
                    self.show_message(f"+{enemy['points']} pts!")
                    break
        
        # Remove bullets that hit enemies
        for idx in sorted(bullets_to_remove, reverse=True):
            if idx < len(self.bullets):
                self.bullets.pop(idx)
        
        # Enemy bullets hitting player
        for bullet in self.enemy_bullets[:]:
            if (abs(bullet[1] - self.player_x) <= 2 and 
                abs(bullet[0] - self.player_y) <= 1):
                
                self.enemy_bullets.remove(bullet)
                self.shield -= 25
                if self.shield <= 0:
                    self.lives -= 1
                    self.shield = 100
                    self.show_message("SHIP HIT!")
                
                if self.lives <= 0:
                    self.state = GameState.GAME_OVER
                    self.message = "Game Over!"
    
    def shoot(self):
        """Player shoots a bullet"""
        current_time = time.time()
        if (current_time - self.last_shot_time >= self.shot_cooldown and
            len([b for b in self.bullets if b[0] > 0]) < 3):
            
            self.bullets.append((self.player_y - 1, self.player_x))
            self.last_shot_time = current_time
            return True
        return False
    
    def move_player(self, direction):
        """Move player left or right"""
        new_x = self.player_x + direction
        if 2 <= new_x < self.width - 2:
            self.player_x = new_x
    
    def show_message(self, msg):
        """Display temporary message"""
        self.message = msg
        self.message_time = time.time()
    
    def next_level(self):
        """Advance to next level"""
        self.level += 1
        self.enemy_speed = max(0.3, self.enemy_speed * 0.9)
        self.enemy_shoot_chance = min(0.08, self.enemy_shoot_chance * 1.3)
        self.reset_gameplay()
        self.show_message(f"LEVEL {self.level}")
    
    def reset_gameplay(self):
        """Reset gameplay elements for new level"""
        self.enemies = []
        enemy_types = ['◉', '◈', '◆']
        for row in range(4 + min(self.level - 1, 2)):  # More rows each level
            for col in range(8 + min(self.level - 1, 2)):  # More columns
                enemy_type = min(row, 2)
                self.enemies.append({
                    'x': 2 + col * 3,
                    'y': 2 + row * 2,
                    'alive': True,
                    'type': enemy_type,
                    'symbol': enemy_types[enemy_type],
                    'points': (3 - enemy_type) * self.level
                })
        
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.player_x = self.width // 2
        self.shield = 100
        self.state = GameState.PLAYING

class MiniSpaceInvadersGame(Game):
    def __init__(self, window):
        super().__init__(window)
        self.game = MiniSpaceInvaders(self.win_height-2, self.win_width-2)
        self.player_frames = ['▲', '△']  # Animation frames for player
        self.player_frame_idx = 0
        self.last_frame_change = time.time()
        self._can_advance_level = True
    
    def _run(self):
        """Main game loop thread"""
        while not self.stop_event.is_set():
            current_time = time.time()
            
            # Animate player
            if current_time - self.last_frame_change >= 0.2:
                self.player_frame_idx = (self.player_frame_idx + 1) % len(self.player_frames)
                self.last_frame_change = current_time
            
            # Update game
            if current_time - self.last_update >= self.update_interval:
                self.game.update()
                self.last_update = current_time
            
            self.draw()
            time.sleep(0.05)
    
    def draw(self):
        """Draw the game state with Mini graphics"""
        self.window.erase()
        
        self.window.border(
            curses.ACS_VLINE,
            curses.ACS_VLINE,
            curses.ACS_HLINE,
            curses.ACS_HLINE,
            curses.ACS_ULCORNER,
            curses.ACS_URCORNER,
            curses.ACS_LLCORNER,
            curses.ACS_LRCORNER
        )

        # Draw title
        title = " SPACE INVADERS "
        title_x = max(1, (self.win_width - len(title)) // 2)
        self.window.addstr(0, title_x, title, curses.A_BOLD)
        
        if self.game.state == GameState.GAME_OVER:
            self.draw_game_over(self.win_height, self.win_width)
        elif self.game.state == GameState.WIN:
            self.draw_win_screen(self.win_height, self.win_width)
        else:
            self.draw_gameplay(self.win_height, self.win_width)
        
        self.window.noutrefresh()
    
    def draw_gameplay(self, height, width):
        """Draw gameplay elements"""
        # Draw HUD at top
        hud = f"Score: {self.game.score:06d} │ Level: {self.game.level} │ Lives: {'♥' * self.game.lives} │ Shield: {self.game.shield}%"
        self.window.addstr(1, 2, hud[:width-4])
        
        # Draw enemies
        for enemy in self.game.enemies:
            if enemy['alive']:
                y, x = enemy['y'], enemy['x']
                if 2 <= y < height-1 and 2 <= x < width-1:
                    self.window.addch(y, x, enemy['symbol'])
        
        # Draw player with animation
        player_char = self.player_frames[self.player_frame_idx]
        y, x = self.game.player_y, self.game.player_x
        if 2 <= y < height-1 and 2 <= x < width-1:
            self.window.addch(y, x, player_char)
            # Draw wings
            if 2 <= x-1 < width-1:
                self.window.addch(y, x-1, '<')
            if 2 <= x+1 < width-1:
                self.window.addch(y, x+1, '>')
        
        # Draw player bullets (lasers)
        for y, x in self.game.bullets:
            if 2 <= y < height-1 and 2 <= x < width-1:
                self.window.addch(y, x, '│', curses.A_BOLD)
        
        # Draw enemy bullets
        for y, x in self.game.enemy_bullets:
            if 2 <= y < height-1 and 2 <= x < width-1:
                self.window.addch(y, x, '•')
        
        # Draw bunkers
        for bunker in self.game.bunkers:
            y, x = bunker['y'], bunker['x']
            if 2 <= y < height-1 and 2 <= x < width-1:
                char = '█' if bunker['health'] == 3 else '▓' if bunker['health'] == 2 else '▒'
                self.window.addch(y, x, char)
        
        # Draw temporary message
        if time.time() - self.game.message_time < 1.5:
            msg = self.game.message
            if msg:
                msg_x = max(2, (width - len(msg)) // 2)
                self.window.addstr(height-3, msg_x, msg, curses.A_BOLD)
        
        # Draw controls at bottom
        controls = "←A/→D: Move │ Space: Shoot │ P: Pause │ Q: Quit"
        self.window.addstr(height-2, max(2, (width - len(controls)) // 2), controls)
    

    def handle_key(self, key):
        """Handle keyboard input"""
        key = self._convert_wasd_to_arrow(key)
        if self.game.state != GameState.PLAYING:
            return False
        
        # Movement
        if key in [curses.KEY_LEFT]:
            self.game.move_player(-1)
            return True
        elif key in [curses.KEY_RIGHT]:
            self.game.move_player(1)
            return True
        elif key in [ord(' '), ord('k'), ord('K')]:  # Shoot
            if self.game.shoot():
                return True
        
        return False
    
