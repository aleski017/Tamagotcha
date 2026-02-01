import json
import curses
from pathlib import Path

class ConfigLoader:
    """Loads and manages configuration from JSON files."""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self._layout = None
        self._colors = None
        self._colors_initialized = False
    
    @property
    def layout(self):
        """Load layout configuration."""
        if self._layout is None:
            with open(self.config_dir / 'layout.json', 'r') as f:
                self._layout = json.load(f)
        return self._layout
    
    @property
    def colors(self):
        """Load color configuration."""
        if self._colors is None:
            with open(self.config_dir / 'colors.json', 'r') as f:
                self._colors = json.load(f)
        return self._colors
    
    def init_colors(self):
        """Initialize all curses color pairs."""
        if self._colors_initialized:
            return
        
        curses.start_color()
        curses.use_default_colors()
        
        # Initialize each color pair from config
        for pair_id, (fg, bg) in self.colors['color_pairs'].items():
            # Handle special color names
            if fg == "COLORS_MINUS_10":
                fg_color = curses.COLORS - 10
            elif isinstance(fg, str):
                fg_color = getattr(curses, f'COLOR_{fg}')
            else:
                fg_color = fg
            
            curses.init_pair(int(pair_id), fg_color, bg)
        
        self._colors_initialized = True
    
    def get_command_colors(self, command_name):
        """Get color mapping for a specific command.
        
        Args:
            command_name: Name of the command (e.g., 'fire', 'idle')
            
        Returns:
            Dictionary mapping characters to curses color_pair objects
        """
        if command_name not in self.colors['commands']:
            # Default color if command not found
            return {'default': curses.color_pair(11)}
        
        # Convert pair IDs to curses color_pair objects
        color_map = {}
        for char, pair_id in self.colors['commands'][command_name].items():
            color_map[char] = curses.color_pair(pair_id)
        
        return color_map

# Global instance for configuration
config = ConfigLoader()