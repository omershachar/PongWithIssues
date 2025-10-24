import {
  BALL_RADIUS,
  CPU_MAX_SPEED,
  CPU_REACTION_TIME,
  GAME_HEIGHT,
  GAME_WIDTH,
  WINNING_SCORE,
} from "./constants.js";
import { Ball } from "./ball.js";
import { Paddle } from "./paddle.js";
import type { InputManager } from "./input.js";

export type GameState = "idle" | "running" | "finished";

export class Game {
  private context: CanvasRenderingContext2D;
  private state: GameState = "idle";
  private lastTimestamp = 0;
  private accumulator = 0;
  private playerScore = 0;
  private cpuScore = 0;
  private ball = new Ball();
  private player = new Paddle(32, GAME_HEIGHT / 2 - 60);
  private cpu = new Paddle(GAME_WIDTH - 48, GAME_HEIGHT / 2 - 60);
  private cpuTimer = 0;

  constructor(private canvas: HTMLCanvasElement, private input: InputManager, private onStatus: (status: string) => void) {
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      throw new Error("Unable to initialise 2D context");
    }
    this.context = ctx;
    this.context.imageSmoothingEnabled = false;
  }

  public start(): void {
    this.state = "running";
    this.lastTimestamp = performance.now();
    this.accumulator = 0;
    this.playerScore = 0;
    this.cpuScore = 0;
    this.ball.reset();
    this.onStatus("Game started. First to " + WINNING_SCORE + " wins!");
    requestAnimationFrame(this.step);
  }

  public resume(): void {
    if (this.state === "running") {
      return;
    }
    this.state = "running";
    this.lastTimestamp = performance.now();
    requestAnimationFrame(this.step);
  }

  private step = (timestamp: number): void => {
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

  private update(deltaTime: number): void {
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
    } else if (scoreDelta === 1) {
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

  private scoreMessage(): string {
    return ` Score ${this.playerScore} - ${this.cpuScore}.`;
  }

  private render(): void {
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

  private drawPaddle(paddle: Paddle): void {
    const ctx = this.context;
    ctx.fillStyle = "#00ffc6";
    ctx.fillRect(paddle.x, paddle.y, paddle.width, paddle.height);
  }

  private drawBall(): void {
    const ctx = this.context;
    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.arc(this.ball.x, this.ball.y, BALL_RADIUS, 0, Math.PI * 2);
    ctx.fill();
  }

  public getScores(): { player: number; cpu: number } {
    return { player: this.playerScore, cpu: this.cpuScore };
  }

  public getState(): GameState {
    return this.state;
  }
}
