/**
 * menu.ts -- Menu system for the game
 */

import { BallClassic } from './ball.js';
import { COLORS, MIDDLE_BOARD, BALL_RADIUS, BALL_DEFAULT_VEL, WIDTH, HEIGHT, PONG_ASCII_3D } from './constants.js';

export class Menu {
    private ball: BallClassic;
    private selectedMode: number = 0; // 0 = Classic, 1 = Physics

    constructor() {
        this.ball = new BallClassic(
            MIDDLE_BOARD[0],
            MIDDLE_BOARD[1],
            BALL_RADIUS,
            COLORS.WHITE,
            BALL_DEFAULT_VEL[0],
            4
        );
    }

    draw(ctx: CanvasRenderingContext2D): void {
        // Clear canvas
        ctx.fillStyle = 'rgb(0, 0, 0)';
        ctx.fillRect(0, 0, WIDTH, HEIGHT);

        // Draw ASCII art
        const lines = PONG_ASCII_3D.split('\n');
        ctx.fillStyle = `rgb(${COLORS.PURPLE[0]}, ${COLORS.PURPLE[1]}, ${COLORS.PURPLE[2]})`;
        ctx.font = '16px monospace';
        ctx.textAlign = 'center';

        let yOffset = 100;
        for (const line of lines) {
            if (line.trim() === '') continue;
            ctx.fillText(line, WIDTH / 2, yOffset);
            yOffset += 20;
        }

        // Draw subtitle
        ctx.fillStyle = `rgb(${COLORS.LIGHT_PURPLE[0]}, ${COLORS.LIGHT_PURPLE[1]}, ${COLORS.LIGHT_PURPLE[2]})`;
        ctx.font = '20px monospace';
        ctx.fillText("A project that probably works. Sometimes. Maybe.", WIDTH / 2, 350);
        ctx.fillText("It compiles. That's enough.", WIDTH / 2, 380);

        // Show mode selection
        const modeText = this.selectedMode === 0 ? "Mode: Classic" : "Mode: Pongception";
        const modeColor = this.selectedMode === 0 ? COLORS.LIGHT_PURPLE : COLORS.RED;
        
        ctx.fillStyle = `rgb(${modeColor[0]}, ${modeColor[1]}, ${modeColor[2]})`;
        ctx.font = '24px monospace';
        ctx.fillText(modeText, WIDTH / 2, 500);

        // Draw prompt
        ctx.fillStyle = `rgb(${COLORS.PURPLE[0]}, ${COLORS.PURPLE[1]}, ${COLORS.PURPLE[2]})`;
        ctx.fillText("Press [SPACE] to start", WIDTH / 2, 550);
        ctx.fillText("Use [LEFT]/[RIGHT] to switch modes", WIDTH / 2, 580);

        // Draw bouncing ball
        this.ball.color = this.selectedMode === 0 ? COLORS.WHITE : COLORS.RED;
        this.ball.draw(ctx);
        this.ball.bounceBox(WIDTH, HEIGHT);
    }

    toggleMode(): void {
        this.selectedMode = this.selectedMode === 0 ? 1 : 0;
    }

    getSelectedMode(): 'classic' | 'physics' {
        return this.selectedMode === 0 ? 'classic' : 'physics';
    }
}
