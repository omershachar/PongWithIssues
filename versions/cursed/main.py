"""
Cursed Pong -- INSANE sword-fighting chaos mode.

Physics paddles with full board movement, ball & paddle grabbing,
directional sword combat with gore, and optional random cursed events.

Controls:
  Left:  WASD = move + aim sword, E = grab/release
  Right: Arrows = move + aim sword, RSHIFT = grab/release
  Sword swings where you point. 3 hits to kill!
"""
import sys
import os
import asyncio
import pygame
import numpy as np
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pong.constants import *
from pong.paddle import Paddle
from pong.ball import Ball
from pong.utilities import draw as draw_game, reset
from pong.helpers import handle_ball_collision_cursed, handle_paddle_movement_cursed
from pong.ai import ai_move_paddle, DIFFICULTY_NAMES
from pong.touch import TouchHandler, draw_touch_buttons, draw_touch_zones
from pong.powerups import PowerUpManager
from pong import audio
from pong.juice import JuiceManager
from pong.game_flow import countdown, PauseMenu, WinScreen, confirm_exit
from pong.cursed import CursedEventManager
from pong.cursed_combat import CursedCombatManager

BALL_FRICTION = 0.997  # Ball slows down faster for easier catching


async def main(vs_ai=False, settings=None):
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CURSED Pong!")
    clock = pygame.time.Clock()

    audio.init()

    paused = False
    show_instructions = False

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
    cursed_events_on = getattr(settings, 'cursed_events_enabled', True) if settings else True

    # Physics-mode paddles with full board access
    left_paddle = Paddle(ORIGINAL_LEFT_PADDLE_POS[0], ORIGINAL_LEFT_PADDLE_POS[1],
                         p_w, p_h, color=l_color, mode='physics', fixed_vel=p_speed)
    right_paddle = Paddle(ORIGINAL_RIGHT_PADDLE_POS[0], ORIGINAL_RIGHT_PADDLE_POS[1],
                          p_w, p_h, color=r_color, mode='physics', fixed_vel=p_speed)

    ball = Ball(*MIDDLE_BOARD, b_radius, (255, 50, 200), mass=1,
                vel=(b_speed, 0), mode='physics')

    touch = TouchHandler(single_player=vs_ai)
    left_score = 0
    right_score = 0

    power_ups_on = settings.power_ups_enabled if settings else False
    pu_mgr = PowerUpManager(left_paddle, right_paddle) if power_ups_on else None
    juice = JuiceManager(settings)
    cursed = CursedEventManager() if cursed_events_on else None
    combat = CursedCombatManager()

    pause_menu = PauseMenu()
    win_screen = WinScreen()

    orig_p_h = p_h

    events_label = " [Events ON]" if cursed_events_on else ""
    if vs_ai:
        diff_name = DIFFICULTY_NAMES.get(ai_diff, "")
        mode_label = f"CURSED vs AI ({diff_name}){events_label}"
    else:
        mode_label = f"CURSED{events_label}"

    def draw_full_scene():
        sx, sy = juice.shake.get_offset()
        if cursed and cursed.has_event('SCREEN FLIP'):
            temp = pygame.Surface((WIDTH, HEIGHT))
            _draw_scene_to(temp, sx, sy)
            flipped = pygame.transform.flip(temp, False, True)
            WIN.blit(flipped, (0, 0))
        else:
            _draw_scene_to(WIN, sx, sy)

    def _draw_scene_to(target, sx, sy):
        use_font = FONT_SCORE_GAME
        hide_ball = False
        if cursed:
            use_font = cursed.get_font(FONT_SCORE_GAME)
            hide_ball = cursed.has_event('INVISIBLE BALL')

        # Don't draw cut paddles through normal draw — combat manager draws them
        paddles_to_draw = []
        if not combat.left_cut:
            paddles_to_draw.append(left_paddle)
        if not combat.right_cut:
            paddles_to_draw.append(right_paddle)

        draw_game(target, paddles_to_draw, ball, left_score, right_score,
                  use_font, bg_color, offset=(sx, sy),
                  hide_ball=(hide_ball or combat.ball_grabbed_by is not None))

        if pu_mgr:
            pu_mgr.draw(target)
            pu_mgr.draw_extra_balls(target)

        # Combat visuals (blood, swords, cut paddles, grab indicators)
        combat.draw(target, left_paddle, right_paddle)

        # Draw grabbed ball on top of paddle
        if combat.ball_grabbed_by and not hide_ball:
            ball.draw(target)

        # Speed & status HUD
        ball_speed = np.linalg.norm(ball.vel)
        lp_speed = np.linalg.norm(left_paddle.vel)
        rp_speed = np.linalg.norm(right_paddle.vel)
        hud = FONT_TINY_DIGITAL.render(
            f"Ball:{ball_speed:.0f} L:{lp_speed:.1f} R:{rp_speed:.1f}", True, GREY)
        target.blit(hud, (10, 55))

        mode_text = FONT_MODE_GAME.render(mode_label, True, GREY)
        target.blit(mode_text, (10, 10))

        # Controls hint
        ctrl_text = FONT_TINY_DIGITAL.render(
            "L:[WASD]=move+sword E=grab  R:[Arrows]=move+sword RShift=grab  3 hits to kill!",
            True, DARK_GREY)
        target.blit(ctrl_text, (10, 35))

        juice.draw(target)
        if cursed:
            cursed.draw_active_bar(target)
            cursed.draw_announcements(target)

    # Initial countdown
    result = await countdown(WIN, draw_full_scene)
    if result == 'quit':
        return

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
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                        cursed.reset()
                    combat.reset()
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    if pu_mgr: pu_mgr.reset()
                    paused = False
                    result = await countdown(WIN, draw_full_scene)
                    if result == 'quit': return
                elif action == 'menu':
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                    return
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    should_exit = await confirm_exit(WIN, draw_full_scene, touch)
                    if should_exit:
                        if cursed:
                            cursed.reset_paddles(left_paddle, right_paddle)
                        return
                if event.key == pygame.K_SPACE:
                    paused = True
                if event.key == pygame.K_r:
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                        cursed.reset()
                    combat.reset()
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    if pu_mgr: pu_mgr.reset()
                    result = await countdown(WIN, draw_full_scene)
                    if result == 'quit': return
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions

                # ---- Combat actions (on key down) ----
                # Left player: E = grab/release
                if event.key == pygame.K_e:
                    if combat.ball_grabbed_by == 'left':
                        combat.release_ball(left_paddle, ball)
                    elif combat.paddle_grabbed and 'left_grabs' in combat.paddle_grabbed:
                        combat.throw_paddle(left_paddle, right_paddle)
                    else:
                        if not combat.try_grab_ball('left', left_paddle, ball):
                            combat.try_grab_paddle('left', left_paddle, right_paddle)

                # Right player: RSHIFT = grab/release
                if event.key == pygame.K_RSHIFT:
                    if combat.ball_grabbed_by == 'right':
                        combat.release_ball(right_paddle, ball)
                    elif combat.paddle_grabbed and 'right_grabs' in combat.paddle_grabbed:
                        combat.throw_paddle(right_paddle, left_paddle)
                    else:
                        if not combat.try_grab_ball('right', right_paddle, ball):
                            combat.try_grab_paddle('right', right_paddle, left_paddle)

        # Touch buttons
        if not paused:
            if touch.tapped_menu_btn():
                should_exit = await confirm_exit(WIN, draw_full_scene, touch)
                touch.clear_taps()
                if should_exit:
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                    return
            if touch.tapped_pause_btn():
                paused = True

        if paused:
            action = pause_menu.handle_touch(touch)
            if action == 'resume':
                paused = False
            elif action == 'restart':
                if cursed:
                    cursed.reset_paddles(left_paddle, right_paddle)
                    cursed.reset()
                combat.reset()
                left_score, right_score = reset(ball, left_paddle, right_paddle)
                if pu_mgr: pu_mgr.reset()
                paused = False
                touch.clear_taps()
                result = await countdown(WIN, draw_full_scene)
                if result == 'quit': return
            elif action == 'menu':
                if cursed:
                    cursed.reset_paddles(left_paddle, right_paddle)
                return

        juice.update()

        skip_frame = False
        if not paused and cursed:
            cursed.update(ball, left_paddle, right_paddle, pu_mgr)
            skip_frame = cursed.should_skip_frame()

        # Draw
        draw_full_scene()

        if paused:
            pause_menu.draw(WIN)

        if show_instructions:
            footer_text = "[SPACE] pause | [R] restart | [M] menu | [E] grab | Sword = move keys"
        else:
            footer_text = "Press [H] for help"
        footer = FONT_SMALL_DIGITAL.render(footer_text, True, GREY)
        WIN.blit(footer, (GAME_MARGIN_X, GAME_FOOTER[1]))

        draw_touch_zones(WIN, touch)
        touch.update_ripples()
        touch.draw_ripples(WIN)
        draw_touch_buttons(WIN, paused)
        pygame.display.update()

        if not paused and not skip_frame:
            # Freeze guard
            frozen_l = pu_mgr.is_frozen(left_paddle) if pu_mgr else False
            frozen_r = pu_mgr.is_frozen(right_paddle) if pu_mgr else False
            if frozen_l: saved_l = left_paddle.pos.copy()
            if frozen_r: saved_r = right_paddle.pos.copy()

            # Skip movement for cut (dead) paddles
            left_can_move = not combat.is_cut('left')
            right_can_move = not combat.is_cut('right')

            # Input handling
            if left_can_move and right_can_move:
                if cursed and cursed.has_event('REVERSE CONTROLS'):
                    reversed_keys = _make_reversed_keys(keys)
                    handle_paddle_movement_cursed(reversed_keys, left_paddle, right_paddle,
                                                 ai_right=vs_ai, touch=touch)
                else:
                    handle_paddle_movement_cursed(keys, left_paddle, right_paddle,
                                                 ai_right=vs_ai, touch=touch)
            elif left_can_move:
                if keys[pygame.K_w]: left_paddle.accelerate(up=True)
                if keys[pygame.K_s]: left_paddle.accelerate(up=False)
                if keys[pygame.K_a]: left_paddle.accelerate_x(forward=False)
                if keys[pygame.K_d]: left_paddle.accelerate_x(forward=True)
            elif right_can_move and not vs_ai:
                if keys[pygame.K_UP]: right_paddle.accelerate(up=True)
                if keys[pygame.K_DOWN]: right_paddle.accelerate(up=False)
                if keys[pygame.K_LEFT]: right_paddle.accelerate_x(forward=True)
                if keys[pygame.K_RIGHT]: right_paddle.accelerate_x(forward=False)

            if vs_ai and right_can_move:
                ai_move_paddle(right_paddle, ball, difficulty=ai_diff)

            # ---- Directional sword from movement keys ----
            # Left sword: WASD direction
            ldx = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
            ldy = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)
            combat.set_sword_direction('left', ldx, ldy)

            # Right sword: Arrow keys direction
            if not vs_ai:
                rdx = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
                rdy = (1 if keys[pygame.K_DOWN] else 0) - (1 if keys[pygame.K_UP] else 0)
                combat.set_sword_direction('right', rdx, rdy)
            else:
                combat.set_sword_direction('right', 0, 0)  # AI has no sword

            # Enforce freeze
            if frozen_l:
                left_paddle.pos[:] = saved_l
                left_paddle.vel[:] = 0
            if frozen_r:
                right_paddle.pos[:] = saved_r
                right_paddle.vel[:] = 0

            # Dead paddles don't move
            if combat.is_cut('left'):
                left_paddle.vel[:] = 0
            if combat.is_cut('right'):
                right_paddle.vel[:] = 0

            # Update paddles with cursed mode physics (full board)
            left_paddle.update(cursed_mode=True)
            right_paddle.update(cursed_mode=True)

            # Update grabbed objects
            if combat.ball_grabbed_by == 'left':
                combat.update_grabbed_ball(left_paddle, ball)
            elif combat.ball_grabbed_by == 'right':
                combat.update_grabbed_ball(right_paddle, ball)

            if combat.paddle_grabbed:
                if 'left_grabs' in combat.paddle_grabbed:
                    combat.update_grabbed_paddle(left_paddle, right_paddle)
                else:
                    combat.update_grabbed_paddle(right_paddle, left_paddle)

            # Ball physics
            if combat.ball_grabbed_by is None:
                ball.update()
                ball.vel *= BALL_FRICTION

                old_vx = ball.vel[0]
                old_vy = ball.vel[1]
                hit = handle_ball_collision_cursed(ball, left_paddle, right_paddle)

                # Wall bounce effects
                if old_vy != 0 and (old_vy > 0) != (ball.vel[1] > 0):
                    audio.play('wall_bounce')
                    wall_y = ball.radius if ball.pos[1] <= HEIGHT // 2 else HEIGHT - ball.radius
                    juice.on_wall_bounce(ball.pos[0], wall_y)

                # Paddle hit effects
                if hit == 'left':
                    audio.play('paddle_hit')
                    hit_speed = np.linalg.norm(ball.vel)
                    shake_mag = min(15, 3 + hit_speed * 0.5)
                    juice.shake.trigger(shake_mag, 0.15)
                    juice.on_paddle_hit(left_paddle.pos[0] + left_paddle.width,
                                        ball.pos[1], l_color)
                    if pu_mgr: pu_mgr.set_last_hit('left')
                elif hit == 'right':
                    audio.play('paddle_hit')
                    hit_speed = np.linalg.norm(ball.vel)
                    shake_mag = min(15, 3 + hit_speed * 0.5)
                    juice.shake.trigger(shake_mag, 0.15)
                    juice.on_paddle_hit(right_paddle.pos[0], ball.pos[1], r_color)
                    if pu_mgr: pu_mgr.set_last_hit('right')

            # Combat system update (swords, blood, ramming)
            combat.update(left_paddle, right_paddle, ball)

            # Extra balls (power-ups)
            if pu_mgr:
                for eb in pu_mgr.extra_balls:
                    eb.update()
                    handle_ball_collision_cursed(eb, left_paddle, right_paddle)
                pu_mgr.update(ball)
                pu_mgr.create_extra_balls(ball, mode='physics')

            # Scoring
            scored = False
            if combat.ball_grabbed_by is None:
                if pu_mgr and (pu_mgr.extra_balls or pu_mgr.main_ball_parked):
                    if not pu_mgr.main_ball_parked:
                        if ball.pos[0] < 0:
                            pu_mgr.park_main_ball(ball, 'left')
                        elif ball.pos[0] > WIDTH:
                            pu_mgr.park_main_ball(ball, 'right')
                    pu_mgr.extra_balls = [
                        eb for eb in pu_mgr.extra_balls
                        if -eb.radius <= eb.pos[0] <= WIDTH + eb.radius
                    ]
                    result = pu_mgr.check_multiball_done()
                    if result == 'right_scores':
                        right_score += 1
                        scored = True
                    elif result == 'left_scores':
                        left_score += 1
                        scored = True
                else:
                    if ball.pos[0] - ball.radius < 0:
                        right_score += 1
                        scored = True
                    elif ball.pos[0] + ball.radius > WIDTH:
                        left_score += 1
                        scored = True

                if scored:
                    audio.play('score')
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                        cursed.reset()
                    # Don't reset combat on score — dead paddles stay dead!
                    left_paddle.height = orig_p_h
                    right_paddle.height = orig_p_h
                    ball.reset()
                    if pu_mgr: pu_mgr.reset()
                    if left_score > right_score or (left_score == right_score and ball.vel[0] > 0):
                        juice.on_score(WIDTH // 4, 20 + 25, str(left_score),
                                       FONT_SCORE_GAME, LIGHT_PURPLE)
                    else:
                        juice.on_score(WIDTH * 3 // 4, 20 + 25, str(right_score),
                                       FONT_SCORE_GAME, LIGHT_PURPLE)

        # Win condition
        if left_score >= win_score or right_score >= win_score:
            right_name = "AI" if vs_ai else "Right Player"
            winner = "Left Player Won!" if left_score > right_score else f"{right_name} Won!"

            if left_score > right_score:
                audio.play('win')
            else:
                audio.play('lose') if vs_ai else audio.play('win')

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
                        if cursed:
                            cursed.reset_paddles(left_paddle, right_paddle)
                            cursed.reset()
                            cursed.total_events_triggered = 0
                        combat.reset()
                        left_paddle.height = orig_p_h
                        right_paddle.height = orig_p_h
                        left_score, right_score = reset(ball, left_paddle, right_paddle)
                        if pu_mgr: pu_mgr.reset()
                        choosing = False
                    elif action == 'menu':
                        return

                action = win_screen.handle_touch(touch)
                if action == 'play_again':
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                        cursed.reset()
                        cursed.total_events_triggered = 0
                    combat.reset()
                    left_paddle.height = orig_p_h
                    right_paddle.height = orig_p_h
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

            result = await countdown(WIN, draw_full_scene)
            if result == 'quit': return

        touch.clear_taps()
        await asyncio.sleep(0)


class _ReversedKeys:
    """Proxy that swaps W/S, A/D, UP/DOWN, LEFT/RIGHT."""

    def __init__(self, keys):
        self._keys = keys

    def __getitem__(self, key):
        swap = {
            pygame.K_w: pygame.K_s, pygame.K_s: pygame.K_w,
            pygame.K_a: pygame.K_d, pygame.K_d: pygame.K_a,
            pygame.K_UP: pygame.K_DOWN, pygame.K_DOWN: pygame.K_UP,
            pygame.K_LEFT: pygame.K_RIGHT, pygame.K_RIGHT: pygame.K_LEFT,
        }
        return self._keys[swap.get(key, key)]


def _make_reversed_keys(keys):
    return _ReversedKeys(keys)


if __name__ == '__main__':
    asyncio.run(main())
