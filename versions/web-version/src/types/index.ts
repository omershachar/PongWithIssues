/**
 * Type definitions for the Pong game
 */

export interface Vector2D {
    x: number;
    y: number;
}

export interface PhysicsObject {
    pos: Vector2D;
    vel: Vector2D;
    acc: Vector2D;
    mass: number;
    color: readonly [number, number, number];
}

export interface Ball extends PhysicsObject {
    radius: number;
    spin: number;
    trail: Vector2D[];
    maxTrail: number;
    originalPos: Vector2D;
    originalVel: Vector2D;
}

export interface Paddle extends PhysicsObject {
    width: number;
    height: number;
    originalPos: Vector2D;
}

export interface GameState {
    mode: 'classic' | 'physics';
    state: 'menu' | 'playing' | 'paused';
    leftScore: number;
    rightScore: number;
    showInstructions: boolean;
}

export interface InputState {
    up: boolean;
    down: boolean;
    left: boolean;
    right: boolean;
    space: boolean;
    escape: boolean;
    m: boolean;
    r: boolean;
    h: boolean;
}

export interface GameConfig {
    width: number;
    height: number;
    fps: number;
    winningScore: number;
}
