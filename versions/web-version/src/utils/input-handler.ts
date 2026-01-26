/**
 * input-handler.ts -- Handles keyboard input for the game
 */

import { InputState } from '../types/index.js';

export class InputHandler {
    private inputState: InputState = {
        // Left paddle (W/S)
        leftUp: false,
        leftDown: false,
        // Right paddle (Arrow keys)
        rightUp: false,
        rightDown: false,
        // Menu navigation
        left: false,
        right: false,
        // Game controls
        space: false,
        escape: false,
        m: false,
        r: false,
        h: false,
    };

    private keyMap: { [key: string]: keyof InputState } = {
        // Left paddle controls
        'KeyW': 'leftUp',
        'KeyS': 'leftDown',
        // Right paddle controls
        'ArrowUp': 'rightUp',
        'ArrowDown': 'rightDown',
        // Menu navigation
        'ArrowLeft': 'left',
        'KeyA': 'left',
        'ArrowRight': 'right',
        'KeyD': 'right',
        // Game controls
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
