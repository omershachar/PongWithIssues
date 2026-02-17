"""
Sandbox Mode -- Debug/practice mode with no scoring and physics info display.
"""
import sys
import os
import asyncio
import pygame

# Add the project root to sys.path so "pong" can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pong.constants import *
from pong.paddle import Paddle
from pong.ball import Ball
from pong.utilities import draw as draw_game, reset, handle_ball_collision
from pong.helpers import handle_paddle_movement
from pong.touch import TouchHandler, draw_touch_buttons, draw_touch_zones
from pong import audio
from pong.juice import JuiceManager
from pong.game_flow import PauseMenu, confirm_exit

def draw_debug_info(win, ball, left_paddle, right_paddle):
    """Draw debug information overlay."""
    debug_lines = [
        f"Ball pos: ({ball.pos[0]:.1f}, {ball.pos[1]:.1f})",
        f"Ball vel: ({ball.vel[0]:.1f}, {ball.vel[1]:.1f})",
        f"Ball speed: {ball.speed:.1f}",
        f"Ball spin: {ball.spin:.2f}",
        f"L-Paddle vel: {left_paddle.vel[1]:.1f}",
        f"R-Paddle vel: {right_paddle.vel[1]:.1f}",
    ]

    y_offset = 40
    for i, line in enumerate(debug_lines):
        text = FONT_TINY_DIGITAL.render(line, True, GREEN)
        win.blit(text, (10, y_offset + i * 16))


async def main(settings=None):
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong - Sandbox")
    clock = pygame.time.Clock()

    # Initialize audio
    audio.init()

    paused = False
    show_debug = True
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

    # Use physics mode for sandbox
    left_paddle = Paddle(ORIGINAL_LEFT_PADDLE_POS[0], ORIGINAL_LEFT_PADDLE_POS[1],
                         p_w, p_h, color=l_color, mode='physics', fixed_vel=p_speed)
    right_paddle = Paddle(ORIGINAL_RIGHT_PADDLE_POS[0], ORIGINAL_RIGHT_PADDLE_POS[1],
                          p_w, p_h, color=r_color, mode='physics', fixed_vel=p_speed)
    ball = Ball(*MIDDLE_BOARD, b_radius, GREEN, mode='physics', vel=(b_speed, 0))

    touch = TouchHandler()
    # No scoring in sandbox - just hit counters
    left_hits = 0
    right_hits = 0

    # Juice (visual effects) — respects settings
    juice = JuiceManager(settings)

    # Pause menu
    pause_menu = PauseMenu()

    def draw_full_scene():
        """Draw the complete game scene."""
        draw_game(WIN, [left_paddle, right_paddle], ball, left_hits, right_hits, FONT_LARGE_DIGITAL, bg_color)
        mode_text = FONT_SMALL_DIGITAL.render("MODE: SANDBOX", True, GREEN)
        WIN.blit(mode_text, (10, 10))
        if show_debug:
            draw_debug_info(WIN, ball, left_paddle, right_paddle)
        juice.draw(WIN)

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
                    ball.pos = ball.original_pos.copy()
                    ball.vel = ball.original_vel.copy()
                    ball.spin = 0
                    ball.trail.clear()
                    left_paddle.reset()
                    right_paddle.reset()
                    left_hits = 0
                    right_hits = 0
                    paused = False
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
                    ball.pos = ball.original_pos.copy()
                    ball.vel = ball.original_vel.copy()
                    ball.spin = 0
                    ball.trail.clear()
                    left_paddle.reset()
                    right_paddle.reset()
                    left_hits = 0
                    right_hits = 0
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions
                if event.key == pygame.K_d:
                    show_debug = not show_debug

        # Touch button actions
        if not paused:
            if touch.tapped_menu_btn():
                should_exit = await confirm_exit(WIN, draw_full_scene, touch)
                touch.clear_taps()
                if should_exit:
                    return
            if touch.tapped_pause_btn():
                paused = True

        if paused:
            action = pause_menu.handle_touch(touch)
            if action == 'resume':
                paused = False
            elif action == 'restart':
                ball.pos = ball.original_pos.copy()
                ball.vel = ball.original_vel.copy()
                ball.spin = 0
                ball.trail.clear()
                left_paddle.reset()
                right_paddle.reset()
                left_hits = 0
                right_hits = 0
                paused = False
            elif action == 'menu':
                return

        # Update juice effects
        juice.update()

        # Draw scene
        draw_full_scene()

        if paused:
            pause_menu.draw(WIN)

        # Footer instructions
        if show_instructions:
            footer_text = "[SPACE] pause | [R] reset | [D] debug | [M] menu | [ESC] quit | [H] hide"
        else:
            footer_text = "Press [H] for help | [D] toggle debug"
        footer = FONT_SMALL_DIGITAL.render(footer_text, True, GREY)
        WIN.blit(footer, (GAME_MARGIN_X, GAME_FOOTER[1]))

        draw_touch_zones(WIN, touch)
        touch.update_ripples()
        touch.draw_ripples(WIN)
        draw_touch_buttons(WIN, paused)
        pygame.display.update()

        if not paused:
            handle_paddle_movement(keys, left_paddle, right_paddle, touch=touch)
            left_paddle.update()
            right_paddle.update()

            ball.update()

            old_vx = ball.vel[0]
            old_vy = ball.vel[1]
            handle_ball_collision(ball, left_paddle, right_paddle, HEIGHT)

            # Wall bounce detection — check if vy flipped sign
            if old_vy != 0 and (old_vy > 0) != (ball.vel[1] > 0):
                audio.play('wall_bounce')
                wall_y = ball.radius if ball.pos[1] <= HEIGHT // 2 else HEIGHT - ball.radius
                juice.on_wall_bounce(ball.pos[0], wall_y)

            # Detect paddle hits — check if vx flipped sign
            if old_vx < 0 and ball.vel[0] > 0:
                left_hits += 1
                audio.play('paddle_hit')
                juice.on_paddle_hit(left_paddle.pos[0] + left_paddle.width, ball.pos[1], l_color)
            elif old_vx > 0 and ball.vel[0] < 0:
                right_hits += 1
                audio.play('paddle_hit')
                juice.on_paddle_hit(right_paddle.pos[0], ball.pos[1], r_color)

            # In sandbox, ball bounces off all walls (no scoring)
            if ball.pos[0] - ball.radius < 0:
                ball.vel[0] = abs(ball.vel[0])
                ball.pos[0] = ball.radius
                audio.play('wall_bounce')
                juice.on_wall_bounce(ball.radius, ball.pos[1])
            elif ball.pos[0] + ball.radius > WIDTH:
                ball.vel[0] = -abs(ball.vel[0])
                ball.pos[0] = WIDTH - ball.radius
                audio.play('wall_bounce')
                juice.on_wall_bounce(WIDTH - ball.radius, ball.pos[1])

        touch.clear_taps()
        await asyncio.sleep(0)


if __name__ == '__main__':
    asyncio.run(main())
