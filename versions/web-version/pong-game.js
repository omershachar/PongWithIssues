/**
 * PongWithIssues - Complete game in a single JavaScript file
 */

// Constants
const COLORS = {
    BLACK: [0, 0, 0],
    WHITE: [255, 255, 255],
    PURPLE: [122, 118, 229],
    LIGHT_PURPLE: [185, 183, 232],
    RED: [255, 0, 0],
    YELLOW: [255, 255, 0],
    GREY: [128, 128, 128],
    DARK_RED: [139, 0, 0],
    SCARLET: [255, 36, 0],
    ORANGE_RED: [255, 69, 0],
    ORANGE: [255, 140, 0],
    GOLD: [255, 215, 0],
};

const WIDTH = 800;
const HEIGHT = 800;
const FPS = 60;
const WINNING_SCORE = 3;

// Game settings
const PADDLE_WIDTH = 15;
const PADDLE_HEIGHT = 85;
const PADDLE_DEFAULT_VEL = 4.5;
const PADDLE_MAX_VEL = 9;
const PADDLE_DEFAULT_ACC = 3;

const BALL_RADIUS = 7;
const BALL_DEFAULT_VEL = 6;
const MAX_DEFLECTION_SPEED = 7;
const SPIN_FACTOR = 0.5;

// Input handler
class InputHandler {
    constructor() {
        this.keys = {
            up: false,
            down: false,
            left: false,
            right: false,
            space: false,
            escape: false,
            m: false,
            r: false,
            h: false,
        };
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.addEventListener('keydown', (event) => {
            switch (event.code) {
                case 'ArrowUp':
                case 'KeyW':
                    this.keys.up = true;
                    break;
                case 'ArrowDown':
                case 'KeyS':
                    this.keys.down = true;
                    break;
                case 'ArrowLeft':
                case 'KeyA':
                    this.keys.left = true;
                    break;
                case 'ArrowRight':
                case 'KeyD':
                    this.keys.right = true;
                    break;
                case 'Space':
                    this.keys.space = true;
                    break;
                case 'Escape':
                    this.keys.escape = true;
                    break;
                case 'KeyM':
                    this.keys.m = true;
                    break;
                case 'KeyR':
                    this.keys.r = true;
                    break;
                case 'KeyH':
                    this.keys.h = true;
                    break;
            }
            event.preventDefault();
        });

        document.addEventListener('keyup', (event) => {
            switch (event.code) {
                case 'ArrowUp':
                case 'KeyW':
                    this.keys.up = false;
                    break;
                case 'ArrowDown':
                case 'KeyS':
                    this.keys.down = false;
                    break;
                case 'ArrowLeft':
                case 'KeyA':
                    this.keys.left = false;
                    break;
                case 'ArrowRight':
                case 'KeyD':
                    this.keys.right = false;
                    break;
                case 'Space':
                    this.keys.space = false;
                    break;
                case 'Escape':
                    this.keys.escape = false;
                    break;
                case 'KeyM':
                    this.keys.m = false;
                    break;
                case 'KeyR':
                    this.keys.r = false;
                    break;
                case 'KeyH':
                    this.keys.h = false;
                    break;
            }
            event.preventDefault();
        });
    }
}

// Ball class
class Ball {
    constructor(x, y, radius, color, velX = BALL_DEFAULT_VEL, velY = 0) {
        this.pos = { x, y };
        this.originalPos = { x, y };
        this.radius = radius;
        this.color = color;
        this.vel = { x: velX, y: velY };
        this.spin = 0;
        this.trail = [];
        this.maxTrail = 10;
    }

    draw(ctx) {
        // Draw trail
        const FIRE_COLORS = [COLORS.DARK_RED, COLORS.SCARLET, COLORS.ORANGE_RED, COLORS.ORANGE, COLORS.GOLD, COLORS.YELLOW, COLORS.WHITE];
        
        for (let i = 0; i < this.trail.length; i++) {
            const pos = this.trail[i];
            const alpha = Math.max(0.1, 1 - i / this.trail.length);
            const radius = Math.max(2, this.radius * (1 - i / this.trail.length * 0.8));
            const colorIdx = Math.floor((i / this.trail.length) * (FIRE_COLORS.length - 1));
            const trailColor = FIRE_COLORS[colorIdx];
            
            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.fillStyle = `rgb(${trailColor[0]}, ${trailColor[1]}, ${trailColor[2]})`;
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        // Draw main ball
        ctx.fillStyle = `rgb(${this.color[0]}, ${this.color[1]}, ${this.color[2]})`;
        ctx.beginPath();
        ctx.arc(this.pos.x, this.pos.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
    }

    move() {
        this.vel.y += this.spin * 0.1; // Magnus effect
        this.pos.x += this.vel.x;
        this.pos.y += this.vel.y;
    }

    update() {
        this.trail.unshift({ x: this.pos.x, y: this.pos.y });
        if (this.trail.length > this.maxTrail) {
            this.trail.pop();
        }
        this.move();
    }

    bounceBox(width, height) {
        this.move();
        if (this.pos.x <= 0 || this.pos.x >= width) {
            this.vel.x *= -1;
        }
        if (this.pos.y <= 0 || this.pos.y >= height) {
            this.vel.y *= -1;
        }
    }

    reset() {
        this.pos = { ...this.originalPos };
        this.vel = { x: -this.vel.x, y: 0 };
        this.spin = 0;
        this.trail = [];
    }

    get speed() {
        return Math.sqrt(this.vel.x * this.vel.x + this.vel.y * this.vel.y);
    }
}

// Paddle class
class Paddle {
    constructor(x, y, width, height, color = COLORS.LIGHT_PURPLE) {
        this.pos = { x, y };
        this.originalPos = { x, y };
        this.width = width;
        this.height = height;
        this.color = color;
        this.vel = { x: 0, y: 0 };
        this.acc = { x: 0, y: 0 };
    }

    draw(ctx) {
        ctx.fillStyle = `rgb(${this.color[0]}, ${this.color[1]}, ${this.color[2]})`;
        ctx.fillRect(this.pos.x, this.pos.y, this.width, this.height);
    }

    accelerate(up = true) {
        if (up) {
            this.acc.y -= PADDLE_DEFAULT_ACC;
        } else {
            this.acc.y += PADDLE_DEFAULT_ACC;
        }
    }

    update() {
        this.vel.x += this.acc.x;
        this.vel.y += this.acc.y;
        this.acc.x = 0;
        this.acc.y = 0;

        // Clamp vertical velocity
        this.vel.y = Math.max(-PADDLE_MAX_VEL, Math.min(PADDLE_MAX_VEL, this.vel.y));

        // Update position
        this.pos.x += this.vel.x;
        this.pos.y += this.vel.y;

        // Apply friction
        this.vel.y *= 0.85;

        // Clamp to screen
        if (this.pos.y < 0) {
            this.pos.y = 0;
            this.vel.y = 0;
        } else if (this.pos.y + this.height > HEIGHT) {
            this.pos.y = HEIGHT - this.height;
            this.vel.y = 0;
        }
    }

    reset() {
        this.pos = { ...this.originalPos };
        this.vel = { x: 0, y: 0 };
        this.acc = { x: 0, y: 0 };
    }
}

// Collision detection
class CollisionDetection {
    static checkBallPaddleCollision(ball, paddle) {
        const ballLeft = ball.pos.x - ball.radius;
        const ballRight = ball.pos.x + ball.radius;
        const ballTop = ball.pos.y - ball.radius;
        const ballBottom = ball.pos.y + ball.radius;

        const paddleLeft = paddle.pos.x;
        const paddleRight = paddle.pos.x + paddle.width;
        const paddleTop = paddle.pos.y;
        const paddleBottom = paddle.pos.y + paddle.height;

        return ballRight >= paddleLeft && 
               ballLeft <= paddleRight && 
               ballBottom >= paddleTop && 
               ballTop <= paddleBottom;
    }

    static resolveBallPaddleCollision(ball, paddle, isLeftPaddle) {
        // Calculate relative position on paddle
        const relativeIntersectY = (ball.pos.y - paddle.pos.y) / paddle.height;
        const normalizedIntersectY = (relativeIntersectY - 0.5) * 2; // -1 to 1

        // Calculate angle
        const maxAngle = Math.PI / 4; // 45 degrees
        const angle = normalizedIntersectY * maxAngle;

        // Calculate new velocity
        const speed = Math.sqrt(ball.vel.x * ball.vel.x + ball.vel.y * ball.vel.y);
        const newSpeed = Math.max(speed, 6);

        // Set new velocity
        if (isLeftPaddle) {
            ball.vel.x = Math.cos(angle) * newSpeed;
            ball.vel.y = Math.sin(angle) * newSpeed;
        } else {
            ball.vel.x = -Math.cos(angle) * newSpeed;
            ball.vel.y = Math.sin(angle) * newSpeed;
        }

        // Add spin
        ball.spin += paddle.vel.y * SPIN_FACTOR;
        ball.spin = Math.max(-10, Math.min(10, ball.spin));

        // Clamp vertical velocity
        ball.vel.y = Math.max(-MAX_DEFLECTION_SPEED, Math.min(MAX_DEFLECTION_SPEED, ball.vel.y));

        // Position ball outside paddle
        if (isLeftPaddle) {
            ball.pos.x = paddle.pos.x + paddle.width + ball.radius;
        } else {
            ball.pos.x = paddle.pos.x - ball.radius;
        }
    }

    static handleBallCollision(ball, leftPaddle, rightPaddle) {
        // Paddle collisions
        if (this.checkBallPaddleCollision(ball, leftPaddle)) {
            this.resolveBallPaddleCollision(ball, leftPaddle, true);
        }
        if (this.checkBallPaddleCollision(ball, rightPaddle)) {
            this.resolveBallPaddleCollision(ball, rightPaddle, false);
        }

        // Wall collisions
        if (ball.pos.y - ball.radius <= 0 || ball.pos.y + ball.radius >= HEIGHT) {
            ball.vel.y *= -1;
            ball.pos.y = ball.pos.y - ball.radius <= 0 ? ball.radius : HEIGHT - ball.radius;
        }
    }
}

// Menu class
class Menu {
    constructor() {
        this.ball = new Ball(WIDTH / 2, HEIGHT / 2, BALL_RADIUS, COLORS.WHITE, BALL_DEFAULT_VEL, 4);
        this.selectedMode = 0; // 0 = Classic, 1 = Physics
    }

    draw(ctx) {
        // Clear canvas
        ctx.fillStyle = 'rgb(0, 0, 0)';
        ctx.fillRect(0, 0, WIDTH, HEIGHT);

        // Draw title
        ctx.fillStyle = `rgb(${COLORS.PURPLE[0]}, ${COLORS.PURPLE[1]}, ${COLORS.PURPLE[2]})`;
        ctx.font = '48px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('PONG WITH ISSUES', WIDTH / 2, 150);

        // Draw subtitle
        ctx.fillStyle = `rgb(${COLORS.LIGHT_PURPLE[0]}, ${COLORS.LIGHT_PURPLE[1]}, ${COLORS.LIGHT_PURPLE[2]})`;
        ctx.font = '20px monospace';
        ctx.fillText("A project that probably works. Sometimes. Maybe.", WIDTH / 2, 200);
        ctx.fillText("It compiles. That's enough.", WIDTH / 2, 230);

        // Show mode selection
        const modeText = this.selectedMode === 0 ? "Mode: Classic" : "Mode: Physics";
        const modeColor = this.selectedMode === 0 ? COLORS.LIGHT_PURPLE : COLORS.RED;
        
        ctx.fillStyle = `rgb(${modeColor[0]}, ${modeColor[1]}, ${modeColor[2]})`;
        ctx.font = '24px monospace';
        ctx.fillText(modeText, WIDTH / 2, 300);

        // Draw prompt
        ctx.fillStyle = `rgb(${COLORS.PURPLE[0]}, ${COLORS.PURPLE[1]}, ${COLORS.PURPLE[2]})`;
        ctx.fillText("Press [SPACE] to start", WIDTH / 2, 350);
        ctx.fillText("Use [LEFT]/[RIGHT] to switch modes", WIDTH / 2, 380);

        // Draw bouncing ball
        this.ball.color = this.selectedMode === 0 ? COLORS.WHITE : COLORS.RED;
        this.ball.draw(ctx);
        this.ball.bounceBox(WIDTH, HEIGHT);
    }

    toggleMode() {
        this.selectedMode = this.selectedMode === 0 ? 1 : 0;
    }

    getSelectedMode() {
        return this.selectedMode === 0 ? 'classic' : 'physics';
    }
}

// Game class
class PhysicsGame {
    constructor() {
        this.leftPaddle = new Paddle(10, HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT);
        this.rightPaddle = new Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT / 2 - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT);
        this.ball = new Ball(WIDTH / 2, HEIGHT / 2, BALL_RADIUS, COLORS.YELLOW, BALL_DEFAULT_VEL, 0);
        this.leftScore = 0;
        this.rightScore = 0;
        this.paused = false;
        this.showInstructions = false;
    }

    update(input) {
        // Handle input
        if (input.space) {
            this.paused = !this.paused;
        }
        if (input.r) {
            this.reset();
            this.paused = false;
        }
        if (input.h) {
            this.showInstructions = !this.showInstructions;
        }

        // Check for game end
        if (this.leftScore >= WINNING_SCORE || this.rightScore >= WINNING_SCORE) {
            return true; // Game ended
        }

        if (!this.paused) {
            // Handle paddle movement
            if (input.up) {
                this.leftPaddle.accelerate(true);
            }
            if (input.down) {
                this.leftPaddle.accelerate(false);
            }

            // Update paddles
            this.leftPaddle.update();
            this.rightPaddle.update();

            // Update ball
            this.ball.update();
            CollisionDetection.handleBallCollision(this.ball, this.leftPaddle, this.rightPaddle);

            // Update score
            if (this.ball.pos.x - this.ball.radius < 0) {
                this.rightScore++;
                this.ball.reset();
            } else if (this.ball.pos.x + this.ball.radius > WIDTH) {
                this.leftScore++;
                this.ball.reset();
            }
        }

        return false; // Game continues
    }

    draw(ctx) {
        // Clear canvas
        ctx.fillStyle = 'rgb(0, 0, 0)';
        ctx.fillRect(0, 0, WIDTH, HEIGHT);

        // Draw center line
        ctx.strokeStyle = 'rgb(128, 128, 128)';
        ctx.lineWidth = 2;
        ctx.setLineDash([10, 10]);
        ctx.beginPath();
        ctx.moveTo(WIDTH / 2, 0);
        ctx.lineTo(WIDTH / 2, HEIGHT);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw paddles
        this.leftPaddle.draw(ctx);
        this.rightPaddle.draw(ctx);

        // Draw ball
        this.ball.draw(ctx);

        // Draw scores
        ctx.fillStyle = 'rgb(255, 255, 255)';
        ctx.font = '48px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(this.leftScore.toString(), WIDTH / 4, 60);
        ctx.fillText(this.rightScore.toString(), 3 * WIDTH / 4, 60);

        // Draw mode label
        ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
        ctx.font = '16px monospace';
        ctx.textAlign = 'left';
        ctx.fillText("MODE: PHYSICS", 10, 30);

        // Draw debug info
        ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
        ctx.font = '12px monospace';
        ctx.fillText(`Velocity: [${this.ball.vel.x.toFixed(2)}, ${this.ball.vel.y.toFixed(2)}]`, 10, 50);
        ctx.fillText(`Spin: ${this.ball.spin.toFixed(2)}`, 10, 70);

        // Draw pause screen
        if (this.paused) {
            ctx.fillStyle = `rgb(${COLORS.PURPLE[0]}, ${COLORS.PURPLE[1]}, ${COLORS.PURPLE[2]})`;
            ctx.font = '48px monospace';
            ctx.textAlign = 'center';
            ctx.fillText("PAUSED", WIDTH / 2, HEIGHT / 2 - 20);

            ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
            ctx.font = '16px monospace';
            ctx.fillText("Press [SPACE] to resume", WIDTH / 2, HEIGHT / 2 + 20);
        }

        // Draw instructions
        if (this.showInstructions) {
            const footerText = "Press [SPACE] to pause | [R] to restart | [M] to return | [ESC] to quit | [H] to hide";
            ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
            ctx.font = '12px monospace';
            ctx.textAlign = 'left';
            ctx.fillText(footerText, 10, HEIGHT - 20);
        } else {
            ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
            ctx.font = '12px monospace';
            ctx.textAlign = 'left';
            ctx.fillText("Press [H] for help", 10, HEIGHT - 20);
        }
    }

    getWinner() {
        if (this.leftScore >= WINNING_SCORE) {
            return "Left Player Won!";
        } else if (this.rightScore >= WINNING_SCORE) {
            return "Right Player Won!";
        }
        return null;
    }

    reset() {
        this.ball.reset();
        this.leftPaddle.reset();
        this.rightPaddle.reset();
        this.leftScore = 0;
        this.rightScore = 0;
        this.paused = false;
    }
}

// Game Manager
class GameManager {
    constructor() {
        this.currentState = 'menu';
        this.menu = new Menu();
        this.physicsGame = new PhysicsGame();
        this.winner = null;
    }

    update(input) {
        switch (this.currentState) {
            case 'menu':
                this.updateMenu(input);
                break;
            case 'physics':
                this.updatePhysicsGame(input);
                break;
            case 'gameOver':
                this.updateGameOver(input);
                break;
        }
    }

    updateMenu(input) {
        if (input.left || input.right) {
            this.menu.toggleMode();
        }
        if (input.space) {
            const mode = this.menu.getSelectedMode();
            this.currentState = mode;
        }
    }

    updatePhysicsGame(input) {
        if (input.m || input.escape) {
            this.currentState = 'menu';
            this.physicsGame.reset();
            return;
        }

        const gameEnded = this.physicsGame.update(input);
        if (gameEnded) {
            this.winner = this.physicsGame.getWinner();
            this.currentState = 'gameOver';
        }
    }

    updateGameOver(input) {
        if (input.space || input.r) {
            this.currentState = 'menu';
            this.winner = null;
            this.physicsGame.reset();
        }
    }

    draw(ctx) {
        switch (this.currentState) {
            case 'menu':
                this.menu.draw(ctx);
                break;
            case 'physics':
                this.physicsGame.draw(ctx);
                break;
            case 'gameOver':
                this.drawGameOver(ctx);
                break;
        }
    }

    drawGameOver(ctx) {
        // Clear canvas
        ctx.fillStyle = 'rgb(0, 0, 0)';
        ctx.fillRect(0, 0, WIDTH, HEIGHT);

        // Draw winner text
        if (this.winner) {
            ctx.fillStyle = `rgb(${COLORS.PURPLE[0]}, ${COLORS.PURPLE[1]}, ${COLORS.PURPLE[2]})`;
            ctx.font = '48px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(this.winner, WIDTH / 2, HEIGHT / 2 - 20);

            ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
            ctx.font = '16px monospace';
            ctx.fillText("Press [SPACE] or [R] to return to menu", WIDTH / 2, HEIGHT / 2 + 20);
        }
    }
}

// Main game class
class PongGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        if (!this.canvas) {
            throw new Error('Canvas element not found');
        }

        this.ctx = this.canvas.getContext('2d');
        if (!this.ctx) {
            throw new Error('Could not get 2D context');
        }

        this.gameManager = new GameManager();
        this.inputHandler = new InputHandler();

        this.hideLoading();
        this.startGameLoop();
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.classList.add('hidden');
        }
    }

    startGameLoop() {
        const gameLoop = (currentTime) => {
            const deltaTime = currentTime - this.lastTime;
            this.lastTime = currentTime;

            // Update game at target FPS
            if (deltaTime >= 1000 / FPS) {
                this.update();
                this.render();
            }

            this.gameLoopId = requestAnimationFrame(gameLoop);
        };

        this.gameLoopId = requestAnimationFrame(gameLoop);
    }

    update() {
        const input = this.inputHandler.keys;
        this.gameManager.update(input);
    }

    render() {
        this.gameManager.draw(this.ctx);
    }

    destroy() {
        if (this.gameLoopId) {
            cancelAnimationFrame(this.gameLoopId);
        }
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    try {
        new PongGame();
    } catch (error) {
        console.error('Failed to initialize game:', error);
        const loading = document.getElementById('loading');
        if (loading) {
            loading.textContent = 'Failed to load game. Please refresh the page.';
        }
    }
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    // Cleanup if needed
});
