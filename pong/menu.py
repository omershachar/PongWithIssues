import pygame
import sys
import os

try:
    import webbrowser
except ImportError:
    webbrowser = None  # Not available in WASM/Pygbag
from pong.constants import *
from pong.ball import Ball
from pong import audio

ball_menu = Ball(*MIDDLE_BOARD, BALL_RADIUS, WHITE, mode='physics', vel=(BALL_DEFAULT_VEL[0], 4))

# Developer info
DEVELOPER = "omershachar"
GITHUB_URL = "github.com/omershachar/PongWithIssues"
GITHUB_FULL_URL = "https://github.com/omershachar/PongWithIssues"
VERSION = "v1.0.0"

# Clickable link rect (set during draw, checked during event handling)
_github_link_rect = None

# Logo loaded lazily on first draw (needs display to be initialized for convert_alpha)
_logo_image = None
_logo_loaded = False


def handle_menu_click(event):
    """Handle mouse clicks in the menu. Call from the event loop.
    Returns True if a click was consumed."""
    global _github_link_rect
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if _github_link_rect and _github_link_rect.collidepoint(event.pos):
            if webbrowser is not None:
                webbrowser.open(GITHUB_FULL_URL)
            return True
    return False


# Game modes configuration
GAME_MODES = [
    {
        'name': 'Classic',
        'description': 'Original Pong experience',
        'color': WHITE,
        'ball_color': WHITE
    },
    {
        'name': 'Pongception',
        'description': 'Physics mode with spin & momentum',
        'color': RED,
        'ball_color': RED
    },
    {
        'name': 'BETA',
        'description': 'Experimental features',
        'color': GREY,
        'ball_color': DARK_GREY
    },
    {
        'name': 'Cursed',
        'description': 'Random chaos events!',
        'color': (255, 50, 200),
        'ball_color': (255, 50, 200)
    },
    {
        'name': 'Crazy',
        'description': 'Small paddles, speed ramps, screen shake',
        'color': (255, 140, 0),
        'ball_color': (255, 180, 50)
    },
    {
        'name': 'Sandbox',
        'description': 'Debug mode - no scoring',
        'color': GREEN,
        'ball_color': GREEN
    }
]

def _mode_layout():
    """Compute box dimensions based on number of modes."""
    n = len(GAME_MODES)
    if n <= 4:
        return 160, 70, 20
    else:
        # Shrink to fit 800px width
        spacing = 12
        box_w = (WIDTH - 20 - (n - 1) * spacing) // n
        return box_w, 70, spacing

def get_mode_box_rects():
    """Return list of pygame.Rect for each mode selection box (for touch hit-testing)."""
    mode_box_width, mode_box_height, mode_spacing = _mode_layout()
    mode_start_y = MENU_SUBTITLES_Y + MENU_MARGIN_Y * 3
    total_width = len(GAME_MODES) * mode_box_width + (len(GAME_MODES) - 1) * mode_spacing
    start_x = (WIDTH - total_width) // 2
    rects = []
    for i in range(len(GAME_MODES)):
        x = start_x + i * (mode_box_width + mode_spacing)
        rects.append(pygame.Rect(x, mode_start_y, mode_box_width, mode_box_height))
    return rects


def draw_menu(WIN, selected_mode, _skip_update=False):
    WIN.fill(BLACK)

    # Draw ASCII art title
    for i, line in enumerate(PONG_ASCII_3D.splitlines()):
        if line.strip() == "":
            continue
        text_surface = ASCII_FONT.render(line, True, PURPLE)
        WIN.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, MENU_MARGIN_Y + i * 30))

    # Subtitle
    sub1 = FONT_MEDIUM_DIGITAL.render("A project that probably works. Sometimes. Maybe.", True, LIGHT_PURPLE)
    WIN.blit(sub1, (WIDTH // 2 - sub1.get_width() // 2, MENU_SUBTITLES_Y))

    sub2 = FONT_MEDIUM_DIGITAL.render("It compiles. That's enough.", True, LIGHT_PURPLE)
    WIN.blit(sub2, (WIDTH // 2 - sub2.get_width() // 2, MENU_SUBTITLES_Y + MENU_MARGIN_Y))

    # Mode selection grid
    mode_start_y = MENU_SUBTITLES_Y + MENU_MARGIN_Y * 3
    mode_box_width, mode_box_height, mode_spacing = _mode_layout()
    total_width = len(GAME_MODES) * mode_box_width + (len(GAME_MODES) - 1) * mode_spacing
    start_x = (WIDTH - total_width) // 2

    for i, mode in enumerate(GAME_MODES):
        x = start_x + i * (mode_box_width + mode_spacing)
        y = mode_start_y

        # Draw selection box
        is_selected = (i == selected_mode)
        box_color = mode['color'] if is_selected else DARK_GREY
        border_width = 3 if is_selected else 1

        # Background for selected
        if is_selected:
            pygame.draw.rect(WIN, (*box_color[:3], 30) if len(box_color) > 3 else box_color,
                           (x, y, mode_box_width, mode_box_height))
        pygame.draw.rect(WIN, box_color, (x, y, mode_box_width, mode_box_height), border_width)

        # Mode name
        name_color = mode['color'] if is_selected else GREY
        name_text = FONT_SMALL_DIGITAL.render(mode['name'], True, name_color)
        WIN.blit(name_text, (x + mode_box_width // 2 - name_text.get_width() // 2, y + 15))

        # Mode description (smaller)
        if is_selected:
            desc_text = FONT_TINY_DIGITAL.render(mode['description'], True, LIGHT_PURPLE)
            WIN.blit(desc_text, (x + mode_box_width // 2 - desc_text.get_width() // 2, y + 45))

    # Update ball color based on selection
    if selected_mode < len(GAME_MODES):
        ball_menu.color = GAME_MODES[selected_mode]['ball_color']

    # Navigation hint
    nav_text = FONT_TINY_DIGITAL.render("[LEFT/RIGHT] Select mode  |  [S] Settings", True, DARK_GREY)
    WIN.blit(nav_text, (WIDTH // 2 - nav_text.get_width() // 2, mode_start_y + mode_box_height + 20))

    # Start prompt
    prompt = FONT_DEFAULT_DIGITAL.render("Press [SPACE] to start", True, PURPLE)
    WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 160))

    # Version in top-left corner
    version_text = FONT_TINY_DIGITAL.render(VERSION, True, DARK_GREY)
    WIN.blit(version_text, (10, 10))

    # Logo + GitHub link in bottom-left corner
    global _github_link_rect, _logo_image, _logo_loaded
    logo_size = 80

    # Lazy-load logo image (needs display initialized for convert_alpha)
    if not _logo_loaded:
        _logo_loaded = True
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        for name in ('omer_logo_128x128.png', 'omer_logo_256x256.png'):
            path = os.path.join(assets_dir, name)
            if os.path.exists(path):
                try:
                    _logo_image = pygame.image.load(path).convert_alpha()
                    break
                except Exception:
                    pass

    # Draw logo (image if available)
    logo_x = 12
    logo_y = HEIGHT - logo_size - 35
    if _logo_image is not None:
        scaled = pygame.transform.smoothscale(_logo_image, (logo_size, logo_size))
        WIN.blit(scaled, (logo_x, logo_y))

    # GitHub link below the logo
    link_text = FONT_MEDIUM_DIGITAL.render(DEVELOPER, True, LIGHT_PURPLE)
    link_x = 12
    link_y = HEIGHT - 30
    WIN.blit(link_text, (link_x, link_y))
    pygame.draw.line(WIN, LIGHT_PURPLE,
                     (link_x, link_y + link_text.get_height()),
                     (link_x + link_text.get_width(), link_y + link_text.get_height()), 1)
    _github_link_rect = pygame.Rect(link_x, link_y,
                                    link_text.get_width(), link_text.get_height() + 2)

    # Draw bouncing ball (skip bounce update if being used as settings background)
    ball_menu.draw(WIN)
    if not _skip_update:
        if ball_menu.bounce_box(WIDTH, HEIGHT):
            audio.play('wall_bounce')
        pygame.display.update()
