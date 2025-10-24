export class InputManager {
    constructor(target = window) {
        this.target = target;
        this.upKeys = new Set(["ArrowUp", "w", "W"]);
        this.downKeys = new Set(["ArrowDown", "s", "S"]);
        this.direction = 0;
        this.handleKeyDown = (event) => {
            if (this.upKeys.has(event.key)) {
                this.direction = -1;
            }
            else if (this.downKeys.has(event.key)) {
                this.direction = 1;
            }
        };
        this.handleKeyUp = (event) => {
            if (this.upKeys.has(event.key) && this.direction === -1) {
                this.direction = 0;
            }
            else if (this.downKeys.has(event.key) && this.direction === 1) {
                this.direction = 0;
            }
        };
    }
    bind() {
        this.target.addEventListener("keydown", this.handleKeyDown);
        this.target.addEventListener("keyup", this.handleKeyUp);
    }
    unbind() {
        this.target.removeEventListener("keydown", this.handleKeyDown);
        this.target.removeEventListener("keyup", this.handleKeyUp);
    }
    getDirection() {
        return this.direction;
    }
}
