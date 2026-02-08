# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PongWithIssues is a multi-platform Pong game with a **single Python codebase**:
- **Desktop**: Python + Pygame (native)
- **Web**: Same Python code compiled to WebAssembly via [Pygbag](https://github.com/pygame-web/pygbag)

## Commands

### Desktop (Python)
```bash
# Install dependencies
pip install -r requirements.txt

# Run the game launcher (menu to select game modes)
python3 launcher.py      # Linux/WSL
python launcher.py       # Windows

# Run specific modes directly
python versions/classic/main.py
python versions/pongception/main.py
python versions/BETA/main.py
```

### Web Version (Pygbag)
```bash
# Install Pygbag
pip install pygbag

# Run locally (opens browser at localhost:8000)
python -m pygbag .

# Build for deployment (output in build/web/)
python -m pygbag --build .
```

## Architecture

### Desktop Structure
```
pong/                    # Shared core library
├── constants.py         # Game config: dimensions, physics, colors, fonts
├── physics_object.py    # Base class with mass, velocity, acceleration
├── ball.py              # Ball with collision physics and trail effects
├── paddle.py            # Paddle with acceleration-based movement
├── helpers.py           # Collision detection, paddle movement logic
├── utilities.py         # Rendering functions, game state helpers
├── menu.py              # Main menu UI with mode selection grid
├── settings.py          # GameSettings and SettingsMenu classes
├── ai.py                # AI opponent with 10 difficulty levels
└── touch.py             # Touch input handler for mobile/web

versions/                # Game mode implementations
├── classic/main.py      # Standard Pong
├── pongception/main.py  # Physics-enhanced mode (spin, momentum, recoil)
├── BETA/main.py         # Experimental features
└── sandbox/main.py      # Debug mode with overlay
```

### Web Deployment (Pygbag)
```
main.py              # Pygbag entry point (async wrapper around launcher)
favicon.png          # Required by Pygbag for web build
build/web/           # Pygbag output (auto-generated, gitignored)
.github/workflows/deploy.yml  # CI: builds with Pygbag, deploys to GitHub Pages
```

### Key Design Patterns

1. **Physics inheritance**: `PhysicsObject` base class provides Newtonian mechanics (F=ma, impulse-based collisions). `Ball` and `Paddle` extend this.

2. **Configuration centralized**: All tuneable values (sizes, speeds, physics constants) live in `pong/constants.py`. Edit this file to adjust game behavior.

3. **Game modes as modules**: Each mode has its own `main.py` that imports from the shared `pong/` library. The launcher imports and calls these.

4. **Async game loops**: All game `main()` functions are `async` with `await asyncio.sleep(0)` each frame. This is required for Pygbag (WebAssembly) and is a no-op on desktop.

## Game Modes

- **Classic**: Basic Pong with standard collision physics
- **Pongception**: Advanced physics with spin (Magnus effect), paddle recoil, and momentum transfer
- **BETA**: Testing ground for new features
- **Sandbox**: Debug mode with overlay (ball stats, hit counter, no scoring)

## Key Constants (pong/constants.py)

- Window: 800x800 pixels, 60 FPS
- Paddle: 15x85 pixels, max velocity 9
- Ball: 7px radius, default velocity (6, 0)
- Win condition: 3 points
- Physics: SPIN_FACTOR=0.5, MAX_DEFLECTION_SPEED=7

## Feature Approval Policy

**IMPORTANT**: A feature is NOT considered finished until the user explicitly approves it. After implementing a feature:
1. Inform the user what was implemented
2. Wait for user to test and approve
3. Only mark as complete in TODO.md after user approval
4. Do not proceed to the next priority until current features are approved

## Workflow: After Each Priority Phase

**IMPORTANT**: After completing each priority phase from TODO.md:

1. **Run Tests**
   ```bash
   # Python tests
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

2. **If tests fail**: Go back and fix the issues before proceeding

3. **If tests pass**: Commit and push changes
   ```bash
   git add -A
   git commit -m "Complete Priority X: [description]"
   git push origin main
   ```

4. **Update documentation**:
   - Mark completed items in `TODO.md`
   - Add session log to `progress.md`

## Progress Tracking

**IMPORTANT**: After completing any task or mission, update `progress.md` with:
1. Date and session number
2. Tasks completed (with checkmarks)
3. Any bugs found or fixed (update the bug table)
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
| `PRD.md` | Product Requirements Document - vision, features, milestones |
| `progress.md` | Session-by-session progress tracker |
| `TODO.md` | Master task list (prioritized) |

## Known Issues

All Priority 1 critical bugs have been **FIXED** (BUG-001 through BUG-015, plus web BUG-W03/W07/W08).

See `TODO.md` for remaining work:
- Priority 2: Code cleanup (complete)
- Priority 3: Code consolidation (complete - Ball/Paddle merged, PhysicsObject unified, AI files merged)
- Priority 4: Essential features (complete - modes, build system, branding)
- Priority 5: Customization (partially complete - settings menu done, mouse controls remaining)
- Priority 6: AI opponent (complete - 10 difficulty levels, spin-aware prediction)
- Priority 7: Audio & visual polish (pending)
- Priority 8: Web & mobile (Pygbag deployment complete, touch controls implemented, README link remaining)
