# PongWithIssues - Master TODO List (v2)

*Rethought priorities — Feb 17, 2026 (Session 17)*
*Pillars: Best Playing Experience | Full Adjustability | Cursed Vibe*

---

## Pending / Unprioritized

- [ ] **Font rights**: read `pong/FONTS/readme.txt` — consider a new font to avoid licensing issues
- [ ] **Legal check**: full repo audit for licensing/legal compliance

---

## P1: Game Feel & Juice ✅ COMPLETE

### Sound Effects ✅
- [X] `pong/audio.py` — Procedural sound manager (11 sounds, numpy-generated)
- [X] Paddle hit sound (classic Pong 480Hz sine beep)
- [X] Wall bounce sound (320Hz sine beep)
- [X] Score point sound (300→800Hz sweep)
- [X] Win/lose fanfare (ascending/descending jingles)
- [X] Power-up collect/activate/expire sounds
- [X] Freeze sound (ice crack)
- [X] Countdown tick/go sounds
- [X] Menu ball bounce sound
- [ ] Background music — looping chiptune/synthwave track

### Visual Juice ✅
- [X] Screen shake — on score, on power-up collect, on freeze
- [X] Flash effect on power-up collection
- [X] Particle burst when ball hits paddle
- [X] Score pop animation (number scales up then settles)
- [ ] Power-up expiry pulse (visual throb before disappearing)

### Game Flow Overhaul ✅
- [X] **Win/lose screen** — Play Again / Main Menu with final score display
- [X] **Pause menu** — Resume / Restart / Main Menu overlay
- [X] **Countdown** — 3-2-1-GO with sound
- [X] **Exit confirmation** — Leave/Cancel dialog

---

## P2: Mobile & Touch Experience ✅ MOSTLY COMPLETE

### Touch Controls ✅
- [X] Bigger touch targets (120x56 buttons, up from 90x40)
- [X] Visual touch feedback — expanding ripple circles
- [X] Touch zone indicators — auto-hiding "LEFT/RIGHT PADDLE" labels
- [X] Touch dead zone increased (10% → 20%) for finger precision
- [X] Faster touch tracking — double-acceleration when far from paddle
- [X] Touch-friendly pause menu (tap targets)
- [X] Touch-friendly win/lose screen (tap buttons)

### Mobile UI — Remaining
- [ ] Responsive layout — detect portrait vs landscape
- [ ] Larger score/mode text for small screens
- [ ] Touch-friendly settings menu — bigger sliders/buttons
- [ ] BETA mode touch controls (drag to apply force, tap for impulse)
- [ ] Orientation lock hint (landscape recommended)
- [ ] Loading screen / progress indicator for Pygbag first load

---

## P3: Full Adjustability

*Every possible game aspect can be altered by the user.*

### Settings Persistence
- [ ] Save settings to JSON (localStorage on web, file on desktop)
- [ ] Load settings on startup
- [ ] "Reset to Defaults" button in settings

### New Settings — Physics
- [ ] Friction slider (currently hardcoded 0.85)
- [ ] Spin factor slider (currently hardcoded 0.5)
- [ ] Magnus effect strength (currently hardcoded 0.1)
- [ ] Ball trail length (currently hardcoded 10)
- [ ] Restitution / bounciness for BETA mode

### New Settings — Power-ups
- [ ] Per-power-up toggles (enable/disable Resize, Freeze, Multi-ball individually)
- [ ] Spawn frequency slider (5-12s range adjustable)
- [ ] Effect duration multiplier (0.5x to 2x)
- [ ] Power-up intensity (resize %, freeze duration, extra ball count)

### New Settings — Gameplay
- [ ] Mouse/trackpad paddle control option (paddle follows cursor Y)
- [ ] Key rebinding (custom control keys)
- [ ] AI difficulty per-parameter override (advanced: reaction, noise, dead zone)
- [ ] Game speed multiplier (0.5x slo-mo to 2x fast)

### New Settings — Audio/Visual
- [ ] Master volume slider
- [ ] SFX volume slider
- [ ] Music volume slider
- [ ] Screen shake intensity (off / subtle / intense)
- [ ] Particle effects toggle (for low-end devices)
- [ ] Fire trail toggle

---

## P4: The Cursed Vibe

*This is what makes PongWithIssues unique. Without it, it's just another Pong clone.*

### Cursed Mode (New Game Mode)
- [ ] Random events every 10-15 seconds during gameplay:
  - Gravity flip (ball falls up/down)
  - Ball splits into 3
  - Paddles swap sides
  - Screen rotates 180 degrees
  - Ball becomes invisible for 2 seconds
  - Paddle shrinks to 5px for 3 seconds
  - Controls reverse for both players
  - Ball speed doubles then halves
  - "Lag simulator" — game stutters artificially for 1 second
  - Comic Sans mode — all text becomes Comic Sans for 10 seconds
- [ ] Event announcement text (big dramatic text: "GRAVITY FLIP!" etc.)
- [ ] Increasingly chaotic (more frequent events as match progresses)

### Crazy Mode (New Game Mode)
- [ ] Everything accelerates over time — ball speed, paddle speed, spawn rate
- [ ] Screen shake intensifies with each rally
- [ ] Trails get longer, colors shift toward red
- [ ] Paddles and ball shrink over time
- [ ] Win score increases each round (3, then 5, then 7...)

### Cursed Power-ups (Add to power-up system)
- [ ] **REVERSE** (purple "X" box) — reverses opponent controls for 5s
- [ ] **DRUNK** (yellow "D" box) — opponent paddle wobbles sinusoidally
- [ ] **BLIND** (black "B" box) — opponent's half of screen goes dark for 3s
- [ ] **GROW_BALL** (orange "G" box) — ball doubles in size for 8s

### Easter Eggs
- [ ] Konami code (up up down down left right left right) → opponent paddle explodes
- [ ] Play 100 games → unlock "golden paddle" (it's just yellow, tooltip: "worth it?")
- [ ] Type "pong" on menu → ball in menu goes haywire
- [ ] PongShit.txt — absurd quotes between rounds ("Pong is just tennis for people who gave up")

### Satirical Micro-transaction Store
- [ ] [S]tore button on main menu
- [ ] Store UI with paddle accessories (hats, swords, flames) priced in "Gems"
- [ ] "Buy Gems" button → opens panel: "Gems cost Gems. You have 0 Gems."
- [ ] "Watch Ad for Free Gems" → rickroll or 10hr YouTube video
- [ ] "Limited Time Offer!" that never expires
- [ ] Final punchline when you try hard enough: "There aren't any Gems, go fuck yourself"
- [ ] Free coins if you wait on the store page for X minutes = X coins (coins do nothing)

---

## P5: Code Health

*Not user-facing, but prevents bugs and makes everything above easier to build.*

- [ ] Consolidate collision handlers — ONE in `helpers.py`, delete duplicates in `utilities.py` and `__init__.py`
- [ ] Extract game loop base class — shared pause/score/reset/draw logic
- [ ] Centralize ALL magic numbers into `constants.py` (friction 0.85, Magnus 0.1, etc.)
- [ ] Fix hit counter display overlap with score in `__init__.py`
- [ ] Clean up unused imports and dead code across all files
- [ ] Add `from_dict()` to GameSettings for settings persistence

---

## P6: Polish & Shipping

- [ ] Gameplay GIF/video for README
- [ ] Mode tutorial overlay on first play (brief "Spin affects ball curve!" etc.)
- [ ] Font licensing resolution
- [ ] CHANGELOG.md with proper versioning
- [ ] GitHub README update — game page link, screenshots, power-ups docs
- [ ] "Buy me a coffee" button in README
- [ ] GitHub Actions badge in README

---

## P7: Stretch Goals (Post v2.0)

- [ ] Peaceful mode — no ball, floating clouds, zen music
- [ ] Online leaderboard
- [ ] Board shape variants (circle mode?)
- [ ] Custom background images / upload
- [ ] User accounts / score persistence
- [ ] Replay system (save and replay matches)
- [ ] Spectator mode (watch two AIs fight)
- [ ] Screen size options (800x800 / 1024x1024 / fullscreen)

---

## Completed Tasks Archive

<details>
<summary>Click to expand completed tasks from v1.0</summary>

### Original Features
- [X] Basic pygame window, game loop, paddles, ball, collision, scoring
- [X] Game determination, start/pause/reset, requirements, LICENSE

### Bug Fixes (Sessions 2-4)
- [X] BUG-001 through BUG-015 (all fixed)
- [X] Web version bugs BUG-W01 through BUG-W08 (obsolete — JS/TS replaced by Pygbag)

### Code Cleanup (Session 2)
- [X] Deleted empty/unused files, removed commented code, fixed hardcoded values

### Code Consolidation (Session 4)
- [X] Unified Ball/BallClassic and Paddle/PaddleClassic (Python & TypeScript)
- [X] Merged AI testing files, reconciled PhysicsObject variants

### Essential Features (Session 4)
- [X] Mode selection grid, Sandbox mode, build system, icons, fox logo, version
- [X] Settings menu with full customization + live AI preview

### Documentation (Sessions 1, 5, 11)
- [X] Created CLAUDE.md, progress.md, TODO.md
- [X] Updated README with features, install guide, tech stack

### Web Deployment (Sessions 10-11, 13)
- [X] Pygbag migration (Python → WebAssembly, single codebase)
- [X] GitHub Actions workflow for automated Pages deployment

### Desktop Launcher (Session 14)
- [X] One-click `play.py` launcher with auto venv + deps
- [X] `play.sh` / `play.bat` double-click wrappers
- [X] AI system: 10 difficulty levels (Beginner → Impossible)

### Touch Controls (Session 15)
- [X] TouchHandler in `pong/touch.py` with full mobile support
- [X] Touch navigation in menus, submenus, settings
- [X] Single-player touch mode for vs AI

### Power-ups (Session 16)
- [X] PowerUpManager with 3 types: Resize, Freeze, Multi-ball
- [X] Integrated into Classic and Pongception modes
- [X] Settings toggle for power-ups on/off

</details>

---

*Last updated: 2026-02-17 (Session 17)*
