"""
PhysicsObject: lightweight 2D body for arcade-style physics.
- Symplectic Euler integration (v first, then x)
- Force accumulation per step
- Impulses
- Optional damping and speed cap
"""

from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

__all__ = ["PhysicsObject"]

@dataclass
class _Limits:
    max_speed: float | None = None  # pixels/sec cap

class PhysicsObject:
    def __init__(
        self,
        pos=(0.0, 0.0),
        vel=(0.0, 0.0),
        mass: float = 1.0,
        color=(255, 255, 255),
        gravity=(0.0, 0.0),
        max_speed: float | None = None,
        damping: float = 0.0,
    ):
        self.pos = np.array(pos, dtype=float)        # (x, y)
        self.vel = np.array(vel, dtype=float)        # (vx, vy)
        self.mass = float(mass)
        self.color = color
        self.gravity = np.array(gravity, dtype=float)  # (gx, gy) px/s^2
        self.damping = float(damping)                 # per-second linear damping
        self._forces: list[np.ndarray] = []           # accumulated this step
        self._limits = _Limits(max_speed=max_speed)

    # --- Properties ---------------------------------------------------------
    @property
    def momentum(self) -> np.ndarray:
        return self.mass * self.vel

    @property
    def polar(self) -> tuple[float, float]:
        r = float(np.linalg.norm(self.pos))
        theta = math.atan2(self.pos[1], self.pos[0])
        return (r, theta)

    @property
    def max_speed(self) -> float | None:
        return self._limits.max_speed

    # --- External controls --------------------------------------------------
    def add_force(self, force) -> None:
        """Queue a force (Fx, Fy) for this step."""
        self._forces.append(np.array(force, dtype=float))

    def apply_impulse(self, J) -> None:
        """Instant velocity change: v += J/m."""
        self.vel += np.array(J, dtype=float) / self.mass

    def set_gravity(self, g) -> None:
        self.gravity[:] = np.array(g, dtype=float)

    def set_max_speed(self, s: float | None) -> None:
        self._limits.max_speed = None if s is None else float(s)

    def set_damping(self, d: float) -> None:
        self.damping = max(0.0, float(d))

    def reset_motion(self, pos=None, vel=None) -> None:
        if pos is not None:
            self.pos[:] = np.array(pos, dtype=float)
        if vel is not None:
            self.vel[:] = np.array(vel, dtype=float)
        self._forces.clear()

    # --- Integration (symplectic Euler) ------------------------------------
    def integrate(self, dt: float) -> None:
        """
        Symplectic Euler (semi-implicit):
            a = (ΣF)/m + g
            v += a*dt
            v *= (1 - damping*dt)     # simple linear drag
            clamp |v|
            x += v*dt
        """
        # Acceleration
        if self._forces:
            total_force = np.sum(self._forces, axis=0)
            self._forces.clear()
        else:
            total_force = np.zeros(2)

        a = total_force / self.mass + self.gravity

        # Update velocity first
        self.vel += a * dt

        # Damping (stable for small dt; avoid negative factor)
        if self.damping > 0.0:
            k = max(0.0, 1.0 - self.damping * dt)
            self.vel *= k

        # Cap speed
        if self._limits.max_speed is not None:
            speed = float(np.linalg.norm(self.vel))
            if speed > self._limits.max_speed:
                self.vel *= (self._limits.max_speed / max(speed, 1e-12))

        # Update position
        self.pos += self.vel * dt

    # --- Optional helpers ---------------------------------------------------
    def clamp_to_rect(self, rect_origin, rect_size, radius=0.0) -> None:
        """
        Clamp inside an axis-aligned rectangle, with optional radius (for discs/boxes).
        No bounce; just clamps position.
        """
        x0, y0 = rect_origin
        w, h = rect_size
        self.pos[0] = np.clip(self.pos[0], x0 + radius, x0 + w - radius)
        self.pos[1] = np.clip(self.pos[1], y0 + radius, y0 + h - radius)

    def bounce_in_rect(self, rect_origin, rect_size, e=1.0, radius=0.0) -> bool:
        """
        Elastic bounce inside rect; returns True if any collision happened.
        """
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
