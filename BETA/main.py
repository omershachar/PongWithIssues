import pygame
from physics import Ball, Paddle

pygame.init()
pygame.display.set_caption("PongWithIssues BETA")

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WIDTH, HEIGHT = 900, 600  # Enlarged board
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7
WINNING_SCORE = 3

FPS = 60
SCORE_FONT = pygame.font.SysFont("comicsans", 50)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

MAX_DEFLECTION_SPEED = 5
SPIN_FACTOR = 0.3

def handle_ball_collision(ball, left_paddle, right_paddle):
    if ball.y + ball.radius >= HEIGHT or ball.y - ball.radius <= 0:
        ball.y_vel *= -1

    if ball.x_vel < 0:
        if left_paddle.y <= ball.y <= left_paddle.y + left_paddle.height:
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                relative_velocity = ball.y_vel - left_paddle.y_vel
                impulse = 2 * ball.mass * relative_velocity
                ball.apply_impulse(0, -impulse)

                if left_paddle.power_spin:
                    ball.spin = left_paddle.y_vel * 2
                    left_paddle.power_spin = False
                else:
                    ball.spin = left_paddle.y_vel * 0.5

                left_paddle.apply_impulse(0, -impulse * 0.1)

                middle_y = left_paddle.y + left_paddle.height / 2
                offset = ball.y - middle_y
                normalized_offset = offset / (left_paddle.height / 2)
                ball.y_vel = normalized_offset * MAX_DEFLECTION_SPEED + left_paddle.y_vel * SPIN_FACTOR

                ball.x_vel *= -1

    elif ball.x_vel > 0:
        if right_paddle.y <= ball.y <= right_paddle.y + right_paddle.height:
            if ball.x + ball.radius >= right_paddle.x:
                relative_velocity = ball.y_vel - right_paddle.y_vel
                impulse = 2 * ball.mass * relative_velocity
                ball.apply_impulse(0, -impulse)

                if right_paddle.power_spin:
                    ball.spin = right_paddle.y_vel * 2
                    right_paddle.power_spin = False
                else:
                    ball.spin = right_paddle.y_vel * 0.5

                right_paddle.apply_impulse(0, -impulse * 0.1)

                middle_y = right_paddle.y + right_paddle.height / 2
                offset = ball.y - middle_y
                normalized_offset = offset / (right_paddle.height / 2)
                ball.y_vel = normalized_offset * MAX_DEFLECTION_SPEED + right_paddle.y_vel * SPIN_FACTOR

                ball.x_vel *= -1

def handle_paddle_movement(keys, left_paddle, right_paddle):
    if keys[pygame.K_q]:
        left_paddle.power_spin = True
    if keys[pygame.K_RSHIFT]:
        right_paddle.power_spin = True

    if keys[pygame.K_w]:
        left_paddle.accelerate(up=True)
    if keys[pygame.K_s]:
        left_paddle.accelerate(up=False)

    if keys[pygame.K_UP]:
        right_paddle.accelerate(up=True)
    if keys[pygame.K_DOWN]:
        right_paddle.accelerate(up=False)

def draw(win, paddles, ball, left_score, right_score):
    win.fill(BLACK)

    left_text = SCORE_FONT.render(f"{left_score}", 1, WHITE)
    right_text = SCORE_FONT.render(f"{right_score}", 1, WHITE)
    win.blit(left_text, (WIDTH//4 - left_text.get_width()//2, 20))
    win.blit(right_text, (WIDTH * 3//4 - right_text.get_width()//2, 20))

    for paddle in paddles:
        paddle.draw(win)

    # Draw a net with a mesh-like effect
    for i in range(10, HEIGHT, HEIGHT // 25):
        pygame.draw.rect(win, WHITE, (WIDTH // 2 - 2, i, 4, HEIGHT // 50))

    ball.draw(win)
    pygame.display.update()

def main():
    clock = pygame.time.Clock()
    run = True

    left_paddle = Paddle(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    left_score = 0
    right_score = 0

    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)

        left_paddle.update()
        right_paddle.update()
        ball.update()

        handle_ball_collision(ball, left_paddle, right_paddle)

        if ball.x < 0:
            right_score += 1
            ball.reset()
        elif ball.x > WIDTH:
            left_score += 1
            ball.reset()

        if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
            winner = "Left Player Won!" if left_score > right_score else "Right Player Won!"
            text = SCORE_FONT.render(winner, 1, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(4000)

            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0

    pygame.quit()

if __name__ == '__main__':
    main()
