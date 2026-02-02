"""
physics_object.py -- Base class for physical objects with position, mass, and velocity.
Used by Ball, Paddle, Box, and any future physics-driven game objects.

Supports:
- Newtonian mechanics (F=ma, impulse-based collisions)
- Force accumulation per step
- Symplectic Euler integration with optional gravity, damping, speed cap
- Rect clamping and elastic bouncing helpers
"""

from __future__ import annotations
import math
import numpy as np
from pong.constants import *

__all__ = ["PhysicsObject"]


class PhysicsObject:
    """
    Base class for all physical game objects with mass, position, and velocity.
    """

    def __init__(
        self,
        pos=(MIDDLE_BOARD[0], MIDDLE_BOARD[1]),
        vel=(0, 0),
        acc=(0, 0),
        mass=1,
        color=WHITE,
        gravity=(0.0, 0.0),
        max_speed: float | None = None,
        damping: float = 0.0,
    ):
        self.pos = np.array(pos, dtype=float)
        self.vel = np.array(vel, dtype=float)
        self.acc = np.array(acc, dtype=float)
        self.mass = float(mass)
        self.color = color
        self.gravity = np.array(gravity, dtype=float)
        self.damping = float(damping)
        self._max_speed = max_speed
        self.forces = []

    # --- Properties ---------------------------------------------------------

    @property
    def momentum(self):
        """Returns the linear momentum vector: P = m * v"""
        return self.mass * self.vel

    @property
    def weight(self):
        """Returns the gravitational force: W = m * g"""
        return self.mass * GRAVITY

    @property
    def polar(self) -> tuple[float, float]:
        """Returns position in polar coordinates (r, theta)."""
        r = float(np.linalg.norm(self.pos))
        theta = math.atan2(self.pos[1], self.pos[0])
        return (r, theta)

    @property
    def max_speed(self) -> float | None:
        return self._max_speed

    @max_speed.setter
    def max_speed(self, value):
        self._max_speed = None if value is None else float(value)

    # --- Forces & Impulses --------------------------------------------------

    def apply_impulse(self, impulse):
        """Instant velocity change: v += J / m."""
        self.vel += np.array(impulse, dtype=float) / self.mass

    def apply_force(self, force, dt):
        """Applies a force over time, converting to impulse."""
        impulse = np.array(force, dtype=float) * dt
        self.apply_impulse(impulse)

    def add_force(self, force):
        """Queue a force (Fx, Fy) to be applied during integration."""
        self.forces.append(np.array(force, dtype=float))

    # --- Setters for runtime tuning -----------------------------------------

    def set_gravity(self, g):
        self.gravity[:] = np.array(g, dtype=float)

    def set_max_speed(self, s: float | None):
        self._max_speed = None if s is None else float(s)

    def set_damping(self, d: float):
        self.damping = max(0.0, float(d))

    def reset_motion(self, pos=None, vel=None):
        if pos is not None:
            self.pos[:] = np.array(pos, dtype=float)
        if vel is not None:
            self.vel[:] = np.array(vel, dtype=float)
        self.acc[:] = 0
        self.forces.clear()

    # --- Integration --------------------------------------------------------

    def update(self, dt=1.0):
        """
        Simple kinematic update: s = v0*t + 0.5*a*t^2, v = v0 + a*t.
        Resets acceleration after update.
        """
        self.pos += self.vel * dt + 0.5 * self.acc * dt ** 2
        self.vel += self.acc * dt
        self.acc[:] = 0

    def integrate(self, dt: float):
        """
        Symplectic Euler integration with accumulated forces, gravity,
        damping, and speed cap.
        """
        if self.forces:
            total_force = np.sum(self.forces, axis=0)
            self.forces.clear()
        else:
            total_force = np.zeros(2)

        a = total_force / self.mass + self.gravity

        # Update velocity first (symplectic Euler)
        self.vel += a * dt

        # Linear damping
        if self.damping > 0.0:
            k = max(0.0, 1.0 - self.damping * dt)
            self.vel *= k

        # Speed cap
        if self._max_speed is not None:
            speed = float(np.linalg.norm(self.vel))
            if speed > self._max_speed:
                self.vel *= (self._max_speed / max(speed, 1e-12))

        # Update position
        self.pos += self.vel * dt

    # --- Clamping & Bouncing ------------------------------------------------

    def clamp_velocity(self, max_speed):
        """Limits velocity magnitude to max_speed."""
        speed = np.linalg.norm(self.vel)
        if speed > max_speed:
            self.vel = self.vel / speed * max_speed

    def clamp_to_board(self, buffer=(0, 0), board=(WIDTH, HEIGHT), board_origin=(0, 0)):
        """Constrains position within the board with buffer padding."""
        self.pos[0] = np.clip(self.pos[0], board_origin[0] + buffer[0], board[0] - buffer[0])
        self.pos[1] = np.clip(self.pos[1], board_origin[1] + buffer[1], board[1] - buffer[1])

    def clamp_to_rect(self, rect_origin, rect_size, radius=0.0):
        """Clamp inside an axis-aligned rectangle with optional radius."""
        x0, y0 = rect_origin
        w, h = rect_size
        self.pos[0] = np.clip(self.pos[0], x0 + radius, x0 + w - radius)
        self.pos[1] = np.clip(self.pos[1], y0 + radius, y0 + h - radius)

    def bounce_in_rect(self, rect_origin, rect_size, e=1.0, radius=0.0):
        """Elastic bounce inside rect; returns True if any collision happened."""
        x0, y0 = rect_origin
        w, h = rect_size
        hit = False

        if self.pos[0] - radius < x0:
            self.pos[0] = x0 + radius
            self.vel[0] = -self.vel[0] * e
            hit = True
        elif self.pos[0] + radius > x0 + w:
            self.pos[0] = x0 + w - radius
            self.vel[0] = -self.vel[0] * e
            hit = True

        if self.pos[1] - radius < y0:
            self.pos[1] = y0 + radius
            self.vel[1] = -self.vel[1] * e
            hit = True
        elif self.pos[1] + radius > y0 + h:
            self.pos[1] = y0 + h - radius
            self.vel[1] = -self.vel[1] * e
            hit = True

        return hit

    # --- Reference Physics Formulas ---
    """
    s = v₀t + ½at²       (position update)
    v = v₀ + at          (velocity update)
    a = dv/dt = Δv/Δt    (acceleration)
    P = mv               (momentum)
    J = FΔt = ΔP = mΔv   (impulse)
    F = ma = dP/dt       (force)
    """
