# PongWithIssues - Master TODO List

## Task to add and prioritize:

- [ ] **Font rights**: read that font txt file in `pong/FONTS/readme.txt` - think on a new font so i won't be sued
- [ ] **Legal check**: make a complete legal check in the repo to make sure i'm ok. maybe even create an agent that his job is to do this legal test from time to time?
- [ ] **work flow**: lets plan a better way to communicate between us.

---

## Priority 1: Bugs

- [X] **BUG-001**: Fix paddle control in `game-helpers.ts` - both paddles respond to same keys (**FIXED**)
- [X] **BUG-002**: Fix InputHandler key mapping - needs separate left/right paddle keys (**FIXED**)
- [X] **BUG-003**: Fix undefined variable in testing.py (**FIXED**)
- [X] **BUG-004**: Fix class ordering in testing.py (**FIXED**)
- [X] **BUG-005**: Fix NameError in tutorial.py (**FIXED**)
- [X] **BUG-006**: Fix property access in BETA main.py (**FIXED**)
- [X] **BUG-007**: Fix undefined method in object_manage.py (**FIXED**)
- [X] **BUG-008**: Fix broken import in `AI/testing/main.py` - `from pong import Game` fails (**FIXED**: created Game class in `pong/__init__.py`)
- [X] **BUG-009**: Fix broken import in `AI/testing/tutorial.py` - same issue (**FIXED**: same fix)
- [X] **BUG-010**: Fix sandbox crash - wrong `handle_ball_collision` import (3-arg vs 4-arg) (**FIXED**)
- [X] **BUG-011**: Classic mode AI paddle double-dampened — physics friction (0.85x) + manual damping (1.75x) makes AI sluggish (**FIXED**: switched to `mode='classic'` paddles)
- [X] **BUG-012**: Classic mode uses physics-mode paddles but applies conflicting manual damping (`vel /= 1.75`) (**FIXED**: removed manual damping, use classic mode)
- [X] **BUG-013**: Dead `state = MENU` / `state == PLAYING` code in `versions/classic/main.py` — never transitions, dead branches (**FIXED**: removed dead code)
- [X] **BUG-014**: No Y-velocity clamping in classic `handle_ball_collision` (`pong/utilities.py`) — can grow unbounded (**FIXED**: clamped to MAX_DEFLECTION_SPEED)
- [X] **BUG-015**: Inconsistent reset — classic uses `utilities.reset()`, pongception does it manually inline (**FIXED**: pongception now uses `reset()`)

### Web Version Bugs (OBSOLETE — JS/TS web version replaced by Pygbag)

- [X] **BUG-W01 through BUG-W08**: No longer applicable — web version now uses Python via Pygbag (WebAssembly)

---

## Priority 2: Code Cleanup (Technical Debt)

- [X] Delete `pong_BETA/helpers.py` (empty file)
- [X] Delete `testing/pygame_example.py` (unused)
- [X] Remove commented code in `versions/BETA/main.py`
- [X] Remove commented code in `pong/physics_object.py`
- [X] Replace hardcoded values in `collision-detection.ts` and `game-helpers.ts` with constants

---

## Priority 3: Code Consolidation (Refactoring)

- [X] Combine `Ball` and `BallClassic` into single class with mode parameter (Python & TypeScript)
- [X] Combine `Paddle` and `PaddleClassic` into single class with mode parameter (Python & TypeScript)
- [X] Merge `AI/testing/main.py` and `AI/testing/tutorial.py` (90% duplicate) — deleted `tutorial.py`, `main.py` is superset
- [X] Reconcile `pong/physics_object.py` and `pong_BETA/physics_object.py` — merged into single class with gravity/damping/max_speed support
- [X] Create single physics system with configurable features — unified PhysicsObject with both simple update() and symplectic Euler integrate()

---

## Priority 4: Essential Features (COMPLETE)

- [X] Basic pygame window, game loop, paddles, ball, collision, scoring
- [X] Game determination (3 points), start/pause/reset
- [X] Mode selection (Classic, Pongception, BETA, Sandbox)
- [X] Build system (`scripts/build.py`, `scripts/generate_icon.py`)
- [X] Fox logo, version number, credits in menu
- [X] Requirements file, LICENSE (MIT)

---

## Priority 5: Customization Features

- [X] Settings menu (ball size/speed, paddle height/speed, colors, background, win score)
- [X] Side-panel settings with live AI preview (two AI paddles play pong in real-time while adjusting settings)
- [ ] Option to choose key settings or play with mouse
- [ ] Change board shape (circle mode?)
- [ ] Custom background images
- [ ] Upload custom photo for background

---

## Priority 6: Game Modes

### AI Opponent

- [X] Add game mode selection (Play with friend / Play against computer)
- [X] Add basic AI opponent
- [X] AI difficulty levels (10 levels: Beginner to Impossible)

### Special Modes

- [ ] Peaceful mode - no ball, no score, just clouds and peaceful music
- [ ] Crazy mode - smaller ball/paddles, higher velocity (increasing?)
- [ ] Cursed mode - all random features combined

---

## Priority 7: Audio & Visual Polish

### Sound Effects

- [ ] Ball collision sound
- [ ] Point scored sound
- [ ] Game determination sound
- [ ] Background music

### Professional Polish

- [X] Add version numbers (v1.0.0 in menu)
- [X] Add custom project logo/favicon
- [X] Include "Features" list in README (Game Modes table)
- [X] Add "Install & Play" guide in README
- [X] Add tech stack list in README
- [ ] Capture GIF/video demo of gameplay
- [ ] Add screenshots in GitHub README
- [ ] Add "buy me a coffee" button
- [ ] Write CONTRIBUTING.md
- [ ] Create CHANGELOG.md
- [ ] Add GitHub Actions badge
- [ ] Write final polished README.md

---

## Priority 8: Web & Mobile

- [X] Set up GitHub Pages landing page
- [X] Set up HTML webpage to host the game
- [X] Connect game to web page
- [X] Style game page with CSS
- [X] Add GitHub Actions workflow for Pages deployment
- [X] **Replaced JS/TS web version with Pygbag (Python → WebAssembly)** — single codebase for desktop and web
- [ ] Add link for game page in GitHub README
- [X] Phone & Tablet touch controls (TouchHandler in `pong/touch.py`, integrated into all game modes and menus)

### User System

- [ ] Sign in with name and password
- [ ] Score board with registered users

---

## Priority 9: Power-Ups System

### Power-Up Mechanics

- [ ] Catching boxes with random powers
- [ ] Choose power from start option
- [ ] Button to select/activate power
- [ ] Display available powers on screen

### Power-Up Ideas

- [ ] Resize paddles/ball randomly
- [ ] Add extra ball on each hit
- [ ] Unpredictable ball speed changes
- [ ] Paddle disappears for 0.5s
- [ ] Invincibility for 3 seconds
- [ ] Extra life
- [ ] Paralyze opponent for 1 second
- [ ] Nuke for instant win
- [ ] Helper AI joins your side
- [ ] Slow zombie ball attack
- [ ] Over-the-top Dragon Ball / LF2 style powers

---

## Priority 10: Cursed Features (For Fun)

### Easter Eggs

- [ ] Secret key sequence that explodes opponent paddle
- [ ] Famous quotes from random users (PongShit.txt)

### Satirical Micro-transactions

- [ ] Store selling paddle accessories (hats, swords) for overpriced Gems
- [ ] Option to buy coins with Gems (which also cost Gems)
- [ ] "Watch video for free Gems" redirects to random 10H YouTube video
- [ ] Clicking store prints: "There aren't any Gems, go fuck yourself"
- [ ] Free coins if you wait on website for [X] days = [X] coins

---

## Completed Tasks Archive

### Original Features

- [X] Basic pygame window, game loop, paddles, ball, collision, scoring
- [X] Game determination, start/pause/reset, requirements, LICENSE

### Documentation (Session 1)

- [X] Create CLAUDE.md, PROJECT_ANALYSIS.md, progress.md, TODO.md

### Bug Fixes (Sessions 2-4)

- [X] BUG-001 through BUG-007 (all fixed)

### Code Cleanup (Session 2)

- [X] Deleted empty/unused files, removed commented code, fixed hardcoded values

### Code Consolidation (Session 4)

- [X] Unified Ball/BallClassic and Paddle/PaddleClassic (Python & TypeScript)

### Features (Session 4)

- [X] Mode selection grid, Sandbox mode, build system, icons, fox logo, version
- [X] Settings menu with full customization

### Documentation Updates (Session 5)

- [X] Updated README.md, CLAUDE.md, PROJECT_ANALYSIS.md, requirements.txt
- [X] Added version numbers, features list, install guide, tech stack to README

---

### Web Version Enhancements (Session 10)

- [X] Aligned constants with Python (canvas size, paddle, ball, scoring)
- [X] Added 4 game modes to web version (Classic, Physics, BETA, Sandbox)
- [X] Integrated digital-7 font for consistent visual style
- [X] Fixed web version bugs (BUG-W03, BUG-W07, BUG-W08)

### GitHub Pages Deployment (Session 11)

- [X] GitHub Pages deployment in `docs/`
- [X] GitHub Actions workflow for automated deployment
- [X] Web version bug fixes

### Logo & Documentation Updates (Session 11)

- [X] Replaced procedural fox logo with professional SVG-based logo
- [X] Updated all documentation files (TODO.md, progress.md, PRD.md, CLAUDE.md)

### Settings Overhaul (Session 12)

- [X] Side-panel settings with live AI preview (PreviewGame class, compact panel layout)

### Pygbag Migration (Session 13)

- [X] Replaced JS/TS web version with Pygbag (Python → WebAssembly)
- [X] Made all game loops async (`await asyncio.sleep(0)` each frame)
- [X] Created `main.py` Pygbag entry point
- [X] Updated GitHub Actions workflow for Pygbag build + deploy
- [X] Deleted `versions/web-version/` and old `docs/` web files

### One-Click Launcher & Pygbag Fixes (Session 14)

- [X] Created `play.py` — one-click cross-platform launcher (auto-creates venv, installs deps, launches game)
- [X] Created `play.sh` / `play.bat` — double-click wrappers
- [X] Fixed Pygbag black screen: moved module-level `display.set_mode()` into functions, added `import numpy` to main.py, guarded `webbrowser` import, removed `neat-python` from requirements
- [X] AI system improved to 10 difficulty levels (1=Beginner to 10=Impossible) with DIFFICULTY_NAMES

### Touch Controls for Mobile Web (Session 15)

- [X] Created `pong/touch.py` — TouchHandler class + draw_touch_buttons overlay
- [X] Modified `pong/helpers.py` — handle_paddle_movement accepts `touch=` parameter
- [X] Added touch controls to Classic, Pongception, Sandbox game modes
- [X] Added touch navigation to main menu, vs-AI submenu, and settings menu
- [X] Added `get_mode_box_rects()` to `pong/menu.py` for touch hit-testing

---

*Last updated: 2026-02-07 (Session 15)*
