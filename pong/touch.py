"""
touch.py -- Touch input handling for mobile/web play.
Maps finger touches to paddle movement and menu interactions.
"""
import sys
import pygame
from pong.constants import WIDTH, HEIGHT, FONT_TINY_DIGITAL, GREY, DARK_GREY

IS_WEB = sys.platform == "emscripten"

# In-game touch button areas (top strip)
BUTTON_H = 40
MENU_BTN = pygame.Rect(0, 0, 90, BUTTON_H)
PAUSE_BTN = pygame.Rect(WIDTH - 90, 0, 90, BUTTON_H)


class TouchHandler:
    """Tracks active touches and maps them to game controls."""

    def __init__(self, single_player=False):
        self.fingers = {}        # finger_id -> (x, y) in pixels
        self.taps = []           # [(x, y)] taps detected this frame
        self.single_player = single_player  # True = all touches control left paddle

    def handle_event(self, event):
        """Process a pygame event. Returns True if it was a touch event."""
        if event.type == pygame.FINGERDOWN:
            x, y = event.x * WIDTH, event.y * HEIGHT
            self.fingers[event.finger_id] = (x, y)
            self.taps.append((x, y))
            return True
        elif event.type == pygame.FINGERMOTION:
            x, y = event.x * WIDTH, event.y * HEIGHT
            self.fingers[event.finger_id] = (x, y)
            return True
        elif event.type == pygame.FINGERUP:
            self.fingers.pop(event.finger_id, None)
            return True
        return False

    def clear_taps(self):
        """Clear tap list. Call once per frame after processing taps."""
        self.taps.clear()

    def get_left_target(self):
        """Get Y target for left paddle (left-half touches). Returns None if none."""
        for fid, (x, y) in self.fingers.items():
            if y < BUTTON_H:
                continue  # Ignore touches in button strip
            if self.single_player or x < WIDTH / 2:
                return y
        return None

    def get_right_target(self):
        """Get Y target for right paddle (right-half touches). Returns None if none."""
        if self.single_player:
            return None
        for fid, (x, y) in self.fingers.items():
            if y < BUTTON_H:
                continue
            if x >= WIDTH / 2:
                return y
        return None

    def tapped_in(self, rect):
        """Check if any tap this frame hit the given rect."""
        return any(rect.collidepoint(x, y) for x, y in self.taps)

    def tapped_menu_btn(self):
        """Check if the in-game MENU button was tapped."""
        return self.tapped_in(MENU_BTN)

    def tapped_pause_btn(self):
        """Check if the in-game PAUSE button was tapped."""
        return self.tapped_in(PAUSE_BTN)


def draw_touch_buttons(win, paused=False):
    """Draw in-game touch buttons. Only visible on web/mobile."""
    if not IS_WEB:
        return

    # Semi-transparent backgrounds
    for btn in (MENU_BTN, PAUSE_BTN):
        overlay = pygame.Surface((btn.width, btn.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        win.blit(overlay, btn.topleft)

    # MENU button (top-left)
    menu_text = FONT_TINY_DIGITAL.render("< MENU", True, GREY)
    win.blit(menu_text, (MENU_BTN.x + 8, MENU_BTN.centery - menu_text.get_height() // 2))

    # PAUSE button (top-right)
    pause_label = "PLAY >" if paused else "PAUSE"
    pause_text = FONT_TINY_DIGITAL.render(pause_label, True, GREY)
    win.blit(pause_text, (PAUSE_BTN.right - pause_text.get_width() - 8,
                          PAUSE_BTN.centery - pause_text.get_height() // 2))

    # Touch zone hint (subtle center line)
    pygame.draw.line(win, (40, 40, 40), (WIDTH // 2, BUTTON_H), (WIDTH // 2, HEIGHT), 1)
