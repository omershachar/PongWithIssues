import pygame
from pong.constants import *
from pong.ball import BallClassic as Ball

ball_menu = Ball(*MIDDLE_BOARD, BALL_RADIUS, WHITE, BALL_DEFAULT_VEL[0], 4)

def draw_menu(WIN, selected_mode):
    WIN.fill(BLACK)

    # Draw ASCII art
    for i, line in enumerate(PONG_ASCII_3D.splitlines()):
        if line.strip() == "": continue
        text_surface = ASCII_FONT.render(line, True, PURPLE)
        WIN.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, MENU_MARGIN_Y + i * 30))

    sub1 = FONT_MEDIUM_DIGITAL.render("A project that probably works. Sometimes. Maybe.", True, LIGHT_PURPLE)
    WIN.blit(sub1, (WIDTH // 2 - sub1.get_width() // 2, MENU_SUBTITLES_Y))

    sub2 = FONT_MEDIUM_DIGITAL.render("It compiles. That's enough.", True, LIGHT_PURPLE)
    WIN.blit(sub2, (WIDTH // 2 - sub2.get_width() // 2, MENU_SUBTITLES_Y + MENU_MARGIN_Y))

    # Show mode selection
    if selected_mode == 0:
        mode_text = FONT_DEFAULT_DIGITAL.render(f"Mode: {'Classic'}", True, LIGHT_PURPLE)
        ball_menu.color = WHITE
    elif selected_mode == 1:
        mode_text = FONT_DEFAULT_DIGITAL.render(f"Mode: {'Pongception'}", True, RED)
        ball_menu.color = RED
    elif selected_mode == 2:
        mode_text = FONT_DEFAULT_DIGITAL.render(f"Mode: {'BETA'}", True, GREY)
        ball_menu.color = DARK_GREY

    WIN.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, MENU_FOOTER - MENU_MARGIN_Y * 2))

    prompt = FONT_DEFAULT_DIGITAL.render("Press [SPACE] to start", True, PURPLE)
    WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, MENU_FOOTER - MENU_MARGIN_Y))

    ball_menu.draw(WIN)
    ball_menu.bounce_box(WIDTH,HEIGHT) # Bouncing ball around the menu window

    pygame.display.update()
