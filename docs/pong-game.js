/**
 * PongWithIssues - Mobile-friendly web version
 * Supports touch controls, responsive scaling, and 2-player local multiplayer
 */

// ============================================================
// CONSTANTS
// ============================================================
const COLORS = {
    BLACK: [0, 0, 0],
    WHITE: [255, 255, 255],
    PURPLE: [122, 118, 229],
    LIGHT_PURPLE: [185, 183, 232],
    RED: [255, 0, 0],
    YELLOW: [255, 255, 0],
    GREY: [128, 128, 128],
    DARK_GREY: [60, 60, 60],
    DARK_RED: [139, 0, 0],
    SCARLET: [255, 36, 0],
    ORANGE_RED: [255, 69, 0],
    ORANGE: [255, 140, 0],
    GOLD: [255, 215, 0],
    GREEN: [0, 200, 80],
};

const GAME_WIDTH = 800;
const GAME_HEIGHT = 600;
const FPS = 60;
const FRAME_TIME = 1000 / FPS;
const WINNING_SCORE = 5;

const PADDLE_WIDTH = 15;
const PADDLE_HEIGHT = 90;
const PADDLE_DEFAULT_VEL = 5;
const PADDLE_MAX_VEL = 9;
const PADDLE_DEFAULT_ACC = 3;

const BALL_RADIUS = 8;
const BALL_DEFAULT_VEL = 5;
const MAX_DEFLECTION_SPEED = 7;
const SPIN_FACTOR = 0.5;

// ============================================================
// INPUT HANDLER (Keyboard + Touch)
// ============================================================
class InputHandler {
    constructor(canvas) {
        this.canvas = canvas;
        this.isMobile = this.detectMobile();

        // Keyboard state
        this.keys = {};

        // Touch state - each player has a touch zone
        this.touches = {
            left: { active: false, y: 0, startY: 0, id: null },
            right: { active: false, y: 0, startY: 0, id: null },
            tap: false,
            doubleTap: false,
        };

        this.lastTapTime = 0;
        this.menuTap = false;
        this.menuTapPos = { x: 0, y: 0 };

        this.setupKeyboard();
        this.setupTouch();
    }

    detectMobile() {
        return ('ontouchstart' in window) ||
            (navigator.maxTouchPoints > 0) ||
            window.matchMedia('(pointer: coarse)').matches;
    }

    setupKeyboard() {
        document.addEventListener('keydown', (e) => {
            this.keys[e.code] = true;
            e.preventDefault();
        });
        document.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
            e.preventDefault();
        });
    }

    setupTouch() {
        this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: false });
        this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: false });
        this.canvas.addEventListener('touchend', (e) => this.handleTouchEnd(e), { passive: false });
        this.canvas.addEventListener('touchcancel', (e) => this.handleTouchEnd(e), { passive: false });
    }

    getCanvasPos(touch) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = GAME_WIDTH / rect.width;
        const scaleY = GAME_HEIGHT / rect.height;
        return {
            x: (touch.clientX - rect.left) * scaleX,
            y: (touch.clientY - rect.top) * scaleY,
        };
    }

    handleTouchStart(e) {
        e.preventDefault();
        const now = Date.now();

        for (const touch of e.changedTouches) {
            const pos = this.getCanvasPos(touch);

            // Double-tap detection
            if (now - this.lastTapTime < 300) {
                this.touches.doubleTap = true;
            }
            this.lastTapTime = now;
            this.menuTap = true;
            this.menuTapPos = pos;

            // Assign touch to left or right zone
            if (pos.x < GAME_WIDTH / 2) {
                this.touches.left = { active: true, y: pos.y, startY: pos.y, id: touch.identifier };
            } else {
                this.touches.right = { active: true, y: pos.y, startY: pos.y, id: touch.identifier };
            }
        }

        this.touches.tap = true;
    }

    handleTouchMove(e) {
        e.preventDefault();
        for (const touch of e.changedTouches) {
            const pos = this.getCanvasPos(touch);

            if (this.touches.left.id === touch.identifier) {
                this.touches.left.y = pos.y;
            }
            if (this.touches.right.id === touch.identifier) {
                this.touches.right.y = pos.y;
            }
        }
    }

    handleTouchEnd(e) {
        e.preventDefault();
        for (const touch of e.changedTouches) {
            if (this.touches.left.id === touch.identifier) {
                this.touches.left.active = false;
                this.touches.left.id = null;
            }
            if (this.touches.right.id === touch.identifier) {
                this.touches.right.active = false;
                this.touches.right.id = null;
            }
        }
    }

    // Called once per frame to consume single-frame events
    consumeEvents() {
        this.touches.tap = false;
        this.touches.doubleTap = false;
        this.menuTap = false;
    }

    isKeyDown(code) {
        return !!this.keys[code];
    }
}

// ============================================================
// BALL
// ============================================================
class Ball {
    constructor(x, y, radius, color, velX = BALL_DEFAULT_VEL, velY = 0) {
        this.pos = { x, y };
        this.originalPos = { x, y };
        this.radius = radius;
        this.color = [...color];
        this.vel = { x: velX, y: velY };
        this.originalVelX = velX;
        this.spin = 0;
        this.trail = [];
        this.maxTrail = 12;
    }

    draw(ctx) {
        const FIRE_COLORS = [COLORS.DARK_RED, COLORS.SCARLET, COLORS.ORANGE_RED, COLORS.ORANGE, COLORS.GOLD, COLORS.YELLOW, COLORS.WHITE];

        // Draw trail
        for (let i = 0; i < this.trail.length; i++) {
            const pos = this.trail[i];
            const alpha = Math.max(0.05, 1 - i / this.trail.length);
            const radius = Math.max(2, this.radius * (1 - i / this.trail.length * 0.8));
            const colorIdx = Math.min(FIRE_COLORS.length - 1, Math.floor((i / this.trail.length) * (FIRE_COLORS.length - 1)));
            const trailColor = FIRE_COLORS[colorIdx];

            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.fillStyle = `rgb(${trailColor[0]},${trailColor[1]},${trailColor[2]})`;
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        // Draw glow when moving fast
        const speed = this.speed;
        if (speed > 8) {
            ctx.save();
            ctx.globalAlpha = Math.min(0.4, (speed - 8) * 0.05);
            ctx.shadowColor = `rgb(${this.color[0]},${this.color[1]},${this.color[2]})`;
            ctx.shadowBlur = 15;
            ctx.fillStyle = `rgb(${this.color[0]},${this.color[1]},${this.color[2]})`;
            ctx.beginPath();
            ctx.arc(this.pos.x, this.pos.y, this.radius * 1.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        // Draw main ball
        ctx.fillStyle = `rgb(${this.color[0]},${this.color[1]},${this.color[2]})`;
        ctx.beginPath();
        ctx.arc(this.pos.x, this.pos.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
    }

    move() {
        this.vel.y += this.spin * 0.1;
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
        this.pos.x += this.vel.x;
        this.pos.y += this.vel.y;
        if (this.pos.x - this.radius <= 0 || this.pos.x + this.radius >= width) {
            this.vel.x *= -1;
            this.pos.x = Math.max(this.radius, Math.min(width - this.radius, this.pos.x));
        }
        if (this.pos.y - this.radius <= 0 || this.pos.y + this.radius >= height) {
            this.vel.y *= -1;
            this.pos.y = Math.max(this.radius, Math.min(height - this.radius, this.pos.y));
        }
    }

    reset(direction) {
        this.pos = { ...this.originalPos };
        this.vel = { x: direction ? this.originalVelX : -this.originalVelX, y: 0 };
        this.spin = 0;
        this.trail = [];
    }

    get speed() {
        return Math.sqrt(this.vel.x * this.vel.x + this.vel.y * this.vel.y);
    }
}

// ============================================================
// PADDLE
// ============================================================
class Paddle {
    constructor(x, y, width, height, color = COLORS.LIGHT_PURPLE) {
        this.pos = { x, y };
        this.originalPos = { x, y };
        this.width = width;
        this.height = height;
        this.color = [...color];
        this.vel = { x: 0, y: 0 };
        this.acc = { x: 0, y: 0 };
    }

    draw(ctx) {
        // Draw paddle with slight rounded corners
        const r = 3;
        ctx.fillStyle = `rgb(${this.color[0]},${this.color[1]},${this.color[2]})`;
        ctx.beginPath();
        ctx.moveTo(this.pos.x + r, this.pos.y);
        ctx.lineTo(this.pos.x + this.width - r, this.pos.y);
        ctx.quadraticCurveTo(this.pos.x + this.width, this.pos.y, this.pos.x + this.width, this.pos.y + r);
        ctx.lineTo(this.pos.x + this.width, this.pos.y + this.height - r);
        ctx.quadraticCurveTo(this.pos.x + this.width, this.pos.y + this.height, this.pos.x + this.width - r, this.pos.y + this.height);
        ctx.lineTo(this.pos.x + r, this.pos.y + this.height);
        ctx.quadraticCurveTo(this.pos.x, this.pos.y + this.height, this.pos.x, this.pos.y + this.height - r);
        ctx.lineTo(this.pos.x, this.pos.y + r);
        ctx.quadraticCurveTo(this.pos.x, this.pos.y, this.pos.x + r, this.pos.y);
        ctx.fill();
    }

    accelerate(up) {
        this.acc.y += up ? -PADDLE_DEFAULT_ACC : PADDLE_DEFAULT_ACC;
    }

    moveToward(targetY) {
        const centerY = this.pos.y + this.height / 2;
        const diff = targetY - centerY;
        if (Math.abs(diff) > 5) {
            this.acc.y += Math.sign(diff) * PADDLE_DEFAULT_ACC;
        }
    }

    update() {
        this.vel.x += this.acc.x;
        this.vel.y += this.acc.y;
        this.acc.x = 0;
        this.acc.y = 0;

        this.vel.y = Math.max(-PADDLE_MAX_VEL, Math.min(PADDLE_MAX_VEL, this.vel.y));

        this.pos.x += this.vel.x;
        this.pos.y += this.vel.y;

        this.vel.y *= 0.85;

        if (this.pos.y < 0) {
            this.pos.y = 0;
            this.vel.y = 0;
        } else if (this.pos.y + this.height > GAME_HEIGHT) {
            this.pos.y = GAME_HEIGHT - this.height;
            this.vel.y = 0;
        }
    }

    // Simpler movement for Classic mode (no acceleration, instant velocity)
    moveClassic(up) {
        this.vel.y = up ? -PADDLE_DEFAULT_VEL : PADDLE_DEFAULT_VEL;
    }

    updateClassic() {
        this.pos.y += this.vel.y;
        this.vel.y = 0;

        if (this.pos.y < 0) {
            this.pos.y = 0;
        } else if (this.pos.y + this.height > GAME_HEIGHT) {
            this.pos.y = GAME_HEIGHT - this.height;
        }
    }

    reset() {
        this.pos = { ...this.originalPos };
        this.vel = { x: 0, y: 0 };
        this.acc = { x: 0, y: 0 };
    }

    get centerY() {
        return this.pos.y + this.height / 2;
    }
}

// ============================================================
// COLLISION DETECTION
// ============================================================
class CollisionDetection {
    static checkBallPaddle(ball, paddle) {
        return ball.pos.x + ball.radius >= paddle.pos.x &&
               ball.pos.x - ball.radius <= paddle.pos.x + paddle.width &&
               ball.pos.y + ball.radius >= paddle.pos.y &&
               ball.pos.y - ball.radius <= paddle.pos.y + paddle.height;
    }

    static resolveBallPaddle(ball, paddle, isLeft) {
        const relY = (ball.pos.y - paddle.pos.y) / paddle.height;
        const normalized = (relY - 0.5) * 2; // -1 to 1

        const speed = Math.max(ball.speed, BALL_DEFAULT_VEL);
        const maxAngle = Math.PI / 4;
        const angle = normalized * maxAngle;

        if (isLeft) {
            ball.vel.x = Math.cos(angle) * speed;
            ball.vel.y = Math.sin(angle) * speed;
            ball.pos.x = paddle.pos.x + paddle.width + ball.radius;
        } else {
            ball.vel.x = -Math.cos(angle) * speed;
            ball.vel.y = Math.sin(angle) * speed;
            ball.pos.x = paddle.pos.x - ball.radius;
        }

        // Transfer spin from paddle velocity
        ball.spin += paddle.vel.y * SPIN_FACTOR;
        ball.spin = Math.max(-10, Math.min(10, ball.spin));

        // Clamp vertical velocity
        ball.vel.y = Math.max(-MAX_DEFLECTION_SPEED, Math.min(MAX_DEFLECTION_SPEED, ball.vel.y));
    }

    static handleWalls(ball) {
        if (ball.pos.y - ball.radius <= 0) {
            ball.vel.y = Math.abs(ball.vel.y);
            ball.pos.y = ball.radius;
        } else if (ball.pos.y + ball.radius >= GAME_HEIGHT) {
            ball.vel.y = -Math.abs(ball.vel.y);
            ball.pos.y = GAME_HEIGHT - ball.radius;
        }
    }
}

// ============================================================
// SIMPLE AI
// ============================================================
class SimpleAI {
    constructor(difficulty = 0.7) {
        this.difficulty = difficulty; // 0 to 1
        this.reactionDelay = 0;
        this.targetY = GAME_HEIGHT / 2;
    }

    update(paddle, ball) {
        // Only react when ball is moving toward this paddle
        if (ball.vel.x > 0) {
            this.reactionDelay++;
            if (this.reactionDelay > (1 - this.difficulty) * 15) {
                this.targetY = ball.pos.y + (Math.random() - 0.5) * (1 - this.difficulty) * 80;
                this.reactionDelay = 0;
            }
        } else {
            // Return to center slowly when ball moving away
            this.targetY = GAME_HEIGHT / 2;
        }

        paddle.moveToward(this.targetY);
    }
}

// ============================================================
// MENU
// ============================================================
class Menu {
    constructor(isMobile) {
        this.ball = new Ball(GAME_WIDTH / 2, GAME_HEIGHT / 2, BALL_RADIUS, COLORS.WHITE, 4, 3);
        this.selectedMode = 0; // 0=Classic, 1=Physics
        this.selectedPlayers = 0; // 0=2P, 1=vs AI
        this.activeRow = 0; // 0=mode, 1=players
        this.isMobile = isMobile;
        this.animTime = 0;
    }

    draw(ctx) {
        ctx.fillStyle = 'rgb(0,0,0)';
        ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

        this.animTime += 0.02;

        // Title
        ctx.fillStyle = `rgb(${COLORS.PURPLE[0]},${COLORS.PURPLE[1]},${COLORS.PURPLE[2]})`;
        ctx.font = 'bold 42px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('PONG WITH ISSUES', GAME_WIDTH / 2, 100);

        // Subtitle
        ctx.fillStyle = `rgb(${COLORS.GREY[0]},${COLORS.GREY[1]},${COLORS.GREY[2]})`;
        ctx.font = '14px monospace';
        ctx.fillText("A project that probably works. Sometimes. Maybe.", GAME_WIDTH / 2, 135);

        // Mode selection
        const modeY = 220;
        const modeHighlight = this.activeRow === 0;
        ctx.fillStyle = modeHighlight ? `rgb(${COLORS.LIGHT_PURPLE[0]},${COLORS.LIGHT_PURPLE[1]},${COLORS.LIGHT_PURPLE[2]})` : `rgb(${COLORS.GREY[0]},${COLORS.GREY[1]},${COLORS.GREY[2]})`;
        ctx.font = '16px monospace';
        ctx.fillText('GAME MODE', GAME_WIDTH / 2, modeY - 25);

        const modes = ['Classic', 'Physics'];
        for (let i = 0; i < modes.length; i++) {
            const x = GAME_WIDTH / 2 + (i - 0.5) * 160;
            const selected = this.selectedMode === i;
            if (selected && modeHighlight) {
                ctx.fillStyle = `rgb(${COLORS.PURPLE[0]},${COLORS.PURPLE[1]},${COLORS.PURPLE[2]})`;
                ctx.fillRect(x - 65, modeY - 15, 130, 30);
                ctx.fillStyle = 'rgb(255,255,255)';
            } else if (selected) {
                ctx.fillStyle = `rgb(${COLORS.DARK_GREY[0]},${COLORS.DARK_GREY[1]},${COLORS.DARK_GREY[2]})`;
                ctx.fillRect(x - 65, modeY - 15, 130, 30);
                ctx.fillStyle = 'rgb(200,200,200)';
            } else {
                ctx.fillStyle = `rgb(${COLORS.GREY[0]},${COLORS.GREY[1]},${COLORS.GREY[2]})`;
            }
            ctx.font = '18px monospace';
            ctx.fillText(modes[i], x, modeY + 5);
        }

        // Players selection
        const playersY = 310;
        const playersHighlight = this.activeRow === 1;
        ctx.fillStyle = playersHighlight ? `rgb(${COLORS.LIGHT_PURPLE[0]},${COLORS.LIGHT_PURPLE[1]},${COLORS.LIGHT_PURPLE[2]})` : `rgb(${COLORS.GREY[0]},${COLORS.GREY[1]},${COLORS.GREY[2]})`;
        ctx.font = '16px monospace';
        ctx.fillText('PLAYERS', GAME_WIDTH / 2, playersY - 25);

        const players = ['2 Players', 'vs AI'];
        for (let i = 0; i < players.length; i++) {
            const x = GAME_WIDTH / 2 + (i - 0.5) * 160;
            const selected = this.selectedPlayers === i;
            if (selected && playersHighlight) {
                ctx.fillStyle = `rgb(${COLORS.PURPLE[0]},${COLORS.PURPLE[1]},${COLORS.PURPLE[2]})`;
                ctx.fillRect(x - 65, playersY - 15, 130, 30);
                ctx.fillStyle = 'rgb(255,255,255)';
            } else if (selected) {
                ctx.fillStyle = `rgb(${COLORS.DARK_GREY[0]},${COLORS.DARK_GREY[1]},${COLORS.DARK_GREY[2]})`;
                ctx.fillRect(x - 65, playersY - 15, 130, 30);
                ctx.fillStyle = 'rgb(200,200,200)';
            } else {
                ctx.fillStyle = `rgb(${COLORS.GREY[0]},${COLORS.GREY[1]},${COLORS.GREY[2]})`;
            }
            ctx.font = '18px monospace';
            ctx.fillText(players[i], x, playersY + 5);
        }

        // Start prompt
        const pulse = Math.sin(this.animTime * 3) * 0.3 + 0.7;
        ctx.globalAlpha = pulse;
        ctx.fillStyle = `rgb(${COLORS.GREEN[0]},${COLORS.GREEN[1]},${COLORS.GREEN[2]})`;
        ctx.font = 'bold 20px monospace';
        if (this.isMobile) {
            ctx.fillText('TAP HERE TO START', GAME_WIDTH / 2, 420);
        } else {
            ctx.fillText('Press [SPACE] to start', GAME_WIDTH / 2, 420);
        }
        ctx.globalAlpha = 1;

        // Controls help
        ctx.fillStyle = `rgb(${COLORS.DARK_GREY[0]},${COLORS.DARK_GREY[1]},${COLORS.DARK_GREY[2]})`;
        ctx.font = '12px monospace';
        if (this.isMobile) {
            ctx.fillText('Tap left/right options to change settings', GAME_WIDTH / 2, 470);
            ctx.fillText('Touch left side = P1 | Touch right side = P2', GAME_WIDTH / 2, 490);
        } else {
            ctx.fillText('[UP/DOWN] switch row | [LEFT/RIGHT] change option | [SPACE] start', GAME_WIDTH / 2, 470);
            ctx.fillText('P1: W/S keys | P2: Arrow keys', GAME_WIDTH / 2, 490);
        }

        // Draw bouncing ball
        this.ball.color = this.selectedMode === 0 ? COLORS.WHITE : COLORS.ORANGE;
        this.ball.draw(ctx);
        this.ball.bounceBox(GAME_WIDTH, GAME_HEIGHT);
    }

    handleInput(input) {
        // Keyboard navigation
        if (input.isKeyDown('ArrowUp') || input.isKeyDown('KeyW')) {
            this.activeRow = 0;
        }
        if (input.isKeyDown('ArrowDown') || input.isKeyDown('KeyS')) {
            this.activeRow = 1;
        }

        // Touch/tap on menu items
        if (input.menuTap) {
            const pos = input.menuTapPos;

            // Mode row tap detection
            if (pos.y > 180 && pos.y < 260) {
                if (pos.x < GAME_WIDTH / 2) this.selectedMode = 0;
                else this.selectedMode = 1;
                this.activeRow = 0;
                return false;
            }

            // Players row tap detection
            if (pos.y > 270 && pos.y < 350) {
                if (pos.x < GAME_WIDTH / 2) this.selectedPlayers = 0;
                else this.selectedPlayers = 1;
                this.activeRow = 1;
                return false;
            }

            // Start button tap
            if (pos.y > 390 && pos.y < 450) {
                return true; // Start game
            }
        }

        return false;
    }

    // Returns true when user wants to start
    handleKeySelect(input) {
        if (input.isKeyDown('ArrowLeft') || input.isKeyDown('KeyA')) {
            if (this.activeRow === 0) this.selectedMode = 0;
            else this.selectedPlayers = 0;
        }
        if (input.isKeyDown('ArrowRight') || input.isKeyDown('KeyD')) {
            if (this.activeRow === 0) this.selectedMode = 1;
            else this.selectedPlayers = 1;
        }
        return false;
    }
}

// ============================================================
// GAME (handles both Classic and Physics modes)
// ============================================================
class PongMatch {
    constructor(mode, vsAI, isMobile) {
        this.mode = mode; // 'classic' or 'physics'
        this.vsAI = vsAI;
        this.isMobile = isMobile;

        const paddleOffset = 20;
        this.leftPaddle = new Paddle(
            paddleOffset, GAME_HEIGHT / 2 - PADDLE_HEIGHT / 2,
            PADDLE_WIDTH, PADDLE_HEIGHT, COLORS.LIGHT_PURPLE
        );
        this.rightPaddle = new Paddle(
            GAME_WIDTH - paddleOffset - PADDLE_WIDTH, GAME_HEIGHT / 2 - PADDLE_HEIGHT / 2,
            PADDLE_WIDTH, PADDLE_HEIGHT, COLORS.LIGHT_PURPLE
        );

        const ballColor = mode === 'classic' ? COLORS.WHITE : COLORS.YELLOW;
        this.ball = new Ball(GAME_WIDTH / 2, GAME_HEIGHT / 2, BALL_RADIUS, ballColor, BALL_DEFAULT_VEL, 0);

        this.leftScore = 0;
        this.rightScore = 0;
        this.paused = false;
        this.showHelp = false;
        this.serveDirection = Math.random() < 0.5;

        if (vsAI) {
            this.ai = new SimpleAI(0.65);
        }

        // Countdown timer for serve
        this.serveCountdown = 60; // 1 second at 60fps
        this.serving = true;
    }

    update(input) {
        // Handle pause (keyboard only, double-tap on mobile)
        if (input.isKeyDown('Space') && !this._spaceWas) {
            this.paused = !this.paused;
        }
        this._spaceWas = input.isKeyDown('Space');

        if (input.touches.doubleTap && this.isMobile) {
            this.paused = !this.paused;
        }

        if (input.isKeyDown('KeyH') && !this._hWas) {
            this.showHelp = !this.showHelp;
        }
        this._hWas = input.isKeyDown('KeyH');

        if (this.leftScore >= WINNING_SCORE || this.rightScore >= WINNING_SCORE) {
            return 'gameover';
        }

        if (input.isKeyDown('KeyM') || input.isKeyDown('Escape')) {
            return 'menu';
        }
        if (input.isKeyDown('KeyR') && !this._rWas) {
            this.reset();
        }
        this._rWas = input.isKeyDown('KeyR');

        if (this.paused) return 'playing';

        // Serve countdown
        if (this.serving) {
            this.serveCountdown--;
            if (this.serveCountdown <= 0) {
                this.serving = false;
            }
            return 'playing';
        }

        // --- Left paddle input ---
        if (this.isMobile && input.touches.left.active) {
            this.handleTouchPaddle(this.leftPaddle, input.touches.left);
        } else {
            if (this.mode === 'classic') {
                if (input.isKeyDown('KeyW')) this.leftPaddle.moveClassic(true);
                else if (input.isKeyDown('KeyS')) this.leftPaddle.moveClassic(false);
            } else {
                if (input.isKeyDown('KeyW')) this.leftPaddle.accelerate(true);
                if (input.isKeyDown('KeyS')) this.leftPaddle.accelerate(false);
            }
        }

        // --- Right paddle input ---
        if (this.vsAI) {
            this.ai.update(this.rightPaddle, this.ball);
        } else if (this.isMobile && input.touches.right.active) {
            this.handleTouchPaddle(this.rightPaddle, input.touches.right);
        } else {
            if (this.mode === 'classic') {
                if (input.isKeyDown('ArrowUp')) this.rightPaddle.moveClassic(true);
                else if (input.isKeyDown('ArrowDown')) this.rightPaddle.moveClassic(false);
            } else {
                if (input.isKeyDown('ArrowUp')) this.rightPaddle.accelerate(true);
                if (input.isKeyDown('ArrowDown')) this.rightPaddle.accelerate(false);
            }
        }

        // Update paddles
        if (this.mode === 'classic') {
            this.leftPaddle.updateClassic();
            this.rightPaddle.updateClassic();
        } else {
            this.leftPaddle.update();
            this.rightPaddle.update();
        }

        // Update ball
        if (this.mode === 'classic') {
            this.ball.pos.x += this.ball.vel.x;
            this.ball.pos.y += this.ball.vel.y;
        } else {
            this.ball.update();
        }

        // Collisions
        CollisionDetection.handleWalls(this.ball);

        if (CollisionDetection.checkBallPaddle(this.ball, this.leftPaddle)) {
            CollisionDetection.resolveBallPaddle(this.ball, this.leftPaddle, true);
        }
        if (CollisionDetection.checkBallPaddle(this.ball, this.rightPaddle)) {
            CollisionDetection.resolveBallPaddle(this.ball, this.rightPaddle, false);
        }

        // Scoring
        if (this.ball.pos.x - this.ball.radius < 0) {
            this.rightScore++;
            this.startServe(true);
        } else if (this.ball.pos.x + this.ball.radius > GAME_WIDTH) {
            this.leftScore++;
            this.startServe(false);
        }

        return 'playing';
    }

    handleTouchPaddle(paddle, touch) {
        // Move paddle toward touch Y position
        paddle.moveToward(touch.y);
    }

    startServe(direction) {
        this.ball.reset(direction);
        this.serving = true;
        this.serveCountdown = 45;
    }

    draw(ctx) {
        // Background
        ctx.fillStyle = 'rgb(0,0,0)';
        ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

        // Touch zones indicator (mobile only, subtle)
        if (this.isMobile) {
            ctx.save();
            ctx.strokeStyle = 'rgba(122, 118, 229, 0.15)';
            ctx.lineWidth = 1;
            ctx.setLineDash([5, 10]);
            ctx.beginPath();
            ctx.moveTo(GAME_WIDTH / 2, 0);
            ctx.lineTo(GAME_WIDTH / 2, GAME_HEIGHT);
            ctx.stroke();
            ctx.setLineDash([]);
            ctx.restore();
        }

        // Center line
        ctx.strokeStyle = 'rgba(128,128,128,0.5)';
        ctx.lineWidth = 2;
        ctx.setLineDash([8, 12]);
        ctx.beginPath();
        ctx.moveTo(GAME_WIDTH / 2, 0);
        ctx.lineTo(GAME_WIDTH / 2, GAME_HEIGHT);
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw paddles
        this.leftPaddle.draw(ctx);
        this.rightPaddle.draw(ctx);

        // Draw ball (skip during serve countdown for blink effect)
        if (!this.serving || Math.floor(this.serveCountdown / 10) % 2 === 0) {
            this.ball.draw(ctx);
        }

        // Scores
        ctx.fillStyle = 'rgba(255,255,255,0.9)';
        ctx.font = 'bold 48px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(this.leftScore.toString(), GAME_WIDTH / 4, 55);
        ctx.fillText(this.rightScore.toString(), 3 * GAME_WIDTH / 4, 55);

        // Mode label
        ctx.fillStyle = 'rgba(128,128,128,0.6)';
        ctx.font = '12px monospace';
        ctx.textAlign = 'left';
        const modeLabel = this.mode === 'classic' ? 'CLASSIC' : 'PHYSICS';
        const playerLabel = this.vsAI ? 'vs AI' : '2P';
        ctx.fillText(`${modeLabel} | ${playerLabel}`, 10, GAME_HEIGHT - 10);

        // Serve countdown
        if (this.serving && this.serveCountdown > 15) {
            ctx.fillStyle = `rgb(${COLORS.PURPLE[0]},${COLORS.PURPLE[1]},${COLORS.PURPLE[2]})`;
            ctx.font = 'bold 24px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('READY', GAME_WIDTH / 2, GAME_HEIGHT / 2 - 30);
        }

        // Pause overlay
        if (this.paused) {
            ctx.fillStyle = 'rgba(0,0,0,0.7)';
            ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

            ctx.fillStyle = `rgb(${COLORS.PURPLE[0]},${COLORS.PURPLE[1]},${COLORS.PURPLE[2]})`;
            ctx.font = 'bold 42px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('PAUSED', GAME_WIDTH / 2, GAME_HEIGHT / 2 - 20);

            ctx.fillStyle = `rgb(${COLORS.GREY[0]},${COLORS.GREY[1]},${COLORS.GREY[2]})`;
            ctx.font = '14px monospace';
            if (this.isMobile) {
                ctx.fillText('Double-tap to resume', GAME_WIDTH / 2, GAME_HEIGHT / 2 + 20);
            } else {
                ctx.fillText('Press [SPACE] to resume', GAME_WIDTH / 2, GAME_HEIGHT / 2 + 20);
                ctx.fillText('[R] restart | [M] menu | [ESC] quit', GAME_WIDTH / 2, GAME_HEIGHT / 2 + 45);
            }
        }

        // Help text
        if (this.showHelp || (this.isMobile && !this.paused)) {
            ctx.fillStyle = 'rgba(128,128,128,0.5)';
            ctx.font = '11px monospace';
            ctx.textAlign = 'right';
            if (this.isMobile) {
                ctx.fillText('Touch & drag to move paddles', GAME_WIDTH - 10, GAME_HEIGHT - 10);
            } else {
                ctx.fillText('[H] help | [SPACE] pause | [R] restart | [M] menu', GAME_WIDTH - 10, GAME_HEIGHT - 10);
            }
        }

        // Physics debug (physics mode only)
        if (this.mode === 'physics' && !this.isMobile) {
            ctx.fillStyle = 'rgba(128,128,128,0.4)';
            ctx.font = '10px monospace';
            ctx.textAlign = 'left';
            ctx.fillText(`vel: [${this.ball.vel.x.toFixed(1)}, ${this.ball.vel.y.toFixed(1)}]  spin: ${this.ball.spin.toFixed(2)}`, 10, 20);
        }
    }

    getWinner() {
        if (this.leftScore >= WINNING_SCORE) return this.vsAI ? 'You Win!' : 'Player 1 Wins!';
        if (this.rightScore >= WINNING_SCORE) return this.vsAI ? 'AI Wins!' : 'Player 2 Wins!';
        return null;
    }

    reset() {
        this.leftScore = 0;
        this.rightScore = 0;
        this.leftPaddle.reset();
        this.rightPaddle.reset();
        this.ball.reset(Math.random() < 0.5);
        this.paused = false;
        this.serving = true;
        this.serveCountdown = 60;
    }
}

// ============================================================
// GAME OVER SCREEN
// ============================================================
class GameOverScreen {
    constructor(winner, isMobile) {
        this.winner = winner;
        this.isMobile = isMobile;
        this.animTime = 0;
    }

    draw(ctx) {
        this.animTime += 0.03;

        ctx.fillStyle = 'rgb(0,0,0)';
        ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

        // Winner text with subtle animation
        const yOffset = Math.sin(this.animTime * 2) * 5;
        ctx.fillStyle = `rgb(${COLORS.PURPLE[0]},${COLORS.PURPLE[1]},${COLORS.PURPLE[2]})`;
        ctx.font = 'bold 40px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(this.winner, GAME_WIDTH / 2, GAME_HEIGHT / 2 - 30 + yOffset);

        const pulse = Math.sin(this.animTime * 3) * 0.3 + 0.7;
        ctx.globalAlpha = pulse;
        ctx.fillStyle = `rgb(${COLORS.GREY[0]},${COLORS.GREY[1]},${COLORS.GREY[2]})`;
        ctx.font = '16px monospace';
        if (this.isMobile) {
            ctx.fillText('Tap to return to menu', GAME_WIDTH / 2, GAME_HEIGHT / 2 + 30);
        } else {
            ctx.fillText('Press [SPACE] or [R] to return to menu', GAME_WIDTH / 2, GAME_HEIGHT / 2 + 30);
        }
        ctx.globalAlpha = 1;
    }
}

// ============================================================
// GAME MANAGER
// ============================================================
class GameManager {
    constructor(isMobile) {
        this.isMobile = isMobile;
        this.state = 'menu';
        this.menu = new Menu(isMobile);
        this.match = null;
        this.gameOverScreen = null;

        // Debounce for menu key navigation
        this._leftWas = false;
        this._rightWas = false;
        this._upWas = false;
        this._downWas = false;
        this._spaceWas = false;
    }

    update(input) {
        switch (this.state) {
            case 'menu':
                this.updateMenu(input);
                break;
            case 'playing':
                this.updatePlaying(input);
                break;
            case 'gameover':
                this.updateGameOver(input);
                break;
        }
    }

    updateMenu(input) {
        // Keyboard debounced navigation
        const leftNow = input.isKeyDown('ArrowLeft') || input.isKeyDown('KeyA');
        const rightNow = input.isKeyDown('ArrowRight') || input.isKeyDown('KeyD');
        const upNow = input.isKeyDown('ArrowUp') || input.isKeyDown('KeyW');
        const downNow = input.isKeyDown('ArrowDown') || input.isKeyDown('KeyS');
        const spaceNow = input.isKeyDown('Space');

        if (leftNow && !this._leftWas) {
            if (this.menu.activeRow === 0) this.menu.selectedMode = 0;
            else this.menu.selectedPlayers = 0;
        }
        if (rightNow && !this._rightWas) {
            if (this.menu.activeRow === 0) this.menu.selectedMode = 1;
            else this.menu.selectedPlayers = 1;
        }
        if (upNow && !this._upWas) {
            this.menu.activeRow = 0;
        }
        if (downNow && !this._downWas) {
            this.menu.activeRow = 1;
        }

        this._leftWas = leftNow;
        this._rightWas = rightNow;
        this._upWas = upNow;
        this._downWas = downNow;

        // Space to start
        if (spaceNow && !this._spaceWas) {
            this.startGame();
        }
        this._spaceWas = spaceNow;

        // Touch handling
        if (this.menu.handleInput(input)) {
            this.startGame();
        }
    }

    startGame() {
        const mode = this.menu.selectedMode === 0 ? 'classic' : 'physics';
        const vsAI = this.menu.selectedPlayers === 1;
        this.match = new PongMatch(mode, vsAI, this.isMobile);
        this.state = 'playing';
    }

    updatePlaying(input) {
        const result = this.match.update(input);
        if (result === 'gameover') {
            this.gameOverScreen = new GameOverScreen(this.match.getWinner(), this.isMobile);
            this.state = 'gameover';
        } else if (result === 'menu') {
            this.state = 'menu';
            this.match = null;
        }
    }

    updateGameOver(input) {
        if (input.isKeyDown('Space') || input.isKeyDown('KeyR') || input.touches.tap) {
            this.state = 'menu';
            this.match = null;
            this.gameOverScreen = null;
        }
    }

    draw(ctx) {
        switch (this.state) {
            case 'menu':
                this.menu.draw(ctx);
                break;
            case 'playing':
                if (this.match) this.match.draw(ctx);
                break;
            case 'gameover':
                if (this.gameOverScreen) this.gameOverScreen.draw(ctx);
                break;
        }
    }
}

// ============================================================
// MAIN APP - Canvas scaling & game loop
// ============================================================
class PongApp {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.container = document.getElementById('gameContainer');

        // Set internal resolution
        this.canvas.width = GAME_WIDTH;
        this.canvas.height = GAME_HEIGHT;

        this.input = new InputHandler(this.canvas);
        this.gameManager = new GameManager(this.input.isMobile);

        this.lastTime = 0;
        this.accumulator = 0;

        this.resize();
        this.setupListeners();
        this.hideLoading();
        this.loop(0);
    }

    hideLoading() {
        const el = document.getElementById('loading');
        if (el) el.classList.add('hidden');
    }

    setupListeners() {
        window.addEventListener('resize', () => this.resize());
        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.resize(), 100);
        });

        // Fullscreen button
        const fsBtn = document.getElementById('fullscreenBtn');
        if (fsBtn) {
            fsBtn.addEventListener('click', () => this.toggleFullscreen());
        }

        // Orientation overlay (show on portrait for phones)
        this.checkOrientation();
        window.addEventListener('resize', () => this.checkOrientation());
    }

    checkOrientation() {
        const overlay = document.getElementById('orientationOverlay');
        if (!overlay) return;

        const isPhone = window.innerWidth < 768 && this.input.isMobile;
        const isPortrait = window.innerHeight > window.innerWidth;

        if (isPhone && isPortrait) {
            overlay.style.display = 'flex';
        } else {
            overlay.style.display = 'none';
        }
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => {});
        } else {
            document.exitFullscreen().catch(() => {});
        }
    }

    resize() {
        const windowW = window.innerWidth;
        const windowH = window.innerHeight;

        // Calculate scale to fit while maintaining aspect ratio
        const gameRatio = GAME_WIDTH / GAME_HEIGHT;
        const windowRatio = windowW / windowH;

        let displayW, displayH;
        if (windowRatio > gameRatio) {
            // Window is wider than game ratio - fit to height
            displayH = windowH;
            displayW = windowH * gameRatio;
        } else {
            // Window is taller than game ratio - fit to width
            displayW = windowW;
            displayH = windowW / gameRatio;
        }

        this.canvas.style.width = `${displayW}px`;
        this.canvas.style.height = `${displayH}px`;
    }

    loop(timestamp) {
        const dt = timestamp - this.lastTime;
        this.lastTime = timestamp;

        // Accumulate time and run fixed timestep updates
        this.accumulator += Math.min(dt, 100); // Cap to prevent spiral of death

        while (this.accumulator >= FRAME_TIME) {
            this.gameManager.update(this.input);
            this.input.consumeEvents();
            this.accumulator -= FRAME_TIME;
        }

        // Render
        this.ctx.clearRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
        this.gameManager.draw(this.ctx);

        requestAnimationFrame((t) => this.loop(t));
    }
}

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    try {
        new PongApp();
    } catch (error) {
        console.error('Failed to initialize PongWithIssues:', error);
        const loading = document.getElementById('loading');
        if (loading) {
            loading.textContent = 'Failed to load game. Please refresh.';
            loading.classList.remove('hidden');
        }
    }
});
