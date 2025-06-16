"""
utilities.py -- File for containing all environment and design methods for the game.
"""

import pygame
import numpy as np
from pong.constants import BLACK, DARK_GREY, GREY, LIGHT_GREY, WHITE, WIDTH, HEIGHT, FPS, WINNING_SCORE

# Function for drawing the board
def draw(win, paddles, ball, left_score, right_score, score_font):
    win.fill(BLACK)

    left_score_text = score_font.render(f"{left_score}", 1, WHITE)
    right_score_text = score_font.render(f"{right_score}", 1, WHITE)
    win.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()//2, 20))
    win.blit(right_score_text, (WIDTH * (3/4) - right_score_text.get_width()//2, 20))

    for paddle in paddles:
        paddle.draw(win)

    for i in range(10, HEIGHT-10, HEIGHT//20): # Drawing the net
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, GREY, (WIDTH//2, i, 3, WIDTH//70))
    ball.draw(win)
    pygame.display.update()
