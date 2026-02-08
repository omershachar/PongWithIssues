# PongWithIssues

```
    ██████╗   ██████╗  ███╗   ██╗  ██████╗   ██╗
    ██╔══██╗ ██╔═══██╗ ████╗  ██║ ██╔════╝   ██║
    ██████╔╝ ██║   ██║ ██╔██╗ ██║ ██║  ███╗  ██║
    ██╔═══╝  ██║   ██║ ██║╚██╗██║ ██║   ██║  ╚═╝
    ██║      ╚██████╔╝ ██║ ╚████║ ╚██████╔╝  ██╗
    ╚═╝       ╚═════╝  ╚═╝  ╚═══╝  ╚═════╝   ╚═╝

Barely functional Pong made by a barely functional dev.

   A project that probably works. Sometimes. Maybe.
                  It compiles. That's enough.
```

> **PongWithIssues** is a game of Pong that you can play Pong in it.
[Click here for further explanations](https://en.wikipedia.org/wiki/Pong)

## Play in Your Browser

**[Play PongWithIssues Online](https://omershachar.github.io/PongWithIssues/)** — no install required. Works on desktop and mobile.

---

## Install & Play (Desktop)

**One command — everything is automatic:**

```bash
git clone https://github.com/omershachar/PongWithIssues.git
cd PongWithIssues
python3 play.py
```

That's it. `play.py` creates a virtual environment, installs dependencies, and launches the game.

**Or double-click:**
- **Linux / macOS:** `play.sh`
- **Windows:** `play.bat`

> Requires Python 3.10+

---

## Game Modes

| Mode | Description |
|------|-------------|
| **Classic** | Original Pong experience — clean, fast, competitive |
| **Pongception** | Physics mode with spin, momentum transfer, fire trails, and paddle recoil |
| **BETA** | Experimental physics sandbox with interactive force/impulse controls |
| **Sandbox** | Debug mode — ball position, velocity, spin overlay, hit counter, no scoring |

All modes support **vs Friend** (local 2-player) and **vs AI** (10 difficulty levels).

---

## AI Opponent

10 difficulty levels from **Beginner** to **Impossible**, with spin-aware trajectory prediction. Adjust in the settings menu.

| Level | Name |
|-------|------|
| 1 | Beginner |
| 2 | Easy |
| 3 | Casual |
| 4 | Normal |
| 5 | Intermediate |
| 6 | Challenging |
| 7 | Hard |
| 8 | Expert |
| 9 | Master |
| 10 | Impossible |

---

## Controls

### Keyboard

| Action              | Key         |
|---------------------|-------------|
| Left Paddle Up      | `W`         |
| Left Paddle Down    | `S`         |
| Right Paddle Up     | `UP`        |
| Right Paddle Down   | `DOWN`      |
| Pause/Resume        | `SPACE`     |
| Restart Game        | `R`         |
| Back to Menu        | `M` / `ESC` |
| Settings Menu       | `S` (menu)  |
| Toggle Instructions | `H`         |
| Toggle Debug (Sandbox) | `D`      |

### Touch (Mobile Web)

| Action | Gesture |
|--------|---------|
| Move Left Paddle | Touch left half of screen |
| Move Right Paddle | Touch right half of screen |
| Pause | Tap top-right corner |
| Back to Menu | Tap top-left corner |
| Select Mode | Tap on mode box |
| Start Game | Tap selected mode again or tap start area |

In vs AI mode, the entire screen controls your paddle.

---

## Settings Menu

Access from the main menu with `S`. Features a **live AI preview** — two AI paddles play pong in real-time while you adjust settings.

Customize:
- Ball size and speed
- Paddle height and speed
- Left/right paddle colors (8 options)
- Background color (6 dark themes)
- Winning score (1-21)
- AI difficulty (1-10)

---

## Building an Executable

```bash
python scripts/build.py            # Standard build
python scripts/build.py --onefile  # Single .exe file
```

Requires [PyInstaller](https://pyinstaller.org/).

---

## Built With

- Python 3.10+
- [Pygame](https://www.pygame.org/)
- [Pygbag](https://github.com/pygame-web/pygbag) (Python → WebAssembly for browser play)
- NumPy

---

## Disclaimer

- I have no idea what I'm doing.
- If this crashes your PC, it's your fault for trusting anything named `PongWithIssues`.
- For any serious fatal problems please contact our team for further support [here](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

---

## WSL / Windows 11 Users

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

## License

> Under the [MIT License](LICENSE)
