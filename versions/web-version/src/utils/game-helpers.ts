/**
 * game-helpers.ts -- Helper functions for game logic
 */

import { Ball, BallClassic } from '../game/ball.js';
import { Paddle, PaddleClassic } from '../game/paddle.js';
import { InputState } from '../types/index.js';
import { PADDLE_DEFAULT_VEL, WIDTH, HEIGHT } from '../game/constants.js';

export class GameHelpers {
    /**
     * Handles paddle movement for physics-based mode
     */
    static handlePaddleMovement(input: InputState, leftPaddle: Paddle, rightPaddle: Paddle): void {
        // Left paddle (W/S keys)
        if (input.leftUp) {
            leftPaddle.accelerate(true);
        }
        if (input.leftDown) {
            leftPaddle.accelerate(false);
        }

        // Right paddle (Arrow Up/Down keys)
        if (input.rightUp) {
            rightPaddle.accelerate(true);
        }
        if (input.rightDown) {
            rightPaddle.accelerate(false);
        }
    }

    /**
     * Handles paddle movement for classic mode
     */
    static handlePaddleMovementClassic(input: InputState, leftPaddle: PaddleClassic, rightPaddle: PaddleClassic): void {
        // Left paddle (W/S keys)
        if (input.leftUp) {
            leftPaddle.move(true);
        }
        if (input.leftDown) {
            leftPaddle.move(false);
        }

        // Right paddle (Arrow Up/Down keys)
        if (input.rightUp) {
            rightPaddle.move(true);
        }
        if (input.rightDown) {
            rightPaddle.move(false);
        }
    }

    /**
     * Handles score updates for physics-based mode
     */
    static handleScore(ball: Ball, leftScore: number, rightScore: number): [number, number] {
        if (ball.pos.x - ball.radius < 0) {
            return [leftScore, rightScore + 1];
        } else if (ball.pos.x + ball.radius > WIDTH) {
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
        } else if (ball.pos.x + ball.radius > WIDTH) {
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
        ctx.fillRect(0, 0, WIDTH, HEIGHT);

        // Draw center line
        ctx.strokeStyle = 'rgb(128, 128, 128)';
        ctx.lineWidth = 2;
        ctx.setLineDash([10, 10]);
        ctx.beginPath();
        ctx.moveTo(WIDTH / 2, 0);
        ctx.lineTo(WIDTH / 2, HEIGHT);
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
        ctx.fillText(leftScore.toString(), WIDTH / 4, 50);
        ctx.fillText(rightScore.toString(), 3 * WIDTH / 4, 50);
    }
}
