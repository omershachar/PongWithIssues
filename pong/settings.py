"""
settings.py -- Game settings and customization options.
Allows players to adjust ball/paddle size, speed, colors, and more.
"""
import pygame
import numpy as np
from pong.constants import *
from pong.ball import Ball
from pong.paddle import Paddle
from pong.ai import ai_move_paddle, DIFFICULTY_NAMES
from pong.helpers import handle_ball_collision


class GameSettings:
    """
    Stores customizable game settings.
    Can be modified in settings menu and passed to game modes.
    """

    def __init__(self):
        # Ball settings
        self.ball_radius = BALL_RADIUS
        self.ball_speed = BALL_DEFAULT_VEL[0]
        self.ball_color = WHITE

        # Paddle settings
        self.paddle_width = PADDLE_SIZE[0]
        self.paddle_height = PADDLE_SIZE[1]
        self.paddle_speed = PADDLE_DEFAULT_VEL
        self.left_paddle_color = LIGHT_PURPLE
        self.right_paddle_color = LIGHT_PURPLE

        # Board settings
        self.background_color = BLACK
        self.winning_score = WINNING_SCORE

        # AI settings
        self.ai_difficulty = 5  # 1 (Beginner) to 10 (Impossible)

        # Control settings
        self.left_up_key = pygame.K_w
        self.left_down_key = pygame.K_s
        self.right_up_key = pygame.K_UP
        self.right_down_key = pygame.K_DOWN

    def reset_defaults(self):
        """Reset all settings to default values."""
        self.__init__()

    def to_dict(self):
        """Export settings as dictionary."""
        return {
            'ball_radius': self.ball_radius,
            'ball_speed': self.ball_speed,
            'ball_color': self.ball_color,
            'paddle_width': self.paddle_width,
            'paddle_height': self.paddle_height,
            'paddle_speed': self.paddle_speed,
            'left_paddle_color': self.left_paddle_color,
            'right_paddle_color': self.right_paddle_color,
            'background_color': self.background_color,
            'winning_score': self.winning_score,
            'ai_difficulty': self.ai_difficulty,
        }


# Predefined color options
COLOR_OPTIONS = {
    'White': WHITE,
    'Purple': PURPLE,
    'Light Purple': LIGHT_PURPLE,
    'Red': RED,
    'Yellow': YELLOW,
    'Green': GREEN,
    'Orange': ORANGE,
    'Grey': GREY,
}

# Background color options (darker colors work best)
BACKGROUND_OPTIONS = {
    'Black': BLACK,
    'Dark Grey': DARK_GREY,
    'Dark Blue': (0, 0, 40),
    'Dark Green': (0, 30, 0),
    'Dark Red': (40, 0, 0),
    'Dark Purple': (30, 0, 40),
}

# Setting ranges
SETTING_RANGES = {
    'ball_radius': {'min': 3, 'max': 20, 'step': 1, 'label': 'Ball Size'},
    'ball_speed': {'min': 2, 'max': 15, 'step': 1, 'label': 'Ball Speed'},
    'paddle_height': {'min': 40, 'max': 200, 'step': 10, 'label': 'Paddle Height'},
    'paddle_speed': {'min': 3, 'max': 15, 'step': 1, 'label': 'Paddle Speed'},
    'winning_score': {'min': 1, 'max': 21, 'step': 1, 'label': 'Winning Score'},
    'ai_difficulty': {'min': 1, 'max': 10, 'step': 1, 'label': 'AI Difficulty'},
}


class PreviewGame:
    """
    A mini pong game with two AI paddles for the settings live preview.
    Runs in a confined area (area_width x area_height) on the left side.
    """

    PREVIEW_MARGIN_X = 10

    def __init__(self, area_width, area_height, settings):
        self.area_width = area_width
        self.area_height = area_height
        self.settings = settings
        self.clip_rect = pygame.Rect(0, 0, area_width, area_height)
        self._create_objects()

    def _create_objects(self):
        """Create ball and paddles scaled to the preview area."""
        s = self.settings
        cx = self.area_width // 2
        cy = self.area_height // 2

        self.ball = Ball(
            cx, cy, s.ball_radius, s.ball_color,
            mass=1, vel=(s.ball_speed, 0), mode='physics'
        )

        self.left_paddle = Paddle(
            self.PREVIEW_MARGIN_X,
            cy - s.paddle_height // 2,
            s.paddle_width, s.paddle_height,
            color=s.left_paddle_color, mode='physics',
            fixed_vel=s.paddle_speed
        )

        self.right_paddle = Paddle(
            self.area_width - self.PREVIEW_MARGIN_X - s.paddle_width,
            cy - s.paddle_height // 2,
            s.paddle_width, s.paddle_height,
            color=s.right_paddle_color, mode='physics',
            fixed_vel=s.paddle_speed
        )

    def apply_settings(self):
        """Update preview objects to match current settings in real-time."""
        s = self.settings

        # Ball radius
        self.ball.radius = s.ball_radius

        # Paddle dimensions and colors
        for paddle, color in [(self.left_paddle, s.left_paddle_color),
                              (self.right_paddle, s.right_paddle_color)]:
            old_center_y = paddle.pos[1] + paddle.height / 2
            paddle.width = s.paddle_width
            paddle.height = s.paddle_height
            paddle.color = color
            paddle.fixed_vel = s.paddle_speed
            # Re-center vertically after height change
            paddle.pos[1] = old_center_y - paddle.height / 2

        # Right paddle x-position depends on width
        self.right_paddle.pos[0] = self.area_width - self.PREVIEW_MARGIN_X - s.paddle_width

    def update(self):
        """Run one frame of AI pong."""
        # AI drives both paddles
        ai_move_paddle(self.right_paddle, self.ball, difficulty=6)
        self._ai_move_left(self.left_paddle, self.ball)

        # Physics update
        self.left_paddle.update()
        self.right_paddle.update()
        self.ball.update()

        # Collisions
        handle_ball_collision(self.ball, self.left_paddle, self.right_paddle)

        # Reset ball if it exits the preview area
        self._check_and_reset_ball()

    def _ai_move_left(self, paddle, ball):
        """AI for the left paddle — tracks ball when it moves left."""
        paddle_center = paddle.pos[1] + paddle.height / 2
        dead_zone = paddle.height * 0.1

        if ball.vel[0] < 0:
            diff = ball.pos[1] - paddle_center
            if abs(diff) > dead_zone:
                paddle.accelerate(up=(diff < 0))
        else:
            center = self.area_height / 2
            diff = center - paddle_center
            if abs(diff) > dead_zone * 2:
                paddle.accelerate(up=(diff < 0))

    def _check_and_reset_ball(self):
        """Reset ball to center when it exits left/right."""
        bx = self.ball.pos[0]
        if bx < -self.ball.radius or bx > self.area_width + self.ball.radius:
            cx = self.area_width // 2
            cy = self.area_height // 2
            # Launch toward the side the ball exited from (so it's interesting)
            direction = 1 if bx < 0 else -1
            self.ball.pos[:] = [cx, cy]
            self.ball.vel[:] = [self.settings.ball_speed * direction, 0]
            self.ball.spin = 0
            self.ball.trail.clear()

    def draw(self, surface):
        """Draw the preview game objects, clipped to the preview area."""
        old_clip = surface.get_clip()
        surface.set_clip(self.clip_rect)

        # Center dashed net
        cx = self.area_width // 2
        dash_len = 10
        gap = 8
        y = 0
        while y < self.area_height:
            pygame.draw.line(surface, DARK_GREY, (cx, y), (cx, min(y + dash_len, self.area_height)), 1)
            y += dash_len + gap

        # Draw game objects
        self.left_paddle.draw(surface)
        self.right_paddle.draw(surface)
        self.ball.draw(surface)

        surface.set_clip(old_clip)


class SettingsMenu:
    """
    Interactive settings menu with a live AI preview on the left
    and a compact settings panel on the right.
    """

    # Layout constants
    PREVIEW_WIDTH = 500
    SEPARATOR_X = 500
    SEPARATOR_WIDTH = 2
    PANEL_X = 502
    PANEL_WIDTH = 298

    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.selected_option = 0
        self.options = list(SETTING_RANGES.keys()) + [
            'left_paddle_color', 'right_paddle_color', 'background_color', 'Reset Defaults'
        ]
        self.color_keys = list(COLOR_OPTIONS.keys())
        self.bg_color_keys = list(BACKGROUND_OPTIONS.keys())
        self.editing = False
        self.preview = PreviewGame(self.PREVIEW_WIDTH, HEIGHT, settings)

    def handle_input(self, event):
        """Handle keyboard input for settings navigation."""
        if event.type != pygame.KEYDOWN:
            return False  # Return False = stay in settings

        if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
            return True  # Return True = exit settings

        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif event.key == pygame.K_LEFT:
            self._adjust_setting(-1)
        elif event.key == pygame.K_RIGHT:
            self._adjust_setting(1)
        elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
            if self.options[self.selected_option] == 'Reset Defaults':
                self.settings.reset_defaults()

        return False

    def _adjust_setting(self, direction):
        """Adjust the currently selected setting."""
        option = self.options[self.selected_option]

        if option in SETTING_RANGES:
            # Numeric setting
            current = getattr(self.settings, option)
            range_info = SETTING_RANGES[option]
            new_value = current + (direction * range_info['step'])
            new_value = max(range_info['min'], min(range_info['max'], new_value))
            setattr(self.settings, option, new_value)

        elif option == 'left_paddle_color':
            self._cycle_color('left_paddle_color', direction, COLOR_OPTIONS)
        elif option == 'right_paddle_color':
            self._cycle_color('right_paddle_color', direction, COLOR_OPTIONS)
        elif option == 'background_color':
            self._cycle_color('background_color', direction, BACKGROUND_OPTIONS)

    def _cycle_color(self, attr, direction, color_dict=None):
        """Cycle through color options."""
        if color_dict is None:
            color_dict = COLOR_OPTIONS
        current_color = getattr(self.settings, attr)
        current_idx = 0
        for i, (name, color) in enumerate(color_dict.items()):
            if color == current_color:
                current_idx = i
                break
        new_idx = (current_idx + direction) % len(color_dict)
        new_color = list(color_dict.values())[new_idx]
        setattr(self.settings, attr, new_color)

    def _get_color_name(self, color, color_dict=None):
        """Get the name of a color."""
        if color_dict is None:
            color_dict = COLOR_OPTIONS
        for name, c in color_dict.items():
            if c == color:
                return name
        # Check background colors too
        for name, c in BACKGROUND_OPTIONS.items():
            if c == color:
                return name
        return 'Custom'

    def draw(self, win):
        """Draw side-panel settings: live preview left, settings right."""
        # --- Live preview (left side) ---
        self.preview.apply_settings()
        self.preview.update()

        # Fill preview area with background color
        preview_rect = pygame.Rect(0, 0, self.PREVIEW_WIDTH, HEIGHT)
        win.fill(self.settings.background_color, preview_rect)
        self.preview.draw(win)

        # --- Separator ---
        pygame.draw.line(win, PURPLE,
                         (self.SEPARATOR_X, 0),
                         (self.SEPARATOR_X, HEIGHT),
                         self.SEPARATOR_WIDTH)

        # --- Settings panel (right side) ---
        panel_rect = pygame.Rect(self.PANEL_X, 0, self.PANEL_WIDTH, HEIGHT)
        win.fill(BLACK, panel_rect)

        px = self.PANEL_X  # panel left edge
        pw = self.PANEL_WIDTH
        pad = 10  # inner padding

        # Title
        title = FONT_MEDIUM_DIGITAL.render("SETTINGS", True, PURPLE)
        win.blit(title, (px + pw // 2 - title.get_width() // 2, 20))

        # Navigation hint
        hint = FONT_TINY_DIGITAL.render("[UP/DN] Nav  [LT/RT] Adj  [ESC] Back", True, GREY)
        win.blit(hint, (px + pw // 2 - hint.get_width() // 2, 55))

        # Compact labels for the narrow panel
        COMPACT_LABELS = {
            'ball_radius': 'Ball Size',
            'ball_speed': 'Ball Speed',
            'paddle_height': 'Paddle Ht',
            'paddle_speed': 'Paddle Spd',
            'winning_score': 'Win Score',
            'left_paddle_color': 'L. Paddle',
            'right_paddle_color': 'R. Paddle',
            'background_color': 'BG Color',
            'ai_difficulty': 'AI Level',
            'Reset Defaults': 'Reset Defaults',
        }

        # Settings list
        start_y = 85
        line_height = 35

        for i, option in enumerate(self.options):
            y = start_y + i * line_height
            is_selected = (i == self.selected_option)

            # Selection highlight
            if is_selected:
                pygame.draw.rect(win, DARK_GREY,
                                 (px + pad, y - 3, pw - pad * 2, line_height - 3))

            label = COMPACT_LABELS.get(option, option)

            # Get value display string
            if option == 'ai_difficulty':
                level = self.settings.ai_difficulty
                name = DIFFICULTY_NAMES.get(level, "")
                value_display = f"< {level} {name} >"
            elif option in SETTING_RANGES:
                value = str(getattr(self.settings, option))
                value_display = f"< {value} >"
            elif option == 'left_paddle_color':
                value_display = f"< {self._get_color_name(self.settings.left_paddle_color)} >"
            elif option == 'right_paddle_color':
                value_display = f"< {self._get_color_name(self.settings.right_paddle_color)} >"
            elif option == 'background_color':
                value_display = f"< {self._get_color_name(self.settings.background_color, BACKGROUND_OPTIONS)} >"
            elif option == 'Reset Defaults':
                value_display = "[ENTER]"
            else:
                value_display = ""

            # Draw label
            label_color = LIGHT_PURPLE if is_selected else GREY
            label_text = FONT_TINY_DIGITAL.render(label, True, label_color)
            win.blit(label_text, (px + pad + 5, y))

            # Draw value (right-aligned in panel)
            value_color = WHITE if is_selected else GREY
            value_text = FONT_TINY_DIGITAL.render(value_display, True, value_color)
            value_x = px + pw - pad - value_text.get_width()

            # If color option, leave room for color swatch
            if option in ['left_paddle_color', 'right_paddle_color', 'background_color']:
                value_x -= 28
            win.blit(value_text, (value_x, y))

            # Color swatch for color options
            if option in ['left_paddle_color', 'right_paddle_color', 'background_color']:
                color = getattr(self.settings, option)
                swatch_rect = (px + pw - pad - 22, y + 1, 18, 14)
                pygame.draw.rect(win, color, swatch_rect)
                pygame.draw.rect(win, WHITE, swatch_rect, 1)

        pygame.display.update()


# Global default settings instance
default_settings = GameSettings()
