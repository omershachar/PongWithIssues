"""
helpers.py -- File for handling object collision.
"""

import pygame
from pong.constants import *

def handle_ball_collision(ball, left_paddle, right_paddle):
    # Top/bottom wall bounce
    if ball.pos[1] + ball.radius >= HEIGHT:
        ball.pos[1] = HEIGHT - ball.radius
        ball.vel[1] *= -1
    elif ball.pos[1] - ball.radius <= 0:
        ball.pos[1] = ball.radius
        ball.vel[1] *= -1

    # Ball moving left (collides with left paddle)
    if ball.vel[0] < 0:
        if (left_paddle.pos[1] <= ball.pos[1] <= left_paddle.pos[1] + left_paddle.height and
            ball.pos[0] - ball.radius <= left_paddle.pos[0] + left_paddle.width):
            
            relative_velocity = ball.vel[1] - left_paddle.vel[1]
            impulse = 2 * ball.mass * relative_velocity
            ball.apply_impulse([0, -impulse])
            ball.spin = left_paddle.vel[1] * 0.5
            left_paddle.apply_impulse([0, -impulse * 0.1])

            # angle deflection logic
            middle_y = left_paddle.pos[1] + left_paddle.height / 2
            offset = ball.pos[1] - middle_y
            normalized_offset = offset / (left_paddle.height / 2)
            ball.vel[1] = normalized_offset * MAX_DEFLECTION_SPEED + left_paddle.vel[1] * SPIN_FACTOR

            ball.vel[0] = abs(ball.vel[0])  # bounce right

    # Ball moving right (collides with right paddle)
    elif ball.vel[0] > 0:
        if (right_paddle.pos[1] <= ball.pos[1] <= right_paddle.pos[1] + right_paddle.height and
            ball.pos[0] + ball.radius >= right_paddle.pos[0]):
            
            relative_velocity = ball.vel[1] - right_paddle.vel[1]
            impulse = 2 * ball.mass * relative_velocity
            ball.apply_impulse([0, -impulse])
            ball.spin = right_paddle.vel[1] * 0.5
            right_paddle.apply_impulse([0, -impulse * 0.1])

            # angle deflection logic
            middle_y = right_paddle.pos[1] + right_paddle.height / 2
            offset = ball.pos[1] - middle_y
            normalized_offset = offset / (right_paddle.height / 2)
            ball.vel[1] = normalized_offset * MAX_DEFLECTION_SPEED + right_paddle.vel[1] * SPIN_FACTOR

            ball.vel[0] = -abs(ball.vel[0])  # bounce left

def handle_paddle_movement(keys, left_paddle, right_paddle):
    if keys[pygame.K_w]:
        left_paddle.accelerate(up=True)
    if keys[pygame.K_s]:
        left_paddle.accelerate(up=False)
    if keys[pygame.K_UP]:
        right_paddle.accelerate(up=True)
    if keys[pygame.K_DOWN]:
        right_paddle.accelerate(up=False)
