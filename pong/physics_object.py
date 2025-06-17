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
    def __init__(self, pos=(0, 0), mass=1, vel=(0, 0), acc=(0, 0)):
        self.mass = mass
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array(vel, dtype=float)
        self.acc = np.array(acc, dtype=float)
    # e.g. - obj1 = PhysicsObject(pos=(100, 200), mass=2, vel=(1, 0)) || obj2 = PhysicsObject() # All zeros, mass=1

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
