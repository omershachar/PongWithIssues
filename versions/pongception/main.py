"""
Pongception -- Main game loop for PongWithIssues.
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
from pong.utilities import draw, reset, handle_score
from pong.helpers import handle_ball_collision, handle_paddle_movement
from pong.ai import ai_move_paddle

# pygame setup
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pongception")

def main(vs_ai=False, settings=None):
    clock = pygame.time.Clock()
    run = True
    paused = False
    show_instructions = False

    # Apply settings or use defaults
    p_w = settings.paddle_width if settings else PADDLE_SIZE[0]
    p_h = settings.paddle_height if settings else PADDLE_SIZE[1]
    p_speed = settings.paddle_speed if settings else PADDLE_DEFAULT_VEL
    b_radius = settings.ball_radius if settings else BALL_RADIUS
    b_speed = settings.ball_speed if settings else BALL_DEFAULT_VEL[0]
    l_color = settings.left_paddle_color if settings else LIGHT_PURPLE
    r_color = settings.right_paddle_color if settings else LIGHT_PURPLE
    bg_color = settings.background_color if settings else BLACK
    win_score = settings.winning_score if settings else WINNING_SCORE

    left_paddle = Paddle(ORIGINAL_LEFT_PADDLE_POS[0], ORIGINAL_LEFT_PADDLE_POS[1],
                         p_w, p_h, color=l_color, mode='physics', fixed_vel=p_speed)
    right_paddle = Paddle(ORIGINAL_RIGHT_PADDLE_POS[0], ORIGINAL_RIGHT_PADDLE_POS[1],
                          p_w, p_h, color=r_color, mode='physics', fixed_vel=p_speed)
    ball = Ball(*MIDDLE_BOARD, b_radius, YELLOW, vel=(b_speed, 0))

    left_score = 0
    right_score = 0

    while run:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score, FONT_LARGE_DIGITAL, bg_color)

        debug_font = pygame.font.SysFont(*FONT_DATA)
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
        mode_label = "MODE: PHYSICS vs AI" if vs_ai else "MODE: PHYSICS"
        mode_text = FONT_SMALL_DIGITAL.render(mode_label, True, GREY)
        WIN.blit(mode_text, (10, 10))

        # Bottom footer instructions
        if show_instructions:
                footer_text = "Press [SPACE] to pause | [R] to restart | [M] to return | [ESC] to quit | [H] to hide"
        else:
            footer_text = "Press [H] for help"
        footer = FONT_SMALL_DIGITAL.render(footer_text, True, GREY)
        WIN.blit(footer, (GAME_MARGIN_X, GAME_FOOTER[1]))

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
                if event.key == pygame.K_r:
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    paused = False
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions

        keys = pygame.key.get_pressed()
        if not paused:
            handle_paddle_movement(keys, left_paddle, right_paddle, ai_right=vs_ai)
            if vs_ai:
                ai_move_paddle(right_paddle, ball)

            left_paddle.update()
            right_paddle.update()
            ball.update()

            handle_ball_collision(ball, left_paddle, right_paddle)
            left_score, right_score = handle_score(ball, left_score, right_score)

        if left_score >= win_score or right_score >= win_score:
            right_name = "AI" if vs_ai else "Right Player"
            winner = "Left Player Won!" if left_score > right_score else f"{right_name} Won!"
            text = FONT_BIG_DIGITAL.render(winner, True, PURPLE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(3000)

            left_score, right_score = reset(ball, left_paddle, right_paddle)
    return

if __name__ == '__main__':
    main()
