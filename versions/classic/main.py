"""
Classic Pong -- Main file containing only essentials and activation commands.
"""
import sys
import os
import asyncio
import pygame

# Add the project root to sys.path so "pong" can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pong.constants import *
from pong.paddle import Paddle
from pong.ball import BallClassic as Ball
from pong.utilities import draw as draw_game, reset, handle_ball_collision
from pong.helpers import handle_paddle_movement
from pong.ai import ai_move_paddle, DIFFICULTY_NAMES
from pong.touch import TouchHandler, draw_touch_buttons

async def main(vs_ai=False, settings=None):
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong!")
    clock = pygame.time.Clock()

    paused = False
    show_instructions = False

    # Apply settings or use defaults
    p_w = settings.paddle_width if settings else PADDLE_SIZE[0]
    p_h = settings.paddle_height if settings else PADDLE_SIZE[1]
    p_speed = settings.paddle_speed if settings else PADDLE_DEFAULT_VEL
    b_radius = settings.ball_radius if settings else BALL_RADIUS
    b_speed = settings.ball_speed if settings else BALL_DEFAULT_VEL[0]
    b_color = LIGHT_PURPLE  # classic always uses this
    l_color = settings.left_paddle_color if settings else LIGHT_PURPLE
    r_color = settings.right_paddle_color if settings else LIGHT_PURPLE
    bg_color = settings.background_color if settings else BLACK
    win_score = settings.winning_score if settings else WINNING_SCORE

    ai_diff = settings.ai_difficulty if settings else 5

    left_paddle = Paddle(ORIGINAL_LEFT_PADDLE_POS[0], ORIGINAL_LEFT_PADDLE_POS[1],
                         p_w, p_h, color=l_color, mode='classic', fixed_vel=p_speed)
    right_paddle = Paddle(ORIGINAL_RIGHT_PADDLE_POS[0], ORIGINAL_RIGHT_PADDLE_POS[1],
                          p_w, p_h, color=r_color, mode='classic', fixed_vel=p_speed)
    ball = Ball(*MIDDLE_BOARD, b_radius, b_color, b_speed, 0)

    touch = TouchHandler(single_player=vs_ai)
    left_score = 0
    right_score = 0

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            touch.handle_event(event)
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    return
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_r:
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    paused = False
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions

        # Touch button actions
        if touch.tapped_menu_btn():
            touch.clear_taps()
            return
        if touch.tapped_pause_btn():
            paused = not paused

        draw_game(WIN, [left_paddle, right_paddle], ball, left_score, right_score, FONT_LARGE_DIGITAL, bg_color)

        # Display "MODE: CLASSIC" at top left
        if vs_ai:
            diff_name = DIFFICULTY_NAMES.get(ai_diff, "")
            mode_label = f"MODE: CLASSIC vs AI ({diff_name})"
        else:
            mode_label = "MODE: CLASSIC"
        mode_text = FONT_SMALL_DIGITAL.render(mode_label, True, GREY)
        WIN.blit(mode_text, (10, 10))

        if paused:
            pause_text = FONT_BIG_DIGITAL.render("PAUSED", True, PURPLE)
            resume_text = FONT_SMALL_DIGITAL.render("Press [SPACE] to resume", True, GREY)
            WIN.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - pause_text.get_height()))
            WIN.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 10))

        # Bottom footer instructions
        if show_instructions:
            footer_text = "Press [SPACE] to pause | [R] to restart | [M] to return | [ESC] to quit | [H] to hide"
        else:
            footer_text = "Press [H] for help"
        footer = FONT_SMALL_DIGITAL.render(footer_text, True, GREY)
        WIN.blit(footer, (GAME_MARGIN_X, GAME_FOOTER[1]))

        draw_touch_buttons(WIN, paused)
        pygame.display.update()

        if not paused:
            handle_paddle_movement(keys, left_paddle, right_paddle, ai_right=vs_ai, touch=touch)
            if vs_ai:
                ai_move_paddle(right_paddle, ball, difficulty=ai_diff)
            left_paddle.update()
            right_paddle.update()

            ball.move()
            handle_ball_collision(ball, left_paddle, right_paddle, HEIGHT)

            # Update score
            if ball.pos[0] - ball.radius < 0:
                right_score += 1
                ball.reset()
            elif ball.pos[0] + ball.radius > WIDTH:
                left_score += 1
                ball.reset()

        if left_score >= win_score or right_score >= win_score:
            right_name = "AI" if vs_ai else "Right Player"
            win_text = "Left Player Won!" if left_score > right_score else f"{right_name} Won!"
            text = FONT_BIG_DIGITAL.render(win_text, True, PURPLE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            await asyncio.sleep(3)
            left_score, right_score = reset(ball, left_paddle, right_paddle)

        touch.clear_taps()
        await asyncio.sleep(0)

if __name__ == '__main__':
    asyncio.run(main())
