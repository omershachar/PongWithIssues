"""
helpers.py -- Handles collision logic and paddle movement input.
"""

import pygame
from pong.constants import *

CURSED_SPIN_FACTOR = 0.25

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

def handle_paddle_movement(keys, left_paddle, right_paddle, ai_right=False, touch=None):
    """
    Handles keyboard and touch input to accelerate paddles.

    Args:
        keys (dict): pygame.key.get_pressed() dictionary.
        left_paddle (Paddle): Left player paddle.
        right_paddle (Paddle): Right player paddle.
        ai_right (bool): If True, right paddle is AI-controlled (skip input).
        touch (TouchHandler|None): Touch handler for mobile input.
    """
    # Keyboard input
    if keys[pygame.K_w]:
        left_paddle.accelerate(up=True)
    if keys[pygame.K_s]:
        left_paddle.accelerate(up=False)
    if not ai_right:
        if keys[pygame.K_UP]:
            right_paddle.accelerate(up=True)
        if keys[pygame.K_DOWN]:
            right_paddle.accelerate(up=False)

    # Touch input (supplements keyboard)
    if touch:
        left_target = touch.get_left_target()
        if left_target is not None:
            _move_to_target(left_paddle, left_target)
        if not ai_right:
            right_target = touch.get_right_target()
            if right_target is not None:
                _move_to_target(right_paddle, right_target)


def _move_to_target(paddle, target_y):
    """Move paddle toward a target Y position (for touch input).
    Uses a larger dead zone for finger precision and double-accelerates
    when far away for more responsive feel."""
    paddle_center = paddle.pos[1] + paddle.height / 2
    dead_zone = paddle.height * 0.2
    diff = target_y - paddle_center
    if diff < -dead_zone:
        paddle.accelerate(up=True)
        if abs(diff) > paddle.height:
            paddle.accelerate(up=True)  # Double speed when far away
    elif diff > dead_zone:
        paddle.accelerate(up=False)
        if abs(diff) > paddle.height:
            paddle.accelerate(up=False)


def handle_paddle_movement_cursed(keys, left_paddle, right_paddle, ai_right=False, touch=None):
    """
    Handles keyboard input for Cursed mode paddles with X+Y movement.
    Left paddle: W/S for up/down, A/D for forward/backward.
    Right paddle: UP/DOWN for up/down, LEFT/RIGHT for forward/backward.

    Args:
        keys: pygame.key.get_pressed() dictionary.
        left_paddle (Paddle): Left player paddle (physics mode).
        right_paddle (Paddle): Right player paddle (physics mode).
        ai_right (bool): If True, right paddle is AI-controlled.
        touch (TouchHandler|None): Touch handler for mobile input.
    """
    # Left paddle: W/S for Y, A/D for X
    if keys[pygame.K_w]:
        left_paddle.accelerate(up=True)
    if keys[pygame.K_s]:
        left_paddle.accelerate(up=False)
    if keys[pygame.K_a]:
        left_paddle.accelerate_x(forward=False)
    if keys[pygame.K_d]:
        left_paddle.accelerate_x(forward=True)

    # Right paddle: arrows for Y, LEFT/RIGHT for X
    if not ai_right:
        if keys[pygame.K_UP]:
            right_paddle.accelerate(up=True)
        if keys[pygame.K_DOWN]:
            right_paddle.accelerate(up=False)
        if keys[pygame.K_LEFT]:
            right_paddle.accelerate_x(forward=True)
        if keys[pygame.K_RIGHT]:
            right_paddle.accelerate_x(forward=False)

    # Touch input (Y-axis only for now, same as regular)
    if touch:
        left_target = touch.get_left_target()
        if left_target is not None:
            _move_to_target(left_paddle, left_target)
        if not ai_right:
            right_target = touch.get_right_target()
            if right_target is not None:
                _move_to_target(right_paddle, right_target)


def handle_ball_collision_cursed(ball, left_paddle, right_paddle):
    """
    Insane cursed mode collision handler.

    Key features vs normal:
    - NO direction restriction: either paddle can hit ball from ANY side
    - Massive X-velocity transfer: charging paddle = cannon shot
    - Paddle recoil proportional to impact
    - Reduced spin (0.25x)
    - Multi-hit: same paddle can hit ball repeatedly

    Returns 'left' or 'right' if a paddle hit occurred, None otherwise.
    """
    import numpy as _np
    hit_side = None

    # Wall collision (top and bottom)
    if ball.pos[1] + ball.radius >= HEIGHT:
        ball.pos[1] = HEIGHT - ball.radius
        ball.vel[1] *= -1
    elif ball.pos[1] - ball.radius <= 0:
        ball.pos[1] = ball.radius
        ball.vel[1] *= -1

    for paddle, side in [(left_paddle, 'left'), (right_paddle, 'right')]:
        # Full rect collision — no direction check! Hit from any side.
        px, py = paddle.pos[0], paddle.pos[1]
        pw, ph = paddle.width, paddle.height

        # Find closest point on paddle rect to ball center
        closest_x = max(px, min(ball.pos[0], px + pw))
        closest_y = max(py, min(ball.pos[1], py + ph))
        dx = ball.pos[0] - closest_x
        dy = ball.pos[1] - closest_y
        dist_sq = dx * dx + dy * dy

        if dist_sq < ball.radius * ball.radius:
            # Collision detected! Compute normal from paddle to ball
            dist = max(dist_sq ** 0.5, 0.01)
            nx = dx / dist
            ny = dy / dist

            # Push ball out of paddle
            overlap = ball.radius - dist
            ball.pos[0] += nx * overlap
            ball.pos[1] += ny * overlap

            # Relative velocity of ball vs paddle
            rel_vx = ball.vel[0] - paddle.vel[0]
            rel_vy = ball.vel[1] - paddle.vel[1]
            rel_dot = rel_vx * nx + rel_vy * ny

            # Only bounce if ball is moving INTO the paddle
            if rel_dot < 0:
                # Reflect ball velocity along collision normal
                ball.vel[0] -= 2 * rel_dot * nx
                ball.vel[1] -= 2 * rel_dot * ny

                # Paddle velocity transfer: add paddle vel to ball
                paddle_speed = _np.linalg.norm(paddle.vel)
                if paddle_speed > 1.0:
                    # Transfer 80% of paddle velocity to ball (INSANE power)
                    ball.vel[0] += paddle.vel[0] * 0.8
                    ball.vel[1] += paddle.vel[1] * 0.4

                # Spin transfer (reduced)
                ball.spin = paddle.vel[1] * CURSED_SPIN_FACTOR

                # Angle deflection based on where ball hit paddle
                middle_y = py + ph / 2
                offset = ball.pos[1] - middle_y
                if ph > 0:
                    normalized_offset = offset / (ph / 2)
                    ball.vel[1] += normalized_offset * 2.0

                # Paddle recoil: proportional to ball speed
                ball_speed = _np.linalg.norm(ball.vel)
                recoil = ball_speed * 0.25
                paddle.apply_impulse([-nx * recoil, -ny * recoil])

                hit_side = side

    return hit_side
