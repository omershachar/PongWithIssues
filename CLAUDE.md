# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PongWithIssues is a multi-platform Pong game with a **single Python codebase** (~2,900 lines):
- **Desktop**: Python + Pygame (native)
- **Web**: Same Python code compiled to WebAssembly via [Pygbag](https://github.com/pygame-web/pygbag)
- **Version**: v1.0.0
- **Dependencies**: `pygame==2.6.1`, `numpy`

## Commands

### Desktop (Python)
```bash
# One-click launcher (auto-installs deps, creates venv)
python3 play.py          # Linux/WSL
python play.py           # Windows

# Or manual setup
pip install -r requirements.txt
python3 launcher.py      # Linux/WSL
python launcher.py       # Windows

# Run specific modes directly
python versions/classic/main.py
python versions/pongception/main.py
python versions/BETA/main.py
python versions/sandbox/main.py
```

### Web Version (Pygbag)
```bash
pip install pygbag
python -m pygbag .              # Dev server at localhost:8000
python -m pygbag --build .      # Build for deployment (output in build/web/)
```

### Import Smoke Test
```bash
python3 -c "
from pong.constants import *
from pong.physics_object import PhysicsObject
from pong.ball import Ball
from pong.paddle import Paddle
from pong.helpers import handle_ball_collision
from pong.settings import GameSettings
from pong_BETA.object_manage import Box
print('All imports OK')
"
```

## Architecture

### Full Project Tree
```
PongWithIssues/
├── launcher.py              # Main menu UI + mode launcher (192 lines)
├── main.py                  # Pygbag web entry point (22 lines)
├── play.py                  # One-click cross-platform launcher
├── play.sh / play.bat       # Double-click wrappers (macOS-Linux / Windows)
├── favicon.png              # Web icon for Pygbag
├── requirements.txt         # pygame, numpy
│
├── pong/                    # Shared core library (~1,750 lines)
│   ├── __init__.py          # Game class (AI training interface)
│   ├── constants.py         # All game config: dimensions, physics, colors, fonts
│   ├── physics_object.py    # Base class: mass, velocity, acceleration, F=ma
│   ├── ball.py              # Ball: collision physics, trail, spin, Magnus effect
│   ├── paddle.py            # Paddle: acceleration-based movement, friction
│   ├── helpers.py           # Collision detection, paddle movement logic
│   ├── utilities.py         # Rendering functions, classic collision handler
│   ├── ai.py                # AI opponent: 10 difficulty levels, spin-aware
│   ├── menu.py              # Main menu UI: 4-mode selection grid
│   ├── settings.py          # GameSettings + SettingsMenu with live AI preview
│   ├── touch.py             # Touch input handler for mobile/web
│   └── FONTS/               # digital-7.ttf, LiberationMono-Bold.ttf
│
├── pong_BETA/               # Experimental physics module
│   └── object_manage.py     # Box objects with forces/impulses for BETA mode
│
├── versions/                # Game mode implementations (~570 lines)
│   ├── classic/main.py      # Standard Pong (137 lines)
│   ├── pongception/main.py  # Physics mode: spin, momentum, recoil (148 lines)
│   ├── BETA/main.py         # Experimental physics sandbox (120 lines)
│   └── sandbox/main.py      # Debug mode: overlay, hit counter (165 lines)
│
├── scripts/
│   ├── build.py             # PyInstaller build system
│   └── generate_icon.py     # Programmatic icon generation
│
├── assets/                  # Game icons & logo
│   ├── icon.png             # 256x256 game icon
│   ├── icon_32x32.png       # Taskbar icon
│   ├── icon.ico             # Windows icon
│   ├── omer_logo_128x128.png
│   └── omer_logo_256x256.png
│
├── CLAUDE.md                # This file
├── PRD.md                   # Product Requirements Document
├── TODO.md                  # Master task list (prioritized)
├── progress.md              # Session-by-session progress tracker
└── README.md                # User documentation
```

### Key Design Patterns

1. **Physics inheritance**: `PhysicsObject` base class provides Newtonian mechanics (F=ma, impulse-based collisions). `Ball` and `Paddle` extend this.

2. **Configuration centralized**: All tuneable values (sizes, speeds, physics constants) live in `pong/constants.py`. Edit this file to adjust game behavior.

3. **Game modes as modules**: Each mode has its own `main.py` that imports from the shared `pong/` library. The launcher imports and calls these.

4. **Async game loops**: All game `main()` functions are `async` with `await asyncio.sleep(0)` each frame. This is **required** for Pygbag (WebAssembly) and is a no-op on desktop.

5. **Settings persistence**: `GameSettings` object is passed between launcher and game modes. Settings apply immediately via a live AI preview in the settings menu.

## Game Modes

| Mode | File | Description | AI Support |
|------|------|-------------|------------|
| **Classic** | `versions/classic/main.py` | Standard Pong with velocity-based physics | Yes (vs Friend / vs AI) |
| **Pongception** | `versions/pongception/main.py` | Spin (Magnus effect), paddle recoil, momentum transfer, fire trail | Yes (vs Friend / vs AI) |
| **BETA** | `versions/BETA/main.py` | Experimental physics sandbox with force/impulse controls | No (keyboard only) |
| **Sandbox** | `versions/sandbox/main.py` | Debug overlay (toggle `D`), ball bounces all walls, hit counter | No |

### Game Flow
```
play.py/launcher.py → Main Menu (4 modes) → [S] Settings
                                           → Select Mode → Sub-menu (vs Friend / vs AI) → Gameplay → Back to Menu
```

## Key Constants (pong/constants.py)

| Constant | Value | Notes |
|----------|-------|-------|
| Window | 800x800 px | Square arena |
| FPS | 60 | Async loop |
| Paddle | 15x85 px | max velocity 9, default 4.5 |
| Ball | 7px radius | default velocity (6, 0) |
| Win condition | 3 points | Configurable in settings |
| SPIN_FACTOR | 0.5 | Magnus effect strength |
| MAX_DEFLECTION_SPEED | 7 | Y-velocity cap on collision |

## AI System (pong/ai.py)

10 difficulty levels (Beginner → Impossible) with parameters:
- `reaction_distance`: How early AI reacts (0.25–1.0 screen width)
- `prediction_skill`: Blend current Y vs predicted arrival Y (0.0–1.0)
- `spin_awareness`: Spin factored into prediction (0.0–1.0)
- `dead_zone_factor`: Lazy zone around paddle center (0.50–0.03)
- `noise`: Random imprecision (70px → 0px)
- `return_speed`: Return-to-center aggressiveness (0.30–1.0)

Main function: `ai_move_paddle(paddle, ball, difficulty)` — uses acceleration-based movement with `_predict_ball_y()` for trajectory simulation including wall bounces and Magnus effect.

## Controls

| Action | Keyboard | Touch (Web) |
|--------|----------|-------------|
| Left paddle up/down | W / S | Left half of screen |
| Right paddle up/down | UP / DOWN | Right half of screen |
| Menu navigation | LEFT / RIGHT arrows | Tap mode boxes |
| Settings | S (from menu) | — |
| Debug overlay (Sandbox) | D | — |
| Back to menu | ESC | Top-left MENU button |

## Feature Approval Policy

**IMPORTANT**: A feature is NOT considered finished until the user explicitly approves it. After implementing a feature:
1. Inform the user what was implemented
2. Wait for user to test and approve
3. Only mark as complete in TODO.md after user approval
4. Do not proceed to the next priority until current features are approved

## Workflow: After Each Priority Phase

1. **Run the import smoke test** (see Commands section above)
2. **If tests fail**: Fix issues before proceeding
3. **If tests pass**: Commit and push changes
   ```bash
   git add -A
   git commit -m "Complete Priority X: [description]"
   git push origin main
   ```
4. **Update documentation**:
   - Mark completed items in `TODO.md` (move to "Completed Tasks Archive")
   - Add session log to `progress.md`

## Progress Tracking

**IMPORTANT**: After completing any task or mission, update `progress.md` with:
1. Date and session number
2. Tasks completed (with checkmarks)
3. Any bugs found or fixed
4. Files created/modified/deleted
5. Notes about issues encountered
6. Next steps

Also update `TODO.md` when:
- Completing tasks (move to "Completed Tasks Archive")
- Discovering new bugs (add to Priority 1)
- Identifying new features or improvements

## Project Documentation

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Guidance for Claude Code (this file) |
| `PRD.md` | Product Requirements Document — vision, features, milestones |
| `progress.md` | Session-by-session progress tracker (16 sessions) |
| `TODO.md` | Master task list (prioritized, 10 levels) |

## Project Status (as of 2026-02-10)

| Priority | Status |
|----------|--------|
| P1: Critical bugs (15 bugs) | **COMPLETE** |
| P2: Code cleanup | **COMPLETE** |
| P3: Code consolidation | **COMPLETE** (Ball/Paddle merged, PhysicsObject unified, AI merged) |
| P4: Essential features | **COMPLETE** (modes, build system, branding) |
| P5: Customization | **MOSTLY COMPLETE** (settings menu done, mouse controls remaining) |
| P6: AI opponent | **COMPLETE** (10 difficulty levels, spin-aware prediction) |
| P7: Audio & visual polish | PENDING (sounds, music, screenshots) |
| P8: Web & mobile | **MOSTLY COMPLETE** (Pygbag deployed, touch controls done, README link remaining) |
| P9: Power-ups | PLANNED |
| P10: Cursed/easter eggs | PLANNED |

### Development Stats
- **16 sessions** of development tracked in `progress.md`
- **15 bugs** found and fixed (BUG-001 through BUG-015 + web bugs)
- **~2,900 lines** of Python across the codebase
- **31 files** cleaned up in Session 16 (6.7 MB freed)
