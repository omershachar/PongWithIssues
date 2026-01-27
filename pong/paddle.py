"""
paddle.py -- Unified Paddle class for both Classic and Physics modes
"""

import pygame
import numpy as np
from pong.physics_object import PhysicsObject
from pong.constants import *


class Paddle(PhysicsObject):
    """
    A unified paddle class supporting both classic and physics-based Pong modes.

    In 'physics' mode: Uses acceleration-based movement with friction and momentum.
    In 'classic' mode: Uses direct velocity-based movement.
    """

    def __init__(self, x, y, width, height, color=LIGHT_PURPLE, mode='physics', fixed_vel=PADDLE_DEFAULT_VEL):
        """
        Initializes the paddle with position, size, and color.

        Args:
            x (float): Initial X position.
            y (float): Initial Y position.
            width (int): Paddle width.
            height (int): Paddle height.
            color (tuple): RGB color value.
            mode (str): 'classic' or 'physics'
            fixed_vel (float): Fixed velocity for classic mode.
        """
        super().__init__(pos=(x, y), mass=1, vel=(0, 0))
        self.original_pos = np.array([x, y], dtype=float)
        self.width = width
        self.height = height
        self.color = color
        self.mode = mode
        self.fixed_vel = fixed_vel

    # Properties for backwards compatibility with classic mode code
    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, val):
        self.pos[0] = val

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, val):
        self.pos[1] = val

    @property
    def original_x(self):
        return self.original_pos[0]

    @property
    def original_y(self):
        return self.original_pos[1]

    def draw(self, win):
        """Draws the paddle on the game window."""
        pygame.draw.rect(win, self.color, (int(self.pos[0]), int(self.pos[1]), self.width, self.height))

    def accelerate(self, up=True):
        """
        Applies acceleration (physics mode) or direct movement (classic mode).

        Args:
            up (bool): Direction of movement. True for up, False for down.
        """
        if self.mode == 'classic':
            self.move(up)
        else:
            if up:
                self.acc[:] -= PADDLE_DEFAULT_ACC[:]
            else:
                self.acc[:] += PADDLE_DEFAULT_ACC[:]

    def move(self, up=True):
        """
        Direct movement for classic mode.

        Args:
            up (bool): Direction of movement. True for up, False for down.
        """
        if up:
            self.pos[1] -= self.fixed_vel
        else:
            self.pos[1] += self.fixed_vel
        self._clamp_to_screen()

    def update(self):
        """
        Updates paddle position. Physics mode uses acceleration, classic uses direct movement.
        """
        if self.mode == 'physics':
            self.vel += self.acc
            self.acc[:] = 0

            # Clamp vertical velocity
            self.vel[1] = np.clip(self.vel[1], -PADDLE_MAX_VEL, PADDLE_MAX_VEL)

            # Update position
            self.pos += self.vel

            # Apply friction on Y axis
            self.vel[1] *= 0.85

        # Classic mode doesn't need update() - movement is direct
        self._clamp_to_screen()

    def _clamp_to_screen(self):
        """Keeps the paddle inside the screen bounds."""
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.vel[1] = 0
        elif self.pos[1] + self.height > HEIGHT:
            self.pos[1] = HEIGHT - self.height
            self.vel[1] = 0

    def reset(self):
        """Resets the paddle to its original position and clears movement."""
        self.pos = self.original_pos.copy()
        self.vel[:] = 0
        self.acc[:] = 0


# ----------------------- Legacy Alias for Backwards Compatibility -----------------------
class PaddleClassic(Paddle):
    """
    @deprecated: Use Paddle with mode='classic' instead
    """
    def __init__(self, x, y, width, height, color, vel):
        super().__init__(x, y, width, height, color, mode='classic', fixed_vel=vel)
