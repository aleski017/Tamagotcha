# Tamagotcha!
Tamagotcha is open-source CLI game simulating the portable tamagotchi game popular in the 90s. This version features save states, 4 animation-cycles and 2 playable retro games renditioned on CLI.

## Usage

This project runs in a terminal using a `curses`-based interface.

### Requirements

#### Unix-based systems (Linux / macOS)

O Unix-based systems, `curses` is available by default and no additional packages are required.

```bash
python3 --version
python3 main.py
```
- A terminal window of at least **80×15**
- Keyboard input enabled

> **Windows users:** Python 3.13+ is not supported due to `curses` limitations.

---

Upon running, insert the desired pet's name, may it be already existing or a new one.

---

---

You'll be greeted by your pet, demonstrating a fiery passion towards his owner! On the right a working atomic set of the pet's attributes are shown.

---

---

### Working features are:
-   **Fire**: Plays the spewing-fire animation. Has no functionality;
-   **Sleep**: The pet recovers fatigue and gets less sleepy;
-   **Snake**: A CLI version of the popular Snake game
-   **Space**: A simplified CLI version of the popular Space Invaders game
-   **Kill**: Kills the pet and deletes the save file
-   **Idle**: Returns the pet into the idle animation
-   **Exit/Quit**: Exit the game 

The game is saved after a command's completion
### Games
The user can play two retro games to increase its pets' experience. 

Snake
---

---

Space Invaders
---

---

#### Playing games fatigues the pet. When fatigue reaches 0, the player dies, destroying the save file forever.
---

--- 
