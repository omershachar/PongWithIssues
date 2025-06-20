import pygame
from pong.constants import *
from pong.ball import BallClassic as Ball

def draw(self, win):
    pygame.draw.circle(win, self.color, (int(self.x), int(self.y)), self.radius)


ball_menu = Ball(*MIDDLE_BOARD, BALL_RADIUS, WHITE, BALL_DEFAULT_VEL[0], 4)

def draw_menu(WIN, selected_mode):
    WIN.fill(BLACK)
    ascii_font = pygame.font.Font("pong/FONTS/LiberationMono-BoldItalic.ttf", 24)
    y_offset = 100


    # Show mode selection
    subtitle_y = y_offset + 260
    mode_text = FONT_DEFAULT_DIGITAL.render(f"Mode: {'Classic' if selected_mode == 0 else 'Physics'}", True, WHITE)
    WIN.blit(mode_text, (WIDTH // 2 - mode_text.get_width() // 2, subtitle_y + 80))

    # Draw ASCII art
    for i, line in enumerate(PONG_ASCII.splitlines()):
        if line.strip() == "": continue
        text_surface = ascii_font.render(line, True, PURPLE)
        WIN.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset + i * 30))

    subtitle = FONT_DEFAULT_DIGITAL.render("A project that probably works. Sometimes. Maybe.", True, LIGHT_PURPLE)
    WIN.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, subtitle_y))

    sub2 = FONT_DEFAULT_DIGITAL.render("It compiles. That's enough.", True, LIGHT_PURPLE)
    WIN.blit(sub2, (WIDTH // 2 - sub2.get_width() // 2, subtitle_y + 45))

    prompt = FONT_DEFAULT_DIGITAL.render("Press [SPACE] to start", True, PURPLE)
    WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, subtitle_y + 110))

    ball_menu.draw(WIN)
    ball_menu.bounce_box(WIDTH,HEIGHT) # Bouncing ball around the menu window

    pygame.display.update()
