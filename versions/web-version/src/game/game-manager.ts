/**
 * game-manager.ts -- Main game manager that handles game states and transitions
 */

import { Menu } from './menu.js';
import { ClassicGame } from './classic-game.js';
import { PhysicsGame } from './physics-game.js';
import { InputState } from '../types/index.js';
import { COLORS, WIDTH, HEIGHT } from './constants.js';

export type GameState = 'menu' | 'classic' | 'physics' | 'gameOver';

export class GameManager {
    private currentState: GameState = 'menu';
    private menu: Menu;
    private classicGame: ClassicGame;
    private physicsGame: PhysicsGame;
    private winner: string | null = null;

    constructor() {
        this.menu = new Menu();
        this.classicGame = new ClassicGame();
        this.physicsGame = new PhysicsGame();
    }

    update(input: InputState): void {
        switch (this.currentState) {
            case 'menu':
                this.updateMenu(input);
                break;
            case 'classic':
                this.updateClassicGame(input);
                break;
            case 'physics':
                this.updatePhysicsGame(input);
                break;
            case 'gameOver':
                this.updateGameOver(input);
                break;
        }
    }

    private updateMenu(input: InputState): void {
        if (input.left || input.right) {
            this.menu.toggleMode();
        }
        if (input.space) {
            const mode = this.menu.getSelectedMode();
            this.currentState = mode;
        }
        if (input.escape) {
            // Could add exit functionality here
        }
    }

    private updateClassicGame(input: InputState): void {
        if (input.m || input.escape) {
            this.currentState = 'menu';
            this.classicGame.reset();
            return;
        }

        const gameEnded = this.classicGame.update(input);
        if (gameEnded) {
            this.winner = this.classicGame.getWinner();
            this.currentState = 'gameOver';
        }
    }

    private updatePhysicsGame(input: InputState): void {
        if (input.m || input.escape) {
            this.currentState = 'menu';
            this.physicsGame.reset();
            return;
        }

        const gameEnded = this.physicsGame.update(input);
        if (gameEnded) {
            this.winner = this.physicsGame.getWinner();
            this.currentState = 'gameOver';
        }
    }

    private updateGameOver(input: InputState): void {
        if (input.space || input.r) {
            // Return to menu
            this.currentState = 'menu';
            this.winner = null;
            this.classicGame.reset();
            this.physicsGame.reset();
        }
    }

    draw(ctx: CanvasRenderingContext2D): void {
        switch (this.currentState) {
            case 'menu':
                this.menu.draw(ctx);
                break;
            case 'classic':
                this.classicGame.draw(ctx);
                break;
            case 'physics':
                this.physicsGame.draw(ctx);
                break;
            case 'gameOver':
                this.drawGameOver(ctx);
                break;
        }
    }

    private drawGameOver(ctx: CanvasRenderingContext2D): void {
        // Clear canvas
        ctx.fillStyle = 'rgb(0, 0, 0)';
        ctx.fillRect(0, 0, WIDTH, HEIGHT);

        // Draw winner text
        if (this.winner) {
            ctx.fillStyle = `rgb(${COLORS.PURPLE[0]}, ${COLORS.PURPLE[1]}, ${COLORS.PURPLE[2]})`;
            ctx.font = '48px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(this.winner, WIDTH / 2, HEIGHT / 2 - 20);

            ctx.fillStyle = `rgb(${COLORS.GREY[0]}, ${COLORS.GREY[1]}, ${COLORS.GREY[2]})`;
            ctx.font = '16px monospace';
            ctx.fillText("Press [SPACE] or [R] to return to menu", WIDTH / 2, HEIGHT / 2 + 20);
        }
    }

    getCurrentState(): GameState {
        return this.currentState;
    }
}
