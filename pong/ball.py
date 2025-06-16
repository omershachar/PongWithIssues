"""
ball.py -- Class for storing ball attributes and methods
"""

import pygame
import numpy as np
from pong.physics_object import PhysicsObject

class Ball(PhysicsObject):
    def __init__(self, x, y, radius, mass=1):
        super().__init__(mass, x, y, x_vel=5, y_vel=0)
        self.spin = 0
        self.trail = []  # stores past positions
        self.max_trail = 10  # max trail length
        self.radius = radius
        self.original_pos = np.array([x, y], dtype=float)
