import pygame
import os
from pong.constants import *
from pong.ball import Ball

ball_menu = Ball(*MIDDLE_BOARD, BALL_RADIUS, WHITE, mode='classic', vel=(BALL_DEFAULT_VEL[0], 4))

# Developer info
DEVELOPER = "omershachar"
GITHUB_URL = "github.com/omershachar/PongWithIssues"
VERSION = "v1.0.0"

# Try to load fox logo if it exists
FOX_LOGO = None
_fox_paths = [
    os.path.join(os.path.dirname(__file__), '..', 'assets', 'fox.png'),
    os.path.join(os.path.dirname(__file__), '..', 'assets', 'fox_logo.png'),
]
for _path in _fox_paths:
    if os.path.exists(_path):
        try:
            FOX_LOGO = pygame.image.load(_path)
            FOX_LOGO = pygame.transform.scale(FOX_LOGO, (24, 24))
            break
        except pygame.error:
            pass

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
    nav_text = FONT_TINY_DIGITAL.render("[LEFT/RIGHT] Select mode", True, DARK_GREY)
    WIN.blit(nav_text, (WIDTH // 2 - nav_text.get_width() // 2, mode_start_y + mode_box_height + 20))

    # Start prompt
    prompt = FONT_DEFAULT_DIGITAL.render("Press [SPACE] to start", True, PURPLE)
    WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, MENU_FOOTER - MENU_MARGIN_Y))

    # Credits footer
    credits_y = HEIGHT - 30
    credits_text = FONT_TINY_DIGITAL.render(f"{VERSION} | {GITHUB_URL}", True, DARK_GREY)
    credits_x = WIDTH - credits_text.get_width() - 10

    # Draw fox logo if available
    if FOX_LOGO:
        WIN.blit(FOX_LOGO, (credits_x - 30, credits_y - 4))
        credits_x -= 30

    WIN.blit(credits_text, (credits_x, credits_y))

    # Draw bouncing ball
    ball_menu.draw(WIN)
    ball_menu.bounce_box(WIDTH, HEIGHT)

    pygame.display.update()
