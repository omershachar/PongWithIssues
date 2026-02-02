# PongWithIssues

            _____     _____    _   _    ____     _
           |  __ \   / ___ \  | \ | |  / ___|   | |
           | |__| | | /   \ | |  \| | | |  _    | |
           |  ___/  | \___/ | | |\  | | |_| |   |_|
           |_|       \_____/  |_| \_|  \____|   (_)

    Barely functional Pong made by a barely functional dev.

       A project that probably works. Sometimes. Maybe.
                      It compiles. That's enough.
---

> **PongWithIssues** is a game of Pong that you can play Pong in it.
[Click here for further explanations](https://en.wikipedia.org/wiki/Pong)

## Requirements

- Python 3.10 or higher (3.11, 3.12, 3.13 all supported)
- pygame==2.6.1
- numpy

---

### How to Play

1. Clone the repo

   ```bash
   git clone https://github.com/omershachar/PongWithIssues.git
   ```

2. Install dependencies

   ```bash
   pip install -r ./PongWithIssues/requirements.txt
   ```

3. Run it

   ```bash
   python3 ./PongWithIssues/launcher.py   # Linux/WSL
   python ./PongWithIssues/launcher.py    # Windows
   ```

> Or download the `.exe` version from the [Releases](https://www.google.com/search?q=Not+yet+...) tab (coming soon).

---

### Game Modes

| Mode | Description |
|------|-------------|
| **Classic** | Original Pong experience |
| **Pongception** | Physics mode with spin, momentum transfer, and paddle recoil |
| **BETA** | Experimental physics sandbox with interactive controls |
| **Sandbox** | Debug mode with overlay - ball position, velocity, spin, hit counter |

---

### Controls

| Action              | Key         |
|---------------------|-------------|
| Left Paddle Up      | `W`         |
| Left Paddle Down    | `S`         |
| Right Paddle Up     | `UP`        |
| Right Paddle Down   | `DOWN`      |
| Open Menu           | `M`         |
| Pause/Resume        | `SPACE`     |
| Restart Game        | `R`         |
| Toggle Instructions | `H`         |
| Settings Menu       | `S` (menu)  |
| Toggle Debug (Sandbox) | `D`      |
| Exit Game           | `ESC`       |

---

### Settings Menu

Access from the main menu with `S`. Customize:
- Ball size and speed
- Paddle height and speed
- Left/right paddle colors (8 options)
- Background color (6 dark themes)
- Winning score (1-21)

---

### Web Version

Coming soon (maybe) via GitHub Pages — for now this is [good enough](https://www.google.com/search?q=Play+Pong+free)

---

### Building an Executable

```bash
python scripts/build.py            # Standard build
python scripts/build.py --onefile  # Single .exe file
```

Requires [PyInstaller](https://pyinstaller.org/).

---

### Built With

- Python 3.10+ (3.10, 3.11, 3.12 and 3.13 all work)
- [Pygame](https://www.pygame.org/)
- TypeScript + HTML5 Canvas (web version)
- Windows Subsystem for Linux (WSL2/WSLg) or native Windows
- VS Code

---

### Disclaimer

- I have no idea what I'm doing.
- If this crashes your PC, it's your fault for trusting anything named `PongWithIssues`.
- For any serious fatal problems please contact our team for further support [here](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

---

### WSL / Windows 11 Users

- **Windows 11 (WSL2):**
You do NOT need an X server (VcXsrv/Xming).
Just make sure your system is up-to-date and fully RESTART Windows if the game window doesn't appear.

- **Windows 10 (WSL2/WSL1):**
You MUST install and run an X server (like VcXsrv) on Windows for any game window to appear.

- If you're using WSL and the window won't show up:

  - Fully restart Windows.

  - Try again in a fresh terminal.

  - Still stuck? Check your Windows version and WSLg setup.

---

### License

> Under the [MIT License](LICENSE)
