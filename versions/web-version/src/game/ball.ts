/**
 * ball.ts -- Unified Ball class for both Classic and Physics modes
 */

import { PhysicsObject } from './physics-object.js';
import { Vector2D } from '../types/index.js';
import {
    COLORS,
    BALL_RADIUS,
    BALL_DEFAULT_VEL,
    MIDDLE_BOARD,
    WIDTH,
    HEIGHT
} from './constants.js';

export type BallMode = 'classic' | 'physics';

export class Ball extends PhysicsObject {
    public radius: number;
    public spin: number;
    public trail: Vector2D[] = [];
    public maxTrail: number = 10;
    public originalPos: Vector2D;
    public originalVel: Vector2D;
    public mode: BallMode;

    constructor(
        x: number = MIDDLE_BOARD[0],
        y: number = MIDDLE_BOARD[1],
        radius: number = BALL_RADIUS,
        color: readonly [number, number, number] = COLORS.WHITE,
        mass: number = 1,
        vel: Vector2D = { x: BALL_DEFAULT_VEL[0], y: BALL_DEFAULT_VEL[1] },
        mode: BallMode = 'physics'
    ) {
        super({ x, y }, vel, { x: 0, y: 0 }, mass, color);
        this.radius = radius;
        this.spin = 0;
        this.originalPos = { x, y };
        this.originalVel = { ...vel };
        this.mode = mode;
    }

    draw(ctx: CanvasRenderingContext2D): void {
        if (this.mode === 'classic') {
            this.drawClassic(ctx);
        } else {
            this.drawPhysics(ctx);
        }
    }

    /**
     * Simple classic mode drawing - just a circle
     */
    private drawClassic(ctx: CanvasRenderingContext2D): void {
        ctx.fillStyle = `rgb(${this.color[0]}, ${this.color[1]}, ${this.color[2]})`;
        ctx.beginPath();
        ctx.arc(this.pos.x, this.pos.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
    }

    /**
     * Physics mode drawing with fire trail, aura, and spin effects
     */
    private drawPhysics(ctx: CanvasRenderingContext2D): void {
        // Fire colors for the trail (from dark to bright)
        const FIRE_COLORS = [
            COLORS.DARK_RED, COLORS.SCARLET, COLORS.ORANGE_RED,
            COLORS.ORANGE, COLORS.GOLD, COLORS.YELLOW, COLORS.WHITE
        ];
        const ALL_FIRE_COLORS = [
            COLORS.DARK_RED, COLORS.SCARLET, COLORS.ORANGE_RED,
            COLORS.ORANGE, COLORS.GOLD, COLORS.YELLOW, COLORS.WHITE,
            COLORS.GOLD, COLORS.YELLOW, COLORS.WHITE
        ];
        const colorCycleLen = ALL_FIRE_COLORS.length;

        const speed = this.speed;
        const maxSpeed = 30;
        const accMagnitude = Math.sqrt(this.acc.x * this.acc.x + this.acc.y * this.acc.y);
        const t = Math.min(accMagnitude / 15, 1);
        const colorIdx = Math.floor(t * (FIRE_COLORS.length - 1));
        const coreColor = FIRE_COLORS[colorIdx];

        // --- 1. Draw fire trail ---
        for (let i = 0; i < this.trail.length; i++) {
            const pos = this.trail[i];
            if (!pos) continue;
            const trailT = i / Math.max(this.trail.length - 1, 1);
            const flicker = speed > 7 ? Math.random() * 32 - 16 : 0;
            const alpha = Math.max(35, 140 - i * 18 + flicker) / 255;
            const radius = Math.max(2, this.radius * (1 - trailT * 0.8));

            const cidx = (colorIdx + i) % colorCycleLen;
            const trailColor = ALL_FIRE_COLORS[cidx];
            if (!trailColor) continue;

            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.fillStyle = `rgb(${trailColor[0]}, ${trailColor[1]}, ${trailColor[2]})`;
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        // --- 2. Glowing aura if fast ---
        if (speed > 6) {
            for (let layer = 3; layer > 0; layer--) {
                const auraR = this.radius * (1.2 + 0.25 * layer);
                const auraAlpha = (25 * layer + Math.min(50, speed * 2)) / 255;
                const auraColor = FIRE_COLORS[Math.min(FIRE_COLORS.length - 1, colorIdx + layer)];
                if (!auraColor) continue;

                ctx.save();
                ctx.globalAlpha = auraAlpha;
                ctx.fillStyle = `rgb(${auraColor[0]}, ${auraColor[1]}, ${auraColor[2]})`;
                ctx.beginPath();
                ctx.arc(this.pos.x, this.pos.y, auraR, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        // --- 3. Spin arc effect ---
        if (Math.abs(this.spin) > 4) {
            const direction = this.spin > 0 ? 0 : Math.PI;
            const arcLen = Math.PI + Math.min(Math.PI * 0.8, (speed / maxSpeed) * Math.PI * 0.8);
            const baseThick = 5 + Math.min(18, (speed / maxSpeed) * 22);

            for (let j = 0; j < 5; j++) {
                const arcAlpha = speed > 8
                    ? (60 + (Math.sin(Date.now() / 40 + j) + 1) * 80) / 255
                    : (50 + j * 10) / 255;
                const arcColor = ALL_FIRE_COLORS[(colorIdx + j) % colorCycleLen];
                if (!arcColor) continue;
                const thick = baseThick + j * 2;

                ctx.save();
                ctx.globalAlpha = Math.min(1, arcAlpha);
                ctx.strokeStyle = `rgb(${arcColor[0]}, ${arcColor[1]}, ${arcColor[2]})`;
                ctx.lineWidth = thick;
                ctx.beginPath();
                ctx.arc(this.pos.x, this.pos.y, this.radius, direction, direction + arcLen);
                ctx.stroke();
                ctx.restore();
            }
        }

        // --- 4. Main ball (core) ---
        if (speed > 21 && coreColor) {
            ctx.fillStyle = `rgb(${COLORS.WHITE[0]}, ${COLORS.WHITE[1]}, ${COLORS.WHITE[2]})`;
            ctx.beginPath();
            ctx.arc(this.pos.x, this.pos.y, this.radius, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = `rgb(${coreColor[0]}, ${coreColor[1]}, ${coreColor[2]})`;
            ctx.beginPath();
            ctx.arc(this.pos.x, this.pos.y, this.radius - 1, 0, Math.PI * 2);
            ctx.fill();
        } else if (coreColor) {
            ctx.fillStyle = `rgb(${coreColor[0]}, ${coreColor[1]}, ${coreColor[2]})`;
            ctx.beginPath();
            ctx.arc(this.pos.x, this.pos.y, this.radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    move(): void {
        if (this.mode === 'physics') {
            // Magnus effect for physics mode
            this.vel.y += this.spin * 0.1;
        }
        this.pos.x += this.vel.x;
        this.pos.y += this.vel.y;
    }

    update(): void {
        if (this.mode === 'physics') {
            // Trail only for physics mode
            this.trail.unshift({ x: this.pos.x, y: this.pos.y });
            if (this.trail.length > this.maxTrail) {
                this.trail.pop();
            }
        }
        this.move();
    }

    /**
     * Bounce off walls - used in menu and classic mode
     */
    bounceBox(width: number, height: number): void {
        this.move();
        if (this.pos.x <= 0 || this.pos.x >= width) {
            this.vel.x *= -1;
        }
        if (this.pos.y <= 0 || this.pos.y >= height) {
            this.vel.y *= -1;
        }
    }

    reset(): void {
        this.pos = { ...this.originalPos };
        this.vel = { x: -this.originalVel.x, y: this.mode === 'classic' ? 0 : -this.originalVel.y };
        this.spin = 0;
        this.trail = [];
    }

    get speed(): number {
        return Math.sqrt(this.vel.x * this.vel.x + this.vel.y * this.vel.y);
    }
}

// ----------------------- Legacy Alias for Backwards Compatibility -----------------------
/**
 * @deprecated Use Ball with mode='classic' instead
 */
export class BallClassic extends Ball {
    constructor(
        x: number,
        y: number,
        radius: number,
        color: readonly [number, number, number],
        velX: number,
        velY: number
    ) {
        super(x, y, radius, color, 1, { x: velX, y: velY }, 'classic');
    }
}
