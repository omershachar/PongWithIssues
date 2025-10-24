import { clamp } from "./math.js";
import { GAME_HEIGHT, PADDLE_HEIGHT, PADDLE_SPEED, PADDLE_WIDTH } from "./constants.js";
export class Paddle {
    constructor(x, y) {
        this.width = PADDLE_WIDTH;
        this.height = PADDLE_HEIGHT;
        this.velocityY = 0;
        this.x = x;
        this.y = y;
    }
    update(direction, deltaTime) {
        this.velocityY = direction * PADDLE_SPEED;
        this.y += this.velocityY * deltaTime;
        this.y = clamp(this.y, 0, GAME_HEIGHT - this.height);
    }
    updateAI(targetY, deltaTime, maxSpeed) {
        const paddleCenter = this.y + this.height / 2;
        const distance = targetY - paddleCenter;
        const direction = Math.sign(distance);
        const speed = Math.min(Math.abs(distance) * 3, maxSpeed);
        this.y += direction * speed * deltaTime;
        this.y = clamp(this.y, 0, GAME_HEIGHT - this.height);
    }
    getState() {
        return {
            x: this.x,
            y: this.y,
            width: this.width,
            height: this.height,
        };
    }
}
