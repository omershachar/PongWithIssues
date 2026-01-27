"""
settings.py -- Game settings and customization options.
Allows players to adjust ball/paddle size, speed, colors, and more.
"""
import pygame
from pong.constants import *


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

# Setting ranges
SETTING_RANGES = {
    'ball_radius': {'min': 3, 'max': 20, 'step': 1, 'label': 'Ball Size'},
    'ball_speed': {'min': 2, 'max': 15, 'step': 1, 'label': 'Ball Speed'},
    'paddle_height': {'min': 40, 'max': 200, 'step': 10, 'label': 'Paddle Height'},
    'paddle_speed': {'min': 3, 'max': 15, 'step': 1, 'label': 'Paddle Speed'},
    'winning_score': {'min': 1, 'max': 21, 'step': 1, 'label': 'Winning Score'},
}


class SettingsMenu:
    """
    Interactive settings menu for customizing game options.
    """

    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.selected_option = 0
        self.options = list(SETTING_RANGES.keys()) + ['left_paddle_color', 'right_paddle_color', 'Reset Defaults']
        self.color_keys = list(COLOR_OPTIONS.keys())
        self.editing = False

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
            self._cycle_color('left_paddle_color', direction)
        elif option == 'right_paddle_color':
            self._cycle_color('right_paddle_color', direction)

    def _cycle_color(self, attr, direction):
        """Cycle through color options."""
        current_color = getattr(self.settings, attr)
        current_idx = 0
        for i, (name, color) in enumerate(COLOR_OPTIONS.items()):
            if color == current_color:
                current_idx = i
                break
        new_idx = (current_idx + direction) % len(COLOR_OPTIONS)
        new_color = list(COLOR_OPTIONS.values())[new_idx]
        setattr(self.settings, attr, new_color)

    def _get_color_name(self, color):
        """Get the name of a color."""
        for name, c in COLOR_OPTIONS.items():
            if c == color:
                return name
        return 'Custom'

    def draw(self, win):
        """Draw the settings menu."""
        win.fill(BLACK)

        # Title
        title = FONT_BIG_DIGITAL.render("SETTINGS", True, PURPLE)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        # Instructions
        hint = FONT_TINY_DIGITAL.render("[UP/DOWN] Navigate  [LEFT/RIGHT] Adjust  [ESC] Back", True, GREY)
        win.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 100))

        # Settings list
        start_y = 150
        line_height = 45

        for i, option in enumerate(self.options):
            y = start_y + i * line_height
            is_selected = (i == self.selected_option)

            # Draw selection indicator
            if is_selected:
                pygame.draw.rect(win, DARK_GREY, (50, y - 5, WIDTH - 100, line_height - 5))
                indicator = FONT_SMALL_DIGITAL.render(">", True, PURPLE)
                win.blit(indicator, (60, y))

            # Get label and value
            if option in SETTING_RANGES:
                label = SETTING_RANGES[option]['label']
                value = str(getattr(self.settings, option))
                range_info = SETTING_RANGES[option]
                value_display = f"< {value} >"
            elif option == 'left_paddle_color':
                label = "Left Paddle Color"
                value_display = f"< {self._get_color_name(self.settings.left_paddle_color)} >"
            elif option == 'right_paddle_color':
                label = "Right Paddle Color"
                value_display = f"< {self._get_color_name(self.settings.right_paddle_color)} >"
            elif option == 'Reset Defaults':
                label = "Reset Defaults"
                value_display = "[ENTER]"
            else:
                label = option
                value_display = ""

            # Draw label
            label_color = LIGHT_PURPLE if is_selected else GREY
            label_text = FONT_SMALL_DIGITAL.render(label, True, label_color)
            win.blit(label_text, (90, y))

            # Draw value
            value_color = WHITE if is_selected else GREY
            value_text = FONT_SMALL_DIGITAL.render(value_display, True, value_color)
            win.blit(value_text, (WIDTH - value_text.get_width() - 80, y))

            # Draw color preview for paddle colors
            if option in ['left_paddle_color', 'right_paddle_color']:
                color = getattr(self.settings, option)
                preview_rect = (WIDTH - 60, y + 2, 30, 20)
                pygame.draw.rect(win, color, preview_rect)
                pygame.draw.rect(win, WHITE, preview_rect, 1)

        # Preview section
        preview_y = start_y + len(self.options) * line_height + 30
        preview_label = FONT_SMALL_DIGITAL.render("Preview:", True, GREY)
        win.blit(preview_label, (WIDTH // 2 - preview_label.get_width() // 2, preview_y))

        # Draw preview paddle and ball
        preview_center_y = preview_y + 60
        # Left paddle preview
        pygame.draw.rect(win, self.settings.left_paddle_color,
                        (WIDTH // 4 - self.settings.paddle_width // 2,
                         preview_center_y - self.settings.paddle_height // 4,
                         self.settings.paddle_width,
                         self.settings.paddle_height // 2))
        # Right paddle preview
        pygame.draw.rect(win, self.settings.right_paddle_color,
                        (3 * WIDTH // 4 - self.settings.paddle_width // 2,
                         preview_center_y - self.settings.paddle_height // 4,
                         self.settings.paddle_width,
                         self.settings.paddle_height // 2))
        # Ball preview
        pygame.draw.circle(win, self.settings.ball_color,
                          (WIDTH // 2, preview_center_y),
                          self.settings.ball_radius)

        pygame.display.update()


# Global default settings instance
default_settings = GameSettings()
