/**
 * Base class for physical objects with position, mass, and velocity.
 * Used by Ball, Paddle, and any future physics-driven game objects.
 */

import { Vector2D } from '../types/index.js';
import { GRAVITY, WIDTH, HEIGHT } from './constants.js';

export abstract class PhysicsObject {
    public pos: Vector2D;
    public vel: Vector2D;
    public acc: Vector2D;
    public mass: number;
    public color: readonly [number, number, number];
    protected forces: Vector2D[] = [];

    constructor(
        pos: Vector2D = { x: WIDTH / 2, y: HEIGHT / 2 },
        vel: Vector2D = { x: 0, y: 0 },
        acc: Vector2D = { x: 0, y: 0 },
        mass: number = 1,
        color: readonly [number, number, number] = [255, 255, 255]
    ) {
        this.pos = { ...pos };
        this.vel = { ...vel };
        this.acc = { ...acc };
        this.mass = mass;
        this.color = color;
    }

    get momentum(): Vector2D {
        /**Returns the linear momentum vector: P = m * v*/
        return {
            x: this.mass * this.vel.x,
            y: this.mass * this.vel.y
        };
    }

    get weight(): number {
        /**Returns the gravitational force: W = m * g*/
        return this.mass * GRAVITY;
    }

    get polar(): { r: number; theta: number } {
        /**
         * Returns the position in polar coordinates (r, θ),
         * where r = √(x² + y²), θ = arctan(y / x)
         */
        const r = Math.sqrt(this.pos.x * this.pos.x + this.pos.y * this.pos.y);
        const theta = Math.atan2(this.pos.y, this.pos.x);
        return { r, theta };
    }

    applyImpulse(impulse: Vector2D): void {
        /**
         * Applies an impulse vector to the object.
         * J = ΔP = m * Δv ⇒ v += J / m
         */
        this.vel.x += impulse.x / this.mass;
        this.vel.y += impulse.y / this.mass;
    }

    applyForce(force: Vector2D, dt: number): void {
        /**
         * Applies a force over time, converting it to an impulse.
         */
        const impulse: Vector2D = {
            x: force.x * dt,
            y: force.y * dt
        };
        this.applyImpulse(impulse);
    }

    update(dt: number = 1.0): void {
        /**
         * Updates the velocity and position using kinematic equations:
         * s = v₀t + ½at², v = v₀ + at
         */
        this.pos.x += this.vel.x * dt + 0.5 * this.acc.x * dt * dt;
        this.pos.y += this.vel.y * dt + 0.5 * this.acc.y * dt * dt;
        this.vel.x += this.acc.x * dt;
        this.vel.y += this.acc.y * dt;
        this.acc.x = 0; // Reset acceleration after update
        this.acc.y = 0;
    }

    addForce(force: Vector2D): void {
        /**
         * Adds a force to be accumulated and integrated during the frame.
         */
        this.forces.push({ ...force });
    }

    integrate(dt: number): void {
        /**
         * Applies all accumulated forces and updates the object's motion.
         */
        const totalForce: Vector2D = this.forces.reduce(
            (sum, force) => ({
                x: sum.x + force.x,
                y: sum.y + force.y
            }),
            { x: 0, y: 0 }
        );
        this.applyForce(totalForce, dt);
        this.update(dt);
        this.forces = [];
    }

    clampVelocity(maxSpeed: number): void {
        /**
         * Limits the velocity magnitude to a maximum value.
         */
        const speed = Math.sqrt(this.vel.x * this.vel.x + this.vel.y * this.vel.y);
        if (speed > maxSpeed) {
            this.vel.x = (this.vel.x / speed) * maxSpeed;
            this.vel.y = (this.vel.y / speed) * maxSpeed;
        }
    }

    clampToBoard(
        buffer: Vector2D = { x: 0, y: 0 },
        board: Vector2D = { x: WIDTH, y: HEIGHT },
        boardOrigin: Vector2D = { x: 0, y: 0 }
    ): void {
        /**
         * Constrains the object to stay within the visible given board.
         */
        this.pos.x = Math.max(boardOrigin.x + buffer.x, Math.min(board.x - buffer.x, this.pos.x));
        this.pos.y = Math.max(boardOrigin.y + buffer.y, Math.min(board.y - buffer.y, this.pos.y));
    }

    abstract draw(ctx: CanvasRenderingContext2D): void;
}
