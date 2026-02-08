import pygame
import sys
import os

try:
    import webbrowser
except ImportError:
    webbrowser = None  # Not available in WASM/Pygbag
from pong.constants import *
from pong.ball import Ball

ball_menu = Ball(*MIDDLE_BOARD, BALL_RADIUS, WHITE, mode='classic', vel=(BALL_DEFAULT_VEL[0], 4))

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


def draw_fox_logo(surface, x, y, size=64):
    """Draw a fox-with-laptop icon matching the GitHub profile picture.
    Multi-toned grey fox sitting with a laptop, curled tail.
    """
    s = size / 24.0

    # Fox palette
    BODY_DARKEST = (55, 55, 60)
    BODY_DARK = (80, 82, 88)
    BODY_MID = (115, 118, 125)
    BODY_LIGHT = (155, 158, 165)
    BODY_HIGHLIGHT = (185, 188, 195)
    SNOUT_WHITE = (220, 222, 228)
    EYE_COLOR = (240, 245, 255)
    NOSE_COLOR = (40, 40, 45)

    # Laptop palette
    LAPTOP_DARK = (50, 52, 58)
    LAPTOP_FRAME = (85, 88, 95)
    LAPTOP_BEZEL = (70, 72, 78)
    SCREEN_BG = (140, 165, 190)
    SCREEN_GLOW = (170, 200, 225)
    KEYBOARD_KEYS = (95, 98, 105)

    # --- Tail (drawn first, behind body) ---
    tail = [
        (x + 14*s, y + 18*s),
        (x + 17*s, y + 15.5*s),
        (x + 20.5*s, y + 14*s),
        (x + 23*s, y + 15.5*s),
        (x + 23.5*s, y + 18*s),
        (x + 22*s, y + 21.5*s),
        (x + 18*s, y + 23*s),
        (x + 14*s, y + 22.5*s),
        (x + 11*s, y + 21*s),
    ]
    pygame.draw.polygon(surface, BODY_MID, tail)
    # Tail tip (lighter)
    tail_tip = [
        (x + 22.5*s, y + 16.5*s),
        (x + 23.5*s, y + 18*s),
        (x + 22*s, y + 21.5*s),
        (x + 19*s, y + 23*s),
        (x + 20*s, y + 20.5*s),
        (x + 21.5*s, y + 18.5*s),
    ]
    pygame.draw.polygon(surface, BODY_HIGHLIGHT, tail_tip)

    # --- Body ---
    body = [
        (x + 10*s, y + 9*s),
        (x + 8*s,  y + 13*s),
        (x + 7*s,  y + 18*s),
        (x + 9*s,  y + 22*s),
        (x + 14*s, y + 22*s),
        (x + 16*s, y + 18*s),
        (x + 15*s, y + 13*s),
        (x + 14*s, y + 9*s),
    ]
    pygame.draw.polygon(surface, BODY_DARK, body)

    # Back shadow (darker stripe along the back/right side)
    back_shadow = [
        (x + 14*s, y + 10*s),
        (x + 16*s, y + 18*s),
        (x + 14*s, y + 22*s),
        (x + 13*s, y + 18*s),
        (x + 13.5*s, y + 13*s),
    ]
    pygame.draw.polygon(surface, BODY_DARKEST, back_shadow)

    # Chest/belly highlight
    chest = [
        (x + 9*s,  y + 12*s),
        (x + 8*s,  y + 16*s),
        (x + 9*s,  y + 20*s),
        (x + 11*s, y + 20*s),
        (x + 11*s, y + 15*s),
        (x + 10*s, y + 11*s),
    ]
    pygame.draw.polygon(surface, BODY_MID, chest)

    # --- Head ---
    head = [
        (x + 8*s,  y + 9*s),
        (x + 9*s,  y + 6*s),
        (x + 12*s, y + 7.5*s),
        (x + 15*s, y + 6*s),
        (x + 16*s, y + 9*s),
        (x + 14*s, y + 12*s),
        (x + 10*s, y + 12*s),
    ]
    pygame.draw.polygon(surface, BODY_MID, head)

    # Forehead highlight
    forehead = [
        (x + 10*s, y + 7*s),
        (x + 12*s, y + 8*s),
        (x + 14*s, y + 7*s),
        (x + 12*s, y + 6.5*s),
    ]
    pygame.draw.polygon(surface, BODY_LIGHT, forehead)

    # --- Ears (shorter) ---
    # Left ear outer
    pygame.draw.polygon(surface, BODY_DARK, [
        (x + 8.5*s, y + 7.5*s), (x + 7.5*s, y + 3*s), (x + 11*s, y + 6.5*s)])
    # Left ear inner
    pygame.draw.polygon(surface, BODY_LIGHT, [
        (x + 9*s, y + 7*s), (x + 8.2*s, y + 4.5*s), (x + 10.5*s, y + 6.5*s)])

    # Right ear outer
    pygame.draw.polygon(surface, BODY_DARK, [
        (x + 13*s, y + 6.5*s), (x + 16.5*s, y + 3*s), (x + 15.5*s, y + 7.5*s)])
    # Right ear inner
    pygame.draw.polygon(surface, BODY_LIGHT, [
        (x + 13.5*s, y + 6.5*s), (x + 15.8*s, y + 4.5*s), (x + 15*s, y + 7*s)])

    # --- Face details ---
    # Snout V-shape
    snout = [
        (x + 10*s, y + 8.5*s),
        (x + 12*s, y + 11.5*s),
        (x + 14*s, y + 8.5*s),
        (x + 12*s, y + 9.5*s),
    ]
    pygame.draw.polygon(surface, SNOUT_WHITE, snout)

    # Cheek highlight (left side)
    cheek = [
        (x + 9*s,  y + 9.5*s),
        (x + 10*s, y + 8.5*s),
        (x + 10.5*s, y + 10.5*s),
        (x + 10*s, y + 11.5*s),
    ]
    pygame.draw.polygon(surface, BODY_HIGHLIGHT, cheek)

    # Nose
    pygame.draw.circle(surface, NOSE_COLOR,
                       (int(x + 12*s), int(y + 11*s)), max(1, int(0.7*s)))

    # Eye (with pupil)
    eye_x, eye_y = int(x + 13.5*s), int(y + 8.5*s)
    eye_r = max(1, int(0.9*s))
    pygame.draw.circle(surface, EYE_COLOR, (eye_x, eye_y), eye_r)
    pygame.draw.circle(surface, NOSE_COLOR, (eye_x, eye_y), max(1, int(0.4*s)))

    # --- Laptop (more distinct) ---
    # Laptop screen outer frame
    pygame.draw.polygon(surface, LAPTOP_DARK, [
        (x + 0.5*s, y + 10.5*s), (x + 8.5*s, y + 10.5*s),
        (x + 9*s, y + 18.5*s), (x + 0*s, y + 18.5*s)])
    # Laptop screen bezel
    pygame.draw.polygon(surface, LAPTOP_BEZEL, [
        (x + 1*s, y + 11*s), (x + 8*s, y + 11*s),
        (x + 8.5*s, y + 18*s), (x + 0.5*s, y + 18*s)])
    # Screen background
    pygame.draw.polygon(surface, SCREEN_BG, [
        (x + 1.8*s, y + 12*s), (x + 7.5*s, y + 12*s),
        (x + 7.8*s, y + 17*s), (x + 1.2*s, y + 17*s)])
    # Screen glow/reflection
    pygame.draw.polygon(surface, SCREEN_GLOW, [
        (x + 2*s, y + 12.5*s), (x + 5*s, y + 12.5*s),
        (x + 4.5*s, y + 14.5*s), (x + 2*s, y + 14.5*s)])

    # Laptop base/keyboard
    pygame.draw.polygon(surface, LAPTOP_FRAME, [
        (x - 0.5*s, y + 18.5*s), (x + 9.5*s, y + 18.5*s),
        (x + 10*s, y + 20.5*s), (x - 1*s, y + 20.5*s)])
    # Keyboard detail lines
    pygame.draw.polygon(surface, KEYBOARD_KEYS, [
        (x + 0.5*s, y + 19*s), (x + 9*s, y + 19*s),
        (x + 9.2*s, y + 19.8*s), (x + 0.2*s, y + 19.8*s)])
    # Trackpad hint
    pygame.draw.polygon(surface, LAPTOP_BEZEL, [
        (x + 3.5*s, y + 19.8*s), (x + 6*s, y + 19.8*s),
        (x + 6.2*s, y + 20.3*s), (x + 3.3*s, y + 20.3*s)])

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
        'name': 'Sandbox',
        'description': 'Debug mode - no scoring',
        'color': GREEN,
        'ball_color': GREEN
    }
]

def get_mode_box_rects():
    """Return list of pygame.Rect for each mode selection box (for touch hit-testing)."""
    mode_box_width = 160
    mode_box_height = 70
    mode_spacing = 20
    mode_start_y = MENU_SUBTITLES_Y + MENU_MARGIN_Y * 3
    total_width = len(GAME_MODES) * mode_box_width + (len(GAME_MODES) - 1) * mode_spacing
    start_x = (WIDTH - total_width) // 2
    rects = []
    for i in range(len(GAME_MODES)):
        x = start_x + i * (mode_box_width + mode_spacing)
        rects.append(pygame.Rect(x, mode_start_y, mode_box_width, mode_box_height))
    return rects


def draw_menu(WIN, selected_mode):
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
    mode_box_width = 160
    mode_box_height = 70
    mode_spacing = 20
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

    # Draw logo (image if available, procedural fallback)
    logo_x = 12
    logo_y = HEIGHT - logo_size - 35
    if _logo_image is not None:
        scaled = pygame.transform.smoothscale(_logo_image, (logo_size, logo_size))
        WIN.blit(scaled, (logo_x, logo_y))
    else:
        draw_fox_logo(WIN, logo_x, logo_y, size=logo_size)

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

    # Draw bouncing ball
    ball_menu.draw(WIN)
    ball_menu.bounce_box(WIDTH, HEIGHT)

    pygame.display.update()
