import { BALL_RADIUS, BALL_SPEED, BALL_SPEED_INCREMENT, GAME_HEIGHT, GAME_WIDTH } from "./constants.js";
function randomDirection() {
    const direction = Math.random() < 0.5 ? -1 : 1;
    const angle = (Math.random() * Math.PI) / 4 + Math.PI / 8; // 22.5° - 67.5°
    return Math.cos(angle) * direction;
}
export class Ball {
    constructor() {
        this.x = GAME_WIDTH / 2;
        this.y = GAME_HEIGHT / 2;
        this.radius = BALL_RADIUS;
        this.speed = BALL_SPEED;
        this.velocityX = BALL_SPEED;
        this.velocityY = 0;
        this.reset();
    }
    reset(direction = Math.random() < 0.5 ? -1 : 1) {
        this.x = GAME_WIDTH / 2;
        this.y = GAME_HEIGHT / 2;
        this.speed = BALL_SPEED;
        const horizontal = randomDirection();
        const vertical = Math.sqrt(1 - horizontal * horizontal);
        this.velocityX = horizontal * this.speed * direction;
        this.velocityY = vertical * this.speed * (Math.random() < 0.5 ? -1 : 1);
    }
    update(deltaTime, paddles) {
        this.x += this.velocityX * deltaTime;
        this.y += this.velocityY * deltaTime;
        if (this.y - this.radius <= 0 || this.y + this.radius >= GAME_HEIGHT) {
            this.velocityY *= -1;
            this.y = Math.max(this.radius, Math.min(GAME_HEIGHT - this.radius, this.y));
        }
        for (const paddle of paddles) {
            if (this.collidesWith(paddle)) {
                this.handlePaddleCollision(paddle);
                break;
            }
        }
        if (this.x + this.radius < 0) {
            return 1; // CPU scores
        }
        if (this.x - this.radius > GAME_WIDTH) {
            return -1; // Player scores
        }
        return 0;
    }
    collidesWith(paddle) {
        return (this.x - this.radius < paddle.x + paddle.width &&
            this.x + this.radius > paddle.x &&
            this.y - this.radius < paddle.y + paddle.height &&
            this.y + this.radius > paddle.y);
    }
    handlePaddleCollision(paddle) {
        const relativeIntersectY = this.y - (paddle.y + paddle.height / 2);
        const normalizedRelativeIntersectionY = relativeIntersectY / (paddle.height / 2);
        const bounceAngle = normalizedRelativeIntersectionY * (Math.PI / 3); // 60° max
        const direction = this.x < GAME_WIDTH / 2 ? 1 : -1;
        this.velocityX = direction * this.speed * Math.cos(bounceAngle);
        this.velocityY = this.speed * Math.sin(bounceAngle);
        this.speed += BALL_SPEED_INCREMENT;
    }
    getState() {
        return {
            x: this.x,
            y: this.y,
            radius: this.radius,
        };
    }
}
