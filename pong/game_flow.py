"""
game_flow.py -- Shared game flow UI: countdown, pause menu, win/lose screen.
Used by all game modes to provide consistent, interactive game state transitions.
"""

import asyncio
import pygame
import sys
from pong.constants import *

IS_WEB = sys.platform == "emscripten"


# -------------------- Countdown --------------------

async def countdown(win, bg_draw_fn, duration=3):
    """
    Display a 3-2-1-GO countdown before starting a round.

    Args:
        win: pygame display surface
        bg_draw_fn: callable that draws the current game state (background, paddles, ball, etc.)
        duration: number of countdown steps (default 3 → "3", "2", "1", "GO!")
    """
    clock = pygame.time.Clock()

    for i in range(duration, 0, -1):
        # Drain events during countdown (prevent input queuing)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'

        bg_draw_fn()

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        win.blit(overlay, (0, 0))

        # Number
        text = FONT_TITLE_DIGITAL.render(str(i), True, WHITE)
        win.blit(text, (WIDTH // 2 - text.get_width() // 2,
                        HEIGHT // 2 - text.get_height() // 2))

        pygame.display.update()

        # Play countdown tick sound
        try:
            from pong import audio
            audio.play('countdown_tick')
        except Exception:
            pass

        # Wait ~1 second (async-friendly)
        for _ in range(60):
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
            await asyncio.sleep(0)

    # "GO!" frame
    bg_draw_fn()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 80))
    win.blit(overlay, (0, 0))

    go_text = FONT_TITLE_DIGITAL.render("GO!", True, GREEN)
    win.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2,
                       HEIGHT // 2 - go_text.get_height() // 2))
    pygame.display.update()

    try:
        from pong import audio
        audio.play('countdown_go')
    except Exception:
        pass

    # Brief "GO!" display
    for _ in range(30):
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
        await asyncio.sleep(0)

    return 'start'


# -------------------- Pause Menu --------------------

class PauseMenu:
    """Interactive pause menu with selectable options."""

    OPTIONS = ['Resume', 'Restart', 'Main Menu']

    def __init__(self):
        self.selected = 0
        self.font_title = FONT_BIG_DIGITAL
        self.font_option = FONT_MEDIUM_DIGITAL
        self.font_hint = FONT_TINY_DIGITAL
        # Touch rects (computed on draw)
        self._option_rects = []

    def handle_event(self, event, touch=None):
        """
        Handle input for the pause menu.
        Returns: 'resume', 'restart', 'menu', or None (no action yet).
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                return 'resume'
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.OPTIONS)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.OPTIONS)
            elif event.key == pygame.K_RETURN:
                return self._get_action()

        return None

    def handle_touch(self, touch):
        """Check touch taps against option rects."""
        if not touch or not self._option_rects:
            return None
        for tap_x, tap_y in touch.taps:
            for i, rect in enumerate(self._option_rects):
                if rect.collidepoint(tap_x, tap_y):
                    return ['resume', 'restart', 'menu'][i]
        return None

    def _get_action(self):
        return ['resume', 'restart', 'menu'][self.selected]

    def draw(self, win):
        """Draw pause menu overlay."""
        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        win.blit(overlay, (0, 0))

        # Title
        title = self.font_title.render("PAUSED", True, PURPLE)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 120))

        # Options
        self._option_rects = []
        y_start = HEIGHT // 2 - 30
        for i, option in enumerate(self.OPTIONS):
            color = WHITE if i == self.selected else GREY
            prefix = "> " if i == self.selected else "  "
            text = self.font_option.render(f"{prefix}{option}", True, color)
            x = WIDTH // 2 - text.get_width() // 2
            y = y_start + i * 45
            win.blit(text, (x, y))
            # Store touch rect (wider for easier tapping)
            self._option_rects.append(pygame.Rect(
                WIDTH // 2 - 120, y - 5, 240, 40
            ))

        # Hint
        hint = self.font_hint.render("[SPACE] Resume  [UP/DOWN] Select  [ENTER] Confirm", True, DARK_GREY)
        win.blit(hint, (WIDTH // 2 - hint.get_width() // 2, y_start + len(self.OPTIONS) * 45 + 20))


# -------------------- Win/Lose Screen --------------------

class WinScreen:
    """Interactive win/lose screen with options and match stats."""

    OPTIONS = ['Play Again', 'Main Menu']

    def __init__(self):
        self.selected = 0
        self.font_title = FONT_BIG_DIGITAL
        self.font_subtitle = FONT_MEDIUM_DIGITAL
        self.font_option = FONT_MEDIUM_DIGITAL
        self.font_stat = FONT_SMALL_DIGITAL
        self.font_hint = FONT_TINY_DIGITAL
        self._option_rects = []

    def handle_event(self, event):
        """
        Handle input for win screen.
        Returns: 'play_again', 'menu', or None.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.OPTIONS)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.OPTIONS)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self._get_action()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                return 'menu'
            elif event.key == pygame.K_r:
                return 'play_again'
        return None

    def handle_touch(self, touch):
        """Check touch taps against option rects."""
        if not touch or not self._option_rects:
            return None
        for tap_x, tap_y in touch.taps:
            for i, rect in enumerate(self._option_rects):
                if rect.collidepoint(tap_x, tap_y):
                    return ['play_again', 'menu'][i]
        return None

    def _get_action(self):
        return ['play_again', 'menu'][self.selected]

    def draw(self, win, winner_text, left_score, right_score, bg_color=BLACK):
        """
        Draw the win/lose screen.

        Args:
            win: pygame surface
            winner_text: e.g. "Left Player Won!" or "AI Won!"
            left_score: final left score
            right_score: final right score
            bg_color: background color
        """
        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        win.blit(overlay, (0, 0))

        # Winner text
        title = self.font_title.render(winner_text, True, PURPLE)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 140))

        # Final score
        score_text = self.font_subtitle.render(
            f"{left_score}  -  {right_score}", True, WHITE
        )
        win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 70))

        # Decorative line
        line_y = HEIGHT // 2 - 40
        pygame.draw.line(win, DARK_GREY, (WIDTH // 2 - 100, line_y), (WIDTH // 2 + 100, line_y), 2)

        # Options
        self._option_rects = []
        y_start = HEIGHT // 2
        for i, option in enumerate(self.OPTIONS):
            color = WHITE if i == self.selected else GREY
            prefix = "> " if i == self.selected else "  "
            text = self.font_option.render(f"{prefix}{option}", True, color)
            x = WIDTH // 2 - text.get_width() // 2
            y = y_start + i * 50
            win.blit(text, (x, y))
            self._option_rects.append(pygame.Rect(
                WIDTH // 2 - 130, y - 5, 260, 45
            ))

        # Hint
        hint = self.font_hint.render("[R] Play Again  [ESC] Menu  [UP/DOWN] Select  [ENTER] Confirm", True, DARK_GREY)
        win.blit(hint, (WIDTH // 2 - hint.get_width() // 2, y_start + len(self.OPTIONS) * 50 + 30))


# -------------------- Exit Confirmation --------------------

async def confirm_exit(win, bg_draw_fn, touch=None):
    """
    Show a "Leave match?" confirmation dialog.
    Returns True if user confirms exit, False to cancel.
    """
    clock = pygame.time.Clock()
    selected = 1  # Default to "Cancel" (safer)
    font_title = FONT_MEDIUM_DIGITAL
    font_option = FONT_SMALL_DIGITAL
    font_hint = FONT_TINY_DIGITAL

    options = ['Leave', 'Cancel']
    option_rects = []

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if touch:
                touch.handle_event(event)
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False  # Cancel on second ESC
                if event.key == pygame.K_LEFT:
                    selected = 0
                elif event.key == pygame.K_RIGHT:
                    selected = 1
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return selected == 0
                elif event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False

        # Touch handling
        if touch and option_rects:
            for tap_x, tap_y in touch.taps:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(tap_x, tap_y):
                        if touch:
                            touch.clear_taps()
                        return i == 0
            touch.clear_taps()

        # Draw background
        bg_draw_fn()

        # Dark overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        win.blit(overlay, (0, 0))

        # Dialog box
        box_w, box_h = 320, 140
        box_x = WIDTH // 2 - box_w // 2
        box_y = HEIGHT // 2 - box_h // 2
        pygame.draw.rect(win, (30, 30, 30), (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(win, PURPLE, (box_x, box_y, box_w, box_h), width=2, border_radius=8)

        # Title
        title = font_title.render("Leave match?", True, WHITE)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, box_y + 20))

        # Options (side by side)
        option_rects = []
        opt_y = box_y + 75
        for i, opt in enumerate(options):
            color = WHITE if i == selected else GREY
            bg = PURPLE if i == selected else (50, 50, 50)
            opt_x = box_x + 40 + i * 150
            rect = pygame.Rect(opt_x, opt_y, 110, 35)
            pygame.draw.rect(win, bg, rect, border_radius=5)
            text = font_option.render(opt, True, color)
            win.blit(text, (rect.centerx - text.get_width() // 2,
                            rect.centery - text.get_height() // 2))
            option_rects.append(rect)

        # Hint
        hint = font_hint.render("[Y] Leave  [N] Cancel  [LEFT/RIGHT] Select", True, DARK_GREY)
        win.blit(hint, (WIDTH // 2 - hint.get_width() // 2, box_y + box_h + 10))

        pygame.display.update()
        await asyncio.sleep(0)
