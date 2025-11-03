import pygame
from pong_BETA.constants import WHITE, BLACK, HEIGHT, WIDTH, MAX_DEFLECTION_SPEED, SPIN_FACTOR
import numpy as np

def draw(win, paddles, ball, left_score, right_score, score_font):
    win.fill(BLACK)
    left_text = score_font.render(f"{left_score}", 1, WHITE)
    right_text = score_font.render(f"{right_score}", 1, WHITE)
    win.blit(left_text, (WIDTH // 4 - left_text.get_width() // 2, 20))
    win.blit(right_text, (WIDTH * 3 // 4 - right_text.get_width() // 2, 20))
    for paddle in paddles:
        paddle.draw(win)
    for i in range(10, HEIGHT, HEIGHT // 20):
        if i % 2 == 0:
            pygame.draw.rect(win, WHITE, (WIDTH // 2 - 5, i, 10, HEIGHT // 20))
    ball.draw(win)
    pygame.display.update()