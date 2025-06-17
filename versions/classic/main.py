"""
classicPong.py -- Main file contain only essentials and activation commands.
"""
import sys
import os
import pygame

# Add the project root to sys.path so "pong" can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pong.constants import *
from pong.paddle import PaddleClassic as Paddle
from pong.ball import BallClassic as Ball
from pong.physics_object import handle_ball_collision, handle_paddle_movement
from pong.utilities import draw

MENU = 0
PLAYING = 1

pygame.init()
pygame.display.set_caption("Pong!") # Windows title

SCORE_FONT = FONT_LARGE_DIGITAL
FONT = FONT_DEFAULT_DIGITAL
FONT_BIG = FONT_BIG_DIGITAL
FONT_TITLE = FONT_TITLE_DIGITAL

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

def draw_menu(WIN):
    WIN.fill(BLACK)
    ascii_font = pygame.font.Font("pong/FONTS/LiberationMono-BoldItalic.ttf", 24)
    y_offset = 100

    # Draw ASCII art
    for i, line in enumerate(PONG_ASCII.splitlines()):
        if line.strip() == "": continue
        text_surface = ascii_font.render(line, True, PURPLE)
        WIN.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, y_offset + i * 30))

    subtitle_y = y_offset + 260
    subtitle = FONT.render("A project that probably works. Sometimes. Maybe.", True, LIGHT_PURPLE)
    WIN.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, subtitle_y))

    sub2 = FONT.render("It compiles. That's enough.", True, LIGHT_PURPLE)
    WIN.blit(sub2, (WIDTH // 2 - sub2.get_width() // 2, subtitle_y + 45))

    prompt = FONT.render("Press [SPACE] to start", True, PURPLE)
    WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, subtitle_y + 110))

    pygame.display.update()
    
def main():
    clock = pygame.time.Clock()
    state = MENU

    # Initializing game the objects
    left_paddle = Paddle(ORIGINAL_LEFT_PADDLE_POS[0], ORIGINAL_LEFT_PADDLE_POS[1], PADDLE_WIDTH, PADDLE_HEIGHT, LIGHT_PURPLE, PADDLE_DEFAULT_VEL)
    right_paddle = Paddle(ORIGINAL_RIGHT_PADDLE_POS[0], ORIGINAL_RIGHT_PADDLE_POS[1], PADDLE_WIDTH, PADDLE_HEIGHT, LIGHT_PURPLE, PADDLE_DEFAULT_VEL)
    ball = Ball(MIDDLE_BOARD[0], MIDDLE_BOARD[1], BALL_RADIUS, LIGHT_PURPLE, BALL_DEFAULT_VEL[0], BALL_DEFAULT_VEL[1])

    ball_menu = Ball(MIDDLE_BOARD[0], MIDDLE_BOARD[1], BALL_RADIUS, WHITE, BALL_DEFAULT_VEL[0], 4)

    left_score = 0
    right_score = 0

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return
            if state == MENU:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    pygame.time.delay(300)
                    state = PLAYING

        if state == MENU:
            draw_menu(WIN)
            Keys = pygame.key.get_pressed() # Getting the pressed keys of the players
            ball_menu.draw(WIN)
            ball_menu.bounce_box(WIDTH,HEIGHT) # Bouncing ball around the menu window
            pygame.display.update()
            continue

        Keys = pygame.key.get_pressed() # Getting the pressed keys of the players
        ball.move()
        handle_ball_collision(ball, left_paddle, right_paddle, HEIGHT)
        handle_paddle_movement(Keys, left_paddle, right_paddle, HEIGHT)

        if state == PLAYING and Keys[pygame.K_m]:
                pygame.time.delay(300)
                state = MENU
                    
        draw(WIN, [left_paddle,right_paddle], ball, left_score, right_score, SCORE_FONT)

        # Updating players score
        if ball.pos[0] - ball.radius < 0:
            right_score += 1
            ball.reset()
        elif ball.pos[0] + ball.radius > WIDTH:
            left_score += 1
            ball.reset()

        # Determining winner
        won = False
        if left_score >= WINNING_SCORE:
            won = True
            win_text = "Left Player Won!"
        elif right_score >= WINNING_SCORE:
            won = True
            win_text = "Right Player Won!"
        
        if won:
            text = FONT_BIG.render(win_text, 1, PURPLE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(3000)
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0
            state = MENU
# End of main()

if __name__ == '__main__':
    main()