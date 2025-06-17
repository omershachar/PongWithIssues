"""
classicPong.py -- Main file contain only essentials and activation commands.
"""
import sys
import os
import pygame

# Add the project root to sys.path so "pong" can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pong.constants import BLACK, WHITE, LIGHT_GREY, PURPLE, LIGHT_PURPLE, WIDTH, HEIGHT, MIDDLE_BOARD, FPS, WINNING_SCORE
from pong.constants import PADDLE_WIDTH, PADDLE_HEIGHT, ORIGINAL_LEFT_PADDLE_POS, ORIGINAL_RIGHT_PADDLE_POS, PADDLE_DEFAULT_VEL
from pong.constants import BALL_RADIUS, BALL_DEFAULT_VEL
from pong.paddle_classic import Paddle
from pong.ball_classic import Ball
from pong.physics_classic import handle_ball_collision, handle_paddle_movement
from pong.utilities_classic import draw

MENU = 0
PLAYING = 1

pygame.init()
pygame.display.set_caption("Pong!") # Windows title

SCORE_FONT = pygame.font.SysFont("comicsans", 50)
SMALL_FONT = pygame.font.SysFont("comicsans", 40)
TITLE_FONT = pygame.font.SysFont("comicsans", 90)
FPS = 60 # Frame Per Second
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

def draw_menu(WIN):
    WIN.fill(BLACK)
    title = TITLE_FONT.render("PONG!", True, PURPLE)
    WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))

    subtitle = SMALL_FONT.render("A project that probably works. Sometimes. Maybe", True, LIGHT_PURPLE)
    WIN.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 3 + 90))
    sub2 = SMALL_FONT.render("It compiles. That's enough.", True, LIGHT_PURPLE)
    WIN.blit(sub2, (WIDTH // 2 - sub2.get_width() // 2, HEIGHT // 3 + 135))

    prompt = SMALL_FONT.render("Press [SPACE] to start", True, PURPLE)
    WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 120))
    pygame.display.update()

def main():
    # run = True # Endless loop variable
    clock = pygame.time.Clock()
    state = MENU

    # Initializing game the objects
    left_paddle = Paddle(ORIGINAL_LEFT_PADDLE_POS[0], ORIGINAL_LEFT_PADDLE_POS[1], PADDLE_WIDTH, PADDLE_HEIGHT, LIGHT_PURPLE, PADDLE_DEFAULT_VEL)
    right_paddle = Paddle(ORIGINAL_RIGHT_PADDLE_POS[0], ORIGINAL_RIGHT_PADDLE_POS[1], PADDLE_WIDTH, PADDLE_HEIGHT, LIGHT_PURPLE, PADDLE_DEFAULT_VEL)
    ball = Ball(MIDDLE_BOARD[0], MIDDLE_BOARD[1], BALL_RADIUS, LIGHT_PURPLE, BALL_DEFAULT_VEL[0], BALL_DEFAULT_VEL[1])

    ball2 = Ball(MIDDLE_BOARD[0], MIDDLE_BOARD[1], BALL_RADIUS, WHITE, BALL_DEFAULT_VEL[0], 4)

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
            ball2.draw(WIN)
            ball2.move()
            # handle_ball_collision(ball2, left_paddle, right_paddle, HEIGHT)
            ball2.bounce_box(WIDTH,HEIGHT)
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
            text = SCORE_FONT.render(win_text, 1, PURPLE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(3000)
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0
            state = MENU

        # if 
# End of main()

if __name__ == '__main__':
    main()