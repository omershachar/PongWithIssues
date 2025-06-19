"""
classicPong.py -- Main file containing only essentials and activation commands.
"""
import sys
import os
import pygame

# Add the project root to sys.path so "pong" can be found
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pong.constants import *
from pong.paddle import PaddleClassic as Paddle
from pong.ball import BallClassic as Ball
from pong.utilities import draw as draw_game, reset, handle_ball_collision, handle_paddle_movement

pygame.init()
pygame.display.set_caption("Pong!")  # Window title
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

def main():
    clock = pygame.time.Clock()
    state = MENU

    left_paddle = Paddle(*ORIGINAL_LEFT_PADDLE_POS, *PADDLE_SIZE, LIGHT_PURPLE, PADDLE_DEFAULT_VEL)
    right_paddle = Paddle(*ORIGINAL_RIGHT_PADDLE_POS, *PADDLE_SIZE, LIGHT_PURPLE, PADDLE_DEFAULT_VEL)
    ball = Ball(*MIDDLE_BOARD, BALL_RADIUS, LIGHT_PURPLE, *BALL_DEFAULT_VEL)

    left_score = 0
    right_score = 0

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    return

            if state == MENU:
                # Top text
                mode_text = FONT_SMALL_DIGITAL.render("MODE: CLASSIC", True, GREY)
                WIN.blit(mode_text, (10, 10))

                # Footer
                footer = FONT_SMALL_DIGITAL.render("Press [M] to return | [ESC] to quit", True, GREY)
                WIN.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 30))

                pygame.display.update()
                continue

        draw_game(WIN, [left_paddle, right_paddle], ball, left_score, right_score, FONT_LARGE_DIGITAL)

        # Display "MODE: CLASSIC" at top left
        mode_text = FONT_SMALL_DIGITAL.render("MODE: CLASSIC", True, GREY)
        WIN.blit(mode_text, (10, 10))
        pygame.display.update()

        ball.move()
        handle_ball_collision(ball, left_paddle, right_paddle, HEIGHT)
        handle_paddle_movement(keys, left_paddle, right_paddle, HEIGHT)

        if state == PLAYING and keys[pygame.K_m]:
            state = MENU
            left_score, right_score = reset(ball, left_paddle, right_paddle)

        if ball.pos[0] - ball.radius < 0:
            right_score += 1
            ball.reset()
        elif ball.pos[0] + ball.radius > WIDTH:
            left_score += 1
            ball.reset()

        if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
            win_text = "Left Player Won!" if left_score > right_score else "Right Player Won!"
            text = FONT_BIG_DIGITAL.render(win_text, True, PURPLE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(3000)
            left_score, right_score = reset(ball, left_paddle, right_paddle)
            state = MENU

if __name__ == '__main__':
    main()
