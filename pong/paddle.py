"""
paddle.py -- Class for storing paddles attributes and methods
"""

import pygame
import numpy as np
from pong.physics_object import PhysicsObject
from pong.constants import *

class Paddle(PhysicsObject):
    def __init__(self, x, y, width, height, color=LIGHT_PURPLE):
        super().__init__(pos=(x, y), mass=1, vel=(0, 0))
        self.original_pos = np.array([x, y], dtype=float)
        self.width = width
        self.height = height
        self.color = color
        
    def draw(self, win):
        pygame.draw.rect(win, self.color, (int(self.pos[0]), int(self.pos[1]), self.width, self.height))

    def accelerate(self, up=True):
        if up:
            self.acc[:] -= PADDLE_DEFAULT_ACC[:]
        else:
            self.acc[:] += PADDLE_DEFAULT_ACC[:]

    def update(self):
        # Apply acceleration to velocity, then decay/friction
        self.vel += self.acc
        self.acc[:] = 0
        # Clamp vertical velocity
        if self.vel[1] > PADDLE_MAX_VEL:
            self.vel[1] = PADDLE_MAX_VEL
        elif self.vel[1] < -PADDLE_MAX_VEL:
            self.vel[1] = -PADDLE_MAX_VEL
        # Update position
        self.pos += self.vel
        # friction_force = self.mass * GRAVITY * FRICTION_COEFFICIENT * -1
        # self.apply_force(friction_force)
        # self.acc *= [0, 1]
        self.vel[1] *= 0.85  # friction/decay only on y
        # Clamp to screen bounds (assuming HEIGHT is global or import)
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.vel[1] = 0
        elif self.pos[1] + self.height > HEIGHT:
            self.pos[1] = HEIGHT - self.height
            self.vel[1] = 0

    def reset(self):
        self.pos = self.original_pos.copy()
        self.vel[:] = 0
        self.acc[:] = 0
# End of class paddle

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
