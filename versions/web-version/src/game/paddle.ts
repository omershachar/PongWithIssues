/**
 * paddle.ts -- Paddle class with physics-based movement.
 */

import { PhysicsObject } from './physics-object.js';
import { Vector2D } from '../types/index.js';
import { 
    COLORS, 
    PADDLE_DEFAULT_ACC, 
    PADDLE_MAX_VEL, 
    HEIGHT 
} from './constants.js';

export class Paddle extends PhysicsObject {
    public width: number;
    public height: number;
    public originalPos: Vector2D;

    constructor(
        x: number,
        y: number,
        width: number,
        height: number,
        color: readonly [number, number, number] = COLORS.LIGHT_PURPLE
    ) {
        super({ x, y }, { x: 0, y: 0 }, { x: 0, y: 0 }, 1, color);
        this.originalPos = { x, y };
        this.width = width;
        this.height = height;
    }

    draw(ctx: CanvasRenderingContext2D): void {
        /**
         * Draws the paddle on the canvas.
         */
        ctx.fillStyle = `rgb(${this.color[0]}, ${this.color[1]}, ${this.color[2]})`;
        ctx.fillRect(this.pos.x, this.pos.y, this.width, this.height);
    }

    accelerate(up: boolean = true): void {
        /**
         * Applies vertical acceleration to the paddle.
         */
        if (up) {
            this.acc.y -= PADDLE_DEFAULT_ACC[1];
        } else {
            this.acc.y += PADDLE_DEFAULT_ACC[1];
        }
    }

    update(): void {
        /**
         * Updates paddle position and velocity, applies vertical clamping,
         * velocity decay (friction), and keeps the paddle inside the screen.
         */
        this.vel.x += this.acc.x;
        this.vel.y += this.acc.y;
        this.acc.x = 0;
        this.acc.y = 0;

        // Clamp vertical velocity
        this.vel.y = Math.max(-PADDLE_MAX_VEL, Math.min(PADDLE_MAX_VEL, this.vel.y));

        // Update position
        this.pos.x += this.vel.x;
        this.pos.y += this.vel.y;

        // Apply friction on Y axis
        this.vel.y *= 0.85;

        // Clamp paddle inside the window (Y axis only)
        if (this.pos.y < 0) {
            this.pos.y = 0;
            this.vel.y = 0;
        } else if (this.pos.y + this.height > HEIGHT) {
            this.pos.y = HEIGHT - this.height;
            this.vel.y = 0;
        }
    }

    reset(): void {
        /**
         * Resets the paddle to its original position and clears movement.
         */
        this.pos = { ...this.originalPos };
        this.vel.x = 0;
        this.vel.y = 0;
        this.acc.x = 0;
        this.acc.y = 0;
    }
}

export class PaddleClassic {
    public x: number;
    public y: number;
    public originalX: number;
    public originalY: number;
    public width: number;
    public height: number;
    public color: readonly [number, number, number];
    public vel: number;

    constructor(
        x: number,
        y: number,
        width: number,
        height: number,
        color: readonly [number, number, number],
        vel: number
    ) {
        this.x = this.originalX = x;
        this.y = this.originalY = y;
        this.width = width;
        this.height = height;
        this.color = color;
        this.vel = vel;
    }

    draw(ctx: CanvasRenderingContext2D): void {
        /**Drawing the paddle on the board*/
        ctx.fillStyle = `rgb(${this.color[0]}, ${this.color[1]}, ${this.color[2]})`;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }

    move(up: boolean = true): void {
        /**Moving the paddle vertically on the board by its fixed velocity*/
        if (up) {
            this.y -= this.vel;
        } else {
            this.y += this.vel;
        }
    }

    reset(): void {
        /**Resetting the paddle position to his original position*/
        this.x = this.originalX;
        this.y = this.originalY;
    }
}
