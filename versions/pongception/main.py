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
from pong.utilities import draw, reset
from pong.helpers import handle_ball_collision, handle_paddle_movement

# pygame setup
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pongception")

def main():
    clock = pygame.time.Clock()
    run = True
    paused = False
    show_instructions = True

    left_paddle = Paddle(*ORIGINAL_LEFT_PADDLE_POS, *PADDLE_SIZE)
    right_paddle = Paddle(*ORIGINAL_RIGHT_PADDLE_POS, *PADDLE_SIZE)
    ball = Ball(*MIDDLE_BOARD, BALL_RADIUS, YELLOW, vel=BALL_DEFAULT_VEL)

    left_score = 0
    right_score = 0

    while run:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score, FONT_LARGE_DIGITAL)

        debug_font = pygame.font.SysFont("consolas", 20)
        vel_text = debug_font.render(f"Velocity: [{ball.vel[0]:.2f}, {ball.vel[1]:.2f}]", True, GREY)
        spin_text = debug_font.render(f"Spin: {getattr(ball, 'spin', 0):.2f}", True, GREY)

        WIN.blit(vel_text, (10, 60))
        WIN.blit(spin_text, (10, 85))

        if paused:
            pause_text = FONT_BIG_DIGITAL.render("PAUSED", True, PURPLE)
            resume_text = FONT_SMALL_DIGITAL.render("Press [SPACE] to resume", True, GREY)
            WIN.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - pause_text.get_height()))
            WIN.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 10))

        # Top-left mode label
        mode_text = FONT_SMALL_DIGITAL.render("MODE: PHYSICS", True, GREY)
        WIN.blit(mode_text, (10, 10))

        # Bottom footer instructions
        if show_instructions:
            footer_text = "Press [SPACE] to pause | [R] to restart | [M] to return | [ESC] to quit | [H] to hide"
        else:
            footer_text = "Press [H] to show instructions"
        footer = FONT_SMALL_DIGITAL.render(footer_text, True, GREY)
        WIN.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 30))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    break
                if event.key == pygame.K_m:
                    run = False
                    break
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_r: # Fix through utilities
                    left_score = right_score = 0
                    left_paddle.reset()
                    right_paddle.reset()
                    ball.reset()
                    paused = False
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions

        keys = pygame.key.get_pressed()
        if not paused:
            handle_paddle_movement(keys, left_paddle,
             right_paddle)

            left_paddle.update()
            right_paddle.update()
            ball.update()

            handle_ball_collision(ball, left_paddle, right_paddle)

            if ball.pos[0] < 0:
                right_score += 1
                ball.reset()
            elif ball.pos[0] > WIDTH:
                left_score += 1
                ball.reset()

        if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
            winner = "Left Player Won!" if left_score > right_score else "Right Player Won!"
            text = FONT_BIG_DIGITAL.render(winner, True, PURPLE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(3000)

            left_score, right_score = reset(ball, left_paddle, right_paddle)
    return

if __name__ == '__main__':
    main()
