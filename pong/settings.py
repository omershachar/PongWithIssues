"""
settings.py -- Game settings and customization options.
Allows players to adjust ball/paddle size, speed, colors, and more.
Supports save/load to JSON for persistence across sessions.
"""
import json
import os
import sys
import pygame
import numpy as np
from pong.constants import *
from pong.ball import Ball
from pong.paddle import Paddle
from pong.ai import ai_move_paddle, DIFFICULTY_NAMES
from pong.helpers import handle_ball_collision

# Settings file path (desktop: next to launcher, web: not used)
_SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.json')
_IS_WEB = sys.platform == "emscripten"


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

        # Power-up settings
        self.power_ups_enabled = True

        # Cursed mode settings
        self.cursed_events_enabled = True

        # Audio settings
        self.master_volume = 0.7
        self.sfx_volume = 1.0

        # Visual settings
        self.screen_shake = 1  # 0=off, 1=subtle, 2=intense
        self.particles_enabled = True

        # Goal net settings (Cursed mode)
        self.goal_net_enabled = False
        self.goal_net_size = 0.40  # fraction of screen height

        # Game speed multiplier
        self.game_speed = 1.0  # 0.5x to 2.0x

        # Control settings
        self.left_up_key = pygame.K_w
        self.left_down_key = pygame.K_s
        self.right_up_key = pygame.K_UP
        self.right_down_key = pygame.K_DOWN

    def reset_defaults(self):
        """Reset all settings to default values."""
        self.__init__()

    def to_dict(self):
        """Export settings as a JSON-serializable dictionary."""
        return {
            'ball_radius': int(self.ball_radius),
            'ball_speed': float(self.ball_speed),
            'ball_color': list(self.ball_color),
            'paddle_width': int(self.paddle_width),
            'paddle_height': int(self.paddle_height),
            'paddle_speed': float(self.paddle_speed),
            'left_paddle_color': list(self.left_paddle_color),
            'right_paddle_color': list(self.right_paddle_color),
            'background_color': list(self.background_color),
            'winning_score': int(self.winning_score),
            'ai_difficulty': int(self.ai_difficulty),
            'power_ups_enabled': bool(self.power_ups_enabled),
            'cursed_events_enabled': bool(self.cursed_events_enabled),
            'master_volume': float(self.master_volume),
            'sfx_volume': float(self.sfx_volume),
            'screen_shake': int(self.screen_shake),
            'particles_enabled': bool(self.particles_enabled),
            'game_speed': float(self.game_speed),
            'goal_net_enabled': bool(self.goal_net_enabled),
            'goal_net_size': float(self.goal_net_size),
        }

    def from_dict(self, data):
        """Load settings from a dictionary. Unknown keys are ignored."""
        color_fields = {'ball_color', 'left_paddle_color', 'right_paddle_color', 'background_color'}
        for key, value in data.items():
            if hasattr(self, key):
                if key in color_fields and isinstance(value, list):
                    setattr(self, key, tuple(value))
                else:
                    setattr(self, key, value)

    def save(self):
        """Save settings to JSON file. No-op on web."""
        if _IS_WEB:
            return
        try:
            with open(_SETTINGS_FILE, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception:
            pass

    def load(self):
        """Load settings from JSON file. No-op on web or if file missing."""
        if _IS_WEB:
            return
        try:
            with open(_SETTINGS_FILE, 'r') as f:
                data = json.load(f)
            self.from_dict(data)
        except Exception:
            pass


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
    'master_volume': {'min': 0.0, 'max': 1.0, 'step': 0.1, 'label': 'Volume'},
    'sfx_volume': {'min': 0.0, 'max': 1.0, 'step': 0.1, 'label': 'SFX Volume'},
    'screen_shake': {'min': 0, 'max': 2, 'step': 1, 'label': 'Shake'},
    'game_speed': {'min': 0.5, 'max': 2.0, 'step': 0.25, 'label': 'Game Speed'},
    'goal_net_size': {'min': 0.2, 'max': 0.7, 'step': 0.05, 'label': 'Goal Net Size'},
}

# Human-readable names for screen shake levels
SHAKE_NAMES = {0: 'OFF', 1: 'Subtle', 2: 'Intense'}


class SettingsMenu:
    """
    Interactive settings menu drawn as a side panel on the RIGHT side of the screen.
    The main menu (with its bouncing ball) is still visible on the LEFT.
    Two AI paddles play against each other using the menu's bouncing ball,
    and all changes apply instantly to the preview.
    """

    # Layout constants — settings panel on the right
    PANEL_WIDTH = 300
    PANEL_X = WIDTH - 300
    SEPARATOR_X = WIDTH - 300
    SEPARATOR_WIDTH = 2

    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.selected_option = 0
        self.options = list(SETTING_RANGES.keys()) + [
            'power_ups_enabled', 'cursed_events_enabled', 'goal_net_enabled', 'particles_enabled',
            'left_paddle_color', 'right_paddle_color', 'background_color', 'Reset Defaults'
        ]
        self.color_keys = list(COLOR_OPTIONS.keys())
        self.bg_color_keys = list(BACKGROUND_OPTIONS.keys())
        self.editing = False

        # Preview paddles (play with the menu's bouncing ball)
        self._left_paddle = None
        self._right_paddle = None
        self._paddles_created = False

    def _ensure_paddles(self):
        """Lazily create preview paddles in the menu area (left side of screen)."""
        if self._paddles_created:
            return
        s = self.settings
        preview_w = self.PANEL_X  # Width of the visible menu area
        cy = HEIGHT // 2
        margin = 15
        self._left_paddle = Paddle(
            margin, cy - s.paddle_height // 2,
            s.paddle_width, s.paddle_height,
            color=s.left_paddle_color, mode='physics', fixed_vel=s.paddle_speed
        )
        self._right_paddle = Paddle(
            preview_w - margin - s.paddle_width, cy - s.paddle_height // 2,
            s.paddle_width, s.paddle_height,
            color=s.right_paddle_color, mode='physics', fixed_vel=s.paddle_speed
        )
        self._paddles_created = True

    def _apply_preview_settings(self):
        """Update preview paddle properties to match current settings."""
        if not self._paddles_created:
            return
        s = self.settings
        preview_w = self.PANEL_X
        margin = 15

        for paddle, color in [(self._left_paddle, s.left_paddle_color),
                              (self._right_paddle, s.right_paddle_color)]:
            old_center_y = paddle.pos[1] + paddle.height / 2
            paddle.width = s.paddle_width
            paddle.height = s.paddle_height
            paddle.color = color
            paddle.fixed_vel = s.paddle_speed
            paddle.pos[1] = old_center_y - paddle.height / 2

        # Right paddle x-position
        self._right_paddle.pos[0] = preview_w - margin - s.paddle_width

    def _update_preview(self, ball_menu):
        """Run one frame of AI pong in the preview area using the menu's bouncing ball."""
        if not self._paddles_created:
            return
        s = self.settings
        preview_w = self.PANEL_X

        # AI for right paddle (tracks ball when it goes right)
        ai_move_paddle(self._right_paddle, ball_menu, difficulty=6)

        # AI for left paddle (tracks ball when it goes left)
        paddle = self._left_paddle
        paddle_center = paddle.pos[1] + paddle.height / 2
        dead_zone = paddle.height * 0.1
        if ball_menu.vel[0] < 0:
            diff = ball_menu.pos[1] - paddle_center
            if abs(diff) > dead_zone:
                paddle.accelerate(up=(diff < 0))
        else:
            center = HEIGHT / 2
            diff = center - paddle_center
            if abs(diff) > dead_zone * 2:
                paddle.accelerate(up=(diff < 0))

        self._left_paddle.update()
        self._right_paddle.update()

        # Move the ball (physics mode with trail + Magnus)
        ball_menu.update()

        # Wall bounce (top/bottom) within the full screen height
        if ball_menu.pos[1] + ball_menu.radius >= HEIGHT:
            ball_menu.pos[1] = HEIGHT - ball_menu.radius
            ball_menu.vel[1] *= -1
        elif ball_menu.pos[1] - ball_menu.radius <= 0:
            ball_menu.pos[1] = ball_menu.radius
            ball_menu.vel[1] *= -1

        # Collisions with preview paddles
        handle_ball_collision(ball_menu, self._left_paddle, self._right_paddle)

        # Reset ball if it exits the preview area (past the paddles)
        bx = ball_menu.pos[0]
        if bx < -ball_menu.radius or bx > preview_w + ball_menu.radius:
            cx = preview_w // 2
            cy = HEIGHT // 2
            direction = 1 if bx < 0 else -1
            ball_menu.pos[:] = [cx, cy]
            ball_menu.vel[:] = [s.ball_speed * direction, 0]
            ball_menu.spin = 0
            ball_menu.trail.clear()

    def handle_input(self, event, touch=None):
        """Handle keyboard and touch input for settings navigation."""
        # Touch input: tap on setting rows or adjustment areas
        if touch and touch.taps:
            for tap_x, tap_y in touch.taps:
                # Check if tap is in the panel area
                if tap_x >= self.PANEL_X:
                    # Map tap Y to a setting row
                    start_y = 85
                    line_height = 35
                    row = int((tap_y - start_y) / line_height)
                    if 0 <= row < len(self.options):
                        if row == self.selected_option:
                            # Already selected: check if tap is left or right to adjust
                            mid_x = self.PANEL_X + self.PANEL_WIDTH // 2
                            if tap_x < mid_x:
                                self._adjust_setting(-1)
                            else:
                                if self.options[row] == 'Reset Defaults':
                                    self.settings.reset_defaults()
                                else:
                                    self._adjust_setting(1)
                        else:
                            self.selected_option = row
                else:
                    # Tap on the menu area = go back
                    self.settings.save()
                    self._apply_audio_settings()
                    self._paddles_created = False
                    return True

        if event.type != pygame.KEYDOWN:
            return False  # Return False = stay in settings

        if event.key == pygame.K_ESCAPE or event.key == pygame.K_m or event.key == pygame.K_s:
            self.settings.save()
            self._apply_audio_settings()
            self._paddles_created = False
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
            # Round floats to avoid drift
            if isinstance(range_info['step'], float):
                new_value = round(new_value, 2)
            setattr(self.settings, option, new_value)
            # Apply audio changes live
            if option in ('master_volume', 'sfx_volume'):
                self._apply_audio_settings()

        elif option == 'power_ups_enabled':
            self.settings.power_ups_enabled = not self.settings.power_ups_enabled
        elif option == 'cursed_events_enabled':
            self.settings.cursed_events_enabled = not self.settings.cursed_events_enabled
        elif option == 'goal_net_enabled':
            self.settings.goal_net_enabled = not self.settings.goal_net_enabled
        elif option == 'particles_enabled':
            self.settings.particles_enabled = not self.settings.particles_enabled
        elif option == 'left_paddle_color':
            self._cycle_color('left_paddle_color', direction, COLOR_OPTIONS)
        elif option == 'right_paddle_color':
            self._cycle_color('right_paddle_color', direction, COLOR_OPTIONS)
        elif option == 'background_color':
            self._cycle_color('background_color', direction, BACKGROUND_OPTIONS)

    def _apply_audio_settings(self):
        """Push current volume settings to the audio system."""
        from pong import audio
        audio.set_volume(master=self.settings.master_volume, sfx=self.settings.sfx_volume)

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

    def draw(self, win, selected_mode=0, draw_menu_fn=None, ball_menu=None):
        """
        Draw the settings as a side panel. The main menu is drawn behind it
        so the bouncing ball and menu art remain visible.

        Args:
            win: pygame display surface
            selected_mode: current selected mode in the main menu
            draw_menu_fn: callable to draw the main menu background
            ball_menu: the menu's bouncing ball object (for live AI preview)
        """
        self._ensure_paddles()
        self._apply_preview_settings()

        # Update ball radius to match settings
        if ball_menu:
            ball_menu.radius = self.settings.ball_radius

        # --- Draw the main menu as background (left side stays visible) ---
        if draw_menu_fn is not None:
            # Draw menu WITHOUT triggering display.update — we'll update after
            # the settings panel is drawn on top
            draw_menu_fn(win, selected_mode, _skip_update=True)
        else:
            win.fill(self.settings.background_color)

        # --- Update and draw preview paddles in the menu area ---
        if ball_menu:
            self._update_preview(ball_menu)
            self._left_paddle.draw(win)
            self._right_paddle.draw(win)

        # --- Dark overlay on right side for the settings panel ---
        panel_rect = pygame.Rect(self.PANEL_X, 0, self.PANEL_WIDTH, HEIGHT)
        panel_bg = pygame.Surface((self.PANEL_WIDTH, HEIGHT), pygame.SRCALPHA)
        panel_bg.fill((0, 0, 0, 220))
        win.blit(panel_bg, (self.PANEL_X, 0))

        # --- Separator line ---
        pygame.draw.line(win, PURPLE,
                         (self.SEPARATOR_X, 0),
                         (self.SEPARATOR_X, HEIGHT),
                         self.SEPARATOR_WIDTH)

        # --- Settings panel content ---
        px = self.PANEL_X
        pw = self.PANEL_WIDTH
        pad = 10

        # Title
        title = FONT_MEDIUM_DIGITAL.render("SETTINGS", True, PURPLE)
        win.blit(title, (px + pw // 2 - title.get_width() // 2, 20))

        # Navigation hint
        hint = FONT_TINY_DIGITAL.render("[UP/DN] Nav  [LT/RT] Adj  [S/ESC] Back", True, GREY)
        win.blit(hint, (px + pw // 2 - hint.get_width() // 2, 55))

        # Compact labels for the narrow panel
        COMPACT_LABELS = {
            'ball_radius': 'Ball Size',
            'ball_speed': 'Ball Speed',
            'paddle_height': 'Paddle Ht',
            'paddle_speed': 'Paddle Spd',
            'winning_score': 'Win Score',
            'ai_difficulty': 'AI Level',
            'master_volume': 'Volume',
            'sfx_volume': 'SFX Vol',
            'screen_shake': 'Shake',
            'game_speed': 'Speed',
            'left_paddle_color': 'L. Paddle',
            'right_paddle_color': 'R. Paddle',
            'background_color': 'BG Color',
            'power_ups_enabled': 'Power-Ups',
            'cursed_events_enabled': 'Cursed Evt',
            'goal_net_enabled': 'Goal Nets',
            'goal_net_size': 'Net Size',
            'particles_enabled': 'Particles',
            'Reset Defaults': 'Reset All',
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
            elif option == 'screen_shake':
                value_display = f"< {SHAKE_NAMES.get(self.settings.screen_shake, '?')} >"
            elif option == 'master_volume' or option == 'sfx_volume':
                val = getattr(self.settings, option)
                pct = int(val * 100)
                value_display = f"< {pct}% >"
            elif option == 'game_speed':
                val = self.settings.game_speed
                value_display = f"< {val:.2g}x >"
            elif option in SETTING_RANGES:
                value = str(getattr(self.settings, option))
                value_display = f"< {value} >"
            elif option == 'power_ups_enabled':
                value_display = "< ON >" if self.settings.power_ups_enabled else "< OFF >"
            elif option == 'cursed_events_enabled':
                value_display = "< ON >" if self.settings.cursed_events_enabled else "< OFF >"
            elif option == 'goal_net_enabled':
                value_display = "< ON >" if self.settings.goal_net_enabled else "< OFF >"
            elif option == 'goal_net_size':
                pct = int(self.settings.goal_net_size * 100)
                value_display = f"< {pct}% >"
            elif option == 'particles_enabled':
                value_display = "< ON >" if self.settings.particles_enabled else "< OFF >"
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
