# PongWithIssues (Browser Edition)

![Animated neon pong table with paddles](https://img.shields.io/badge/platform-web-blueviolet)
![TypeScript](https://img.shields.io/badge/typescript-5.4-informational)

PongWithIssues is now a browser-first remake of the original buggy Python project. The new version is written in TypeScript, rendered on an HTML5 canvas, and ships with zero-install instructions so you can play in any modern browser.

---

## ✨ Features

- ⚡ Smooth 144 Hz game loop for responsive gameplay
- 🧠 CPU opponent with adjustable reaction speed
- 🎨 Glow-inspired retro visuals with subtle effects
- ♿ Keyboard friendly controls (`W`/`S` or arrow keys)
- 🧰 Straightforward TypeScript codebase ready for tinkering

---

## 🚀 Getting Started

You can either open the game directly from the repository or run a tiny local web server for development.

### Option 1: Just open it

1. Clone or download the repository.
2. Open `index.html` in any modern browser.

### Option 2: Build from TypeScript sources

1. Install dependencies (requires Node 18+):
   ```bash
   npm install
   ```
2. Build the TypeScript sources:
   ```bash
   npm run build
   ```
3. Launch any static server and visit `http://localhost:PORT/index.html`.
   - For example: `npx http-server .`

The compiled JavaScript lives in `dist/` and is already included for convenience.

---

## 🎮 Controls

| Action           | Key(s)       |
|------------------|--------------|
| Move up          | `W` or `↑`   |
| Move down        | `S` or `↓`   |
| Restart the game | Click `Restart`

---

## 🧱 Project Structure

```
.
├── dist/           # Compiled JavaScript (ready for the browser)
├── src/            # TypeScript source files
├── index.html      # Entry point for the web version
├── package.json    # npm scripts and dev dependencies
└── tsconfig.json   # TypeScript compiler configuration
```

Key modules:
- `src/game.ts` – game loop orchestration, rendering, score tracking
- `src/ball.ts` – ball physics, collisions, scoring
- `src/paddle.ts` – player & CPU paddle behaviour
- `src/input.ts` – keyboard input manager
- `src/constants.ts` – tweakable gameplay constants

---

## 🛠 Tech Stack

- [TypeScript 5](https://www.typescriptlang.org/)
- HTML5 Canvas
- Modern ES Modules

---

## 📜 License

Released under the [MIT License](LICENSE).
