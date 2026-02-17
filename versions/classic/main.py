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
from pong.touch import TouchHandler, draw_touch_buttons, draw_touch_zones
from pong.powerups import PowerUpManager
from pong import audio
from pong.juice import JuiceManager
from pong.game_flow import countdown, PauseMenu, WinScreen, confirm_exit

async def main(vs_ai=False, settings=None):
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong!")
    clock = pygame.time.Clock()

    # Initialize audio
    audio.init()

    paused = False
    show_instructions = False
    game_started = False  # For countdown

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

    # Power-ups
    power_ups_on = settings.power_ups_enabled if settings else False
    pu_mgr = PowerUpManager(left_paddle, right_paddle) if power_ups_on else None

    # Juice (visual effects) — respects settings
    juice = JuiceManager(settings)

    # Pause menu & win screen
    pause_menu = PauseMenu()
    win_screen = WinScreen()

    # Mode label
    if vs_ai:
        diff_name = DIFFICULTY_NAMES.get(ai_diff, "")
        mode_label = f"MODE: CLASSIC vs AI ({diff_name})"
    else:
        mode_label = "MODE: CLASSIC"

    def draw_full_scene():
        """Draw the complete game scene (used by countdown/pause as background)."""
        sx, sy = juice.shake.get_offset()
        draw_game(WIN, [left_paddle, right_paddle], ball, left_score, right_score, FONT_SCORE_GAME, bg_color, offset=(sx, sy))
        if pu_mgr:
            pu_mgr.draw(WIN)
            pu_mgr.draw_extra_balls(WIN)
        mode_text = FONT_MODE_GAME.render(mode_label, True, GREY)
        WIN.blit(mode_text, (10, 10))
        juice.draw(WIN)

    # Initial countdown
    result = await countdown(WIN, draw_full_scene)
    if result == 'quit':
        return
    game_started = True

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            touch.handle_event(event)
            if event.type == pygame.QUIT:
                return

            if paused:
                action = pause_menu.handle_event(event, touch)
                if action == 'resume':
                    paused = False
                elif action == 'restart':
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    if pu_mgr: pu_mgr.reset()
                    paused = False
                    result = await countdown(WIN, draw_full_scene)
                    if result == 'quit': return
                elif action == 'menu':
                    return
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    should_exit = await confirm_exit(WIN, draw_full_scene, touch)
                    if should_exit:
                        return
                if event.key == pygame.K_SPACE:
                    paused = True
                if event.key == pygame.K_r:
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    if pu_mgr: pu_mgr.reset()
                    result = await countdown(WIN, draw_full_scene)
                    if result == 'quit': return
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions

        # Touch button actions
        if not paused:
            if touch.tapped_menu_btn():
                should_exit = await confirm_exit(WIN, draw_full_scene, touch)
                touch.clear_taps()
                if should_exit:
                    return
            if touch.tapped_pause_btn():
                paused = True

        # Touch pause menu handling
        if paused:
            action = pause_menu.handle_touch(touch)
            if action == 'resume':
                paused = False
            elif action == 'restart':
                left_score, right_score = reset(ball, left_paddle, right_paddle)
                if pu_mgr: pu_mgr.reset()
                paused = False
                touch.clear_taps()
                result = await countdown(WIN, draw_full_scene)
                if result == 'quit': return
            elif action == 'menu':
                return

        # Update juice effects
        juice.update()

        # Draw scene
        draw_full_scene()

        if paused:
            pause_menu.draw(WIN)

        # Bottom footer instructions
        if show_instructions:
            footer_text = "Press [SPACE] to pause | [R] to restart | [M] to return | [ESC] to quit | [H] to hide"
        else:
            footer_text = "Press [H] for help"
        footer = FONT_SMALL_DIGITAL.render(footer_text, True, GREY)
        WIN.blit(footer, (GAME_MARGIN_X, GAME_FOOTER[1]))

        draw_touch_zones(WIN, touch)
        touch.update_ripples()
        touch.draw_ripples(WIN)
        draw_touch_buttons(WIN, paused)
        pygame.display.update()

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

            ball.move()

            old_vx = ball.vel[0]
            old_vy = ball.vel[1]
            handle_ball_collision(ball, left_paddle, right_paddle, HEIGHT)

            # Wall bounce detection — check if vy flipped sign
            if old_vy != 0 and (old_vy > 0) != (ball.vel[1] > 0):
                audio.play('wall_bounce')
                wall_y = ball.radius if ball.pos[1] <= HEIGHT // 2 else HEIGHT - ball.radius
                juice.on_wall_bounce(ball.pos[0], wall_y)

            # Detect paddle hit — check if vx flipped sign
            if old_vx < 0 and ball.vel[0] > 0:
                audio.play('paddle_hit')
                juice.on_paddle_hit(left_paddle.pos[0] + left_paddle.width, ball.pos[1], l_color)
                if pu_mgr: pu_mgr.set_last_hit('left')
            elif old_vx > 0 and ball.vel[0] < 0:
                audio.play('paddle_hit')
                juice.on_paddle_hit(right_paddle.pos[0], ball.pos[1], r_color)
                if pu_mgr: pu_mgr.set_last_hit('right')

            # Extra balls physics
            if pu_mgr:
                for eb in pu_mgr.extra_balls:
                    eb.move()
                    handle_ball_collision(eb, left_paddle, right_paddle, HEIGHT)
                pu_mgr.update(ball)
                pu_mgr.create_extra_balls(ball, mode='classic')

            # Scoring
            scored = False
            if pu_mgr and (pu_mgr.extra_balls or pu_mgr.main_ball_parked):
                # Multi-ball active
                if not pu_mgr.main_ball_parked:
                    if ball.pos[0] - ball.radius < 0:
                        pu_mgr.park_main_ball(ball, 'left')
                    elif ball.pos[0] + ball.radius > WIDTH:
                        pu_mgr.park_main_ball(ball, 'right')
                pu_mgr.extra_balls = [
                    eb for eb in pu_mgr.extra_balls
                    if -eb.radius <= eb.pos[0] <= WIDTH + eb.radius
                ]
                result = pu_mgr.check_multiball_done()
                if result == 'right_scores':
                    right_score += 1
                    scored = True
                    ball.reset()
                    pu_mgr.reset()
                elif result == 'left_scores':
                    left_score += 1
                    scored = True
                    ball.reset()
                    pu_mgr.reset()
            else:
                # Normal scoring
                if ball.pos[0] - ball.radius < 0:
                    right_score += 1
                    scored = True
                    ball.reset()
                    if pu_mgr: pu_mgr.reset()
                elif ball.pos[0] + ball.radius > WIDTH:
                    left_score += 1
                    scored = True
                    ball.reset()
                    if pu_mgr: pu_mgr.reset()

            if scored:
                audio.play('score')
                # Score pop on the side that scored
                if left_score > right_score or (left_score == right_score and ball.vel[0] > 0):
                    juice.on_score(WIDTH // 4, 20 + 25, str(left_score), FONT_SCORE_GAME, LIGHT_PURPLE)
                else:
                    juice.on_score(WIDTH * 3 // 4, 20 + 25, str(right_score), FONT_SCORE_GAME, LIGHT_PURPLE)

        # Win condition
        if left_score >= win_score or right_score >= win_score:
            right_name = "AI" if vs_ai else "Right Player"
            winner = "Left Player Won!" if left_score > right_score else f"{right_name} Won!"

            if left_score > right_score:
                audio.play('win')
            else:
                audio.play('lose') if vs_ai else audio.play('win')

            # Interactive win screen — save final scores before potential reset
            final_left, final_right = left_score, right_score
            win_screen.selected = 0
            choosing = True
            while choosing:
                clock.tick(FPS)
                for event in pygame.event.get():
                    touch.handle_event(event)
                    if event.type == pygame.QUIT:
                        return
                    action = win_screen.handle_event(event)
                    if action == 'play_again':
                        left_score, right_score = reset(ball, left_paddle, right_paddle)
                        if pu_mgr: pu_mgr.reset()
                        choosing = False
                    elif action == 'menu':
                        return

                # Touch handling for win screen
                action = win_screen.handle_touch(touch)
                if action == 'play_again':
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    if pu_mgr: pu_mgr.reset()
                    choosing = False
                elif action == 'menu':
                    return

                draw_full_scene()
                win_screen.draw(WIN, winner, final_left, final_right)
                draw_touch_buttons(WIN, False)
                pygame.display.update()
                touch.clear_taps()
                await asyncio.sleep(0)

            # Countdown before next match
            result = await countdown(WIN, draw_full_scene)
            if result == 'quit': return

        touch.clear_taps()
        await asyncio.sleep(0)

if __name__ == '__main__':
    asyncio.run(main())
