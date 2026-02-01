import importlib.resources as r
import curses
import time
import threading


class Animation:
    def __init__(self, package: str, window: curses.window, color_pairs = {'default': None}):
        self.name = package
        self.frames = self._load_frames('animations.' + package)
        self.window = window
        self.stop_event = threading.Event()
        self.color_pairs = color_pairs
        

    def _load_frames(self, package: str):
        """
        loads all string-frames from animation directory
        
        :param package: name of animation package
        :type package: str
        """
        pkg = r.files(package)
        return [f.read_text() for f in sorted(pkg.iterdir()) if f.name.endswith(".txt")]
    
    def start(self):
        """
        Starts the thread playing the animation
        """
        animation_thread = threading.Thread(target=self._play_animation, args=())
        animation_thread.daemon = True
        animation_thread.start()
        return self
    
    def stop(self):
        """
        Updates stop event to kill thread
        """
        self.stop_event.set()
    
    def _play_animation(self, frame_delay = 0.2):
        """
        Displays animation line by line

        :param frame_delay: speed of animation playing
        """
        frame_index = 0
        while not self.stop_event.is_set():
            self.window.erase()
            frame_lines = self.frames[frame_index].split('\n')
            win_height, win_width = self.window.getmaxyx()

            for i, line in enumerate(frame_lines):
                if i >= win_height - 1:
                    break

                x = 0
                while x < len(line):
                    #if self.color_pairs and x in self.color_pairs.keys():
                    if line[x] in self.color_pairs.keys():
                        self.window.addstr(i, x, line[x], self.color_pairs[line[x]])
                    else: self.window.addstr(i, x, line[x], self.color_pairs['default'])
                    x += 1

            self.window.noutrefresh()  # Changed from refresh()
            curses.doupdate()  
            frame_index = (frame_index + 1) % len(self.frames)
            time.sleep(frame_delay)
