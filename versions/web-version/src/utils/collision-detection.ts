/**
 * collision-detection.ts -- Handles collision detection and response
 */

import { Ball, BallClassic } from '../game/ball.js';
import { Paddle, PaddleClassic } from '../game/paddle.js';
import { Vector2D } from '../types/index.js';
import { MAX_DEFLECTION_SPEED, SPIN_FACTOR, HEIGHT } from '../game/constants.js';

export class CollisionDetection {
    /**
     * Handles ball collision with paddles for physics-based mode
     */
    static handleBallCollision(ball: Ball, leftPaddle: Paddle, rightPaddle: Paddle): void {
        // Left paddle collision
        if (this.checkBallPaddleCollision(ball, leftPaddle)) {
            this.resolveBallPaddleCollision(ball, leftPaddle, true);
        }

        // Right paddle collision
        if (this.checkBallPaddleCollision(ball, rightPaddle)) {
            this.resolveBallPaddleCollision(ball, rightPaddle, false);
        }

        // Top and bottom wall collision
        if (ball.pos.y - ball.radius <= 0 || ball.pos.y + ball.radius >= HEIGHT) {
            ball.vel.y *= -1;
            ball.pos.y = ball.pos.y - ball.radius <= 0 
                ? ball.radius 
                : HEIGHT - ball.radius;
        }
    }

    /**
     * Handles ball collision with paddles for classic mode
     */
    static handleBallCollisionClassic(ball: BallClassic, leftPaddle: PaddleClassic, rightPaddle: PaddleClassic, height: number): void {
        // Left paddle collision
        if (this.checkBallPaddleCollisionClassic(ball, leftPaddle)) {
            this.resolveBallPaddleCollisionClassic(ball, leftPaddle, true);
        }

        // Right paddle collision
        if (this.checkBallPaddleCollisionClassic(ball, rightPaddle)) {
            this.resolveBallPaddleCollisionClassic(ball, rightPaddle, false);
        }

        // Top and bottom wall collision
        if (ball.pos.y - ball.radius <= 0 || ball.pos.y + ball.radius >= height) {
            ball.vel.y *= -1;
            ball.pos.y = ball.pos.y - ball.radius <= 0 
                ? ball.radius 
                : height - ball.radius;
        }
    }

    private static checkBallPaddleCollision(ball: Ball, paddle: Paddle): boolean {
        const ballLeft = ball.pos.x - ball.radius;
        const ballRight = ball.pos.x + ball.radius;
        const ballTop = ball.pos.y - ball.radius;
        const ballBottom = ball.pos.y + ball.radius;

        const paddleLeft = paddle.pos.x;
        const paddleRight = paddle.pos.x + paddle.width;
        const paddleTop = paddle.pos.y;
        const paddleBottom = paddle.pos.y + paddle.height;

        return ballRight >= paddleLeft && 
               ballLeft <= paddleRight && 
               ballBottom >= paddleTop && 
               ballTop <= paddleBottom;
    }

    private static checkBallPaddleCollisionClassic(ball: BallClassic, paddle: PaddleClassic): boolean {
        const ballLeft = ball.pos.x - ball.radius;
        const ballRight = ball.pos.x + ball.radius;
        const ballTop = ball.pos.y - ball.radius;
        const ballBottom = ball.pos.y + ball.radius;

        const paddleLeft = paddle.x;
        const paddleRight = paddle.x + paddle.width;
        const paddleTop = paddle.y;
        const paddleBottom = paddle.y + paddle.height;

        return ballRight >= paddleLeft && 
               ballLeft <= paddleRight && 
               ballBottom >= paddleTop && 
               ballTop <= paddleBottom;
    }

    private static resolveBallPaddleCollision(ball: Ball, paddle: Paddle, isLeftPaddle: boolean): void {
        // Calculate relative position on paddle (0 = top, 1 = bottom)
        const relativeIntersectY = (ball.pos.y - paddle.pos.y) / paddle.height;
        const normalizedIntersectY = (relativeIntersectY - 0.5) * 2; // -1 to 1

        // Calculate angle based on where ball hits paddle
        const maxAngle = Math.PI / 4; // 45 degrees
        const angle = normalizedIntersectY * maxAngle;

        // Calculate new velocity
        const speed = Math.sqrt(ball.vel.x * ball.vel.x + ball.vel.y * ball.vel.y);
        const newSpeed = Math.max(speed, 6); // Minimum speed

        // Set new velocity based on angle and direction
        if (isLeftPaddle) {
            ball.vel.x = Math.cos(angle) * newSpeed;
            ball.vel.y = Math.sin(angle) * newSpeed;
        } else {
            ball.vel.x = -Math.cos(angle) * newSpeed;
            ball.vel.y = Math.sin(angle) * newSpeed;
        }

        // Add spin based on paddle movement
        ball.spin += paddle.vel.y * SPIN_FACTOR;
        ball.spin = Math.max(-10, Math.min(10, ball.spin)); // Clamp spin

        // Clamp vertical velocity
        ball.vel.y = Math.max(-MAX_DEFLECTION_SPEED, Math.min(MAX_DEFLECTION_SPEED, ball.vel.y));

        // Position ball outside paddle to prevent multiple collisions
        if (isLeftPaddle) {
            ball.pos.x = paddle.pos.x + paddle.width + ball.radius;
        } else {
            ball.pos.x = paddle.pos.x - ball.radius;
        }
    }

    private static resolveBallPaddleCollisionClassic(ball: BallClassic, paddle: PaddleClassic, isLeftPaddle: boolean): void {
        // Calculate relative position on paddle (0 = top, 1 = bottom)
        const relativeIntersectY = (ball.pos.y - paddle.y) / paddle.height;
        const normalizedIntersectY = (relativeIntersectY - 0.5) * 2; // -1 to 1

        // Calculate angle based on where ball hits paddle
        const maxAngle = Math.PI / 4; // 45 degrees
        const angle = normalizedIntersectY * maxAngle;

        // Calculate new velocity
        const speed = Math.sqrt(ball.vel.x * ball.vel.x + ball.vel.y * ball.vel.y);
        const newSpeed = Math.max(speed, 6); // Minimum speed

        // Set new velocity based on angle and direction
        if (isLeftPaddle) {
            ball.vel.x = Math.cos(angle) * newSpeed;
            ball.vel.y = Math.sin(angle) * newSpeed;
        } else {
            ball.vel.x = -Math.cos(angle) * newSpeed;
            ball.vel.y = Math.sin(angle) * newSpeed;
        }

        // Clamp vertical velocity
        ball.vel.y = Math.max(-MAX_DEFLECTION_SPEED, Math.min(MAX_DEFLECTION_SPEED, ball.vel.y));

        // Position ball outside paddle to prevent multiple collisions
        if (isLeftPaddle) {
            ball.pos.x = paddle.x + paddle.width + ball.radius;
        } else {
            ball.pos.x = paddle.x - ball.radius;
        }
    }
}
