/**
 * paddle.ts -- Unified Paddle class for both Classic and Physics modes
 */

import { PhysicsObject } from './physics-object.js';
import { Vector2D } from '../types/index.js';
import {
    COLORS,
    PADDLE_DEFAULT_ACC,
    PADDLE_DEFAULT_VEL,
    PADDLE_MAX_VEL,
    HEIGHT
} from './constants.js';

export type PaddleMode = 'classic' | 'physics';

export class Paddle extends PhysicsObject {
    public width: number;
    public height: number;
    public originalPos: Vector2D;
    public mode: PaddleMode;
    public fixedVel: number; // Used in classic mode

    // Aliases for backwards compatibility with classic mode code that uses x, y directly
    get x(): number { return this.pos.x; }
    set x(val: number) { this.pos.x = val; }
    get y(): number { return this.pos.y; }
    set y(val: number) { this.pos.y = val; }
    get originalX(): number { return this.originalPos.x; }
    get originalY(): number { return this.originalPos.y; }

    constructor(
        x: number,
        y: number,
        width: number,
        height: number,
        color: readonly [number, number, number] = COLORS.LIGHT_PURPLE,
        mode: PaddleMode = 'physics',
        fixedVel: number = PADDLE_DEFAULT_VEL
    ) {
        super({ x, y }, { x: 0, y: 0 }, { x: 0, y: 0 }, 1, color);
        this.originalPos = { x, y };
        this.width = width;
        this.height = height;
        this.mode = mode;
        this.fixedVel = fixedVel;
    }

    draw(ctx: CanvasRenderingContext2D): void {
        ctx.fillStyle = `rgb(${this.color[0]}, ${this.color[1]}, ${this.color[2]})`;
        ctx.fillRect(this.pos.x, this.pos.y, this.width, this.height);
    }

    /**
     * Applies acceleration (physics mode) or direct movement (classic mode)
     */
    accelerate(up: boolean = true): void {
        if (this.mode === 'classic') {
            this.move(up);
        } else {
            if (up) {
                this.acc.y -= PADDLE_DEFAULT_ACC[1];
            } else {
                this.acc.y += PADDLE_DEFAULT_ACC[1];
            }
        }
    }

    /**
     * Direct movement for classic mode
     */
    move(up: boolean = true): void {
        if (up) {
            this.pos.y -= this.fixedVel;
        } else {
            this.pos.y += this.fixedVel;
        }
        // Clamp to screen
        this.clampToScreen();
    }

    /**
     * Updates paddle position - physics mode uses acceleration, classic uses direct movement
     */
    update(): void {
        if (this.mode === 'physics') {
            // Apply acceleration to velocity
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
        }
        // Classic mode doesn't need update() - movement is direct

        this.clampToScreen();
    }

    private clampToScreen(): void {
        if (this.pos.y < 0) {
            this.pos.y = 0;
            this.vel.y = 0;
        } else if (this.pos.y + this.height > HEIGHT) {
            this.pos.y = HEIGHT - this.height;
            this.vel.y = 0;
        }
    }

    reset(): void {
        this.pos = { ...this.originalPos };
        this.vel = { x: 0, y: 0 };
        this.acc = { x: 0, y: 0 };
    }
}

// ----------------------- Legacy Alias for Backwards Compatibility -----------------------
/**
 * @deprecated Use Paddle with mode='classic' instead
 */
export class PaddleClassic extends Paddle {
    constructor(
        x: number,
        y: number,
        width: number,
        height: number,
        color: readonly [number, number, number],
        vel: number
    ) {
        super(x, y, width, height, color, 'classic', vel);
    }
}
