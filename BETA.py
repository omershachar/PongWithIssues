import pygame
from pong.ball import Ball
from pong.paddle import Paddle
from pong.constants import WHITE, BLACK, HEIGHT, WIDTH, PADDLE_WIDTH, PADDLE_HEIGHT, BALL_RADIUS, WINNING_SCORE, FPS
from pong.helpers import handle_ball_collision, handle_paddle_movement, draw

pygame.init()
SCORE_FONT = pygame.font.SysFont("comicsans", 50)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PongWithIssues BETA")

def main():
    clock = pygame.time.Clock()
    run = True

    left_paddle = Paddle(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    left_score = 0
    right_score = 0

    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score, SCORE_FONT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)

        left_paddle.update()
        right_paddle.update()
        ball.update()

        handle_ball_collision(ball, left_paddle, right_paddle)

        # Scoring logic (using vector position)
        if ball.pos[0] < 0:
            right_score += 1
            ball.reset()
        elif ball.pos[0] > WIDTH:
            left_score += 1
            ball.reset()

        # Win check
        if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
            winner = "Left Player Won!" if left_score > right_score else "Right Player Won!"
            text = SCORE_FONT.render(winner, 1, WHITE)
            WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(4000)

            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0

    pygame.quit()

if __name__ == '__main__':
    main()
