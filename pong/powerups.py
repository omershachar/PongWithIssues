"""
powerups.py -- Power-up system for Classic and Pongception modes.
Spawn collectible boxes, apply timed effects, handle multi-ball scoring.
"""

import math
import random
import pygame
import numpy as np
from enum import Enum
from pong.constants import *
from pong.ball import Ball, BallClassic


class PowerUpType(Enum):
    RESIZE = "resize"
    FREEZE = "freeze"
    MULTI_BALL = "multi_ball"
    REVERSE = "reverse"
    DRUNK = "drunk"
    BLIND = "blind"
    GROW_BALL = "grow_ball"


# Cursed power-up colors
POWERUP_COLOR_REVERSE = (180, 80, 255)    # purple
POWERUP_COLOR_DRUNK = (255, 255, 0)       # yellow
POWERUP_COLOR_BLIND = (40, 40, 40)        # near-black
POWERUP_COLOR_GROW_BALL = (255, 140, 0)   # orange

# Map type → color, letter
_TYPE_INFO = {
    PowerUpType.RESIZE:     (POWERUP_COLOR_RESIZE, "R"),
    PowerUpType.FREEZE:     (POWERUP_COLOR_FREEZE, "F"),
    PowerUpType.MULTI_BALL: (POWERUP_COLOR_MULTI,  "M"),
    PowerUpType.REVERSE:    (POWERUP_COLOR_REVERSE, "R"),
    PowerUpType.DRUNK:      (POWERUP_COLOR_DRUNK,   "D"),
    PowerUpType.BLIND:      (POWERUP_COLOR_BLIND,   "B"),
    PowerUpType.GROW_BALL:  (POWERUP_COLOR_GROW_BALL, "G"),
}

# Duration constants for cursed power-ups (in frames at 60 FPS)
REVERSE_DURATION = 300     # 5s
DRUNK_DURATION = 300       # 5s
BLIND_DURATION = 180       # 3s
GROW_BALL_DURATION = 480   # 8s

# Standard (non-cursed) power-up types for random selection in classic modes
_STANDARD_TYPES = [PowerUpType.RESIZE, PowerUpType.FREEZE, PowerUpType.MULTI_BALL]
# All types including cursed for cursed mode
_ALL_TYPES = list(PowerUpType)

_ICON_FONT = None

def _get_icon_font():
    global _ICON_FONT
    if _ICON_FONT is None:
        _ICON_FONT = pygame.font.Font("pong/FONTS/LiberationMono-Bold.ttf", 16)
    return _ICON_FONT


class PowerUp:
    """A floating power-up box on the field."""

    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type
        self.age = 0
        self.size = POWERUP_BOX_SIZE
        self.color, self.letter = _TYPE_INFO[power_type]

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2),
            int(self.y - self.size / 2),
            self.size, self.size
        )

    def collides_with_ball(self, ball):
        """Circle-rect collision between ball and this box."""
        r = self.rect
        # Find closest point on rect to ball center
        cx = max(r.left, min(ball.pos[0], r.right))
        cy = max(r.top, min(ball.pos[1], r.bottom))
        dx = ball.pos[0] - cx
        dy = ball.pos[1] - cy
        return (dx * dx + dy * dy) <= (ball.radius * ball.radius)

    def collides_with_paddle(self, paddle):
        """Rect-rect collision between paddle and this box."""
        pr = pygame.Rect(int(paddle.pos[0]), int(paddle.pos[1]),
                         int(paddle.width), int(paddle.height))
        return self.rect.colliderect(pr)

    def update(self):
        """Advance age. Returns False if expired."""
        self.age += 1
        return self.age < POWERUP_LIFETIME

    def draw(self, win):
        """Draw the power-up box with bob and blink."""
        # Blink when near expiry
        if self.age >= POWERUP_BLINK_AT:
            if (self.age // 10) % 2 == 0:
                return  # invisible during blink-off frames

        # Gentle sine bob
        bob = math.sin(self.age * 0.06) * 3
        draw_y = self.y + bob

        r = pygame.Rect(
            int(self.x - self.size / 2),
            int(draw_y - self.size / 2),
            self.size, self.size
        )

        # Colored rounded rect with white border
        pygame.draw.rect(win, self.color, r, border_radius=5)
        pygame.draw.rect(win, WHITE, r, width=2, border_radius=5)

        # Letter icon
        font = _get_icon_font()
        txt = font.render(self.letter, True, BLACK)
        win.blit(txt, (r.centerx - txt.get_width() // 2,
                       r.centery - txt.get_height() // 2))


class ActiveEffect:
    """Tracks a timed power-up effect on a paddle."""

    def __init__(self, power_type, paddle, duration, original_value=None):
        self.power_type = power_type
        self.paddle = paddle
        self.duration = duration
        self.remaining = duration
        self.original_value = original_value

    def tick(self):
        """Returns True if effect is still active."""
        self.remaining -= 1
        return self.remaining > 0


class PowerUpManager:
    """Orchestrates power-up spawning, collection, effects, and multi-ball."""

    def __init__(self, left_paddle, right_paddle, cursed=False):
        self.left_paddle = left_paddle
        self.right_paddle = right_paddle
        self.cursed = cursed  # If True, include cursed power-up types
        self.field_powerups = []
        self.active_effects = []
        self.extra_balls = []
        self.spawn_timer = random.randint(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)
        self.last_hit_side = 'left'
        self.main_ball_parked = False
        self.pending_score_side = None
        self._frozen_paddles = set()
        self._stored_originals = {}  # id(paddle) → original height
        self._reversed_paddles = set()
        self._drunk_paddles = {}  # id(paddle) → phase offset
        self._blind_side = None  # 'left' or 'right' or None
        self._ball_grown = False
        self._original_ball_radius = None

    def set_last_hit(self, side):
        self.last_hit_side = side

    def is_frozen(self, paddle):
        return id(paddle) in self._frozen_paddles

    def update(self, ball):
        """Per-frame update: spawn, age, collect, tick effects."""
        # Spawn timer
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self._spawn()
            self.spawn_timer = random.randint(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)

        # Age field power-ups, remove expired
        self.field_powerups = [p for p in self.field_powerups if p.update()]

        # Check collections
        self._check_ball_collection(ball)
        self._check_paddle_collection()

        # Tick active effects, remove expired
        expired = []
        for effect in self.active_effects:
            if not effect.tick():
                expired.append(effect)
        for effect in expired:
            self._remove_effect(effect)
            self.active_effects.remove(effect)

        # Clean up extra balls that have exited
        self.extra_balls = [
            eb for eb in self.extra_balls
            if -eb.radius <= eb.pos[0] <= WIDTH + eb.radius
        ]

    def _spawn(self):
        """Spawn a random power-up in the middle zone of the field."""
        margin_x = WIDTH * 0.25
        margin_y = 60
        x = random.uniform(margin_x, WIDTH - margin_x)
        y = random.uniform(margin_y, HEIGHT - margin_y)
        pool = _ALL_TYPES if self.cursed else _STANDARD_TYPES
        ptype = random.choice(pool)
        self.field_powerups.append(PowerUp(x, y, ptype))

    def _check_ball_collection(self, ball):
        """Check if ball collects any field power-up."""
        collected = []
        for pu in self.field_powerups:
            if pu.collides_with_ball(ball):
                collected.append(pu)
        for pu in collected:
            self.field_powerups.remove(pu)
            self._apply(pu.power_type, self.last_hit_side)
        # Also check extra balls
        for eb in self.extra_balls:
            collected = []
            for pu in self.field_powerups:
                if pu.collides_with_ball(eb):
                    collected.append(pu)
            for pu in collected:
                self.field_powerups.remove(pu)
                self._apply(pu.power_type, self.last_hit_side)

    def _check_paddle_collection(self):
        """Check if paddles overlap any field power-up."""
        collected = []
        for pu in self.field_powerups:
            if pu.collides_with_paddle(self.left_paddle):
                collected.append((pu, 'left'))
            elif pu.collides_with_paddle(self.right_paddle):
                collected.append((pu, 'right'))
        for pu, side in collected:
            if pu in self.field_powerups:
                self.field_powerups.remove(pu)
                self._apply(pu.power_type, side)

    def _apply(self, power_type, collector_side, ball=None):
        """Apply a power-up effect for the collecting side."""
        collector = self.left_paddle if collector_side == 'left' else self.right_paddle
        opponent = self.right_paddle if collector_side == 'left' else self.left_paddle
        opponent_side = 'right' if collector_side == 'left' else 'left'

        if power_type == PowerUpType.RESIZE:
            self._apply_resize(collector, opponent)
        elif power_type == PowerUpType.FREEZE:
            self._apply_freeze(opponent)
        elif power_type == PowerUpType.MULTI_BALL:
            self._apply_multiball(collector_side)
        elif power_type == PowerUpType.REVERSE:
            self._apply_reverse(opponent)
        elif power_type == PowerUpType.DRUNK:
            self._apply_drunk(opponent)
        elif power_type == PowerUpType.BLIND:
            self._apply_blind(opponent_side)
        elif power_type == PowerUpType.GROW_BALL:
            self._apply_grow_ball()

    def _apply_resize(self, collector, opponent):
        """Grow collector paddle, shrink opponent."""
        # Store originals if not already stored
        if id(collector) not in self._stored_originals:
            self._stored_originals[id(collector)] = collector.height
        if id(opponent) not in self._stored_originals:
            self._stored_originals[id(opponent)] = opponent.height

        orig_c = self._stored_originals[id(collector)]
        orig_o = self._stored_originals[id(opponent)]

        # Apply resize from original values
        new_c = orig_c * RESIZE_GROW
        new_o = orig_o * RESIZE_SHRINK

        # Re-center paddles
        old_center_c = collector.pos[1] + collector.height / 2
        collector.height = new_c
        collector.pos[1] = max(0, min(HEIGHT - collector.height, old_center_c - collector.height / 2))

        old_center_o = opponent.pos[1] + opponent.height / 2
        opponent.height = new_o
        opponent.pos[1] = max(0, min(HEIGHT - opponent.height, old_center_o - opponent.height / 2))

        # Remove any existing resize effects before adding new one
        existing = [e for e in self.active_effects if e.power_type == PowerUpType.RESIZE]
        for e in existing:
            self.active_effects.remove(e)

        self.active_effects.append(
            ActiveEffect(PowerUpType.RESIZE, collector, RESIZE_DURATION,
                         original_value=(collector, opponent))
        )

    def _apply_freeze(self, opponent):
        """Freeze opponent paddle."""
        self._frozen_paddles.add(id(opponent))
        # Remove existing freeze on this paddle
        existing = [e for e in self.active_effects
                    if e.power_type == PowerUpType.FREEZE and e.paddle is opponent]
        for e in existing:
            self.active_effects.remove(e)
        self.active_effects.append(
            ActiveEffect(PowerUpType.FREEZE, opponent, FREEZE_DURATION)
        )

    def _apply_multiball(self, collector_side):
        """Spawn 2 extra balls from main ball position."""
        # We'll create extra balls in create_extra_balls, called from game loop
        # Store the side so game loop can create balls with correct attributes
        self._pending_multiball_side = collector_side

    def create_extra_balls(self, main_ball, mode='classic'):
        """Called from game loop to create extra balls (needs access to ball)."""
        if not hasattr(self, '_pending_multiball_side'):
            return
        del self._pending_multiball_side

        bx, by = main_ball.pos[0], main_ball.pos[1]
        speed = np.linalg.norm(main_ball.vel)
        if speed < 1:
            speed = 6
        # Base angle from main ball velocity
        base_angle = math.atan2(main_ball.vel[1], main_ball.vel[0])
        spread = math.radians(23)

        for offset in [-spread, spread]:
            angle = base_angle + offset
            vx = speed * math.cos(angle)
            vy = speed * math.sin(angle)
            if mode == 'classic':
                eb = BallClassic(bx, by, main_ball.radius, POWERUP_COLOR_MULTI, vx, vy)
            else:
                eb = Ball(bx, by, main_ball.radius, POWERUP_COLOR_MULTI,
                          mass=1, vel=(vx, vy), mode='physics')
            self.extra_balls.append(eb)

    def _apply_reverse(self, opponent):
        """Reverse opponent's controls for a duration."""
        self._reversed_paddles.add(id(opponent))
        existing = [e for e in self.active_effects
                    if e.power_type == PowerUpType.REVERSE and e.paddle is opponent]
        for e in existing:
            self.active_effects.remove(e)
        self.active_effects.append(
            ActiveEffect(PowerUpType.REVERSE, opponent, REVERSE_DURATION)
        )

    def _apply_drunk(self, opponent):
        """Make opponent paddle wobble sinusoidally."""
        self._drunk_paddles[id(opponent)] = 0
        existing = [e for e in self.active_effects
                    if e.power_type == PowerUpType.DRUNK and e.paddle is opponent]
        for e in existing:
            self.active_effects.remove(e)
        self.active_effects.append(
            ActiveEffect(PowerUpType.DRUNK, opponent, DRUNK_DURATION)
        )

    def _apply_blind(self, opponent_side):
        """Darken opponent's half of the screen."""
        self._blind_side = opponent_side
        existing = [e for e in self.active_effects
                    if e.power_type == PowerUpType.BLIND]
        for e in existing:
            self.active_effects.remove(e)
        # Use left_paddle as placeholder (side tracked via _blind_side)
        paddle = self.left_paddle if opponent_side == 'left' else self.right_paddle
        self.active_effects.append(
            ActiveEffect(PowerUpType.BLIND, paddle, BLIND_DURATION)
        )

    def _apply_grow_ball(self):
        """Double the ball's radius for a duration."""
        self._ball_grown = True
        existing = [e for e in self.active_effects
                    if e.power_type == PowerUpType.GROW_BALL]
        for e in existing:
            self.active_effects.remove(e)
        self.active_effects.append(
            ActiveEffect(PowerUpType.GROW_BALL, self.left_paddle, GROW_BALL_DURATION)
        )

    def is_reversed(self, paddle):
        """Check if a paddle has reversed controls."""
        return id(paddle) in self._reversed_paddles

    def is_drunk(self, paddle):
        """Check if a paddle is drunk (wobbling)."""
        return id(paddle) in self._drunk_paddles

    def get_blind_side(self):
        """Return the side that is blinded, or None."""
        return self._blind_side

    def is_ball_grown(self):
        """Return True if ball is currently enlarged."""
        return self._ball_grown

    def apply_drunk_wobble(self, paddle):
        """Apply sinusoidal wobble to a drunk paddle. Call after movement."""
        pid = id(paddle)
        if pid in self._drunk_paddles:
            self._drunk_paddles[pid] += 1
            phase = self._drunk_paddles[pid]
            wobble = math.sin(phase * 0.15) * 4.0
            paddle.pos[1] += wobble

    def apply_ball_grow(self, ball):
        """Apply ball growth effect if active. Call once after ball creation."""
        if self._ball_grown:
            if self._original_ball_radius is None:
                self._original_ball_radius = ball.radius
            ball.radius = self._original_ball_radius * 2

    def _remove_effect(self, effect):
        """Restore state when an effect expires."""
        if effect.power_type == PowerUpType.RESIZE:
            collector, opponent = effect.original_value
            # Restore original heights
            for paddle in [collector, opponent]:
                pid = id(paddle)
                if pid in self._stored_originals:
                    orig_h = self._stored_originals.pop(pid)
                    old_center = paddle.pos[1] + paddle.height / 2
                    paddle.height = orig_h
                    paddle.pos[1] = max(0, min(HEIGHT - paddle.height,
                                               old_center - paddle.height / 2))
        elif effect.power_type == PowerUpType.FREEZE:
            self._frozen_paddles.discard(id(effect.paddle))
        elif effect.power_type == PowerUpType.REVERSE:
            self._reversed_paddles.discard(id(effect.paddle))
        elif effect.power_type == PowerUpType.DRUNK:
            self._drunk_paddles.pop(id(effect.paddle), None)
        elif effect.power_type == PowerUpType.BLIND:
            self._blind_side = None
        elif effect.power_type == PowerUpType.GROW_BALL:
            self._ball_grown = False
            self._original_ball_radius = None

    def park_main_ball(self, ball, exit_side):
        """Park the main ball at center when it exits during multi-ball."""
        self.main_ball_parked = True
        # exit_side = side the ball went past (e.g., 'left' means right scores)
        self.pending_score_side = 'right' if exit_side == 'left' else 'left'
        ball.pos[:] = [WIDTH // 2, HEIGHT // 2]
        ball.vel[:] = 0
        ball.spin = 0
        if hasattr(ball, 'trail'):
            ball.trail.clear()

    def check_multiball_done(self):
        """Check if multi-ball round is resolved.
        Returns 'left_scores', 'right_scores', or None."""
        if not self.main_ball_parked:
            return None
        if len(self.extra_balls) == 0:
            side = self.pending_score_side
            self.main_ball_parked = False
            self.pending_score_side = None
            if side == 'left':
                return 'left_scores'
            else:
                return 'right_scores'
        return None

    def reset(self):
        """Reset all effects and state. Called on score or game-over."""
        # Restore resize effects
        for effect in self.active_effects:
            self._remove_effect(effect)
        self.active_effects.clear()
        self.field_powerups.clear()
        self.extra_balls.clear()
        self._frozen_paddles.clear()
        self._stored_originals.clear()
        self._reversed_paddles.clear()
        self._drunk_paddles.clear()
        self._blind_side = None
        self._ball_grown = False
        self._original_ball_radius = None
        self.main_ball_parked = False
        self.pending_score_side = None
        if hasattr(self, '_pending_multiball_side'):
            del self._pending_multiball_side
        self.spawn_timer = random.randint(POWERUP_SPAWN_MIN, POWERUP_SPAWN_MAX)

    def draw(self, win):
        """Draw field power-ups and effect indicators."""
        # Field boxes
        for pu in self.field_powerups:
            pu.draw(win)

        # Effect indicators on paddles
        for effect in self.active_effects:
            if effect.power_type == PowerUpType.FREEZE:
                self._draw_freeze_overlay(win, effect.paddle)
            elif effect.power_type == PowerUpType.REVERSE:
                self._draw_effect_overlay(win, effect.paddle, POWERUP_COLOR_REVERSE, 50)
            elif effect.power_type == PowerUpType.DRUNK:
                self._draw_effect_overlay(win, effect.paddle, POWERUP_COLOR_DRUNK, 40)
            self._draw_timer_bar(win, effect)

        # Blind effect: darken half the screen
        if self._blind_side is not None:
            blind_surf = pygame.Surface((WIDTH // 2, HEIGHT), pygame.SRCALPHA)
            blind_surf.fill((0, 0, 0, 200))
            if self._blind_side == 'left':
                win.blit(blind_surf, (0, 0))
            else:
                win.blit(blind_surf, (WIDTH // 2, 0))

    def draw_extra_balls(self, win):
        """Render multi-ball extras."""
        for eb in self.extra_balls:
            eb.draw(win)

    def _draw_effect_overlay(self, win, paddle, color, alpha):
        """Semi-transparent color overlay on a paddle."""
        overlay = pygame.Surface((int(paddle.width) + 4, int(paddle.height) + 4), pygame.SRCALPHA)
        overlay.fill((*color, alpha))
        win.blit(overlay, (int(paddle.pos[0]) - 2, int(paddle.pos[1]) - 2))

    def _draw_freeze_overlay(self, win, paddle):
        """Semi-transparent blue overlay on frozen paddle."""
        overlay = pygame.Surface((int(paddle.width) + 4, int(paddle.height) + 4), pygame.SRCALPHA)
        overlay.fill((*POWERUP_COLOR_FREEZE, 80))
        win.blit(overlay, (int(paddle.pos[0]) - 2, int(paddle.pos[1]) - 2))

    def _draw_timer_bar(self, win, effect):
        """Draw a colored bar on inner edge of paddle showing remaining time."""
        paddle = effect.paddle
        frac = effect.remaining / effect.duration
        bar_height = int(paddle.height * frac)
        bar_width = 3

        color = _TYPE_INFO[effect.power_type][0]

        # Inner edge: left paddle → right edge, right paddle → left edge
        if paddle is self.left_paddle:
            x = int(paddle.pos[0] + paddle.width)
        else:
            x = int(paddle.pos[0]) - bar_width

        y = int(paddle.pos[1] + paddle.height - bar_height)
        pygame.draw.rect(win, color, (x, y, bar_width, bar_height))
