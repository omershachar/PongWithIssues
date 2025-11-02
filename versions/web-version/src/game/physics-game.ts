/**
 * physics-game.ts -- Physics-based Pong game implementation
 */

import { Ball } from './ball.js';
import { Paddle } from './paddle.js';
import { InputState } from '../types/index.js';
import { 
    COLORS, 
    ORIGINAL_LEFT_PADDLE_POS, 
    ORIGINAL_RIGHT_PADDLE_POS, 
    PADDLE_SIZE, 
    MIDDLE_BOARD, 
    BALL_RADIUS, 
    BALL_DEFAULT_VEL,
    WIDTH,
    HEIGHT,
    WINNING_SCORE
} from './constants.js';
import { CollisionDetection } from '../utils/collision-detection.js';
import { GameHelpers } from '../utils/game-helpers.js';

export class PhysicsGame {
    private leftPaddle: Paddle;
    private rightPaddle: Paddle;
    private ball: Ball;
    private leftScore: number = 0;
    private rightScore: number = 0;
    private paused: boolean = false;
    private showInstructions: boolean = false;

    constructor() {
        this.leftPaddle = new Paddle(
            ORIGINAL_LEFT_PADDLE_POS[0],
            ORIGINAL_LEFT_PADDLE_POS[1],
            PADDLE_SIZE[0],
            PADDLE_SIZE[1]
        );

        this.rightPaddle = new Paddle(
            ORIGINAL_RIGHT_PADDLE_POS[0],
            ORIGINAL_RIGHT_PADDLE_POS[1],
            PADDLE_SIZE[0],
            PADDLE_SIZE[1]
        );

        this.ball = new Ball(
            MIDDLE_BOARD[0],
            MIDDLE_BOARD[1],
            BALL_RADIUS,
            COLORS.YELLOW,
            1,
            { x: BALL_DEFAULT_VEL[0], y: BALL_DEFAULT_VEL[1] }
        );
    }

    update(input: InputState): boolean {
        // Handle input
        if (input.space) {
            this.paused = !this.paused;
        }
        if (input.r) {
            [this.leftScore, this.rightScore] = GameHelpers.reset(this.ball, this.leftPaddle, this.rightPaddle);
            this.paused = false;
        }
        if (input.h) {
            this.showInstructions = !this.showInstructions;
        }

        // Check for game end
        if (this.leftScore >= WINNING_SCORE || this.rightScore >= WINNING_SCORE) {
            return true; // Game ended
        }

        if (!this.paused) {
            // Handle paddle movement
            GameHelpers.handlePaddleMovement(input, this.leftPaddle, this.rightPaddle);

            // Update paddles
            this.leftPaddle.update();
            this.rightPaddle.update();

            // Update ball
            this.ball.update();
            CollisionDetection.handleBallCollision(this.ball, this.leftPaddle, this.rightPaddle);

            // Update score
            [this.leftScore, this.rightScore] = GameHelpers.handleScore(this.ball, this.leftScore, this.rightScore);

            // Reset ball if scored
            if (this.ball.pos.x - this.ball.radius < 0 || this.ball.pos.x + this.ball.radius > WIDTH) {
                this.ball.reset();
            }
        }

        return false; // Game continues
    }

    draw(ctx: CanvasRenderingContext2D): void {
        // Draw game
        GameHelpers.draw(ctx, [this.leftPaddle, this.rightPaddle], this.ball, this.leftScore, this.rightScore);

        // Draw mode label
        ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
        ctx.font = '16px monospace';
        ctx.textAlign = 'left';
        ctx.fillText("MODE: PHYSICS", 10, 30);

        // Draw debug info
        ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
        ctx.font = '12px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(`Velocity: [${this.ball.vel.x.toFixed(2)}, ${this.ball.vel.y.toFixed(2)}]`, 10, 50);
        ctx.fillText(`Spin: ${this.ball.spin.toFixed(2)}`, 10, 70);

        // Draw pause screen
        if (this.paused) {
            ctx.fillStyle = `rgb(${COLORS.PURPLE[0]}, ${COLORS.PURPLE[1]}, ${COLORS.PURPLE[2]})`;
            ctx.font = '48px monospace';
            ctx.textAlign = 'center';
            ctx.fillText("PAUSED", WIDTH / 2, HEIGHT / 2 - 20);

            ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
            ctx.font = '16px monospace';
            ctx.fillText("Press [SPACE] to resume", WIDTH / 2, HEIGHT / 2 + 20);
        }

        // Draw instructions
        if (this.showInstructions) {
            const footerText = "Press [SPACE] to pause | [R] to restart | [M] to return | [ESC] to quit | [H] to hide";
            ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
            ctx.font = '12px monospace';
            ctx.textAlign = 'left';
            ctx.fillText(footerText, 10, HEIGHT - 20);
        } else {
            ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
            ctx.font = '12px monospace';
            ctx.textAlign = 'left';
            ctx.fillText("Press [H] for help", 10, HEIGHT - 20);
        }
    }

    getWinner(): string | null {
        if (this.leftScore >= WINNING_SCORE) {
            return "Left Player Won!";
        } else if (this.rightScore >= WINNING_SCORE) {
            return "Right Player Won!";
        }
        return null;
    }

    reset(): void {
        [this.leftScore, this.rightScore] = GameHelpers.reset(this.ball, this.leftPaddle, this.rightPaddle);
        this.paused = false;
    }
}
