"""
helpers.py -- Handles collision logic and paddle movement input.
"""

import pygame
from pong.constants import *

def handle_ball_collision(ball, left_paddle, right_paddle):
    """
    Handles collisions between the ball and walls or paddles.
    Applies impulse and spin when hitting paddles, and reflects on walls.

    Args:
        ball (Ball): The ball object.
        left_paddle (Paddle): The left paddle.
        right_paddle (Paddle): The right paddle.
    """

    # Wall collision (top and bottom)
    if ball.pos[1] + ball.radius >= HEIGHT:
        ball.pos[1] = HEIGHT - ball.radius
        ball.vel[1] *= -1
    elif ball.pos[1] - ball.radius <= 0:
        ball.pos[1] = ball.radius
        ball.vel[1] *= -1

    # Left paddle collision
    if ball.vel[0] < 0:
        if (left_paddle.pos[1] <= ball.pos[1] <= left_paddle.pos[1] + left_paddle.height and
            ball.pos[0] - ball.radius <= left_paddle.pos[0] + left_paddle.width):

            # Y-direction impulse and spin transfer
            relative_velocity = ball.vel[1] - left_paddle.vel[1]
            impulse = 2 * ball.mass * relative_velocity
            ball.apply_impulse([0, -impulse])
            left_paddle.apply_impulse([0, -impulse * 0.1])
            ball.spin = left_paddle.vel[1] * 0.5

            # Angle deflection logic
            middle_y = left_paddle.pos[1] + left_paddle.height / 2
            offset = ball.pos[1] - middle_y
            normalized_offset = offset / (left_paddle.height / 2)
            ball.vel[1] = normalized_offset * MAX_DEFLECTION_SPEED + left_paddle.vel[1] * SPIN_FACTOR

            ball.vel[0] = abs(ball.vel[0])  # bounce right

    # Right paddle collision
    elif ball.vel[0] > 0:
        if (right_paddle.pos[1] <= ball.pos[1] <= right_paddle.pos[1] + right_paddle.height and
            ball.pos[0] + ball.radius >= right_paddle.pos[0]):

            # Y-direction impulse and spin transfer
            relative_velocity = ball.vel[1] - right_paddle.vel[1]
            impulse = 2 * ball.mass * relative_velocity
            ball.apply_impulse([0, -impulse])
            right_paddle.apply_impulse([0, -impulse * 0.1])
            ball.spin = right_paddle.vel[1] * 0.5

            # Angle deflection logic
            middle_y = right_paddle.pos[1] + right_paddle.height / 2
            offset = ball.pos[1] - middle_y
            normalized_offset = offset / (right_paddle.height / 2)
            ball.vel[1] = normalized_offset * MAX_DEFLECTION_SPEED + right_paddle.vel[1] * SPIN_FACTOR

            ball.vel[0] = -abs(ball.vel[0])  # bounce left

def handle_paddle_movement(keys, left_paddle, right_paddle):
    """
    Handles keyboard input and accelerates paddles accordingly.

    Args:
        keys (dict): pygame.key.get_pressed() dictionary.
        left_paddle (Paddle): Left player paddle.
        right_paddle (Paddle): Right player paddle.
    """
    if keys[pygame.K_w]:
        left_paddle.accelerate(up=True)
    if keys[pygame.K_s]:
        left_paddle.accelerate(up=False)
    if keys[pygame.K_UP]:
        right_paddle.accelerate(up=True)
    if keys[pygame.K_DOWN]:
        right_paddle.accelerate(up=False)
