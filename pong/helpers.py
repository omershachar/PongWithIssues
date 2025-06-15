import pygame
from pong.constants import WHITE, BLACK, HEIGHT, WIDTH, MAX_DEFLECTION_SPEED, SPIN_FACTOR
# SCORE_FONT = pygame.font.SysFont("comicsans", 50)

def handle_ball_collision(ball, left_paddle, right_paddle):
    # Top/bottom wall bounce
    if ball.pos[1] + ball.radius >= HEIGHT or ball.pos[1] - ball.radius <= 0:
        ball.vel[1] *= -1  # bounce off top/bottom

    # Ball moving left (collides with left paddle)
    if ball.vel[0] < 0:
        if left_paddle.pos[1] <= ball.pos[1] <= left_paddle.pos[1] + left_paddle.height:
            if ball.pos[0] - ball.radius <= left_paddle.pos[0] + left_paddle.width:
                relative_velocity = ball.vel[1] - left_paddle.vel[1]
                impulse = 2 * ball.mass * relative_velocity
                ball.apply_impulse([0, -impulse])
                ball.spin = left_paddle.vel[1] * 0.5

                # recoil effect on paddle
                left_paddle.apply_impulse([0, -impulse * 0.1])

                # angle deflection logic
                middle_y = left_paddle.pos[1] + left_paddle.height / 2
                offset = ball.pos[1] - middle_y
                normalized_offset = offset / (left_paddle.height / 2)
                ball.vel[1] = normalized_offset * MAX_DEFLECTION_SPEED + left_paddle.vel[1] * SPIN_FACTOR

                ball.vel[0] *= -1

    # Ball moving right (collides with right paddle)
    elif ball.vel[0] > 0:
        if right_paddle.pos[1] <= ball.pos[1] <= right_paddle.pos[1] + right_paddle.height:
            if ball.pos[0] + ball.radius >= right_paddle.pos[0]:
                relative_velocity = ball.vel[1] - right_paddle.vel[1]
                impulse = 2 * ball.mass * relative_velocity
                ball.apply_impulse([0, -impulse])
                ball.spin = right_paddle.vel[1] * 0.5

                # recoil effect on paddle
                right_paddle.apply_impulse([0, -impulse * 0.1])

                # angle deflection logic
                middle_y = right_paddle.pos[1] + right_paddle.height / 2
                offset = ball.pos[1] - middle_y
                normalized_offset = offset / (right_paddle.height / 2)
                ball.vel[1] = normalized_offset * MAX_DEFLECTION_SPEED + right_paddle.vel[1] * SPIN_FACTOR

                ball.vel[0] *= -1

def handle_paddle_movement(keys, left_paddle, right_paddle):
    if keys[pygame.K_w]:
        left_paddle.accelerate(up=True)
    if keys[pygame.K_s]:
        left_paddle.accelerate(up=False)

    if keys[pygame.K_UP]:
        right_paddle.accelerate(up=True)
    if keys[pygame.K_DOWN]:
        right_paddle.accelerate(up=False)

def draw(win, paddles, ball, left_score, right_score, score_font):
    win.fill(BLACK)

    left_text = score_font.render(f"{left_score}", 1, WHITE)
    right_text = score_font.render(f"{right_score}", 1, WHITE)
    win.blit(left_text, (WIDTH // 4 - left_text.get_width() // 2, 20))
    win.blit(right_text, (WIDTH * 3 // 4 - right_text.get_width() // 2, 20))

    for paddle in paddles:
        paddle.draw(win)

    for i in range(10, HEIGHT, HEIGHT // 20):
        if i % 2 == 0:
            pygame.draw.rect(win, WHITE, (WIDTH // 2 - 5, i, 10, HEIGHT // 20))

    ball.draw(win)
    pygame.display.update()
