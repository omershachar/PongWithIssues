"""
Base class for physical objects with position, mass, and velocity.
Used by Ball, Paddle, and any future physics-driven game objects.
"""

import pygame
import numpy as np
import math
from pong.constants import *

class PhysicsObject:
    """
    A base class for all physical game objects with mass, position, and velocity.
    Handles motion using Newtonian physics and time-based integration.
    """

    def __init__(self, pos=(MIDDLE_BOARD[0], MIDDLE_BOARD[1]), vel=(0, 0), acc=(0, 0), mass=1, color=WHITE):
        """
        Initializes the physical object.

        Args:
            pos (tuple): Initial position (x, y).
            vel (tuple): Initial velocity (vx, vy).
            acc (tuple): Initial acceleration (ax, ay).
            mass (float): Object's mass.
            color (tuple): RGB color (used for drawing).
        """
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array(vel, dtype=float)
        self.acc = np.array(acc, dtype=float)
        self.mass = mass
        self.color = color
        self.forces = []

    @property
    def momentum(self):
        """Returns the linear momentum vector: P = m * v"""
        return self.mass * self.vel

    @property
    def weight(self):
        """Returns the gravitational force: W = m * g"""
        return self.mass * GRAVITY

    @property
    def polar(self):
        """
        Returns the position in polar coordinates (r, θ),
        where r = √(x² + y²), θ = arctan(y / x)
        """
        r = np.linalg.norm(self.pos)
        theta = math.atan2(self.pos[1], self.pos[0])
        return (r, theta)

    def apply_impulse(self, impulse):
        """
        Applies an impulse vector to the object.
        J = ΔP = m * Δv ⇒ v += J / m

        Args:
            impulse (array-like): Impulse vector (Ix, Iy)
        """
        self.vel += np.array(impulse, dtype=float) / self.mass

    def apply_force(self, force, dt):
        """
        Applies a force over time, converting it to an impulse.

        Args:
            force (array-like): Force vector (Fx, Fy)
            dt (float): Time interval (in seconds)
        """
        impulse = np.array(force, dtype=float) * dt
        self.apply_impulse(impulse)

    def update(self, dt=1.0):
        """
        Updates the velocity and position using kinematic equations:
        s = v₀t + ½at², v = v₀ + at

        Args:
            dt (float): Time interval in seconds
        """
        self.pos += self.vel * dt + 0.5 * self.acc * dt ** 2
        self.vel += self.acc * dt
        self.acc[:] = 0  # Reset acceleration after update

    def add_force(self, force):
        """
        Adds a force to be accumulated and integrated during the frame.

        Args:
            force (array-like): Force vector (Fx, Fy)
        """
        self.forces.append(np.array(force, dtype=float))

    def integrate(self, dt):
        """
        Applies all accumulated forces and updates the object's motion.

        Args:
            dt (float): Time step in seconds
        """
        total_force = np.sum(self.forces, axis=0) if self.forces else np.zeros(2)
        self.apply_force(total_force, dt)
        self.update(dt)
        self.forces.clear()

    def clamp_velocity(self, max_speed):
        """
        Limits the velocity magnitude to a maximum value.

        Args:
            max_speed (float): Maximum speed allowed
        """
        speed = np.linalg.norm(self.vel)
        if speed > max_speed:
            self.vel = self.vel / speed * max_speed

    def clamp_to_board(self, buffer=(0, 0), board=(WIDTH, HEIGHT), board_origin=(0,0)):
        """
        Constrains the object to stay within the visible given board.

        Args:
            buffer (tuple): (x_buffer, y_buffer) padding from edges (object dimensions usually)
            board (tuple): (x_board, y_board) board sizes (the default is the width and height in constants.py)
            board origin (tuple): (board_origin_x, board_origin_y) the start location of the board (default is 0,0)
        """
        self.pos[0] = np.clip(self.pos[0], board_origin[0] + buffer[0], board[0] - buffer[0])
        self.pos[1] = np.clip(self.pos[1], board_origin[1] + buffer[1], board[1] - buffer[1])

    # --- Reference Physics Formulas ---
    """
    s = v₀t + ½at²       (position update)
    v = v₀ + at          (velocity update)
    a = dv/dt            (acceleration)
    P = mv               (momentum)
    J = FΔt = ΔP         (impulse)
    F = ma = dP/dt       (force)

    v² = v₀² + 2as       (used for some collision detection)
    """
