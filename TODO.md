# PongWithIssues - Master TODO List

## Priority 1: Bugs

- [x] **BUG-001**: Fix paddle control in `game-helpers.ts` - both paddles respond to same keys (**FIXED**)
- [x] **BUG-002**: Fix InputHandler key mapping - needs separate left/right paddle keys (**FIXED**)
- [x] **BUG-003**: Fix undefined variable in testing.py (**FIXED**)
- [x] **BUG-004**: Fix class ordering in testing.py (**FIXED**)
- [x] **BUG-005**: Fix NameError in tutorial.py (**FIXED**)
- [x] **BUG-006**: Fix property access in BETA main.py (**FIXED**)
- [x] **BUG-007**: Fix undefined method in object_manage.py (**FIXED**)
- [x] **BUG-008**: Fix broken import in `AI/testing/main.py` - `from pong import Game` fails (**FIXED**: created Game class in `pong/__init__.py`)
- [x] **BUG-009**: Fix broken import in `AI/testing/tutorial.py` - same issue (**FIXED**: same fix)
- [x] **BUG-010**: Fix sandbox crash - wrong `handle_ball_collision` import (3-arg vs 4-arg) (**FIXED**)
- [x] **BUG-011**: Classic mode AI paddle double-dampened — physics friction (0.85x) + manual damping (1.75x) makes AI sluggish (**FIXED**: switched to `mode='classic'` paddles)
- [x] **BUG-012**: Classic mode uses physics-mode paddles but applies conflicting manual damping (`vel /= 1.75`) (**FIXED**: removed manual damping, use classic mode)
- [x] **BUG-013**: Dead `state = MENU` / `state == PLAYING` code in `versions/classic/main.py` — never transitions, dead branches (**FIXED**: removed dead code)
- [x] **BUG-014**: No Y-velocity clamping in classic `handle_ball_collision` (`pong/utilities.py`) — can grow unbounded (**FIXED**: clamped to MAX_DEFLECTION_SPEED)
- [x] **BUG-015**: Inconsistent reset — classic uses `utilities.reset()`, pongception does it manually inline (**FIXED**: pongception now uses `reset()`)

### Web Version Bugs
- [ ] **BUG-W01**: TypeScript build output (`dist/`) never loaded — `index.html` loads `pong-game.js` instead
- [ ] **BUG-W02**: Missing PWA icons — `manifest.json` references `icons/icon-192.png` and `icons/icon-512.png` that don't exist
- [x] **BUG-W03**: Canvas size mismatch — TS uses 800x800, standalone JS uses 800x600 (**FIXED**: JS now uses 800x800)
- [ ] **BUG-W04**: TS input handler has no key debouncing — pause/restart toggle rapidly when held
- [ ] **BUG-W05**: TS game loop uses flawed frame rate limiting — no fixed timestep accumulator
- [ ] **BUG-W06**: TS version never sets canvas width/height — defaults to 300x150
- [x] **BUG-W07**: Winning score mismatch — TS/Python use 3, standalone JS uses 5 (**FIXED**: JS now uses 3)
- [x] **BUG-W08**: Constants mismatch — standalone JS has different paddle vel (5 vs 4.5), ball radius (8 vs 7) (**FIXED**: all constants aligned)

---

## Priority 2: Code Cleanup (Technical Debt)

- [x] Delete `pong_BETA/helpers.py` (empty file)
- [x] Delete `testing/pygame_example.py` (unused)
- [x] Remove commented code in `versions/BETA/main.py`
- [x] Remove commented code in `pong/physics_object.py`
- [x] Replace hardcoded values in `collision-detection.ts` and `game-helpers.ts` with constants

---

## Priority 3: Code Consolidation (Refactoring)

- [x] Combine `Ball` and `BallClassic` into single class with mode parameter (Python & TypeScript)
- [x] Combine `Paddle` and `PaddleClassic` into single class with mode parameter (Python & TypeScript)
- [x] Merge `AI/testing/main.py` and `AI/testing/tutorial.py` (90% duplicate) — deleted `tutorial.py`, `main.py` is superset
- [x] Reconcile `pong/physics_object.py` and `pong_BETA/physics_object.py` — merged into single class with gravity/damping/max_speed support
- [x] Create single physics system with configurable features — unified PhysicsObject with both simple update() and symplectic Euler integrate()

---

## Priority 4: Essential Features (COMPLETE)

- [x] Basic pygame window, game loop, paddles, ball, collision, scoring
- [x] Game determination (3 points), start/pause/reset
- [x] Mode selection (Classic, Pongception, BETA, Sandbox)
- [x] Build system (`scripts/build.py`, `scripts/generate_icon.py`)
- [x] Fox logo, version number, credits in menu
- [x] Requirements file, LICENSE (MIT)

---

## Priority 5: Customization Features

- [x] Settings menu (ball size/speed, paddle height/speed, colors, background, win score)
- [x] Side-panel settings with live AI preview (two AI paddles play pong in real-time while adjusting settings)
- [ ] Option to choose key settings or play with mouse
- [ ] Change board shape (circle mode?)
- [ ] Custom background images
- [ ] Upload custom photo for background

---

## Priority 6: Game Modes

### AI Opponent
- [x] Add game mode selection (Play with friend / Play against computer)
- [x] Add basic AI opponent
- [ ] AI difficulty levels

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
- [x] Add version numbers (v1.0.0 in menu)
- [x] Add custom project logo/favicon
- [x] Include "Features" list in README (Game Modes table)
- [x] Add "Install & Play" guide in README
- [x] Add tech stack list in README
- [ ] Capture GIF/video demo of gameplay
- [ ] Add screenshots in GitHub README
- [ ] Add "buy me a coffee" button
- [ ] Write CONTRIBUTING.md
- [ ] Create CHANGELOG.md
- [ ] Add GitHub Actions badge
- [ ] Write final polished README.md

---

## Priority 8: Web & Mobile

- [x] Set up GitHub Pages landing page (deployed in `docs/`)
- [x] Set up HTML webpage to host the game
- [x] Connect game to web page
- [x] Style game page with CSS
- [x] Add GitHub Actions workflow for Pages deployment
- [ ] Add link for game page in GitHub README
- [ ] Phone & Tablet touch controls

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
- [x] Basic pygame window, game loop, paddles, ball, collision, scoring
- [x] Game determination, start/pause/reset, requirements, LICENSE

### Documentation (Session 1)
- [x] Create CLAUDE.md, PROJECT_ANALYSIS.md, progress.md, TODO.md

### Bug Fixes (Sessions 2-4)
- [x] BUG-001 through BUG-007 (all fixed)

### Code Cleanup (Session 2)
- [x] Deleted empty/unused files, removed commented code, fixed hardcoded values

### Code Consolidation (Session 4)
- [x] Unified Ball/BallClassic and Paddle/PaddleClassic (Python & TypeScript)

### Features (Session 4)
- [x] Mode selection grid, Sandbox mode, build system, icons, fox logo, version
- [x] Settings menu with full customization

### Documentation Updates (Session 5)
- [x] Updated README.md, CLAUDE.md, PROJECT_ANALYSIS.md, requirements.txt
- [x] Added version numbers, features list, install guide, tech stack to README

---

### Web Version Enhancements (Session 10)
- [x] Aligned constants with Python (canvas size, paddle, ball, scoring)
- [x] Added 4 game modes to web version (Classic, Physics, BETA, Sandbox)
- [x] Integrated digital-7 font for consistent visual style
- [x] Fixed web version bugs (BUG-W03, BUG-W07, BUG-W08)

### GitHub Pages Deployment (Session 11)
- [x] GitHub Pages deployment in `docs/`
- [x] GitHub Actions workflow for automated deployment
- [x] Web version bug fixes

### Logo & Documentation Updates (Session 11)
- [x] Replaced procedural fox logo with professional SVG-based logo
- [x] Updated all documentation files (TODO.md, progress.md, PRD.md, CLAUDE.md)

### Settings Overhaul (Session 12)
- [x] Side-panel settings with live AI preview (PreviewGame class, compact panel layout)

---

*Last updated: 2026-02-07 (Session 12)*
