import pygame
from pong_BETA.constants import WHITE, BLACK, HEIGHT, WIDTH, MAX_DEFLECTION_SPEED, SPIN_FACTOR
import numpy as np

def handle_ball_collision(ball, left_paddle, right_paddle):
    max_ball_speed = 7  # Safe ball speed

    # Top/bottom wall bounce
    if ball.pos[1] + ball.radius >= HEIGHT or ball.pos[1] - ball.radius <= 0:
        ball.vel[1] *= -1

    # LEFT PADDLE collision (swept + overlap check, real x transfer)
    hit_x = (
        (ball.prev_pos[0] - ball.radius > left_paddle.pos[0] + left_paddle.width and
         ball.pos[0] - ball.radius <= left_paddle.pos[0] + left_paddle.width)
        or
        (left_paddle.pos[0] < ball.pos[0] < left_paddle.pos[0] + left_paddle.width)
    )
    if (
        hit_x and
        left_paddle.pos[1] - ball.radius <= ball.pos[1] <= left_paddle.pos[1] + left_paddle.height + ball.radius and
        ball.last_hit_by != "left"
    ):
        relative_velocity = ball.vel[1] - left_paddle.vel[1]
        impulse = 2 * ball.mass * relative_velocity
        ball.apply_impulse([0, -impulse])
        ball.spin = left_paddle.vel[1] * 0.5

        bounce_speed = max_ball_speed * 0.8
        ball.vel[0] = abs(bounce_speed) + left_paddle.vel[0] * 0.6
        ball.spin += left_paddle.vel[0] * 0.15

        left_paddle.apply_impulse([0, -impulse * 0.1])

        middle_y = left_paddle.pos[1] + left_paddle.height / 2
        offset = ball.pos[1] - middle_y
        normalized_offset = offset / (left_paddle.height / 2)
        ball.vel[1] = normalized_offset * MAX_DEFLECTION_SPEED + left_paddle.vel[1] * SPIN_FACTOR

        ball.last_hit_by = "left"

    # RIGHT PADDLE collision (swept + overlap check, real x transfer)
    hit_x = (
        (ball.prev_pos[0] + ball.radius < right_paddle.pos[0] and
         ball.pos[0] + ball.radius >= right_paddle.pos[0])
        or
        (right_paddle.pos[0] < ball.pos[0] < right_paddle.pos[0] + right_paddle.width)
    )
    if (
        hit_x and
        right_paddle.pos[1] - ball.radius <= ball.pos[1] <= right_paddle.pos[1] + right_paddle.height + ball.radius and
        ball.last_hit_by != "right"
    ):
        relative_velocity = ball.vel[1] - right_paddle.vel[1]
        impulse = 2 * ball.mass * relative_velocity
        ball.apply_impulse([0, -impulse])
        ball.spin = right_paddle.vel[1] * 0.5

        bounce_speed = max_ball_speed * 0.8
        ball.vel[0] = -abs(bounce_speed) + right_paddle.vel[0] * 0.6
        ball.spin += right_paddle.vel[0] * 0.15

        right_paddle.apply_impulse([0, -impulse * 0.1])

        middle_y = right_paddle.pos[1] + right_paddle.height / 2
        offset = ball.pos[1] - middle_y
        normalized_offset = offset / (right_paddle.height / 2)
        ball.vel[1] = normalized_offset * MAX_DEFLECTION_SPEED + right_paddle.vel[1] * SPIN_FACTOR

        ball.last_hit_by = "right"

    # Clamp ball speed after all modifications
    ball.vel[0] = np.clip(ball.vel[0], -max_ball_speed, max_ball_speed)
    ball.vel[1] = np.clip(ball.vel[1], -max_ball_speed, max_ball_speed)

    # Reset hit protection when ball is far away from both paddles
    if ball.pos[0] < left_paddle.pos[0] - 2 * ball.radius or ball.pos[0] > right_paddle.pos[0] + right_paddle.width + 2 * ball.radius:
        ball.last_hit_by = None

def handle_paddle_movement(keys, left_paddle, right_paddle):
    # Left paddle (WASD)
    if keys[pygame.K_w]:
        left_paddle.accelerate(up=True)
    if keys[pygame.K_s]:
        left_paddle.accelerate(up=False)
    if keys[pygame.K_a]:
        left_paddle.accelerate(right=False)
    if keys[pygame.K_d]:
        left_paddle.accelerate(right=True)

    # Right paddle (Arrow keys)
    if keys[pygame.K_UP]:
        right_paddle.accelerate(up=True)
    if keys[pygame.K_DOWN]:
        right_paddle.accelerate(up=False)
    if keys[pygame.K_LEFT]:
        right_paddle.accelerate(right=False)
    if keys[pygame.K_RIGHT]:
        right_paddle.accelerate(right=True)

