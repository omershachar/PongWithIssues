"""
ball.py -- Class for storing ball attributes and methods
"""

import pygame
import numpy as np
import math
from pong.physics_object import PhysicsObject
from pong.constants import *

class Ball(PhysicsObject):
    """
    A physics-based ball used in the Pong game.
    Supports spin (Magnus effect), visual trail, and velocity-based motion.
    """

    def __init__(self, x, y, radius, color, mass=1, vel=(0, 0)):
        """
        Initializes the ball with position, size, color, and optional velocity.

        Args:
            x (float): Initial X position.
            y (float): Initial Y position.
            radius (int): Ball radius in pixels.
            color (tuple): RGB color value.
            mass (float): Ball mass.
            vel (tuple): Initial velocity vector (vx, vy).
        """
        super().__init__(pos=(x, y), mass=mass, vel=vel)
        self.radius = radius
        self.color = color
        self.spin = 0

        self.trail = []         # Stores previous positions for drawing motion blur
        self.max_trail = 10     # Max trail length
        self.original_pos = np.array([x, y], dtype=float)
        self.original_vel = np.array(vel, dtype=float)

    def draw(self, win):
        """
        Draws the ball, its trail, and spin indicator on the game window.

        Args:
            win (pygame.Surface): Surface to draw on.
        """
        # Draw fading trail behind the ball
        for i, pos in enumerate(self.trail):
            alpha = max(50, 255 - i * 20)
            radius = max(1, self.radius - i // 2)
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*GREY, alpha), (radius, radius), radius)
            win.blit(surface, (pos[0] - radius, pos[1] - radius))

        # Draw main ball
        pygame.draw.circle(win, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

        # Draw red spin arc to indicate rotation direction
        if abs(self.spin) > 0.2:
            direction = 0 if self.spin > 0 else math.pi
            arc_rect = pygame.Rect(int(self.pos[0] - self.radius), int(self.pos[1] - self.radius),
                                   self.radius * 2, self.radius * 2)
            pygame.draw.arc(win, RED, arc_rect, direction, direction + math.pi, 2)

    def move(self):
        """
        Updates velocity and position, applying Magnus effect (curve) based on spin.
        """
        self.vel[1] += self.spin * 0.1  # Magnus effect
        self.pos += self.vel

    def update(self):
        """
        Updates the ball's state each frame:
        - Adds current position to trail
        - Moves the ball using spin
        """
        self.trail.insert(0, (int(self.pos[0]), int(self.pos[1])))
        if len(self.trail) > self.max_trail:
            self.trail.pop()
        self.move()

    def reset(self):
        """
        Resets ball to original position and velocity (with reversed direction),
        clears spin and trail.
        """
        self.pos = self.original_pos.copy()
        self.vel = -self.original_vel.copy()  # Reverses direction
        self.spin = 0
        self.trail.clear()

    @property
    def speed(self):
        """Returns the current speed (magnitude of velocity)."""
        return np.linalg.norm(self.vel)

class BallClassic:
    def __init__(self, x, y, radius, color, vel_x, vel_y):
        self.pos = np.array([x,y], dtype=float)
        self.original_pos = np.array([x, y], dtype=float)
        self.radius = radius
        self.color = color
        self.vel = np.array([vel_x, vel_y], dtype=float)

    # Functions
    def draw(self, win): # Drawing the ball on the board
        pygame.draw.circle(win, self.color, self.pos, self.radius)

    def move(self): # Moving the ball around the board by its current velocity
        self.pos += self.vel

    def bounce_box(self, width, height):
        self.move()
        if self.pos[0] <= 0 or self.pos[0] >= width:
            self.vel *= [-1,1]
        if self.pos[1] <= 0 or self.pos[1] >= height:
            self.vel *= [1,-1]

    def reset(self): # Resetting the ball position to its original position
        self.pos[:] = self.original_pos[:]
        self.vel *= [-1, 0]
# End of class BallClassic
