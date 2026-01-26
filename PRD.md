# Product Requirements Document (PRD)
## PongWithIssues

```
██████╗   ██████╗  ███╗   ██╗  ██████╗   ██╗
██╔══██╗ ██╔═══██╗ ████╗  ██║ ██╔════╝   ██║
██████╔╝ ██║   ██║ ██╔██╗ ██║ ██║  ███╗  ██║
██╔═══╝  ██║   ██║ ██║╚██╗██║ ██║   ██║  ╚═╝
██║      ╚██████╔╝ ██║ ╚████║ ╚██████╔╝  ██╗
╚═╝       ╚═════╝  ╚═╝  ╚═══╝  ╚═════╝   ╚═╝

"Barely functional Pong made by a barely functional dev."
```

---

## 1. Product Vision

**PongWithIssues** is a full-featured, tongue-in-cheek recreation of the classic Pong arcade game. It combines nostalgic gameplay with modern physics simulation, multiple game modes, and a healthy dose of humor.

### What Makes It Unique
- **Physics-based gameplay**: Real momentum, spin, and collision physics
- **Multi-platform**: Desktop (Python/Pygame) and Web (TypeScript/Canvas)
- **Self-aware humor**: Satirical features, absurd power-ups, and a "broken by design" aesthetic
- **Educational value**: Clean, readable code for learning game dev, physics, and AI

---

## 2. Target Audience

| Audience | Needs |
|----------|-------|
| **Casual Gamers** | Quick, fun games to play with friends |
| **Developers/Learners** | Clean code examples for Python, TypeScript, Pygame, game physics |
| **AI/ML Enthusiasts** | NEAT-based AI training playground |
| **Friends & Personal** | Shareable fun project with inside jokes |

---

## 3. Platforms

| Platform | Technology | Status |
|----------|------------|--------|
| Desktop (Windows/Linux/Mac) | Python 3.10+ / Pygame | Working |
| Web (Desktop browsers) | TypeScript / HTML5 Canvas | Working (needs polish) |
| Web (Mobile) | TypeScript / Touch controls | Partial (needs work) |
| PWA (Offline) | Service Worker | Implemented |

---

## 4. Feature Requirements

### 4.1 Must-Have (MVP)

| Feature | Description | Status |
|---------|-------------|--------|
| **Local Multiplayer** | Two players on same device (W/S vs Arrows) | ✅ Done |
| **AI Opponent** | Computer-controlled paddle for single player | 🔲 Planned |
| **Working Web Version** | Fully playable in browser | 🟡 Partial |
| **Multiple Game Modes** | Classic, Physics (Pongception), + special modes | 🟡 2 of 4+ |
| **Scoring System** | First to 3 points wins | ✅ Done |
| **Pause/Resume** | Space to pause, M for menu | ✅ Done |

### 4.2 Should-Have (Core Experience)

| Feature | Description | Priority |
|---------|-------------|----------|
| **AI Difficulty Levels** | Easy, Medium, Hard (or humorous names) | High |
| **Mobile Touch Controls** | Swipe/drag to control paddles | High |
| **Sound Effects** | Ball hit, score, win/lose sounds | Medium |
| **Settings Menu** | Volume, controls, display options | Medium |
| **Fullscreen Mode** | Desktop and web fullscreen support | Medium |

### 4.3 Could-Have (Enhanced Experience)

| Feature | Description | Priority |
|---------|-------------|----------|
| **Power-Ups System** | Collectible abilities during gameplay | High |
| **Crazy Mode** | Fast, chaotic gameplay variant | High |
| **Peaceful Mode** | No ball, just clouds and chill music | Medium |
| **Cursed Mode** | Random chaos, unexpected behaviors | Medium |
| **Customization** | Paddle colors, ball styles, backgrounds | Low |
| **Leaderboard** | Local high scores | Low |

### 4.4 Won't-Have (Out of Scope... for now)

| Feature | Reason |
|---------|--------|
| Online multiplayer | Requires server infrastructure |
| Account system | Complexity vs. value |
| Real microtransactions | It's a joke, not a business |

---

## 5. Game Modes

### 5.1 Classic Mode
- Standard Pong rules
- Simple velocity-based physics
- First to 3 points wins
- **Status**: ✅ Complete

### 5.2 Pongception (Physics Mode)
- Advanced Newtonian physics
- Ball spin from paddle motion (Magnus effect)
- Paddle recoil on hit
- Momentum transfer
- **Status**: ✅ Complete

### 5.3 Crazy Mode
- Smaller paddles and ball
- Higher ball velocity (increases over time?)
- Screen shake on hits
- **Status**: 🔲 Planned

### 5.4 Peaceful Mode
- No ball, no score
- Floating clouds/particles
- Relaxing background music
- Zen garden aesthetic
- **Status**: 🔲 Planned

### 5.5 Cursed Mode
- Random physics glitches
- Ball splits unexpectedly
- Paddles occasionally disappear
- Gravity shifts randomly
- **Status**: 🔲 Planned

---

## 6. Power-Ups System

### 6.1 Mechanics
- Power-up boxes spawn randomly during gameplay
- Catch with paddle to collect
- Activate with dedicated button or auto-activate
- Limited uses or time-based

### 6.2 Power-Up Ideas

| Power-Up | Effect | Duration |
|----------|--------|----------|
| **Big Paddle** | Increase paddle size 50% | 10 seconds |
| **Multi-Ball** | Add extra ball on next hit | Until scored |
| **Shield** | Can't lose for 3 seconds | 3 seconds |
| **Speed Boost** | Paddle moves faster | 8 seconds |
| **Freeze** | Opponent paddle slows down | 5 seconds |
| **Reverse** | Opponent controls inverted | 5 seconds |
| **Magnet** | Ball curves toward your paddle | 6 seconds |
| **Nuke** | Instant win (ultra rare) | Instant |

---

## 7. AI Opponent

### 7.1 Architecture
- NEAT (NeuroEvolution of Augmenting Topologies)
- Pre-trained models for each difficulty
- Can continue training locally

### 7.2 Difficulty Levels

| Level | Internal Name | Behavior |
|-------|---------------|----------|
| Easy | "Fucking terrible" | Slow reactions, misses often |
| Medium | "Fine I guess" | Decent tracking, occasional mistakes |
| Hard | "GOD OF PONG" | Near-perfect, predicts ball trajectory |

---

## 8. Technical Requirements

### 8.1 Desktop (Python)
- Python 3.10 - 3.13
- Pygame 2.6.1
- NumPy
- 60 FPS target
- 800x800 window (resizable?)

### 8.2 Web (TypeScript)
- TypeScript 5.0+
- ES2020 modules
- HTML5 Canvas 2D
- 60 FPS via requestAnimationFrame
- Responsive canvas sizing
- PWA with offline support

### 8.3 Shared
- Consistent physics between platforms
- Same game feel on desktop and web
- Shared constants (speeds, sizes, etc.)

---

## 9. User Stories

### Player Stories
1. As a **casual player**, I want to quickly start a game so I can play with a friend.
2. As a **solo player**, I want to play against AI so I can practice.
3. As a **mobile user**, I want touch controls so I can play on my phone.
4. As a **competitive player**, I want multiple difficulty levels to challenge myself.

### Developer Stories
1. As a **learner**, I want clean code examples to understand game physics.
2. As an **AI enthusiast**, I want to train my own Pong AI using NEAT.
3. As a **contributor**, I want clear documentation to add features.

---

## 10. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Game loads without errors | 100% | Manual testing |
| Consistent 60 FPS | >95% of frames | Performance monitoring |
| Mobile usability | Playable on phone | User testing |
| Code quality | No critical bugs | Automated + manual testing |
| Fun factor | Friends enjoy it | Subjective feedback |

---

## 11. Milestones

### Phase 1: Core Polish (Current)
- [x] Fix all critical bugs
- [x] Clean up codebase
- [ ] Fix TypeScript strict mode errors
- [ ] Improve mobile web experience

### Phase 2: AI Opponent
- [ ] Integrate NEAT training into main game
- [ ] Create difficulty presets
- [ ] Add AI vs Human mode to menu

### Phase 3: Additional Modes
- [ ] Implement Crazy Mode
- [ ] Implement Peaceful Mode
- [ ] Add mode selection to web version

### Phase 4: Power-Ups
- [ ] Design power-up spawn system
- [ ] Implement 4-6 core power-ups
- [ ] Balance testing

### Phase 5: Polish & Fun
- [ ] Add sound effects
- [ ] Implement Cursed Mode
- [ ] Add satirical store (non-functional)
- [ ] Easter eggs and secrets

---

## 12. Open Questions

1. Should web and desktop share the same save data format?
2. How to handle AI training in web version (WebWorkers?)?
3. Should power-ups be in all modes or dedicated mode?
4. What's the right balance for Cursed Mode chaos?

---

## 13. References

- [Original TODO.txt](docs/TODO.txt) - Feature ideas
- [CLAUDE.md](CLAUDE.md) - Development guidance
- [TODO.md](TODO.md) - Prioritized task list
- [progress.md](progress.md) - Development history

---

*Document Version: 1.0*
*Last Updated: 2026-01-26*
