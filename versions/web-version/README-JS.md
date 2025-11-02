# PongWithIssues - JavaScript/TypeScript Version

A browser-based Pong game with two modes: Classic and Physics-based Pongception.

## Features

- **Classic Mode**: Traditional Pong with simple physics
- **Physics Mode**: Advanced physics with spin effects, trails, and realistic ball behavior
- **Menu System**: Easy mode selection and game controls
- **Responsive Controls**: Keyboard input for paddle movement
- **Visual Effects**: Fire trails, spin indicators, and smooth animations

## How to Run

### Option 1: Simple HTTP Server (Recommended)

1. Open a terminal in the project directory
2. Run one of these commands:

**Python 3:**

```bash
python3 -m http.server 8000
```

**Python 2:**

```bash
python -m SimpleHTTPServer 8000
```

**Node.js (if you have it installed):**

```bash
npx http-server
```

3. Open your browser and go to `http://localhost:8000`

### Option 2: Direct File Opening

1. Simply open `index.html` in your web browser
2. Note: Some browsers may block local file access for security reasons

## Controls

### Menu

- **Arrow Keys Left/Right** or **A/D**: Switch between Classic and Physics modes
- **Space**: Start the selected game mode

### In Game

- **W/S** or **Arrow Up/Down**: Move left paddle
- **Space**: Pause/Resume game
- **R**: Restart game
- **M**: Return to menu
- **H**: Toggle help instructions
- **Escape**: Return to menu

## Game Modes

### Classic Mode

- Traditional Pong gameplay
- Simple ball physics
- Fixed paddle movement speed

### Physics Mode

- Advanced physics simulation
- Ball spin effects (Magnus effect)
- Fire trail visual effects
- Realistic paddle acceleration
- Debug information display

## Technical Details

- **Canvas-based rendering**: Uses HTML5 Canvas for smooth 60 FPS gameplay
- **Object-oriented design**: Clean class structure for game objects
- **Collision detection**: Precise ball-paddle and ball-wall collision handling
- **Input handling**: Responsive keyboard input system
- **State management**: Clean game state transitions

## File Structure

```bash
├── index.html          # Main HTML file
├── pong-game.js        # Complete game implementation
├── package.json        # Node.js dependencies (optional)
├── tsconfig.json       # TypeScript configuration (optional)
└── src/                # TypeScript source files (optional)
    ├── game/           # Game classes
    ├── types/          # Type definitions
    └── utils/          # Utility functions
```

## Browser Compatibility

- Modern browsers with HTML5 Canvas support
- ES6+ JavaScript features required
- Tested on Chrome, Firefox, Safari, and Edge

## Development

If you want to modify the TypeScript source files:

1. Install dependencies: `npm install`
2. Compile TypeScript: `npm run build`
3. Serve the files: `npm run serve`

The `pong-game.js` file is a standalone version that includes all the game logic in a single file for easy deployment.
