"""
paddle.py -- Paddle class with physics-based movement.
"""

import pygame
import numpy as np
from pong.physics_object import PhysicsObject
from pong.constants import *

class Paddle(PhysicsObject):
    """
    A vertical paddle controlled by the player or AI.
    Inherits from PhysicsObject to support force-based movement.
    """

    def __init__(self, x, y, width, height, color=LIGHT_PURPLE):
        """
        Initializes the paddle with position, size, and color.

        Args:
            x (float): Initial X position.
            y (float): Initial Y position.
            width (int): Paddle width.
            height (int): Paddle height.
            color (tuple): RGB color value.
        """
        super().__init__(pos=(x, y), mass=1, vel=(0, 0))
        self.original_pos = np.array([x, y], dtype=float)
        self.width = width
        self.height = height
        self.color = color

    def draw(self, win):
        """
        Draws the paddle on the game window.

        Args:
            win (pygame.Surface): Target surface to draw on.
        """
        pygame.draw.rect(win, self.color, (int(self.pos[0]), int(self.pos[1]), self.width, self.height))

    def accelerate(self, up=True):
        """
        Applies vertical acceleration to the paddle.

        Args:
            up (bool): Direction of movement. True for up, False for down.
        """
        if up:
            self.acc[:] -= PADDLE_DEFAULT_ACC[:]
        else:
            self.acc[:] += PADDLE_DEFAULT_ACC[:]

    def update(self):
        """
        Updates paddle position and velocity, applies vertical clamping,
        velocity decay (friction), and keeps the paddle inside the screen.
        """
        self.vel += self.acc
        self.acc[:] = 0

        # Clamp vertical velocity
        self.vel[1] = np.clip(self.vel[1], -PADDLE_MAX_VEL, PADDLE_MAX_VEL)

        # Update position
        self.pos += self.vel

        # Apply friction on Y axis
        self.vel[1] *= 0.85

        # Clamp paddle inside the window (Y axis only)
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.vel[1] = 0
        elif self.pos[1] + self.height > HEIGHT:
            self.pos[1] = HEIGHT - self.height
            self.vel[1] = 0

    def reset(self):
        """
        Resets the paddle to its original position and clears movement.
        """
        self.pos = self.original_pos.copy()
        self.vel[:] = 0
        self.acc[:] = 0

class PaddleClassic:
    def __init__(self, x, y, width, height, color, vel):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = vel
    
    # Functions
    def draw(self, win): # Drawing the paddle on the board
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

    def move(self, up=True): # Moving the paddle vertically on the board by its fixed velocity
        if up:
            self.y -= self.vel
        else:
            self.y += self.vel
    
    def reset(self): # Resetting the paddle position to his original position
        self.x = self.original_x
        self.y = self.original_y
# End of class PaddleClassic
