"""
Cursed Pong -- INSANE sword-fighting chaos mode with dual combat modes.

Bigger arena, slower paddles, Force/Saber toggle, charged force powers,
lightning bolt kill move, goal nets, Rayman-style cartoon hands.

Controls:
  Left:  WASD = move, E = toggle Force/Saber, G = grab/release
         Force: F = push, Q = pull, F+Q hold = LIGHTNING
         Saber: F = swing, Q = block
  Right: Arrows = move, RShift = toggle, Backslash = grab/release
         Force: RAlt = push, RCtrl = pull, RAlt+RCtrl hold = LIGHTNING
         Saber: RAlt = swing, RCtrl = block
"""
import sys
import os
import asyncio
import time
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
from pong.cursed_combat import CursedCombatManager, MODE_FORCE, MODE_SABER, CHARGE_FORCE_TIME
from pong.abilities import AbilityManager, ForcePush, ForcePull, ChargedForcePush, ChargedForcePull
from pong.force_effects import ForceEffectSystem

BALL_FRICTION = 0.997  # Ball slows down faster for easier catching

# Cursed arena dimensions
CW, CH = CURSED_WIDTH, CURSED_HEIGHT


async def main(vs_ai=False, settings=None):
    WIN = pygame.display.set_mode((CW, CH))
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
    goal_net_on = getattr(settings, 'goal_net_enabled', False) if settings else False
    goal_frac = getattr(settings, 'goal_net_size', 0.40) if settings else 0.40

    # Physics-mode paddles at new arena positions
    left_paddle = Paddle(GAME_MARGIN_X, CH // 2 - p_h // 2,
                         p_w, p_h, color=l_color, mode='physics', fixed_vel=p_speed, side='left')
    right_paddle = Paddle(CW - GAME_MARGIN_X - p_w, CH // 2 - p_h // 2,
                          p_w, p_h, color=r_color, mode='physics', fixed_vel=p_speed, side='right')

    ball = Ball(CW // 2, CH // 2, b_radius, (255, 50, 200), mass=1,
                vel=(b_speed, 0), mode='physics')
    # Override ball reset position for larger arena
    ball.original_pos = np.array([CW // 2, CH // 2], dtype=float)

    touch = TouchHandler(single_player=vs_ai)
    left_score = 0
    right_score = 0

    power_ups_on = settings.power_ups_enabled if settings else False
    pu_mgr = PowerUpManager(left_paddle, right_paddle) if power_ups_on else None
    juice = JuiceManager(settings)
    cursed = CursedEventManager() if cursed_events_on else None
    combat = CursedCombatManager(left_color=l_color, right_color=r_color, screen_w=CW, screen_h=CH)

    # Force abilities
    ability_mgr = AbilityManager()
    ability_mgr.register('left', 'push', ForcePush())
    ability_mgr.register('left', 'pull', ForcePull())
    ability_mgr.register('right', 'push', ForcePush())
    ability_mgr.register('right', 'pull', ForcePull())
    force_fx = ForceEffectSystem()

    pause_menu = PauseMenu()
    win_screen = WinScreen()

    orig_p_h = p_h

    # Keydown timestamps for charged force detection
    _l_push_down_t = 0.0
    _l_pull_down_t = 0.0
    _r_push_down_t = 0.0
    _r_pull_down_t = 0.0
    # Track if lightning was firing (to skip force on keyup)
    _l_lightning_was_charging = False
    _r_lightning_was_charging = False

    events_label = " [Events ON]" if cursed_events_on else ""
    if vs_ai:
        diff_name = DIFFICULTY_NAMES.get(ai_diff, "")
        mode_label = f"CURSED vs AI ({diff_name}){events_label}"
    else:
        mode_label = f"CURSED{events_label}"

    def _draw_goal_nets(target):
        """Draw golden goal net frames on left and right edges."""
        if not goal_net_on:
            return
        net_h = int(CH * goal_frac)
        net_top = CH // 2 - net_h // 2
        net_bottom = net_top + net_h
        net_depth = 20
        gold = (255, 215, 0)
        dark_gold = (180, 150, 0)

        for side_x in [0, CW - net_depth]:
            # Frame
            pygame.draw.rect(target, gold,
                             (side_x, net_top, net_depth, net_h), 2)
            # Net mesh lines
            mesh_spacing = 12
            for y in range(net_top, net_bottom, mesh_spacing):
                pygame.draw.line(target, dark_gold,
                                 (side_x, y), (side_x + net_depth, y), 1)
            for x in range(side_x, side_x + net_depth, mesh_spacing // 2):
                pygame.draw.line(target, dark_gold,
                                 (x, net_top), (x, net_bottom), 1)

    def _ball_in_goal_zone(ball_y):
        """Check if ball Y is within the goal net zone."""
        if not goal_net_on:
            return True  # no nets = always scores
        net_h = int(CH * goal_frac)
        net_top = CH // 2 - net_h // 2
        net_bottom = net_top + net_h
        return net_top <= ball_y <= net_bottom

    def draw_full_scene():
        sx, sy = juice.shake.get_offset()
        if cursed and cursed.has_event('SCREEN FLIP'):
            temp = pygame.Surface((CW, CH))
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
                  hide_ball=(hide_ball or combat.ball_grabbed_by is not None),
                  screen_w=CW, screen_h=CH)

        # Goal nets
        _draw_goal_nets(target)

        if pu_mgr:
            pu_mgr.draw(target)
            pu_mgr.draw_extra_balls(target)

        # Combat visuals (blood, swords, cut paddles, grab indicators, lightning, mode badges)
        combat.draw(target, left_paddle, right_paddle)

        # Force effects (shockwaves, particles) + cooldown bars
        force_fx.draw(target)
        ability_mgr.draw_cooldown_bars(target, left_paddle, right_paddle)

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
            "[E]=mode [G]=grab  Force:[F]push [Q]pull [F+Q]LIGHTNING  Saber:[F]swing [Q]block",
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
        now = time.monotonic()

        for event in pygame.event.get():
            touch.handle_event(event)
            if event.type == pygame.QUIT:
                # Restore window size before returning
                pygame.display.set_mode((WIDTH, HEIGHT))
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
                    ability_mgr.reset()
                    force_fx.reset()
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    ball.original_pos = np.array([CW // 2, CH // 2], dtype=float)
                    ball.pos[:] = ball.original_pos
                    if pu_mgr: pu_mgr.reset()
                    paused = False
                    result = await countdown(WIN, draw_full_scene)
                    if result == 'quit':
                        pygame.display.set_mode((WIDTH, HEIGHT))
                        return
                elif action == 'menu':
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                    pygame.display.set_mode((WIDTH, HEIGHT))
                    return
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    should_exit = await confirm_exit(WIN, draw_full_scene, touch)
                    if should_exit:
                        if cursed:
                            cursed.reset_paddles(left_paddle, right_paddle)
                        pygame.display.set_mode((WIDTH, HEIGHT))
                        return
                if event.key == pygame.K_SPACE:
                    paused = True
                if event.key == pygame.K_r:
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                        cursed.reset()
                    combat.reset()
                    ability_mgr.reset()
                    force_fx.reset()
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    ball.original_pos = np.array([CW // 2, CH // 2], dtype=float)
                    ball.pos[:] = ball.original_pos
                    if pu_mgr: pu_mgr.reset()
                    result = await countdown(WIN, draw_full_scene)
                    if result == 'quit':
                        pygame.display.set_mode((WIDTH, HEIGHT))
                        return
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions

                # ---- Mode toggle ----
                if event.key == pygame.K_e:
                    combat.toggle_mode('left')
                if event.key == pygame.K_RSHIFT:
                    combat.toggle_mode('right')

                # ---- Grab/Release: G / BACKSLASH ----
                if event.key == pygame.K_g:
                    if combat.ball_grabbed_by == 'left':
                        combat.release_ball(left_paddle, ball)
                    elif combat.paddle_grabbed and 'left_grabs' in combat.paddle_grabbed:
                        combat.throw_paddle(left_paddle, right_paddle)
                    else:
                        if not combat.try_grab_ball('left', left_paddle, ball):
                            combat.try_grab_paddle('left', left_paddle, right_paddle)

                if event.key == pygame.K_BACKSLASH:
                    if combat.ball_grabbed_by == 'right':
                        combat.release_ball(right_paddle, ball)
                    elif combat.paddle_grabbed and 'right_grabs' in combat.paddle_grabbed:
                        combat.throw_paddle(right_paddle, left_paddle)
                    else:
                        if not combat.try_grab_ball('right', right_paddle, ball):
                            combat.try_grab_paddle('right', right_paddle, left_paddle)

                # ---- Saber actions (on keydown) ----
                if event.key == pygame.K_f and combat.mode_left == MODE_SABER:
                    ldx = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
                    ldy = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)
                    combat.left_sword.apply_swing_impulse(ldx, ldy)
                    audio.play('lightsaber_clash')

                if event.key == pygame.K_RALT and combat.mode_right == MODE_SABER:
                    rdx = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
                    rdy = (1 if keys[pygame.K_DOWN] else 0) - (1 if keys[pygame.K_UP] else 0)
                    combat.right_sword.apply_swing_impulse(rdx, rdy)
                    audio.play('lightsaber_clash')

                # ---- Force mode: record keydown timestamps ----
                if event.key == pygame.K_f and combat.mode_left == MODE_FORCE:
                    _l_push_down_t = now
                if event.key == pygame.K_q and combat.mode_left == MODE_FORCE:
                    _l_pull_down_t = now
                if event.key == pygame.K_RALT and combat.mode_right == MODE_FORCE:
                    _r_push_down_t = now
                if event.key == pygame.K_RCTRL and combat.mode_right == MODE_FORCE:
                    _r_pull_down_t = now

            # ---- Force mode: KEYUP → fire normal or charged ----
            if event.type == pygame.KEYUP:
                def _get_force_dir(sword, paddle, default_forward):
                    if sword.visible:
                        return sword._base_angle() + sword.angle
                    return default_forward

                def _get_paddle_center(p):
                    return (p.pos[0] + p.width / 2, p.pos[1] + p.height / 2)

                def _force_targets(side):
                    targets = [(ball, 1.0)]
                    if side == 'left':
                        targets.append((right_paddle, 0.6))
                    else:
                        targets.append((left_paddle, 0.6))
                    return targets

                # Left push release
                if event.key == pygame.K_f and combat.mode_left == MODE_FORCE:
                    if not _l_lightning_was_charging:
                        hold = now - _l_push_down_t if _l_push_down_t > 0 else 0
                        origin = _get_paddle_center(left_paddle)
                        direction = _get_force_dir(combat.left_sword, left_paddle, 0.0)
                        if hold >= CHARGE_FORCE_TIME:
                            ab = ChargedForcePush()
                            ab.try_activate(origin=origin, direction=direction)
                            ab.apply_to_objects(_force_targets('left'),
                                                grabbed_obj=ball if combat.ball_grabbed_by else None)
                            force_fx.emit_push(origin[0], origin[1], direction, l_color)
                            audio.play('force_push')
                            juice.shake.trigger(14, 0.2)
                        else:
                            if ability_mgr.try_activate('left', 'push', origin=origin, direction=direction):
                                ab = ability_mgr.get('left', 'push')
                                ab.apply_to_objects(_force_targets('left'),
                                                    grabbed_obj=ball if combat.ball_grabbed_by else None)
                                force_fx.emit_push(origin[0], origin[1], direction, l_color)
                                audio.play('force_push')
                                juice.shake.trigger(8, 0.12)
                    _l_push_down_t = 0.0
                    _l_lightning_was_charging = False

                # Left pull release
                if event.key == pygame.K_q and combat.mode_left == MODE_FORCE:
                    if not _l_lightning_was_charging:
                        hold = now - _l_pull_down_t if _l_pull_down_t > 0 else 0
                        origin = _get_paddle_center(left_paddle)
                        direction = _get_force_dir(combat.left_sword, left_paddle, 0.0)
                        if hold >= CHARGE_FORCE_TIME:
                            ab = ChargedForcePull()
                            ab.try_activate(origin=origin, direction=direction)
                            ab.apply_to_objects(_force_targets('left'),
                                                grabbed_obj=ball if combat.ball_grabbed_by else None)
                            force_fx.emit_pull(origin[0], origin[1], direction, l_color)
                            audio.play('force_pull')
                            juice.shake.trigger(12, 0.18)
                        else:
                            if ability_mgr.try_activate('left', 'pull', origin=origin, direction=direction):
                                ab = ability_mgr.get('left', 'pull')
                                ab.apply_to_objects(_force_targets('left'),
                                                    grabbed_obj=ball if combat.ball_grabbed_by else None)
                                force_fx.emit_pull(origin[0], origin[1], direction, l_color)
                                audio.play('force_pull')
                    _l_pull_down_t = 0.0
                    _l_lightning_was_charging = False

                # Right push release
                if event.key == pygame.K_RALT and combat.mode_right == MODE_FORCE:
                    if not _r_lightning_was_charging:
                        hold = now - _r_push_down_t if _r_push_down_t > 0 else 0
                        origin = _get_paddle_center(right_paddle)
                        direction = _get_force_dir(combat.right_sword, right_paddle, math.pi)
                        if hold >= CHARGE_FORCE_TIME:
                            ab = ChargedForcePush()
                            ab.try_activate(origin=origin, direction=direction)
                            ab.apply_to_objects(_force_targets('right'),
                                                grabbed_obj=ball if combat.ball_grabbed_by else None)
                            force_fx.emit_push(origin[0], origin[1], direction, r_color)
                            audio.play('force_push')
                            juice.shake.trigger(14, 0.2)
                        else:
                            if ability_mgr.try_activate('right', 'push', origin=origin, direction=direction):
                                ab = ability_mgr.get('right', 'push')
                                ab.apply_to_objects(_force_targets('right'),
                                                    grabbed_obj=ball if combat.ball_grabbed_by else None)
                                force_fx.emit_push(origin[0], origin[1], direction, r_color)
                                audio.play('force_push')
                                juice.shake.trigger(8, 0.12)
                    _r_push_down_t = 0.0
                    _r_lightning_was_charging = False

                # Right pull release
                if event.key == pygame.K_RCTRL and combat.mode_right == MODE_FORCE:
                    if not _r_lightning_was_charging:
                        hold = now - _r_pull_down_t if _r_pull_down_t > 0 else 0
                        origin = _get_paddle_center(right_paddle)
                        direction = _get_force_dir(combat.right_sword, right_paddle, math.pi)
                        if hold >= CHARGE_FORCE_TIME:
                            ab = ChargedForcePull()
                            ab.try_activate(origin=origin, direction=direction)
                            ab.apply_to_objects(_force_targets('right'),
                                                grabbed_obj=ball if combat.ball_grabbed_by else None)
                            force_fx.emit_pull(origin[0], origin[1], direction, r_color)
                            audio.play('force_pull')
                            juice.shake.trigger(12, 0.18)
                        else:
                            if ability_mgr.try_activate('right', 'pull', origin=origin, direction=direction):
                                ab = ability_mgr.get('right', 'pull')
                                ab.apply_to_objects(_force_targets('right'),
                                                    grabbed_obj=ball if combat.ball_grabbed_by else None)
                                force_fx.emit_pull(origin[0], origin[1], direction, r_color)
                                audio.play('force_pull')
                    _r_pull_down_t = 0.0
                    _r_lightning_was_charging = False

        # Touch buttons
        if not paused:
            if touch.tapped_menu_btn():
                should_exit = await confirm_exit(WIN, draw_full_scene, touch)
                touch.clear_taps()
                if should_exit:
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                    pygame.display.set_mode((WIDTH, HEIGHT))
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
                ability_mgr.reset()
                force_fx.reset()
                left_score, right_score = reset(ball, left_paddle, right_paddle)
                ball.original_pos = np.array([CW // 2, CH // 2], dtype=float)
                ball.pos[:] = ball.original_pos
                if pu_mgr: pu_mgr.reset()
                paused = False
                touch.clear_taps()
                result = await countdown(WIN, draw_full_scene)
                if result == 'quit':
                    pygame.display.set_mode((WIDTH, HEIGHT))
                    return
            elif action == 'menu':
                if cursed:
                    cursed.reset_paddles(left_paddle, right_paddle)
                pygame.display.set_mode((WIDTH, HEIGHT))
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
            footer_text = "[SPACE] pause | [R] restart | [M] menu | [E] mode | [G] grab | [F/Q] Force/Swing | [F+Q] LIGHTNING"
        else:
            footer_text = "Press [H] for help"
        footer = FONT_SMALL_DIGITAL.render(footer_text, True, GREY)
        WIN.blit(footer, (GAME_MARGIN_X, CH - 30))

        draw_touch_zones(WIN, touch)
        touch.update_ripples()
        touch.draw_ripples(WIN)
        draw_touch_buttons(WIN, paused)
        pygame.display.update()

        if not paused and not skip_frame:
            dt = 1 / 60

            # Freeze guard
            frozen_l = pu_mgr.is_frozen(left_paddle) if pu_mgr else False
            frozen_r = pu_mgr.is_frozen(right_paddle) if pu_mgr else False
            if frozen_l: saved_l = left_paddle.pos.copy()
            if frozen_r: saved_r = right_paddle.pos.copy()

            # Skip movement for cut (dead) paddles
            left_can_move = not combat.is_cut('left')
            right_can_move = not combat.is_cut('right')

            # Lightning freeze check
            if combat.is_lightning_frozen('left'):
                left_can_move = False
            if combat.is_lightning_frozen('right'):
                right_can_move = False

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

            # ---- Saber block: Q/RCTRL held in saber mode ----
            if combat.mode_left == MODE_SABER:
                combat.left_sword.set_blocking(keys[pygame.K_q])
            else:
                combat.left_sword.set_blocking(False)

            if combat.mode_right == MODE_SABER:
                combat.right_sword.set_blocking(keys[pygame.K_RCTRL])
            else:
                combat.right_sword.set_blocking(False)

            # ---- Directional sword from movement keys (saber mode only) ----
            if combat.mode_left == MODE_SABER:
                ldx = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
                ldy = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)
                combat.set_sword_direction('left', ldx, ldy)
            else:
                # Force mode: sword hidden
                combat.set_sword_direction('left', 0, 0)

            if not vs_ai:
                if combat.mode_right == MODE_SABER:
                    rdx = (1 if keys[pygame.K_RIGHT] else 0) - (1 if keys[pygame.K_LEFT] else 0)
                    rdy = (1 if keys[pygame.K_DOWN] else 0) - (1 if keys[pygame.K_UP] else 0)
                    combat.set_sword_direction('right', rdx, rdy)
                else:
                    combat.set_sword_direction('right', 0, 0)
            else:
                combat.set_sword_direction('right', 0, 0)  # AI has no sword

            # ---- Lightning: detect both push+pull held in force mode ----
            l_both = (keys[pygame.K_f] and keys[pygame.K_q] and
                      combat.mode_left == MODE_FORCE)
            r_both = (keys[pygame.K_RALT] and keys[pygame.K_RCTRL] and
                      combat.mode_right == MODE_FORCE)

            combat.update_lightning_charge('left', l_both, dt,
                                           (left_paddle, right_paddle))
            combat.update_lightning_charge('right', r_both, dt,
                                           (left_paddle, right_paddle))

            if l_both:
                _l_lightning_was_charging = True
            if r_both:
                _r_lightning_was_charging = True

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

            # Update paddles with cursed mode physics (bigger arena, slower)
            left_paddle.update(cursed_mode=True, max_vel_override=CURSED_PADDLE_MAX_VEL,
                               screen_w=CW, screen_h=CH)
            right_paddle.update(cursed_mode=True, max_vel_override=CURSED_PADDLE_MAX_VEL,
                                screen_w=CW, screen_h=CH)

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
                hit = handle_ball_collision_cursed(ball, left_paddle, right_paddle,
                                                  screen_h=CH)

                # Wall bounce effects
                if old_vy != 0 and (old_vy > 0) != (ball.vel[1] > 0):
                    audio.play('wall_bounce')
                    wall_y = ball.radius if ball.pos[1] <= CH // 2 else CH - ball.radius
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

            # Combat system update (swords, blood, ramming, lightning)
            combat.update(left_paddle, right_paddle, ball)

            # Force abilities & effects
            ability_mgr.update(dt)
            force_fx.update(dt)

            # Extra balls (power-ups)
            if pu_mgr:
                for eb in pu_mgr.extra_balls:
                    eb.update()
                    handle_ball_collision_cursed(eb, left_paddle, right_paddle,
                                                screen_h=CH)
                pu_mgr.update(ball)
                pu_mgr.create_extra_balls(ball, mode='physics')

            # Scoring
            scored = False
            if combat.ball_grabbed_by is None:
                if pu_mgr and (pu_mgr.extra_balls or pu_mgr.main_ball_parked):
                    if not pu_mgr.main_ball_parked:
                        if ball.pos[0] < 0:
                            if _ball_in_goal_zone(ball.pos[1]):
                                pu_mgr.park_main_ball(ball, 'left')
                            else:
                                # Bounce off wall outside goal zone
                                ball.pos[0] = ball.radius
                                ball.vel[0] = abs(ball.vel[0])
                        elif ball.pos[0] > CW:
                            if _ball_in_goal_zone(ball.pos[1]):
                                pu_mgr.park_main_ball(ball, 'right')
                            else:
                                ball.pos[0] = CW - ball.radius
                                ball.vel[0] = -abs(ball.vel[0])
                    pu_mgr.extra_balls = [
                        eb for eb in pu_mgr.extra_balls
                        if -eb.radius <= eb.pos[0] <= CW + eb.radius
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
                        if _ball_in_goal_zone(ball.pos[1]):
                            right_score += 1
                            scored = True
                        else:
                            # Bounce off wall outside goal zone
                            ball.pos[0] = ball.radius
                            ball.vel[0] = abs(ball.vel[0])
                    elif ball.pos[0] + ball.radius > CW:
                        if _ball_in_goal_zone(ball.pos[1]):
                            left_score += 1
                            scored = True
                        else:
                            ball.pos[0] = CW - ball.radius
                            ball.vel[0] = -abs(ball.vel[0])

                if scored:
                    audio.play('score')
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                        cursed.reset()
                    # Don't reset combat on score — dead paddles stay dead!
                    left_paddle.height = orig_p_h
                    right_paddle.height = orig_p_h
                    ball.pos[:] = [CW // 2, CH // 2]
                    ball.vel[:] = [b_speed if left_score > right_score else -b_speed, 0]
                    ball.spin = 0
                    ball.trail.clear()
                    if pu_mgr: pu_mgr.reset()
                    if left_score > right_score or (left_score == right_score and ball.vel[0] > 0):
                        juice.on_score(CW // 4, 20 + 25, str(left_score),
                                       FONT_SCORE_GAME, LIGHT_PURPLE)
                    else:
                        juice.on_score(CW * 3 // 4, 20 + 25, str(right_score),
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
                        pygame.display.set_mode((WIDTH, HEIGHT))
                        return
                    action = win_screen.handle_event(event)
                    if action == 'play_again':
                        if cursed:
                            cursed.reset_paddles(left_paddle, right_paddle)
                            cursed.reset()
                            cursed.total_events_triggered = 0
                        combat.reset()
                        ability_mgr.reset()
                        force_fx.reset()
                        left_paddle.height = orig_p_h
                        right_paddle.height = orig_p_h
                        left_score, right_score = reset(ball, left_paddle, right_paddle)
                        ball.original_pos = np.array([CW // 2, CH // 2], dtype=float)
                        ball.pos[:] = ball.original_pos
                        if pu_mgr: pu_mgr.reset()
                        choosing = False
                    elif action == 'menu':
                        pygame.display.set_mode((WIDTH, HEIGHT))
                        return

                action = win_screen.handle_touch(touch)
                if action == 'play_again':
                    if cursed:
                        cursed.reset_paddles(left_paddle, right_paddle)
                        cursed.reset()
                        cursed.total_events_triggered = 0
                    combat.reset()
                    ability_mgr.reset()
                    force_fx.reset()
                    left_paddle.height = orig_p_h
                    right_paddle.height = orig_p_h
                    left_score, right_score = reset(ball, left_paddle, right_paddle)
                    ball.original_pos = np.array([CW // 2, CH // 2], dtype=float)
                    ball.pos[:] = ball.original_pos
                    if pu_mgr: pu_mgr.reset()
                    choosing = False
                elif action == 'menu':
                    pygame.display.set_mode((WIDTH, HEIGHT))
                    return

                draw_full_scene()
                win_screen.draw(WIN, winner, final_left, final_right)
                draw_touch_buttons(WIN, False)
                pygame.display.update()
                touch.clear_taps()
                await asyncio.sleep(0)

            result = await countdown(WIN, draw_full_scene)
            if result == 'quit':
                pygame.display.set_mode((WIDTH, HEIGHT))
                return

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
