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
        # Fire colors for the trail (from dark to bright)
        FIRE_COLORS = [DARK_RED, SCARLET, ORANGE_RED, ORANGE, GOLD, YELLOW, WHITE]
        ALL_FIRE_COLORS = [DARK_RED, SCARLET, ORANGE_RED, ORANGE, GOLD, YELLOW, WHITE, GOLD, YELLOW, WHITE]
        color_cycle_len = len(ALL_FIRE_COLORS)

        speed = self.speed
        max_speed = 18
        acc_magnitude = np.linalg.norm(self.acc)
        t = min(acc_magnitude / 15, 1)  # 0 (idle) to 1 (max fire)
        color_idx = int(t * (len(FIRE_COLORS) - 1))
        core_color = FIRE_COLORS[color_idx]

        # --- 1. Draw crazy fire trail ---
        for i, pos in enumerate(self.trail):
            trail_t = i / max(len(self.trail)-1, 1)
            # Flicker alpha for extra fire
            flicker = np.random.randint(-15, 16) if speed > 7 else 0
            alpha = int(max(35, 140 - i * 18 + flicker))
            radius = max(2, int(self.radius * (1 - trail_t * 0.8)))

            # Switch between fire colors in a pattern
            cidx = int((color_idx + i) % color_cycle_len)
            trail_color = ALL_FIRE_COLORS[cidx]
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*trail_color, alpha), (radius, radius), radius)
            win.blit(surface, (pos[0] - radius, pos[1] - radius))

        # --- 2. Glowing "aura" if fast ---
        if speed > 7:
            for layer in range(3, 0, -1):
                aura_r = int(self.radius * (1.2 + 0.25 * layer))
                aura_alpha = 25 * layer + int(min(50, speed * 2))
                aura_color = FIRE_COLORS[min(len(FIRE_COLORS) - 1, color_idx + layer)]
                surf = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*aura_color, aura_alpha), (aura_r, aura_r), aura_r)
                win.blit(surf, (int(self.pos[0]) - aura_r, int(self.pos[1]) - aura_r))

        # --- 3. Over-the-top, animated, color-cycling, growing arc if spinning fast ---
        if abs(self.spin) > 2:
            direction = 0 if self.spin > 0 else math.pi
            arc_rect = pygame.Rect(int(self.pos[0] - self.radius), int(self.pos[1] - self.radius),
                                self.radius * 2, self.radius * 2)
            # The arc's parameters
            arc_len = math.pi + min(math.pi * 0.8, (speed / max_speed) * math.pi * 0.8)
            base_thick = int(5 + min(18, (speed / max_speed) * 22))  # 5 to 23 px

            # Draw multiple arcs: wide blurry base, medium, and tight bright core
            for j in range(5):
                # Flicker/throb by speed
                arc_alpha = 60 + int((np.sin(pygame.time.get_ticks() / 40 + j) + 1) * 80) if speed > 8 else 50 + j*10
                arc_color = ALL_FIRE_COLORS[(color_idx + j) % color_cycle_len]
                thick = base_thick + j * 2
                arc_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                pygame.draw.arc(arc_surf, (*arc_color, min(255, arc_alpha)),
                                pygame.Rect(0, 0, self.radius * 2, self.radius * 2),
                                direction, direction + arc_len, thick)
                win.blit(arc_surf, (int(self.pos[0]) - self.radius, int(self.pos[1]) - self.radius), special_flags=pygame.BLEND_ADD)

        # --- 4. Main ball (core) ---
        # Flicker/brighten a little if super fast
        if speed > 12:
            for k in range(2):
                pygame.draw.circle(
                    win, WHITE if k else core_color,
                    (int(self.pos[0]), int(self.pos[1])),
                    self.radius - k,
                    0
                )
        else:
            pygame.draw.circle(win, core_color, (int(self.pos[0]), int(self.pos[1])), self.radius)

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

# ----------------------- Classic Pong Ball -----------------------
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
