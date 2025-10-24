import { BALL_RADIUS, CPU_MAX_SPEED, CPU_REACTION_TIME, GAME_HEIGHT, GAME_WIDTH, WINNING_SCORE, } from "./constants.js";
import { Ball } from "./ball.js";
import { Paddle } from "./paddle.js";
export class Game {
    constructor(canvas, input, onStatus) {
        this.canvas = canvas;
        this.input = input;
        this.onStatus = onStatus;
        this.state = "idle";
        this.lastTimestamp = 0;
        this.accumulator = 0;
        this.playerScore = 0;
        this.cpuScore = 0;
        this.ball = new Ball();
        this.player = new Paddle(32, GAME_HEIGHT / 2 - 60);
        this.cpu = new Paddle(GAME_WIDTH - 48, GAME_HEIGHT / 2 - 60);
        this.cpuTimer = 0;
        this.step = (timestamp) => {
            if (this.state !== "running") {
                this.render();
                return;
            }
            const delta = (timestamp - this.lastTimestamp) / 1000;
            this.lastTimestamp = timestamp;
            this.accumulator += delta;
            while (this.accumulator >= 1 / 144) {
                this.update(1 / 144);
                this.accumulator -= 1 / 144;
            }
            this.render();
            requestAnimationFrame(this.step);
        };
        const ctx = canvas.getContext("2d");
        if (!ctx) {
            throw new Error("Unable to initialise 2D context");
        }
        this.context = ctx;
        this.context.imageSmoothingEnabled = false;
    }
    start() {
        this.state = "running";
        this.lastTimestamp = performance.now();
        this.accumulator = 0;
        this.playerScore = 0;
        this.cpuScore = 0;
        this.ball.reset();
        this.onStatus("Game started. First to " + WINNING_SCORE + " wins!");
        requestAnimationFrame(this.step);
    }
    resume() {
        if (this.state === "running") {
            return;
        }
        this.state = "running";
        this.lastTimestamp = performance.now();
        requestAnimationFrame(this.step);
    }
    update(deltaTime) {
        const direction = this.input.getDirection();
        this.player.update(direction, deltaTime);
        this.cpuTimer += deltaTime;
        if (this.cpuTimer >= CPU_REACTION_TIME) {
            this.cpu.updateAI(this.ball.y, this.cpuTimer, CPU_MAX_SPEED);
            this.cpuTimer = 0;
        }
        const scoreDelta = this.ball.update(deltaTime, [this.player, this.cpu]);
        if (scoreDelta === -1) {
            this.playerScore += 1;
            this.ball.reset(-1);
            this.onStatus("You scored!" + this.scoreMessage());
        }
        else if (scoreDelta === 1) {
            this.cpuScore += 1;
            this.ball.reset(1);
            this.onStatus("CPU scored." + this.scoreMessage());
        }
        if (this.playerScore >= WINNING_SCORE || this.cpuScore >= WINNING_SCORE) {
            this.state = "finished";
            const winner = this.playerScore > this.cpuScore ? "You win!" : "CPU wins.";
            this.onStatus(winner + " Press Start to play again.");
        }
    }
    scoreMessage() {
        return ` Score ${this.playerScore} - ${this.cpuScore}.`;
    }
    render() {
        const ctx = this.context;
        ctx.clearRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
        ctx.fillStyle = "rgba(255, 255, 255, 0.08)";
        const dashHeight = 20;
        for (let y = 0; y < GAME_HEIGHT; y += dashHeight * 2) {
            ctx.fillRect(GAME_WIDTH / 2 - 2, y, 4, dashHeight);
        }
        this.drawPaddle(this.player);
        this.drawPaddle(this.cpu);
        this.drawBall();
    }
    drawPaddle(paddle) {
        const ctx = this.context;
        ctx.fillStyle = "#00ffc6";
        ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
    }
    drawBall() {
        const ctx = this.context;
        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.arc(this.ball.x, this.ball.y, BALL_RADIUS, 0, Math.PI * 2);
        ctx.fill();
    }
    getScores() {
        return { player: this.playerScore, cpu: this.cpuScore };
    }
    getState() {
        return this.state;
    }
}
