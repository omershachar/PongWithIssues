"""
Base class for physical objects with position, mass, and velocity.
Used by Ball, Paddle, and any future physics-driven game objects.
"""

import pygame
import numpy as np
import math
from pong.constants import *

class PhysicsObject:
    """A base class for all physical game objects with mass, position, and velocity."""
    def __init__(self, mass, x, y, x_vel=0, y_vel=0):
        self.mass = mass
        self.pos = np.array([x, y], dtype=float) # Object position in (x,y)
        self.vel = np.array([x_vel, y_vel], dtype=float) # Object velocity in (x,y)
        self.acc = np.array([0.0, 0.0]) # Object acceleration in (x,y)

    @property
    def momentum(self):
        return (self.mass * self.vel) # Momentum = P = m * v

    @property
    def weight(self):
        return self.mass * GRAVITY
    
    @property
    def polar(self):
        r = np.linalg.norm(self.pos) # r = sqrt(x^2 + y^2)
        theta = math.atan2(self.pos[1], self.pos[0]) # theta = arctan(y/x)
        return (r, theta)

    # Functions
    def apply_impulse(self, impulse):
        self.vel += np.array(impulse, dtype=float) / self.mass # Impulse -> J = F * ∆t

    def apply_force(self, force):
        self.acc += np.array(force, dtype=float) / self.mass # force -> F = m * a -> a = F / m

    def update(self, dt=1.0):
        # Update velocity with acceleration, then position with velocity
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        self.acc[:] = 0  # Reset acceleration


"""
physics_objects_classic -- Section containing all physics methods for the game objects collision and movement.
"""

def handle_ball_collision(ball, left_paddle, right_paddle, board_height):
    if ball.pos[1] + ball.radius >= board_height: # Check if the ball has reached the bottom of the board
        ball.vel[1] *= -1 # Changing the ball bouncing direction downwards
    elif ball.pos[1] - ball.radius <= 0: # Check if the ball has reached the top of the board
        ball.vel[1] *= -1 # Changing the ball bouncing direction downwards
    
    # Ball is moving to the left
    if ball.vel[0] < 0:
        # Ball is in the left paddle height range
        if ball.pos[1] >= left_paddle.y and ball.pos[1] <= left_paddle.y + left_paddle.height:
            # Ball is in the left paddle width range
            if ball.pos[0] - ball.radius <= left_paddle.x + left_paddle.width:
                # Collision! Changing the ball direction to the left
                ball.vel[0] *= -1

                # Vertical movement logic
                middle_y = left_paddle.y + left_paddle.height / 2
                difference_in_y = middle_y - ball.pos[1]
                reduction_factor = (left_paddle.height / 2) / abs(ball.vel[0]) # !!
                y_vel = difference_in_y / reduction_factor
                ball.vel[1] = -1 * y_vel

    # Ball is moving to the right
    if ball.vel[0] > 0:
        # Ball is in the right paddle height range
        if ball.pos[1] >= right_paddle.y and ball.pos[1] <= right_paddle.y + right_paddle.height:
            # Ball is in the right paddle width range
            if ball.pos[0] + ball.radius >= right_paddle.x:
                # Collision! Changing the ball direction to the left
                ball.vel[0] *= -1

                # Vertical movement logic
                middle_y = right_paddle.y + right_paddle.height / 2
                difference_in_y = middle_y - ball.pos[1]
                reduction_factor = (right_paddle.height / 2) / abs(ball.vel[0]) # !!
                y_vel = difference_in_y / reduction_factor
                ball.vel[1] = -1 * y_vel
# End of handle_ball_collision()

def handle_paddle_movement(Keys, left_paddle, right_paddle, board_height):
    # Checking if the 'w' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_w] and left_paddle.y - left_paddle.vel >= 0:
        left_paddle.move(up=True)
    # Checking if the 's' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_s] and left_paddle.y + left_paddle.vel + left_paddle.height <= board_height:
        left_paddle.move(up=False)

    # Checking if the 'UP' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_UP] and right_paddle.y - right_paddle.vel >= 0:
        right_paddle.move(up=True)
    # Checking if the 'DOWN' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_DOWN] and right_paddle.y + right_paddle.vel + right_paddle.height <= board_height:
        right_paddle.move(up=False)
# End of handle_paddle_movement()