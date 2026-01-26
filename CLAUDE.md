# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PongWithIssues is a multi-platform Pong game with two implementations:
- **Desktop**: Python + Pygame
- **Web**: TypeScript + HTML5 Canvas (PWA-enabled)

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

### Web Version
```bash
cd versions/web-version

npm run build    # Compile TypeScript
npm run dev      # Watch mode for development
npm run serve    # Start local server on port 8000
npm run start    # Build and serve
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
└── menu.py              # Main menu UI

versions/                # Game mode implementations
├── classic/main.py      # Standard Pong
├── pongception/main.py  # Physics-enhanced mode (spin, momentum, recoil)
└── BETA/main.py         # Experimental features
```

### Web Structure
```
versions/web-version/
├── src/
│   ├── index.ts         # Entry point
│   ├── game/            # TypeScript game logic (mirrors Python structure)
│   └── utils/           # Input handling, collision detection
├── dist/                # Compiled output
└── index.html           # Web app entry
```

### Key Design Patterns

1. **Physics inheritance**: `PhysicsObject` base class provides Newtonian mechanics (F=ma, impulse-based collisions). `Ball` and `Paddle` extend this.

2. **Configuration centralized**: All tuneable values (sizes, speeds, physics constants) live in `pong/constants.py`. Edit this file to adjust game behavior.

3. **Game modes as modules**: Each mode has its own `main.py` that imports from the shared `pong/` library. The launcher imports and calls these.

4. **Web mirrors desktop**: TypeScript classes in `src/game/` follow the same architecture as Python classes in `pong/`.

## Game Modes

- **Classic**: Basic Pong with standard collision physics
- **Pongception**: Advanced physics with spin (Magnus effect), paddle recoil, and momentum transfer
- **BETA**: Testing ground for new features

## Key Constants (pong/constants.py)

- Window: 800x800 pixels, 60 FPS
- Paddle: 15x85 pixels, max velocity 9
- Ball: 7px radius, default velocity (6, 0)
- Win condition: 3 points
- Physics: SPIN_FACTOR=0.5, MAX_DEFLECTION_SPEED=7

## Workflow: After Each Priority Phase

**IMPORTANT**: After completing each priority phase from TODO.md:

1. **Run Tests**
   ```bash
   # Python tests
   python3 -c "
   from pong.constants import *
   from pong.physics_object import PhysicsObject
   from pong.ball import Ball, BallClassic
   from pong.paddle import Paddle, PaddleClassic
   from pong.helpers import handle_ball_collision
   from pong_BETA.physics_object import PhysicsObject as BetaPhysics
   print('All imports OK')
   "

   # TypeScript check (in web-version/)
   cd versions/web-version && npx tsc --noEmit
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
| `docs/PROJECT_ANALYSIS.md` | Full codebase analysis with all methods |
| `docs/TODO.txt` | Original TODO (legacy, see TODO.md) |

## Known Issues

All Priority 1 critical bugs have been **FIXED** (BUG-001 through BUG-007).

See `TODO.md` for remaining work:
- Priority 2: Minor code cleanup (partially complete)
- Priority 3: Code consolidation/refactoring
- Priority 4+: Feature development
