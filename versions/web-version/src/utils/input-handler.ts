/**
 * input-handler.ts -- Handles keyboard input for the game
 */

import { InputState } from '../types/index.js';

export class InputHandler {
    private inputState: InputState = {
        up: false,
        down: false,
        left: false,
        right: false,
        space: false,
        escape: false,
        m: false,
        r: false,
        h: false,
    };

    private keyMap: { [key: string]: keyof InputState } = {
        'ArrowUp': 'up',
        'KeyW': 'up',
        'ArrowDown': 'down',
        'KeyS': 'down',
        'ArrowLeft': 'left',
        'KeyA': 'left',
        'ArrowRight': 'right',
        'KeyD': 'right',
        'Space': 'space',
        'Escape': 'escape',
        'KeyM': 'm',
        'KeyR': 'r',
        'KeyH': 'h',
    };

    constructor() {
        this.setupEventListeners();
    }

    private setupEventListeners(): void {
        document.addEventListener('keydown', (event) => {
            const key = this.keyMap[event.code];
            if (key) {
                this.inputState[key] = true;
                event.preventDefault();
            }
        });

        document.addEventListener('keyup', (event) => {
            const key = this.keyMap[event.code];
            if (key) {
                this.inputState[key] = false;
                event.preventDefault();
            }
        });
    }

    public getInputState(): InputState {
        return { ...this.inputState };
    }

    public isKeyPressed(key: keyof InputState): boolean {
        return this.inputState[key];
    }

    public isAnyKeyPressed(): boolean {
        return Object.values(this.inputState).some(pressed => pressed);
    }

    public reset(): void {
        Object.keys(this.inputState).forEach(key => {
            this.inputState[key as keyof InputState] = false;
        });
    }
}
