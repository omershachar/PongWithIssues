# PongWithIssues - Master TODO List

```
██████╗   ██████╗  ███╗   ██╗  ██████╗   ██╗
██╔══██╗ ██╔═══██╗ ████╗  ██║ ██╔════╝   ██║
██████╔╝ ██║   ██║ ██╔██╗ ██║ ██║  ███╗  ██║
██╔═══╝  ██║   ██║ ██║╚██╗██║ ██║   ██║  ╚═╝
██║      ╚██████╔╝ ██║ ╚████║ ╚██████╔╝  ██╗
╚═╝       ╚═════╝  ╚═╝  ╚═══╝  ╚═════╝   ╚═╝
```

---

## Priority 1: Critical Bugs (Blocking Functionality)

### TypeScript Web Version
- [x] **BUG-001**: Fix paddle control in `game-helpers.ts` - both paddles respond to same keys
  - File: `versions/web-version/src/utils/game-helpers.ts:14-50`
  - **FIXED**: Left paddle uses `leftUp`/`leftDown`, right uses `rightUp`/`rightDown`
- [x] **BUG-002**: Fix InputHandler key mapping - needs separate left/right paddle keys
  - File: `versions/web-version/src/utils/input-handler.ts:20-34`
  - **FIXED**: Added separate keys, W/S for left, Arrow keys for right

### Python Testing Module
- [x] **BUG-003**: Fix undefined variable in testing.py
  - File: `testing/testing.py:75`
  - **FIXED**: Changed to `draw_ASCII_art(WIN)`
- [x] **BUG-004**: Fix class ordering in testing.py
  - File: `testing/testing.py:31`
  - **FIXED**: Moved `BallTesting` class before `main()`, removed duplicate

### Python AI Module
- [x] **BUG-005**: Fix NameError in tutorial.py
  - File: `AI/testing/tutorial.py:82`
  - **FIXED**: Changed to `self.game.loop()`, `self.game.draw()`

### Python BETA Module
- [x] **BUG-006**: Fix property access in BETA main.py
  - File: `versions/BETA/main.py:109`
  - **FIXED**: Added `max_speed` property, changed to `box.max_speed`
- [x] **BUG-007**: Fix undefined method in object_manage.py
  - File: `pong_BETA/object_manage.py:137`
  - **FIXED**: Removed broken call, added TODO comment

---

## Priority 2: Code Cleanup (Technical Debt)

### Delete Redundant Files
- [x] Delete `pong_BETA/helpers.py` (empty file, no functions)
- [x] Delete `testing/pygame_example.py` (unused example)

### Remove Duplicate Code
- [x] Remove `handle_ball_collision()` from `pong/utilities.py` (NOT a duplicate - classic vs physics mode, keeping both)
- [x] Remove commented code block in `versions/BETA/main.py:121-193`
- [x] Remove commented code block in `pong/physics_object.py:132-153`

### Fix Hardcoded Values
- [x] Replace hardcoded `800` with `WIDTH` constant in `collision-detection.ts` (already uses HEIGHT from constants)
- [x] Replace hardcoded values in `game-helpers.ts` with constants

---

## Priority 3: Code Consolidation (Refactoring)

### Merge Similar Classes
- [x] Combine `Ball` and `BallClassic` into single class with mode parameter (Python & TypeScript)
- [x] Combine `Paddle` and `PaddleClassic` into single class with mode parameter (Python & TypeScript)
- [ ] Merge `AI/testing/main.py` and `AI/testing/tutorial.py` (90% duplicate)

### Unify Physics Implementations
- [ ] Reconcile `pong/physics_object.py` and `pong_BETA/physics_object.py`
- [ ] Create single physics system with configurable features

---

## Priority 4: Essential Features

- [x] Set up basic pygame window
- [x] Fix __main__ typo and game loop
- [x] Draw paddles and ball
- [x] Handle paddle movement (W/S and UP/DOWN keys)
- [x] Ball movement and bouncing
- [x] Collision detection with paddles
- [x] Scoring system
- [x] Game determination (3 points for winner)
- [x] Game determination message
- [x] Separate classes and methods
- [x] Start, Pause and Reset buttons
- [x] Add a requirements file
- [x] Add a LICENSE file (MIT)
- [x] Change mode selection (classic, pongception, BETA/WTF, SandBox/Debug)
  - Added visual mode selection grid in menu
  - Added Sandbox mode with debug overlay
  - 4 modes: Classic, Pongception, BETA, Sandbox
- [x] Make an easy download version with an icon
  - Created `scripts/build.py` for PyInstaller builds
  - Created `scripts/generate_icon.py` for icon generation
  - Generated icons in multiple sizes (16x16 to 256x256)
  - Window icon set in launcher
- [x] Implement omershachar github fox somewhere
  - Fox logo displayed in menu footer
  - Version and GitHub URL shown in credits
  - Auto-loads `assets/fox.png` when present

---

## Priority 5: Customization Features

### Ball & Paddle Customization
- [x] Add function for changing size and speed of ball and paddles
  - Created `pong/settings.py` with GameSettings class
  - Settings menu accessible via [S] key from main menu
- [ ] Option to choose key settings or play with mouse
- [x] Change paddle colors (left and right separately)
  - 8 color options: White, Purple, Light Purple, Red, Yellow, Green, Orange, Grey
- [x] Resize paddles (affect mass?)
  - Paddle height adjustable 40-200px
- [x] Adjust ball velocity/acceleration/spin/friction
  - Ball speed adjustable 2-15
  - Ball radius adjustable 3-20
- [x] Adjust paddle velocity/acceleration/spin/friction
  - Paddle speed adjustable 3-15

### Board Customization
- [ ] Change board shape (circle mode?)
- [x] Change board background color
  - 6 options: Black, Dark Grey, Dark Blue, Dark Green, Dark Red, Dark Purple
- [ ] Custom background images (Nick Cage background!)
- [ ] Upload custom photo for background

---

## Priority 6: Game Modes

### AI Opponent
- [ ] Add game mode selection (Play with friend / Play against computer)
- [ ] Add basic AI opponent
- [ ] AI difficulty levels:
  - [ ] "Fucking terrible"
  - [ ] "Fine I guess but still kind of shit at it..."
  - [ ] "THE INVINCIBLE GOD OF PONG"

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
- [ ] Add version numbers (v0.1, v1.0)
- [ ] Add custom project logo/favicon
- [ ] Capture GIF/video demo of gameplay
- [ ] Add screenshots in GitHub README
- [ ] Add "buy me a coffee" button
- [ ] Include "Features" list in README
- [ ] Write CONTRIBUTING.md
- [ ] Create CHANGELOG.md
- [ ] Add GitHub Actions badge
- [ ] Add "Install & Play" guide in README
- [ ] Add tech stack list in README
- [ ] Write final polished README.md

---

## Priority 8: Web & Mobile

- [?] Set up GitHub Pages landing page
- [?] Set up HTML webpage to host the game
- [?] Connect game to web page
- [?] Style game page with CSS
- [?] Add link for game page in GitHub
- [?] Phone & Tablet touch controls

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
- [ ] Secret key sequence that explodes opponent paddle (reward for beating AI boss)
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
- [x] Set up basic pygame window
- [x] Fix __main__ typo and game loop
- [x] Draw paddles and ball
- [x] Handle paddle movement (W/S and UP/DOWN keys)
- [x] Ball movement and bouncing
- [x] Collision detection with paddles
- [x] Scoring system
- [x] Game determination method
- [x] Game determination message
- [x] Separate classes and methods
- [x] Start, Pause and Reset buttons
- [x] Add requirements file
- [x] Add physics elements (paddle recoil, acceleration)
- [x] Add LICENSE file (MIT)

### Documentation (Session 1)
- [x] Create CLAUDE.md
- [x] Create PROJECT_ANALYSIS.md
- [x] Create progress.md
- [x] Create TODO.md

### Bug Fixes (Session 2)
- [x] BUG-001: TypeScript paddle control fixed
- [x] BUG-002: InputHandler key mapping fixed
- [x] BUG-003: testing.py undefined variable fixed
- [x] BUG-004: testing.py class ordering fixed
- [x] BUG-005: AI tutorial.py NameError fixed
- [x] BUG-006: BETA main.py property access fixed
- [x] BUG-007: object_manage.py undefined method fixed

### Code Cleanup (Session 2)
- [x] Deleted pong_BETA/helpers.py (empty)
- [x] Deleted testing/pygame_example.py (unused)
- [x] Removed commented code in BETA/main.py
- [x] Removed commented code in physics_object.py
- [x] Fixed hardcoded values in game-helpers.ts

### Code Consolidation (Session 4)
- [x] Combined Ball/BallClassic into single class (Python: `pong/ball.py`)
- [x] Combined Ball/BallClassic into single class (TypeScript: `src/game/ball.ts`)
- [x] Combined Paddle/PaddleClassic into single class (Python: `pong/paddle.py`)
- [x] Combined Paddle/PaddleClassic into single class (TypeScript: `src/game/paddle.ts`)
- [x] Fixed TypeScript null check error in `src/index.ts`

### Priority 4 Features (Session 4)
- [x] Enhanced mode selection with visual grid
- [x] Added GAME_MODES configuration in `pong/menu.py`
- [x] Created Sandbox mode (`versions/sandbox/main.py`)
- [x] Added GREEN color and FONT_TINY_DIGITAL to constants
- [x] Updated launcher to support 4 modes
- [x] Created build system (`scripts/build.py`, `scripts/generate_icon.py`)
- [x] Generated game icons (PNG and ICO formats)
- [x] Added window icon support to launcher
- [x] Added fox logo and credits to menu footer
- [x] Added version number (v1.0.0) to menu

---

*Last updated: 2026-01-27*
