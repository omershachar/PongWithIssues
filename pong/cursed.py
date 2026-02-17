"""
cursed.py -- CursedEventManager: random chaos events for Cursed Mode.
Triggers timed disruptions like gravity flip, paddle swap, invisible ball, etc.
"""

import math
import random
import time
import pygame
import numpy as np
from pong.constants import *


# ---------------------------------------------------------------------------
# Event definitions
# ---------------------------------------------------------------------------

CURSED_EVENTS = [
    {
        'name': 'GRAVITY FLIP',
        'duration': 300,   # 5s at 60 FPS
        'color': (180, 80, 255),
    },
    {
        'name': 'PADDLE SWAP',
        'duration': 300,
        'color': (255, 100, 100),
    },
    {
        'name': 'SCREEN FLIP',
        'duration': 300,
        'color': (255, 50, 200),
    },
    {
        'name': 'INVISIBLE BALL',
        'duration': 120,   # 2s
        'color': (100, 100, 100),
    },
    {
        'name': 'TINY PADDLES',
        'duration': 180,   # 3s
        'color': (255, 200, 0),
    },
    {
        'name': 'REVERSE CONTROLS',
        'duration': 300,
        'color': (0, 200, 255),
    },
    {
        'name': 'SPEED SURGE',
        'duration': 180,   # 3s
        'color': (255, 60, 0),
    },
    {
        'name': 'BALL SPLIT',
        'duration': 0,     # instant (multi-ball handles itself)
        'color': (255, 180, 0),
    },
    {
        'name': 'COMIC SANS',
        'duration': 600,   # 10s
        'color': (255, 150, 200),
    },
    {
        'name': 'LAG SIMULATOR',
        'duration': 60,    # 1s
        'color': (200, 200, 200),
    },
]


# ---------------------------------------------------------------------------
# Announcement (floating text that fades)
# ---------------------------------------------------------------------------

class _Announcement:
    """A big text announcement that scales up and fades out."""

    __slots__ = ('text', 'color', 'start_time', 'duration')

    def __init__(self, text, color):
        self.text = text
        self.color = color
        self.start_time = time.monotonic()
        self.duration = 2.0  # seconds

    def alive(self):
        return (time.monotonic() - self.start_time) < self.duration

    def draw(self, surface):
        elapsed = time.monotonic() - self.start_time
        progress = elapsed / self.duration

        # Scale: grow from 0.5 to 1.2 in first 20%, then hold at 1.0
        if progress < 0.2:
            scale = 0.5 + (progress / 0.2) * 0.7
        else:
            scale = 1.2 - 0.2 * min((progress - 0.2) / 0.8, 1.0)

        # Alpha: full for first 60%, then fade
        if progress < 0.6:
            alpha = 255
        else:
            alpha = int(255 * (1.0 - (progress - 0.6) / 0.4))
            alpha = max(0, alpha)

        font = FONT_BIG_DIGITAL
        rendered = font.render(self.text, True, self.color)
        w = max(1, int(rendered.get_width() * scale))
        h = max(1, int(rendered.get_height() * scale))
        scaled = pygame.transform.smoothscale(rendered, (w, h))

        # Apply alpha
        if alpha < 255:
            scaled.set_alpha(alpha)

        rect = scaled.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        surface.blit(scaled, rect)


# ---------------------------------------------------------------------------
# Active cursed event tracker
# ---------------------------------------------------------------------------

class _ActiveCursedEvent:
    """Tracks a currently active timed cursed event."""

    __slots__ = ('name', 'remaining', 'data')

    def __init__(self, name, duration, data=None):
        self.name = name
        self.remaining = duration
        self.data = data or {}

    def tick(self):
        """Returns True if still active."""
        self.remaining -= 1
        return self.remaining > 0


# ---------------------------------------------------------------------------
# CursedEventManager
# ---------------------------------------------------------------------------

class CursedEventManager:
    """
    Triggers random chaos events on a timer, manages active events,
    and draws announcement text.
    """

    # Timer range (frames) — shrinks as match progresses
    INITIAL_MIN = 600   # 10s
    INITIAL_MAX = 900   # 15s
    FINAL_MIN = 360     # 6s
    FINAL_MAX = 540     # 9s

    def __init__(self):
        self.timer = random.randint(self.INITIAL_MIN, self.INITIAL_MAX)
        self.active_events = []
        self.announcements = []
        self.total_events_triggered = 0

        # Gravity bias direction (set when gravity flip triggers)
        self.gravity_bias = 0.0

        # Stored paddle state for swap
        self._swap_stored = None

        # Stored paddle heights for tiny paddles
        self._tiny_stored = None

        # Speed surge: stored ball speed
        self._speed_stored = None

        # Comic Sans font (lazy-loaded)
        self._comic_font = None

        # Lag simulator: skip frames counter
        self.lag_skip_frames = 0

    def _get_timer_range(self):
        """Timer range shrinks as more events are triggered (chaos escalation)."""
        t = min(self.total_events_triggered / 10.0, 1.0)
        min_val = int(self.INITIAL_MIN + (self.FINAL_MIN - self.INITIAL_MIN) * t)
        max_val = int(self.INITIAL_MAX + (self.FINAL_MAX - self.INITIAL_MAX) * t)
        return min_val, max_val

    def has_event(self, name):
        """Check if a named event is currently active."""
        return any(e.name == name for e in self.active_events)

    def update(self, ball, left_paddle, right_paddle, pu_mgr=None):
        """
        Per-frame update. Decrements timer, triggers new events,
        ticks active events, applies continuous effects.

        Args:
            ball: main Ball object
            left_paddle, right_paddle: Paddle objects
            pu_mgr: PowerUpManager (for ball split multi-ball)
        """
        # Lag simulator: skip rendering/updating some frames
        if self.lag_skip_frames > 0:
            self.lag_skip_frames -= 1

        # Tick timer
        self.timer -= 1
        if self.timer <= 0:
            self._trigger_random(ball, left_paddle, right_paddle, pu_mgr)
            lo, hi = self._get_timer_range()
            self.timer = random.randint(lo, hi)

        # Tick active events, remove expired
        expired = []
        for event in self.active_events:
            if not event.tick():
                expired.append(event)
        for event in expired:
            self._on_expire(event, ball, left_paddle, right_paddle)
            self.active_events.remove(event)

        # Apply continuous gravity bias
        if self.has_event('GRAVITY FLIP'):
            ball.vel[1] += self.gravity_bias

        # Remove dead announcements
        self.announcements = [a for a in self.announcements if a.alive()]

    def _trigger_random(self, ball, left_paddle, right_paddle, pu_mgr):
        """Pick a random event and trigger it."""
        # Don't stack same event type
        active_names = {e.name for e in self.active_events}
        available = [ev for ev in CURSED_EVENTS if ev['name'] not in active_names]
        if not available:
            return

        event_def = random.choice(available)
        name = event_def['name']
        duration = event_def['duration']
        color = event_def['color']

        self.total_events_triggered += 1

        # Announce
        self.announcements.append(_Announcement(name + "!", color))

        # Play cursed sound
        try:
            from pong import audio
            audio.play('cursed_event')
        except Exception:
            pass

        # Apply the event
        if name == 'GRAVITY FLIP':
            self.gravity_bias = random.choice([-0.15, 0.15])
            self.active_events.append(_ActiveCursedEvent(name, duration))

        elif name == 'PADDLE SWAP':
            # Swap paddle Y positions
            self._swap_stored = (
                left_paddle.pos[1],
                right_paddle.pos[1]
            )
            left_paddle.pos[1], right_paddle.pos[1] = right_paddle.pos[1], left_paddle.pos[1]
            self.active_events.append(_ActiveCursedEvent(name, duration))

        elif name == 'SCREEN FLIP':
            self.active_events.append(_ActiveCursedEvent(name, duration))

        elif name == 'INVISIBLE BALL':
            self.active_events.append(_ActiveCursedEvent(name, duration))

        elif name == 'TINY PADDLES':
            self._tiny_stored = (left_paddle.height, right_paddle.height)
            # Shrink paddles, re-center
            for paddle in [left_paddle, right_paddle]:
                old_center = paddle.pos[1] + paddle.height / 2
                paddle.height = 20
                paddle.pos[1] = max(0, min(HEIGHT - paddle.height, old_center - paddle.height / 2))
            self.active_events.append(_ActiveCursedEvent(name, duration))

        elif name == 'REVERSE CONTROLS':
            self.active_events.append(_ActiveCursedEvent(name, duration))

        elif name == 'SPEED SURGE':
            self._speed_stored = ball.vel.copy()
            ball.vel *= 2.0
            self.active_events.append(_ActiveCursedEvent(name, duration))

        elif name == 'BALL SPLIT':
            # Use PowerUpManager's multi-ball if available
            if pu_mgr is not None:
                pu_mgr._pending_multiball_side = 'left'
            # No active event needed (instant)

        elif name == 'COMIC SANS':
            self.active_events.append(_ActiveCursedEvent(name, duration))

        elif name == 'LAG SIMULATOR':
            self.lag_skip_frames = 20  # Skip ~20 frames over 1s
            self.active_events.append(_ActiveCursedEvent(name, duration))

    def _on_expire(self, event, ball, left_paddle, right_paddle):
        """Undo effects when an event expires."""
        name = event.name

        if name == 'GRAVITY FLIP':
            self.gravity_bias = 0.0

        elif name == 'PADDLE SWAP':
            if self._swap_stored:
                left_paddle.pos[1], right_paddle.pos[1] = self._swap_stored
                self._swap_stored = None

        elif name == 'TINY PADDLES':
            if self._tiny_stored:
                orig_l, orig_r = self._tiny_stored
                for paddle, orig_h in [(left_paddle, orig_l), (right_paddle, orig_r)]:
                    old_center = paddle.pos[1] + paddle.height / 2
                    paddle.height = orig_h
                    paddle.pos[1] = max(0, min(HEIGHT - paddle.height, old_center - paddle.height / 2))
                self._tiny_stored = None

        elif name == 'SPEED SURGE':
            if self._speed_stored is not None:
                # Restore direction but use original magnitude
                if np.linalg.norm(ball.vel) > 0:
                    direction = ball.vel / np.linalg.norm(ball.vel)
                    speed = np.linalg.norm(self._speed_stored)
                    ball.vel[:] = direction * speed
                self._speed_stored = None

    def get_font(self, original_font):
        """Return Comic Sans font if that event is active, else the original."""
        if self.has_event('COMIC SANS'):
            if self._comic_font is None:
                try:
                    self._comic_font = pygame.font.SysFont('comicsansms', 45)
                except Exception:
                    # SysFont not available on WASM/Pygbag — use bundled font
                    self._comic_font = pygame.font.Font(
                        "pong/FONTS/LiberationMono-Bold.ttf", 45)
            return self._comic_font
        return original_font

    def should_skip_frame(self):
        """Returns True if lag simulator says to skip this frame's update."""
        if self.has_event('LAG SIMULATOR') and self.lag_skip_frames > 0:
            # Skip every other frame for stutter effect
            return (self.lag_skip_frames % 3) != 0
        return False

    def draw_announcements(self, surface):
        """Draw all active announcement texts."""
        for ann in self.announcements:
            ann.draw(surface)

    def draw_active_bar(self, surface):
        """Draw small indicator icons for active cursed events at the top."""
        if not self.active_events:
            return
        x = WIDTH // 2 - (len(self.active_events) * 50) // 2
        y = 35
        for event in self.active_events:
            # Find color from event definitions
            color = WHITE
            for ev_def in CURSED_EVENTS:
                if ev_def['name'] == event.name:
                    color = ev_def['color']
                    break
            # Timer bar background
            bar_w = 40
            bar_h = 4
            frac = max(0, event.remaining / max(1, event.remaining + 1))
            # Find original duration
            for ev_def in CURSED_EVENTS:
                if ev_def['name'] == event.name:
                    frac = event.remaining / max(1, ev_def['duration'])
                    break
            frac = min(1.0, frac)

            # Short label
            short = event.name[:3]
            label = FONT_TINY_DIGITAL.render(short, True, color)
            surface.blit(label, (x, y))
            # Timer bar
            pygame.draw.rect(surface, DARK_GREY, (x, y + 16, bar_w, bar_h))
            pygame.draw.rect(surface, color, (x, y + 16, int(bar_w * frac), bar_h))
            x += 50

    def reset(self):
        """Reset all events (called on score)."""
        self.active_events.clear()
        self.announcements.clear()
        self.gravity_bias = 0.0
        self._swap_stored = None
        self._speed_stored = None
        self.lag_skip_frames = 0
        lo, hi = self._get_timer_range()
        self.timer = random.randint(lo, hi)

    def reset_paddles(self, left_paddle, right_paddle):
        """Restore paddle state on score/reset. Call before general reset."""
        if self._tiny_stored:
            orig_l, orig_r = self._tiny_stored
            left_paddle.height = orig_l
            right_paddle.height = orig_r
            self._tiny_stored = None
