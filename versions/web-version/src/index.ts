/**
 * index.ts -- Main entry point for the PongWithIssues game
 */

import { GameManager } from './game/game-manager.js';
import { InputHandler } from './utils/input-handler.js';
import { FPS } from './game/constants.js';

class PongGame {
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    private gameManager: GameManager;
    private inputHandler: InputHandler;
    private lastTime: number = 0;
    private gameLoopId: number | null = null;

    constructor() {
        this.canvas = document.getElementById('gameCanvas') as HTMLCanvasElement;
        if (!this.canvas) {
            throw new Error('Canvas element not found');
        }

        const ctx = this.canvas.getContext('2d');
        if (!ctx) {
            throw new Error('Could not get 2D context');
        }
        this.ctx = ctx;

        this.gameManager = new GameManager();
        this.inputHandler = new InputHandler();

        this.hideLoading();
        this.startGameLoop();
    }

    private hideLoading(): void {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.classList.add('hidden');
        }
    }

    private startGameLoop(): void {
        const gameLoop = (currentTime: number) => {
            const deltaTime = currentTime - this.lastTime;
            this.lastTime = currentTime;

            // Update game at target FPS
            if (deltaTime >= 1000 / FPS) {
                this.update();
                this.render();
            }

            this.gameLoopId = requestAnimationFrame(gameLoop);
        };

        this.gameLoopId = requestAnimationFrame(gameLoop);
    }

    private update(): void {
        const input = this.inputHandler.getInputState();
        this.gameManager.update(input);
    }

    private render(): void {
        this.gameManager.draw(this.ctx);
    }

    public destroy(): void {
        if (this.gameLoopId) {
            cancelAnimationFrame(this.gameLoopId);
        }
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    try {
        new PongGame();
    } catch (error) {
        console.error('Failed to initialize game:', error);
        const loading = document.getElementById('loading');
        if (loading) {
            loading.textContent = 'Failed to load game. Please refresh the page.';
        }
    }
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    // Cleanup if needed
});
