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
