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
from pong.utilities import *
from pong.menu import *

pygame.init()
pygame.display.set_caption("Pong!") # Windows title
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    
def main():
    clock = pygame.time.Clock()
    state = MENU

    # Initializing game the objects
    left_paddle = Paddle(*ORIGINAL_LEFT_PADDLE_POS, *PADDLE_SIZE, LIGHT_PURPLE, PADDLE_DEFAULT_VEL)
    right_paddle = Paddle(*ORIGINAL_RIGHT_PADDLE_POS, *PADDLE_SIZE, LIGHT_PURPLE, PADDLE_DEFAULT_VEL)
    ball = Ball(*MIDDLE_BOARD, BALL_RADIUS, LIGHT_PURPLE, *BALL_DEFAULT_VEL)

    left_score = 0
    right_score = 0

    while True:
        clock.tick(FPS)
        Keys = pygame.key.get_pressed() # Getting the pressed keys of the players
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return
            if state == MENU:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    state = PLAYING

        if state == MENU:
            draw_menu(WIN)
            pygame.display.update()
            continue

        draw(WIN, [left_paddle,right_paddle], ball, left_score, right_score, FONT_LARGE_DIGITAL)
        ball.move()
        handle_ball_collision(ball, left_paddle, right_paddle, HEIGHT)
        handle_paddle_movement(Keys, left_paddle, right_paddle, HEIGHT)

        if state == PLAYING and Keys[pygame.K_m]:
                state = MENU

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
            text = FONT_BIG_DIGITAL.render(win_text, 1, PURPLE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(3000)
            left_score, right_score = reset(ball, left_paddle, right_paddle)
            state = MENU
# End of main()

if __name__ == '__main__':
    main()