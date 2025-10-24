import { clamp } from "./math.js";
import { GAME_HEIGHT, PADDLE_HEIGHT, PADDLE_SPEED, PADDLE_WIDTH } from "./constants.js";
import type { Direction } from "./input.js";

export interface PaddleState {
  x: number;
  y: number;
  width: number;
  height: number;
}

export class Paddle {
  public x: number;
  public y: number;
  public width = PADDLE_WIDTH;
  public height = PADDLE_HEIGHT;
  public velocityY = 0;

  constructor(x: number, y: number) {
    this.x = x;
    this.y = y;
  }

  public update(direction: Direction, deltaTime: number): void {
    this.velocityY = direction * PADDLE_SPEED;
    this.y += this.velocityY * deltaTime;
    this.y = clamp(this.y, 0, GAME_HEIGHT - this.height);
  }

  public updateAI(targetY: number, deltaTime: number, maxSpeed: number): void {
    const paddleCenter = this.y + this.height / 2;
    const distance = targetY - paddleCenter;
    const direction = Math.sign(distance);
    const speed = Math.min(Math.abs(distance) * 3, maxSpeed);
    this.y += direction * speed * deltaTime;
    this.y = clamp(this.y, 0, GAME_HEIGHT - this.height);
  }

  public getState(): PaddleState {
    return {
      x: this.x,
      y: this.y,
      width: this.width,
      height: this.height,
    };
  }
}
