"""
Base class for physical objects with position, mass, and velocity.
Used by Ball, Paddle, and any future physics-driven game objects.
"""

import numpy as np
import math
from pong.constants import GRAVITY

class PhysicsObject:
    """A base class for all physical game objects with mass, position, and velocity."""
    def __init__(self, mass, x, y, x_vel=0, y_vel=0):
        self.mass = mass
        self.pos = np.array([x, y], dtype=float) # Object position in (x,y)
        self.vel = np.array([x_vel, y_vel], dtype=float) # Object velocity in (x,y)
        self.acc = np.array([0.0, 0.0]) # Object acceleration in (x,y)

    @property
    def momentum(self):
        return (self.mass * self.vel) # Momentum -> P = m * v

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