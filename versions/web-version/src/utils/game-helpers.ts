/**
 * game-helpers.ts -- Helper functions for game logic
 */

import { Ball, BallClassic } from '../game/ball.js';
import { Paddle, PaddleClassic } from '../game/paddle.js';
import { InputState } from '../types/index.js';
import { PADDLE_DEFAULT_VEL } from '../game/constants.js';

export class GameHelpers {
    /**
     * Handles paddle movement for physics-based mode
     */
    static handlePaddleMovement(input: InputState, leftPaddle: Paddle, rightPaddle: Paddle): void {
        // Left paddle (W/S or Arrow Up/Down)
        if (input.up) {
            leftPaddle.accelerate(true);
        }
        if (input.down) {
            leftPaddle.accelerate(false);
        }

        // Right paddle (Arrow Up/Down)
        if (input.up) {
            rightPaddle.accelerate(true);
        }
        if (input.down) {
            rightPaddle.accelerate(false);
        }
    }

    /**
     * Handles paddle movement for classic mode
     */
    static handlePaddleMovementClassic(input: InputState, leftPaddle: PaddleClassic, rightPaddle: PaddleClassic): void {
        // Left paddle (W/S)
        if (input.up) {
            leftPaddle.move(true);
        }
        if (input.down) {
            leftPaddle.move(false);
        }

        // Right paddle (Arrow Up/Down)
        if (input.up) {
            rightPaddle.move(true);
        }
        if (input.down) {
            rightPaddle.move(false);
        }
    }

    /**
     * Handles score updates for physics-based mode
     */
    static handleScore(ball: Ball, leftScore: number, rightScore: number): [number, number] {
        if (ball.pos.x - ball.radius < 0) {
            return [leftScore, rightScore + 1];
        } else if (ball.pos.x + ball.radius > 800) { // WIDTH constant
            return [leftScore + 1, rightScore];
        }
        return [leftScore, rightScore];
    }

    /**
     * Handles score updates for classic mode
     */
    static handleScoreClassic(ball: BallClassic, leftScore: number, rightScore: number): [number, number] {
        if (ball.pos.x - ball.radius < 0) {
            return [leftScore, rightScore + 1];
        } else if (ball.pos.x + ball.radius > 800) { // WIDTH constant
            return [leftScore + 1, rightScore];
        }
        return [leftScore, rightScore];
    }

    /**
     * Resets game objects for physics-based mode
     */
    static reset(ball: Ball, leftPaddle: Paddle, rightPaddle: Paddle): [number, number] {
        ball.reset();
        leftPaddle.reset();
        rightPaddle.reset();
        return [0, 0];
    }

    /**
     * Resets game objects for classic mode
     */
    static resetClassic(ball: BallClassic, leftPaddle: PaddleClassic, rightPaddle: PaddleClassic): [number, number] {
        ball.reset();
        leftPaddle.reset();
        rightPaddle.reset();
        return [0, 0];
    }

    /**
     * Draws game elements on canvas
     */
    static draw(
        ctx: CanvasRenderingContext2D,
        paddles: (Paddle | PaddleClassic)[],
        ball: Ball | BallClassic,
        leftScore: number,
        rightScore: number,
        font: string = '24px monospace'
    ): void {
        // Clear canvas
        ctx.fillStyle = 'rgb(0, 0, 0)';
        ctx.fillRect(0, 0, 800, 800); // WIDTH, HEIGHT constants

        // Draw center line
        ctx.strokeStyle = 'rgb(128, 128, 128)';
        ctx.lineWidth = 2;
        ctx.setLineDash([10, 10]);
        ctx.beginPath();
        ctx.moveTo(400, 0); // WIDTH / 2
        ctx.lineTo(400, 800); // HEIGHT
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw paddles
        paddles.forEach(paddle => paddle.draw(ctx));

        // Draw ball
        ball.draw(ctx);

        // Draw scores
        ctx.fillStyle = 'rgb(255, 255, 255)';
        ctx.font = font;
        ctx.textAlign = 'center';
        ctx.fillText(leftScore.toString(), 200, 50); // WIDTH / 4
        ctx.fillText(rightScore.toString(), 600, 50); // 3 * WIDTH / 4
    }
}
