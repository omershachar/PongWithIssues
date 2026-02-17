"""
paddle.py -- Unified Paddle class for both Classic and Physics modes
"""

import pygame
import numpy as np
from pong.physics_object import PhysicsObject
from pong.constants import *


class Paddle(PhysicsObject):
    """
    A unified paddle class supporting both classic and physics-based Pong modes.

    In 'physics' mode: Uses acceleration-based movement with friction and momentum.
    In 'classic' mode: Uses direct velocity-based movement.
    """

    def __init__(self, x, y, width, height, color=LIGHT_PURPLE, mode='physics', fixed_vel=PADDLE_DEFAULT_VEL, side=None):
        """
        Initializes the paddle with position, size, and color.

        Args:
            x (float): Initial X position.
            y (float): Initial Y position.
            width (int): Paddle width.
            height (int): Paddle height.
            color (tuple): RGB color value.
            mode (str): 'classic' or 'physics'
            fixed_vel (float): Fixed velocity for classic mode.
            side (str|None): 'left' or 'right'. Auto-detected from x if None.
        """
        super().__init__(pos=(x, y), mass=1, vel=(0, 0))
        self.original_pos = np.array([x, y], dtype=float)
        self.width = width
        self.height = height
        self.color = color
        self.mode = mode
        self.fixed_vel = fixed_vel
        # Side detection: explicit or auto from spawn position
        if side is not None:
            self.side = side
        else:
            self.side = 'left' if x < WIDTH / 2 else 'right'

    # Properties for backwards compatibility with classic mode code
    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, val):
        self.pos[0] = val

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, val):
        self.pos[1] = val

    @property
    def original_x(self):
        return self.original_pos[0]

    @property
    def original_y(self):
        return self.original_pos[1]

    def draw(self, win):
        """Draws the paddle on the game window."""
        pygame.draw.rect(win, self.color, (int(self.pos[0]), int(self.pos[1]), self.width, self.height))

    def accelerate(self, up=True):
        """
        Applies acceleration (physics mode) or direct movement (classic mode).

        Args:
            up (bool): Direction of movement. True for up, False for down.
        """
        if self.mode == 'classic':
            self.move(up)
        else:
            if up:
                self.acc[:] -= PADDLE_DEFAULT_ACC[:]
            else:
                self.acc[:] += PADDLE_DEFAULT_ACC[:]

    def move(self, up=True):
        """
        Direct movement for classic mode.

        Args:
            up (bool): Direction of movement. True for up, False for down.
        """
        if up:
            self.pos[1] -= self.fixed_vel
        else:
            self.pos[1] += self.fixed_vel
        self._clamp_to_screen()

    def accelerate_x(self, forward=True, multiplier=1.0):
        """
        Applies X-axis acceleration (physics mode only, for Cursed mode).
        Forward means toward the center of the board.

        Args:
            forward (bool): True to move toward center, False to move back.
            multiplier (float): Acceleration multiplier for charge-up.
        """
        if self.mode != 'physics':
            return
        accel = PADDLE_DEFAULT_ACC[1] * 0.8 * multiplier
        # Left paddle: forward = positive X. Right paddle: forward = negative X.
        is_left = self.side == 'left'
        if is_left:
            self.acc[0] += accel if forward else -accel
        else:
            self.acc[0] += -accel if forward else accel

    def update(self, cursed_mode=False, max_vel_override=None, screen_w=None, screen_h=None):
        """
        Updates paddle position. Physics mode uses acceleration, classic uses direct movement.

        Args:
            cursed_mode (bool): If True, use higher velocity limits and looser clamping.
            max_vel_override (float|None): Override max velocity for cursed paddles.
            screen_w (int|None): Override screen width for larger arenas.
            screen_h (int|None): Override screen height for larger arenas.
        """
        if self.mode == 'physics':
            self.vel += self.acc
            self.acc[:] = 0

            if cursed_mode:
                # Use override if provided, else legacy 1.8x
                base_max = max_vel_override if max_vel_override is not None else PADDLE_MAX_VEL * 1.8
                max_y = base_max
                max_x = base_max * 0.83
                friction_y = 0.88
                friction_x = 0.85
            else:
                max_y = PADDLE_MAX_VEL
                max_x = PADDLE_MAX_VEL * 0.6
                friction_y = 0.85
                friction_x = 0.80

            # Clamp velocities
            self.vel[1] = np.clip(self.vel[1], -max_y, max_y)
            self.vel[0] = np.clip(self.vel[0], -max_x, max_x)

            # Update position
            self.pos += self.vel

            # Apply friction
            self.vel[1] *= friction_y
            self.vel[0] *= friction_x

        # Classic mode doesn't need update() - movement is direct
        self._clamp_to_screen(cursed_mode=cursed_mode, screen_w=screen_w, screen_h=screen_h)

    def _clamp_to_screen(self, cursed_mode=False, screen_w=None, screen_h=None):
        """Keeps the paddle inside the screen bounds (Y and X)."""
        W = screen_w or WIDTH
        H = screen_h or HEIGHT

        # Y bounds
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.vel[1] = 0
        elif self.pos[1] + self.height > H:
            self.pos[1] = H - self.height
            self.vel[1] = 0

        if cursed_mode:
            # CURSED: Full board access! Only clamp to screen edges.
            if self.pos[0] < GAME_MARGIN_X:
                self.pos[0] = GAME_MARGIN_X
                self.vel[0] = 0
            elif self.pos[0] + self.width > W - GAME_MARGIN_X:
                self.pos[0] = W - GAME_MARGIN_X - self.width
                self.vel[0] = 0
        else:
            # Normal: paddle can't cross center
            is_left = self.side == 'left'
            if is_left:
                x_min = GAME_MARGIN_X
                x_max = W // 2 - self.width - 10
            else:
                x_min = W // 2 + 10
                x_max = W - GAME_MARGIN_X - self.width
            if self.pos[0] < x_min:
                self.pos[0] = x_min
                self.vel[0] = 0
            elif self.pos[0] > x_max:
                self.pos[0] = x_max
                self.vel[0] = 0

    def reset(self):
        """Resets the paddle to its original position and clears movement."""
        self.pos = self.original_pos.copy()
        self.vel[:] = 0
        self.acc[:] = 0


# ----------------------- Legacy Alias for Backwards Compatibility -----------------------
class PaddleClassic(Paddle):
    """
    @deprecated: Use Paddle with mode='classic' instead
    """
    def __init__(self, x, y, width, height, color, vel):
        super().__init__(x, y, width, height, color, mode='classic', fixed_vel=vel)
