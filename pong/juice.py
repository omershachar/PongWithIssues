"""
Visual effects system ("game juice") for PongWithIssues.

Provides screen shake, flash overlays, particles, and score pop animations
to make the game feel alive. All effects are lightweight and designed for
60 FPS on an 800x800 window.
"""

import math
import random
import time

import pygame


# ---------------------------------------------------------------------------
# Screen Shake
# ---------------------------------------------------------------------------

class ScreenShake:
    """Camera shake effect with exponential decay."""

    _INTENSITY_SCALE = {
        "off": 0.0,
        "subtle": 0.5,
        "intense": 1.0,
    }

    def __init__(self, intensity="subtle"):
        self.set_intensity(intensity)
        self._magnitude = 0.0
        self._duration = 0.0
        self._start_time = 0.0
        self._active = False

    # -- public API --

    def set_intensity(self, intensity):
        self._scale = self._INTENSITY_SCALE.get(intensity, 0.5)

    def trigger(self, magnitude=5, duration=0.15):
        if self._scale == 0.0:
            return
        self._magnitude = magnitude * self._scale
        self._duration = duration
        self._start_time = time.monotonic()
        self._active = True

    def update(self):
        if not self._active:
            return
        elapsed = time.monotonic() - self._start_time
        if elapsed >= self._duration:
            self._active = False
            self._magnitude = 0.0

    def get_offset(self):
        if not self._active or self._magnitude <= 0.0:
            return (0, 0)
        elapsed = time.monotonic() - self._start_time
        progress = min(elapsed / self._duration, 1.0) if self._duration > 0 else 1.0
        # Exponential decay
        current_mag = self._magnitude * math.exp(-4.0 * progress)
        dx = random.uniform(-current_mag, current_mag)
        dy = random.uniform(-current_mag, current_mag)
        return (int(dx), int(dy))


# ---------------------------------------------------------------------------
# Flash Effect
# ---------------------------------------------------------------------------

class FlashEffect:
    """Semi-transparent full-screen colour overlay that fades out."""

    def __init__(self):
        self._active = False
        self._color = (255, 255, 255)
        self._alpha = 0
        self._max_alpha = 100
        self._duration = 0.1
        self._start_time = 0.0
        # Re-use a single surface to avoid per-frame allocation
        self._surface = pygame.Surface((800, 800), pygame.SRCALPHA)

    def trigger(self, color=(255, 255, 255), alpha=100, duration=0.1):
        self._color = color
        self._max_alpha = alpha
        self._alpha = alpha
        self._duration = duration
        self._start_time = time.monotonic()
        self._active = True

    def update(self):
        if not self._active:
            return
        elapsed = time.monotonic() - self._start_time
        if elapsed >= self._duration:
            self._active = False
            self._alpha = 0
            return
        progress = elapsed / self._duration if self._duration > 0 else 1.0
        self._alpha = int(self._max_alpha * (1.0 - progress))

    def draw(self, surface):
        if not self._active or self._alpha <= 0:
            return
        r, g, b = self._color
        self._surface.fill((r, g, b, self._alpha))
        surface.blit(self._surface, (0, 0))


# ---------------------------------------------------------------------------
# Particle System
# ---------------------------------------------------------------------------

_MAX_PARTICLES = 200
_GRAVITY = 60  # pixels / s^2 (gentle downward pull)


class Particle:
    """Lightweight particle with position, velocity, colour, life, and size."""

    __slots__ = ("x", "y", "vx", "vy", "r", "g", "b", "life", "max_life", "size")

    def __init__(self, x, y, vx, vy, color, life, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r, self.g, self.b = color
        self.life = life
        self.max_life = life
        self.size = size


class ParticleSystem:
    """Manages a pool of lightweight particles."""

    def __init__(self, enabled=True):
        self.enabled = enabled
        self._particles: list[Particle] = []
        self._last_time = time.monotonic()

    def emit(self, x, y, count=10, color=(255, 255, 255), speed=3,
             spread=360, life=0.5, size=3):
        if not self.enabled:
            return
        half_spread = spread / 2.0
        base_angle = 0.0 if spread >= 360 else 0.0
        for _ in range(count):
            angle_deg = random.uniform(base_angle - half_spread,
                                       base_angle + half_spread)
            angle = math.radians(angle_deg)
            spd = speed * random.uniform(0.5, 1.5)
            vx = math.cos(angle) * spd * 60  # convert to px/s
            vy = math.sin(angle) * spd * 60
            p = Particle(x, y, vx, vy, color, life, size)
            self._particles.append(p)
        # Drop oldest if over budget
        overflow = len(self._particles) - _MAX_PARTICLES
        if overflow > 0:
            del self._particles[:overflow]

    def update(self):
        now = time.monotonic()
        dt = now - self._last_time
        self._last_time = now
        if dt <= 0 or not self._particles:
            return
        alive = []
        grav = _GRAVITY * dt
        for p in self._particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += grav
            alive.append(p)
        self._particles = alive

    def draw(self, surface):
        for p in self._particles:
            ratio = max(p.life / p.max_life, 0.0)
            alpha = int(255 * ratio)
            cur_size = max(int(p.size * ratio), 1)
            color = (p.r, p.g, p.b, alpha)
            # Fast path: fully opaque — just draw directly
            if alpha >= 250:
                pygame.draw.circle(surface, (p.r, p.g, p.b),
                                   (int(p.x), int(p.y)), cur_size)
            else:
                # Minimal temp surface for alpha blending
                d = cur_size * 2 + 2
                tmp = pygame.Surface((d, d), pygame.SRCALPHA)
                pygame.draw.circle(tmp, color, (cur_size + 1, cur_size + 1),
                                   cur_size)
                surface.blit(tmp, (int(p.x) - cur_size - 1,
                                   int(p.y) - cur_size - 1))


# ---------------------------------------------------------------------------
# Score Pop
# ---------------------------------------------------------------------------

class _ScorePopEntry:
    """Single score pop animation."""

    __slots__ = ("text", "x", "y", "font", "color", "start_time",
                 "scale", "phase_dur")

    def __init__(self, text, x, y, font, color):
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.start_time = time.monotonic()
        self.scale = 1.0
        self.phase_dur = 0.15  # each phase: grow, then settle

    @property
    def total_duration(self):
        return self.phase_dur * 2

    def alive(self):
        return (time.monotonic() - self.start_time) < self.total_duration

    def update(self):
        elapsed = time.monotonic() - self.start_time
        if elapsed < self.phase_dur:
            # Growing: 1.0 -> 1.5
            t = elapsed / self.phase_dur
            self.scale = 1.0 + 0.5 * t
        elif elapsed < self.total_duration:
            # Settling: 1.5 -> 1.0
            t = (elapsed - self.phase_dur) / self.phase_dur
            self.scale = 1.5 - 0.5 * t
        else:
            self.scale = 1.0


class ScorePop:
    """Manages score pop-up text animations."""

    def __init__(self):
        self._entries: list[_ScorePopEntry] = []

    def trigger(self, text, x, y, font, color=(255, 255, 255)):
        self._entries.append(_ScorePopEntry(text, x, y, font, color))

    def update(self):
        for e in self._entries:
            e.update()
        self._entries = [e for e in self._entries if e.alive()]

    def draw(self, surface):
        for e in self._entries:
            rendered = e.font.render(e.text, True, e.color)
            if abs(e.scale - 1.0) < 0.01:
                # No scaling needed
                rect = rendered.get_rect(center=(e.x, e.y))
                surface.blit(rendered, rect)
            else:
                w = int(rendered.get_width() * e.scale)
                h = int(rendered.get_height() * e.scale)
                if w < 1 or h < 1:
                    continue
                scaled = pygame.transform.smoothscale(rendered, (w, h))
                rect = scaled.get_rect(center=(e.x, e.y))
                surface.blit(scaled, rect)


# ---------------------------------------------------------------------------
# Juice Manager (convenience wrapper)
# ---------------------------------------------------------------------------

class JuiceManager:
    """Central hub for all visual juice effects."""

    def __init__(self, settings=None):
        self.shake = ScreenShake()
        self.flash = FlashEffect()
        self.particles = ParticleSystem()
        self.score_pop = ScorePop()
        self._particles_enabled = True
        if settings:
            self.apply_settings(settings)

    def apply_settings(self, settings):
        """Configure juice from GameSettings."""
        shake_map = {0: "off", 1: "subtle", 2: "intense"}
        self.shake.set_intensity(shake_map.get(settings.screen_shake, "subtle"))
        self._particles_enabled = settings.particles_enabled

    def update(self):
        self.shake.update()
        self.flash.update()
        self.particles.update()
        self.score_pop.update()

    def draw(self, surface):
        """Draw flash overlay, particles, and score pops.

        Screen shake offset is NOT applied here — the caller should use
        ``shake.get_offset()`` to offset their own blit position.
        """
        self.flash.draw(surface)
        self.particles.draw(surface)
        self.score_pop.draw(surface)

    # -- high-level event triggers --

    def on_paddle_hit(self, x, y, color):
        self.shake.trigger(3, 0.1)
        if self._particles_enabled:
            self.particles.emit(x, y, count=8, color=color, speed=3,
                                spread=360, life=0.35, size=3)

    def on_score(self, x, y, score_text, font, color=(255, 255, 255)):
        self.shake.trigger(6, 0.2)
        self.flash.trigger((255, 255, 255), 60, 0.08)
        self.score_pop.trigger(score_text, x, y, font, color)

    def on_powerup_collect(self, x, y, color):
        self.shake.trigger(4, 0.12)
        self.flash.trigger(color, 50, 0.1)
        if self._particles_enabled:
            self.particles.emit(x, y, count=15, color=color, speed=4,
                                spread=360, life=0.5, size=4)

    def on_freeze(self, x, y):
        ice_blue = (80, 180, 255)
        self.flash.trigger(ice_blue, 70, 0.15)
        if self._particles_enabled:
            self.particles.emit(x, y, count=12, color=(255, 255, 255), speed=2,
                                spread=360, life=0.6, size=3)

    def on_wall_bounce(self, x, y):
        if self._particles_enabled:
            self.particles.emit(x, y, count=4, color=(255, 255, 255), speed=2,
                                spread=180, life=0.3, size=2)
