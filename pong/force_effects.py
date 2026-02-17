"""
force_effects.py -- Visual effects for Force Push and Force Pull abilities.

Shockwave arcs, speed-line particles, and converging/expanding ring effects.
Uses __slots__ particles for performance (same pattern as BloodParticle).
"""

import math
import random
import pygame
import numpy as np


class ForceParticle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'life', 'max_life', 'size')

    def __init__(self, x, y, vx, vy, color, life, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size


class Shockwave:
    """Expanding or contracting arc effect."""
    __slots__ = ('x', 'y', 'angle', 'arc_half', 'radius', 'max_radius',
                 'life', 'max_life', 'color', 'expanding', 'width')

    def __init__(self, x, y, angle, arc_half, max_radius, life, color, expanding=True, width=4):
        self.x = x
        self.y = y
        self.angle = angle
        self.arc_half = arc_half
        self.radius = 10.0 if expanding else max_radius
        self.max_radius = max_radius
        self.life = life
        self.max_life = life
        self.color = color
        self.expanding = expanding
        self.width = width


class ForceEffectSystem:
    """Manages Force Push/Pull visual effects: shockwaves + particles."""

    MAX_PARTICLES = 150

    def __init__(self):
        self._particles = []
        self._shockwaves = []
        self._glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)

    def emit_push(self, x, y, angle, color, push_range=250):
        """Expanding shockwave arc + speed-line particles in cone direction."""
        bright = _brighten(color)
        self._shockwaves.append(
            Shockwave(x, y, angle, math.radians(30), push_range * 0.8,
                      life=0.3, color=bright, expanding=True, width=5))

        # Speed-line particles outward
        for _ in range(18):
            a = angle + random.uniform(-0.5, 0.5)
            spd = random.uniform(300, 600)
            vx = math.cos(a) * spd
            vy = math.sin(a) * spd
            life = random.uniform(0.15, 0.35)
            size = random.randint(1, 3)
            self._particles.append(
                ForceParticle(x, y, vx, vy, bright, life, size))

    def emit_pull(self, x, y, angle, color, pull_range=300):
        """Contracting ring + converging particles from range boundary inward."""
        bright = _brighten(color)
        self._shockwaves.append(
            Shockwave(x, y, angle, math.radians(35), pull_range * 0.7,
                      life=0.35, color=bright, expanding=False, width=4))

        # Converging particles from range boundary toward origin
        for _ in range(15):
            a = angle + random.uniform(-0.5, 0.5)
            start_dist = pull_range * random.uniform(0.5, 1.0)
            px = x + math.cos(a) * start_dist
            py = y + math.sin(a) * start_dist
            spd = random.uniform(250, 500)
            vx = math.cos(a + math.pi) * spd
            vy = math.sin(a + math.pi) * spd
            life = random.uniform(0.2, 0.4)
            size = random.randint(1, 3)
            self._particles.append(
                ForceParticle(px, py, vx, vy, bright, life, size))

    def update(self, dt):
        # Update shockwaves
        alive_sw = []
        for sw in self._shockwaves:
            sw.life -= dt
            if sw.life <= 0:
                continue
            if sw.expanding:
                progress = 1.0 - sw.life / sw.max_life
                sw.radius = 10.0 + (sw.max_radius - 10.0) * progress
            else:
                progress = 1.0 - sw.life / sw.max_life
                sw.radius = sw.max_radius * (1.0 - progress)
            alive_sw.append(sw)
        self._shockwaves = alive_sw

        # Update particles
        alive = []
        for p in self._particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            # Slow down
            p.vx *= 0.95
            p.vy *= 0.95
            alive.append(p)

        if len(alive) > self.MAX_PARTICLES:
            alive = alive[-self.MAX_PARTICLES:]
        self._particles = alive

    def draw(self, surface):
        # Draw shockwaves as arcs on SRCALPHA surface
        for sw in self._shockwaves:
            alpha_ratio = sw.life / sw.max_life
            r, g, b = sw.color
            alpha = int(180 * alpha_ratio)
            radius = max(5, int(sw.radius))
            rect = pygame.Rect(int(sw.x) - radius, int(sw.y) - radius,
                               radius * 2, radius * 2)
            start_angle = sw.angle - sw.arc_half
            stop_angle = sw.angle + sw.arc_half

            # Draw arc with alpha using a temporary surface
            arc_size = radius * 2 + 20
            if arc_size < 4:
                continue
            temp = pygame.Surface((arc_size, arc_size), pygame.SRCALPHA)
            local_rect = pygame.Rect(10, 10, radius * 2, radius * 2)
            arc_color = (r, g, b, alpha)
            pygame.draw.arc(temp, arc_color, local_rect,
                            start_angle, stop_angle, sw.width)
            surface.blit(temp, (int(sw.x) - radius - 10,
                                int(sw.y) - radius - 10))

        # Draw particles as streaks
        for p in self._particles:
            ratio = max(p.life / p.max_life, 0.0)
            cur_size = max(1, int(p.size * ratio))
            r, g, b = p.color
            alpha = int(220 * ratio)
            speed = math.sqrt(p.vx * p.vx + p.vy * p.vy)
            if speed > 50 and cur_size >= 1:
                dx = p.vx / speed * cur_size * 3
                dy = p.vy / speed * cur_size * 3
                pygame.draw.line(surface, (r, g, b),
                                 (int(p.x - dx), int(p.y - dy)),
                                 (int(p.x + dx), int(p.y + dy)),
                                 max(cur_size, 1))
            else:
                pygame.draw.circle(surface, (r, g, b),
                                   (int(p.x), int(p.y)), cur_size)

    def reset(self):
        self._particles.clear()
        self._shockwaves.clear()


def _brighten(color):
    """Return a brighter, more saturated variant of a color."""
    r, g, b = color[:3]
    return (min(255, r + 80), min(255, g + 80), min(255, b + 80))
