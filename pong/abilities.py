"""
abilities.py -- Extensible ability system for Cursed Mode.

Provides a base Ability class and concrete Force Push / Force Pull powers.
AbilityManager routes activation, update, and draw for both sides.
"""

import math
import time
import pygame
import numpy as np
from pong.constants import WIDTH, HEIGHT, FONT_TINY_DIGITAL, DARK_GREY


class Ability:
    """Base class for all abilities. Subclass and override activate/update/draw."""

    def __init__(self, cooldown_duration=2.0, active_duration=0.15):
        self.cooldown_duration = cooldown_duration
        self.active_duration = active_duration
        self._cooldown_timer = 0.0
        self._active_timer = 0.0
        self._active = False

    def is_ready(self):
        return self._cooldown_timer <= 0.0 and not self._active

    def try_activate(self, **kwargs):
        if not self.is_ready():
            return False
        self._active = True
        self._active_timer = self.active_duration
        self._cooldown_timer = self.cooldown_duration
        self.activate(**kwargs)
        return True

    def activate(self, **kwargs):
        """Override in subclass. Called once when ability fires."""
        pass

    def tick(self, dt):
        """Per-frame update. Call from AbilityManager."""
        if self._cooldown_timer > 0:
            self._cooldown_timer = max(0.0, self._cooldown_timer - dt)
        if self._active:
            self._active_timer -= dt
            if self._active_timer <= 0:
                self._active = False
            else:
                self.update_active(dt)

    def update_active(self, dt):
        """Override for per-frame logic while ability is active."""
        pass

    @property
    def cooldown_fraction(self):
        """0.0 = ready, 1.0 = full cooldown remaining."""
        if self.cooldown_duration <= 0:
            return 0.0
        return min(1.0, self._cooldown_timer / self.cooldown_duration)


class ForcePush(Ability):
    """Cone-based impulse pushing objects away from the player."""

    RANGE = 250.0
    CONE_HALF_ANGLE = math.radians(30)  # 60 deg total
    STRENGTH = 15.0

    def __init__(self):
        super().__init__(cooldown_duration=2.0, active_duration=0.15)
        self._origin = None
        self._direction = None
        self._applied = False

    def activate(self, origin=None, direction=None, **kwargs):
        self._origin = np.array(origin, dtype=float) if origin is not None else None
        self._direction = float(direction) if direction is not None else 0.0
        self._applied = False

    def apply_to_objects(self, objects, grabbed_obj=None):
        """Apply impulse to objects in cone. Call once per activation."""
        if self._applied or self._origin is None:
            return
        self._applied = True

        for obj, multiplier in objects:
            if obj is grabbed_obj:
                continue
            obj_center = np.array([
                obj.pos[0] + getattr(obj, 'width', getattr(obj, 'radius', 0)) / 2,
                obj.pos[1] + getattr(obj, 'height', getattr(obj, 'radius', 0)) / 2,
            ], dtype=float)
            delta = obj_center - self._origin
            dist = float(np.linalg.norm(delta))
            if dist < 1.0 or dist > self.RANGE:
                continue

            # Check cone angle
            angle_to_obj = math.atan2(delta[1], delta[0])
            angle_diff = angle_to_obj - self._direction
            # Normalize to [-pi, pi]
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.CONE_HALF_ANGLE:
                continue

            # Impulse falls off with distance
            falloff = 1.0 - dist / self.RANGE
            strength = self.STRENGTH * falloff * multiplier
            impulse = np.array([
                math.cos(self._direction) * strength,
                math.sin(self._direction) * strength,
            ])
            obj.apply_impulse(impulse)


class ForcePull(Ability):
    """Cone-based impulse pulling objects toward the player."""

    RANGE = 300.0
    CONE_HALF_ANGLE = math.radians(30)
    STRENGTH = 12.0

    def __init__(self):
        super().__init__(cooldown_duration=2.5, active_duration=0.15)
        self._origin = None
        self._direction = None
        self._applied = False

    def activate(self, origin=None, direction=None, **kwargs):
        self._origin = np.array(origin, dtype=float) if origin is not None else None
        self._direction = float(direction) if direction is not None else 0.0
        self._applied = False

    def apply_to_objects(self, objects, grabbed_obj=None):
        """Apply pull impulse to objects in cone."""
        if self._applied or self._origin is None:
            return
        self._applied = True

        for obj, multiplier in objects:
            if obj is grabbed_obj:
                continue
            obj_center = np.array([
                obj.pos[0] + getattr(obj, 'width', getattr(obj, 'radius', 0)) / 2,
                obj.pos[1] + getattr(obj, 'height', getattr(obj, 'radius', 0)) / 2,
            ], dtype=float)
            delta = obj_center - self._origin
            dist = float(np.linalg.norm(delta))
            if dist < 1.0 or dist > self.RANGE:
                continue

            angle_to_obj = math.atan2(delta[1], delta[0])
            angle_diff = angle_to_obj - self._direction
            angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.CONE_HALF_ANGLE:
                continue

            falloff = 1.0 - dist / self.RANGE
            strength = self.STRENGTH * falloff * multiplier
            # Pull = impulse TOWARD origin (opposite of delta direction)
            pull_angle = math.atan2(-delta[1], -delta[0])
            impulse = np.array([
                math.cos(pull_angle) * strength,
                math.sin(pull_angle) * strength,
            ])
            obj.apply_impulse(impulse)


class ChargedForcePush(ForcePush):
    """Charged version: 2.8x strength, 50deg half-cone, 1.3x range, 0.5s cooldown."""

    RANGE = ForcePush.RANGE * 1.3
    CONE_HALF_ANGLE = math.radians(50)
    STRENGTH = ForcePush.STRENGTH * 2.8

    def __init__(self):
        super().__init__()
        self.cooldown_duration = 0.5


class ChargedForcePull(ForcePull):
    """Charged version: 2.8x strength, 50deg half-cone, 1.3x range, 0.5s cooldown."""

    RANGE = ForcePull.RANGE * 1.3
    CONE_HALF_ANGLE = math.radians(50)
    STRENGTH = ForcePull.STRENGTH * 2.8

    def __init__(self):
        super().__init__()
        self.cooldown_duration = 0.5


class AbilityManager:
    """Holds abilities per side, routes activation/update/draw."""

    def __init__(self):
        # {side: {key_name: Ability}}
        self._abilities = {'left': {}, 'right': {}}

    def register(self, side, key_name, ability):
        self._abilities[side][key_name] = ability

    def try_activate(self, side, key_name, **kwargs):
        """Try to activate an ability. Returns True if activated."""
        ability = self._abilities[side].get(key_name)
        if ability is None:
            return False
        return ability.try_activate(**kwargs)

    def get(self, side, key_name):
        return self._abilities[side].get(key_name)

    def update(self, dt, targets_func=None):
        """Update all abilities. targets_func(side) returns [(obj, mult), ...] for force application."""
        for side in ('left', 'right'):
            for key_name, ability in self._abilities[side].items():
                ability.tick(dt)
                # Apply force effects on the frame they activate
                if ability._active and not getattr(ability, '_applied', True):
                    if targets_func is not None:
                        grabbed = None  # caller can set via kwargs
                        ability.apply_to_objects(targets_func(side), grabbed)

    def draw_cooldown_bars(self, surface, left_paddle, right_paddle):
        """Draw cooldown bars below each paddle's HP pips."""
        for side, paddle in [('left', left_paddle), ('right', right_paddle)]:
            abilities = self._abilities[side]
            if not abilities:
                continue
            bar_x = int(paddle.pos[0])
            bar_y = int(paddle.pos[1]) - 22  # below HP pips which are at -12
            i = 0
            for key_name, ability in abilities.items():
                x = bar_x + i * 12
                w = 10
                h = 3
                # Background
                pygame.draw.rect(surface, (40, 40, 40), (x, bar_y, w, h))
                # Fill based on readiness
                frac = 1.0 - ability.cooldown_fraction
                if frac >= 1.0:
                    color = (0, 200, 255)
                else:
                    color = (80, 80, 80)
                fill_w = max(0, int(w * frac))
                if fill_w > 0:
                    pygame.draw.rect(surface, color, (x, bar_y, fill_w, h))
                i += 1

    def reset(self):
        """Reset all cooldowns."""
        for side in ('left', 'right'):
            for ability in self._abilities[side].values():
                ability._cooldown_timer = 0.0
                ability._active = False
                ability._active_timer = 0.0
