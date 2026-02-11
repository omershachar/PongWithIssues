"""
Pongception -- Main game loop for PongWithIssues.
Contains only the essentials and high-level orchestration.
"""

import sys
import os
import asyncio
import pygame

# Allow running from subdirectories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pong.constants import *
from pong.paddle import Paddle
from pong.ball import Ball
from pong.utilities import draw, reset
from pong.helpers import handle_ball_collision, handle_paddle_movement
from pong.ai import ai_move_paddle, DIFFICULTY_NAMES
from pong.touch import TouchHandler, draw_touch_buttons
from pong.powerups import PowerUpManager

async def main(vs_ai=False, settings=None):
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pongception")
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

    ai_diff = settings.ai_difficulty if settings else 5

    left_paddle = Paddle(ORIGINAL_LEFT_PADDLE_POS[0], ORIGINAL_LEFT_PADDLE_POS[1],
                         p_w, p_h, color=l_color, mode='physics', fixed_vel=p_speed)
    right_paddle = Paddle(ORIGINAL_RIGHT_PADDLE_POS[0], ORIGINAL_RIGHT_PADDLE_POS[1],
                          p_w, p_h, color=r_color, mode='physics', fixed_vel=p_speed)
    ball = Ball(*MIDDLE_BOARD, b_radius, YELLOW, vel=(b_speed, 0))

    touch = TouchHandler(single_player=vs_ai)
    left_score = 0
    right_score = 0

    # Power-ups
    power_ups_on = settings.power_ups_enabled if settings else False
    pu_mgr = PowerUpManager(left_paddle, right_paddle) if power_ups_on else None

    while run:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score, FONT_LARGE_DIGITAL, bg_color)

        # Draw power-ups and extra balls (between base render and UI overlay)
        if pu_mgr:
            pu_mgr.draw(WIN)
            pu_mgr.draw_extra_balls(WIN)

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
        if vs_ai:
            diff_name = DIFFICULTY_NAMES.get(ai_diff, "")
            mode_label = f"MODE: PHYSICS vs AI ({diff_name})"
        else:
            mode_label = "MODE: PHYSICS"
        mode_text = FONT_SMALL_DIGITAL.render(mode_label, True, GREY)
        WIN.blit(mode_text, (10, 10))

        # Bottom footer instructions
        if show_instructions:
                footer_text = "Press [SPACE] to pause | [R] to restart | [M] to return | [ESC] to quit | [H] to hide"
        else:
            footer_text = "Press [H] for help"
        footer = FONT_SMALL_DIGITAL.render(footer_text, True, GREY)
        WIN.blit(footer, (GAME_MARGIN_X, GAME_FOOTER[1]))

        draw_touch_buttons(WIN, paused)
        pygame.display.update()

        for event in pygame.event.get():
            touch.handle_event(event)
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
                    if pu_mgr: pu_mgr.reset()
                    paused = False
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions

        # Touch button actions
        if touch.tapped_menu_btn():
            touch.clear_taps()
            run = False
            continue
        if touch.tapped_pause_btn():
            paused = not paused

        keys = pygame.key.get_pressed()
        if not paused:
            # Freeze guard: save positions for frozen paddles
            if pu_mgr:
                frozen_l = pu_mgr.is_frozen(left_paddle)
                frozen_r = pu_mgr.is_frozen(right_paddle)
                if frozen_l: saved_l = left_paddle.pos.copy()
                if frozen_r: saved_r = right_paddle.pos.copy()
            else:
                frozen_l = frozen_r = False

            handle_paddle_movement(keys, left_paddle, right_paddle, ai_right=vs_ai, touch=touch)
            if vs_ai:
                ai_move_paddle(right_paddle, ball, difficulty=ai_diff)

            # Enforce freeze: restore position, zero velocity
            if frozen_l:
                left_paddle.pos[:] = saved_l
                left_paddle.vel[:] = 0
            if frozen_r:
                right_paddle.pos[:] = saved_r
                right_paddle.vel[:] = 0

            left_paddle.update()
            right_paddle.update()
            ball.update()

            old_vx = ball.vel[0]
            handle_ball_collision(ball, left_paddle, right_paddle)
            # Track last paddle hit for power-up attribution
            if pu_mgr:
                if old_vx < 0 and ball.vel[0] > 0:
                    pu_mgr.set_last_hit('left')
                elif old_vx > 0 and ball.vel[0] < 0:
                    pu_mgr.set_last_hit('right')

            # Extra balls physics
            if pu_mgr:
                for eb in pu_mgr.extra_balls:
                    eb.update()
                    handle_ball_collision(eb, left_paddle, right_paddle)
                pu_mgr.update(ball)
                pu_mgr.create_extra_balls(ball, mode='physics')

            # Scoring
            if pu_mgr and (pu_mgr.extra_balls or pu_mgr.main_ball_parked):
                # Multi-ball active: park main if it exits, wait for all
                if not pu_mgr.main_ball_parked:
                    if ball.pos[0] < 0:
                        pu_mgr.park_main_ball(ball, 'left')
                    elif ball.pos[0] > WIDTH:
                        pu_mgr.park_main_ball(ball, 'right')
                # Remove exited extra balls
                pu_mgr.extra_balls = [
                    eb for eb in pu_mgr.extra_balls
                    if -eb.radius <= eb.pos[0] <= WIDTH + eb.radius
                ]
                result = pu_mgr.check_multiball_done()
                if result == 'right_scores':
                    right_score += 1
                    ball.reset()
                    pu_mgr.reset()
                elif result == 'left_scores':
                    left_score += 1
                    ball.reset()
                    pu_mgr.reset()
            else:
                # Normal scoring
                if ball.pos[0] < 0:
                    right_score += 1
                    ball.reset()
                    if pu_mgr: pu_mgr.reset()
                elif ball.pos[0] > WIDTH:
                    left_score += 1
                    ball.reset()
                    if pu_mgr: pu_mgr.reset()

        if left_score >= win_score or right_score >= win_score:
            right_name = "AI" if vs_ai else "Right Player"
            winner = "Left Player Won!" if left_score > right_score else f"{right_name} Won!"
            text = FONT_BIG_DIGITAL.render(winner, True, PURPLE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            await asyncio.sleep(3)

            left_score, right_score = reset(ball, left_paddle, right_paddle)
            if pu_mgr: pu_mgr.reset()

        touch.clear_taps()
        await asyncio.sleep(0)
    return

if __name__ == '__main__':
    asyncio.run(main())
