"""
Sandbox Mode -- Debug/practice mode with no scoring and physics info display.
"""
import sys
import os
import pygame

# Add the project root to sys.path so "pong" can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pong.constants import *
from pong.paddle import Paddle
from pong.ball import Ball
from pong.utilities import draw as draw_game, reset, handle_ball_collision
from pong.helpers import handle_paddle_movement

pygame.init()
pygame.display.set_caption("Pong - Sandbox")
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


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


def main():
    paused = False
    show_debug = True
    show_instructions = False

    # Use physics mode for sandbox
    left_paddle = Paddle(*ORIGINAL_LEFT_PADDLE_POS, *PADDLE_SIZE, mode='physics')
    right_paddle = Paddle(*ORIGINAL_RIGHT_PADDLE_POS, *PADDLE_SIZE, mode='physics')
    ball = Ball(*MIDDLE_BOARD, BALL_RADIUS, GREEN, mode='physics', vel=BALL_DEFAULT_VEL)

    # No scoring in sandbox - just hit counters
    left_hits = 0
    right_hits = 0

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    return
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_r:
                    ball.pos = ball.original_pos.copy()
                    ball.vel = ball.original_vel.copy()
                    ball.spin = 0
                    ball.trail.clear()
                    left_paddle.reset()
                    right_paddle.reset()
                    left_hits = 0
                    right_hits = 0
                    paused = False
                if event.key == pygame.K_h:
                    show_instructions = not show_instructions
                if event.key == pygame.K_d:
                    show_debug = not show_debug

        # Draw game
        draw_game(WIN, [left_paddle, right_paddle], ball, left_hits, right_hits, FONT_LARGE_DIGITAL)

        # Mode label
        mode_text = FONT_SMALL_DIGITAL.render("MODE: SANDBOX", True, GREEN)
        WIN.blit(mode_text, (10, 10))

        # Debug info overlay
        if show_debug:
            draw_debug_info(WIN, ball, left_paddle, right_paddle)

        if paused:
            # Dark overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            WIN.blit(overlay, (0, 0))

            pause_text = FONT_BIG_DIGITAL.render("PAUSED", True, GREEN)
            resume_text = FONT_SMALL_DIGITAL.render("Press [SPACE] to resume", True, GREY)
            WIN.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - pause_text.get_height()))
            WIN.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 10))

        # Footer instructions
        if show_instructions:
            footer_text = "[SPACE] pause | [R] reset | [D] debug | [M] menu | [ESC] quit | [H] hide"
        else:
            footer_text = "Press [H] for help | [D] toggle debug"
        footer = FONT_SMALL_DIGITAL.render(footer_text, True, GREY)
        WIN.blit(footer, (GAME_MARGIN_X, GAME_FOOTER[1]))

        pygame.display.update()

        if not paused:
            handle_paddle_movement(keys, left_paddle, right_paddle)
            left_paddle.update()
            right_paddle.update()

            ball.update()

            # Check paddle collisions and track hits
            ball_before_x = ball.pos[0]
            handle_ball_collision(ball, left_paddle, right_paddle, HEIGHT)

            # Count hits (ball direction changed)
            if ball.vel[0] > 0 and ball_before_x < WIDTH / 2:
                left_hits += 1
            elif ball.vel[0] < 0 and ball_before_x > WIDTH / 2:
                right_hits += 1

            # In sandbox, ball bounces off all walls (no scoring)
            if ball.pos[0] - ball.radius < 0:
                ball.vel[0] = abs(ball.vel[0])
                ball.pos[0] = ball.radius
            elif ball.pos[0] + ball.radius > WIDTH:
                ball.vel[0] = -abs(ball.vel[0])
                ball.pos[0] = WIDTH - ball.radius


if __name__ == '__main__':
    main()
