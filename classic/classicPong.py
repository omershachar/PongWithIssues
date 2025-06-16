"""
classicPong.py -- Main file contain only essentials and activation commands.
"""

import pygame
import numpy as np
from pong.constants import BLACK, DARK_GREY, GREY, LIGHT_GREY, WHITE, WIDTH, HEIGHT, MIDDLE_BOARD, FPS, WINNING_SCORE
from pong.constants import PADDLE_WIDTH, PADDLE_HEIGHT, ORIGINAL_LEFT_PADDLE_POS, ORIGINAL_RIGHT_PADDLE_POS, PADDLE_DEFAULT_VEL
from pong.constants import BALL_RADIUS, BALL_DEFAULT_VEL
from pong.paddle import Paddle
from pong.ball import Ball
from pong.physics import handle_ball_collision, handle_paddle_movement
from pong.utilities import draw

pygame.init()
pygame.display.set_caption("Pong!") # Windows title

SCORE_FONT = pygame.font.SysFont("comicsans", 50)

FPS = 60 # Frame Per Second
WIN = pygame.display.set_mode((WIDTH, HEIGHT))


def main():
    run = True # Endless loop variable
    clock = pygame.time.Clock()

    # Initializing the paddles and the ball on the board
    left_paddle = Paddle(ORIGINAL_LEFT_PADDLE_POS[0], ORIGINAL_LEFT_PADDLE_POS[1], PADDLE_WIDTH, PADDLE_HEIGHT, WHITE, PADDLE_DEFAULT_VEL)
    right_paddle = Paddle(ORIGINAL_RIGHT_PADDLE_POS[0], ORIGINAL_RIGHT_PADDLE_POS[1], PADDLE_WIDTH, PADDLE_HEIGHT, WHITE, PADDLE_DEFAULT_VEL)
    ball = Ball(MIDDLE_BOARD[0], MIDDLE_BOARD[1], BALL_RADIUS, WHITE, BALL_DEFAULT_VEL[0], BALL_DEFAULT_VEL[1])

    left_score = 0
    right_score = 0

    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle,right_paddle], ball, left_score, right_score, SCORE_FONT)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False # Breaking the loop
                break
        Keys = pygame.key.get_pressed() # Getting the pressed keys of the players
        
        ball.move()
        handle_ball_collision(ball, left_paddle, right_paddle, HEIGHT)
        handle_paddle_movement(Keys, left_paddle, right_paddle, HEIGHT)

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
            text = SCORE_FONT.render(win_text, 1, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(3000)
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0
            won = False

    pygame.quit() # Exiting the game
# End of main()

if __name__ == '__main__':
    main()