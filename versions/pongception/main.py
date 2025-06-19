"""
pongception.py -- Main game loop for PongWithIssues.
Contains only the essentials and high-level orchestration.
"""

import sys
import os
import pygame

# Allow running from subdirectories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pong.constants import *
from pong.paddle import Paddle
from pong.ball import Ball
from pong.utilities import draw
from pong.helpers import handle_ball_collision, handle_paddle_movement

# pygame setup
pygame.init()
SCORE_FONT = pygame.font.SysFont("comicsans", 50)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pongception")

def main():
    """
    Main game loop. Handles object initialization, input, updates, collisions,
    rendering, scoring, and win condition.
    """
    clock = pygame.time.Clock()
    run = True

    # Initialize game objects
    left_paddle = Paddle(*ORIGINAL_LEFT_PADDLE_POS, *PADDLE_SIZE)
    right_paddle = Paddle(*ORIGINAL_RIGHT_PADDLE_POS, *PADDLE_SIZE)
    ball = Ball(*MIDDLE_BOARD, BALL_RADIUS, YELLOW, vel=BALL_DEFAULT_VEL)

    left_score = 0
    right_score = 0

    while run:
        dt = clock.tick(FPS) / 1000.0  # delta time in seconds

        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score, SCORE_FONT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)

        # Update objects
        left_paddle.update()
        right_paddle.update()
        ball.update()

        # Handle collisions
        handle_ball_collision(ball, left_paddle, right_paddle)

        # Scoring logic
        if ball.pos[0] < 0:
            right_score += 1
            ball.reset()
        elif ball.pos[0] > WIDTH:
            left_score += 1
            ball.reset()

        # Check for winner
        if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
            winner = "Left Player Won!" if left_score > right_score else "Right Player Won!"
            text = SCORE_FONT.render(winner, True, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(4000)

            # Reset game state
            left_score = right_score = 0
            left_paddle.reset()
            right_paddle.reset()
            ball.reset()

    pygame.quit()

if __name__ == '__main__':
    main()
