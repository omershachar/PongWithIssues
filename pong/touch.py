"""
touch.py -- Touch input handling for mobile/web play.
Maps finger touches to paddle movement and menu interactions.
"""
import sys
import pygame
from pong.constants import WIDTH, HEIGHT, FONT_TINY_DIGITAL, FONT_SMALL_DIGITAL, GREY, DARK_GREY, LIGHT_PURPLE

IS_WEB = sys.platform == "emscripten"

# In-game touch button areas (top strip) — large targets for thumbs
BUTTON_H = 56
MENU_BTN = pygame.Rect(0, 0, 120, BUTTON_H)
PAUSE_BTN = pygame.Rect(WIDTH - 120, 0, 120, BUTTON_H)


class _Ripple:
    """A single expanding ripple for touch feedback."""
    __slots__ = ('x', 'y', 'age', 'max_age', 'color')

    def __init__(self, x, y, color=(185, 183, 232)):
        self.x = x
        self.y = y
        self.age = 0
        self.max_age = 15  # frames (~0.25s)
        self.color = color


class TouchHandler:
    """Tracks active touches and maps them to game controls."""

    def __init__(self, single_player=False):
        self.fingers = {}        # finger_id -> (x, y) in pixels
        self.taps = []           # [(x, y)] taps detected this frame
        self.single_player = single_player  # True = all touches control left paddle
        self._ripples = []       # Visual feedback ripples
        self._show_zones = True  # Show zone indicators on first touches
        self._zone_touches = 0   # Count touches to auto-hide zone indicators

    def handle_event(self, event):
        """Process a pygame event. Returns True if it was a touch event."""
        if event.type == pygame.FINGERDOWN:
            x, y = event.x * WIDTH, event.y * HEIGHT
            self.fingers[event.finger_id] = (x, y)
            self.taps.append((x, y))
            self._ripples.append(_Ripple(x, y))
            self._zone_touches += 1
            if self._zone_touches > 6:
                self._show_zones = False
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

    def update_ripples(self):
        """Age ripple effects. Call once per frame."""
        for r in self._ripples:
            r.age += 1
        self._ripples = [r for r in self._ripples if r.age < r.max_age]

    def draw_ripples(self, win):
        """Draw touch ripple feedback."""
        for r in self._ripples:
            t = r.age / r.max_age  # 0.0 -> 1.0
            radius = int(10 + 30 * t)
            alpha = int(120 * (1.0 - t))
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*r.color[:3], alpha), (radius, radius), radius, 2)
            win.blit(surf, (int(r.x) - radius, int(r.y) - radius))


def draw_touch_buttons(win, paused=False):
    """Draw in-game touch buttons. Only visible on web/mobile."""
    if not IS_WEB:
        return

    # Semi-transparent backgrounds
    for btn in (MENU_BTN, PAUSE_BTN):
        overlay = pygame.Surface((btn.width, btn.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        win.blit(overlay, btn.topleft)
        # Subtle border
        pygame.draw.rect(win, (60, 60, 60), btn, 1)

    # MENU button (top-left)
    menu_text = FONT_SMALL_DIGITAL.render("< MENU", True, GREY)
    win.blit(menu_text, (MENU_BTN.x + 10, MENU_BTN.centery - menu_text.get_height() // 2))

    # PAUSE button (top-right)
    pause_label = "PLAY >" if paused else "PAUSE"
    pause_text = FONT_SMALL_DIGITAL.render(pause_label, True, GREY)
    win.blit(pause_text, (PAUSE_BTN.right - pause_text.get_width() - 10,
                          PAUSE_BTN.centery - pause_text.get_height() // 2))

    # Touch zone hint (subtle center line)
    pygame.draw.line(win, (40, 40, 40), (WIDTH // 2, BUTTON_H), (WIDTH // 2, HEIGHT), 1)


def draw_touch_zones(win, touch):
    """Draw paddle zone indicators on first play. Only on web."""
    if not IS_WEB or not touch._show_zones:
        return

    # Semi-transparent zone overlays
    zone_w = WIDTH // 2
    zone_h = HEIGHT - BUTTON_H

    # Left zone
    left_surf = pygame.Surface((zone_w, zone_h), pygame.SRCALPHA)
    left_surf.fill((185, 183, 232, 12))
    win.blit(left_surf, (0, BUTTON_H))

    # Right zone
    right_surf = pygame.Surface((zone_w, zone_h), pygame.SRCALPHA)
    right_surf.fill((185, 183, 232, 12))
    win.blit(right_surf, (zone_w, BUTTON_H))

    # Zone labels
    if touch.single_player:
        label = FONT_TINY_DIGITAL.render("TAP & DRAG TO MOVE", True, (100, 100, 100))
        win.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT - 60))
    else:
        left_label = FONT_TINY_DIGITAL.render("LEFT PADDLE", True, (80, 80, 80))
        right_label = FONT_TINY_DIGITAL.render("RIGHT PADDLE", True, (80, 80, 80))
        win.blit(left_label, (zone_w // 2 - left_label.get_width() // 2, HEIGHT - 60))
        win.blit(right_label, (zone_w + zone_w // 2 - right_label.get_width() // 2, HEIGHT - 60))
