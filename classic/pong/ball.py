"""
ball.py -- Class for storing ball attributes and methods
"""

import pygame
import numpy as np

class Ball:
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

    def reset(self): # Resetting the ball position to its original position
        self.pos[:] = self.original_pos[:]
        self.vel *= [-1, 0]
# End of class Ball
