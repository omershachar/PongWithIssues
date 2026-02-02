"""
pong - Shared core library for PongWithIssues.

Exports the Game class used by AI training modules.
"""

import pygame
from pong.constants import (
    WIDTH, HEIGHT, FPS, BALL_RADIUS, LIGHT_PURPLE, BALL_DEFAULT_VEL,
    ORIGINAL_LEFT_PADDLE_POS, ORIGINAL_RIGHT_PADDLE_POS, PADDLE_SIZE,
    FONT_LARGE_DIGITAL, FONT_SMALL_DIGITAL, GREY, BLACK, WHITE
)
from pong.ball import Ball
from pong.paddle import Paddle
from pong.utilities import handle_ball_collision


class GameInfo:
    """Holds per-frame game state for AI training."""

    def __init__(self, left_hits, right_hits, left_score, right_score):
        self.left_hits = left_hits
        self.right_hits = right_hits
        self.left_score = left_score
        self.right_score = right_score


class Game:
    """
    Self-contained Pong game used by AI training modules.

    Provides loop(), draw(), and move_paddle() so NEAT genomes
    can play against each other or a human.
    """

    def __init__(self, window, width, height):
        self.window = window
        self.width = width
        self.height = height

        self.left_paddle = Paddle(
            10, height // 2 - PADDLE_SIZE[1] // 2,
            *PADDLE_SIZE, mode='classic'
        )
        self.right_paddle = Paddle(
            width - 10 - PADDLE_SIZE[0], height // 2 - PADDLE_SIZE[1] // 2,
            *PADDLE_SIZE, mode='classic'
        )
        self.ball = Ball(
            width // 2, height // 2, BALL_RADIUS, LIGHT_PURPLE,
            vel=BALL_DEFAULT_VEL, mode='classic'
        )

        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0

    def _handle_collision(self):
        """Handle ball-wall and ball-paddle collisions, track hits."""
        ball = self.ball
        lp = self.left_paddle
        rp = self.right_paddle

        # Wall bounce (top/bottom)
        if ball.pos[1] - ball.radius <= 0:
            ball.vel[1] = abs(ball.vel[1])
        elif ball.pos[1] + ball.radius >= self.height:
            ball.vel[1] = -abs(ball.vel[1])

        # Left paddle collision
        if (ball.vel[0] < 0
                and lp.pos[0] <= ball.pos[0] - ball.radius <= lp.pos[0] + lp.width
                and lp.pos[1] <= ball.pos[1] <= lp.pos[1] + lp.height):
            ball.vel[0] = abs(ball.vel[0])
            mid = lp.pos[1] + lp.height / 2
            diff = ball.pos[1] - mid
            ball.vel[1] = diff / (lp.height / 2) * abs(ball.vel[0])
            self.left_hits += 1

        # Right paddle collision
        if (ball.vel[0] > 0
                and rp.pos[0] <= ball.pos[0] + ball.radius <= rp.pos[0] + rp.width
                and rp.pos[1] <= ball.pos[1] <= rp.pos[1] + rp.height):
            ball.vel[0] = -abs(ball.vel[0])
            mid = rp.pos[1] + rp.height / 2
            diff = ball.pos[1] - mid
            ball.vel[1] = diff / (rp.height / 2) * abs(ball.vel[0])
            self.right_hits += 1

    def loop(self):
        """Advance one frame. Returns GameInfo."""
        self.ball.move()
        self._handle_collision()

        # Scoring
        if self.ball.pos[0] - self.ball.radius < 0:
            self.right_score += 1
            self.ball.reset()
        elif self.ball.pos[0] + self.ball.radius > self.width:
            self.left_score += 1
            self.ball.reset()

        return GameInfo(self.left_hits, self.right_hits,
                        self.left_score, self.right_score)

    def draw(self, draw_score=True, draw_hits=False):
        """Render the game state."""
        self.window.fill(BLACK)

        # Draw paddles and ball
        self.left_paddle.draw(self.window)
        self.right_paddle.draw(self.window)
        self.ball.draw(self.window)

        # Center line
        for i in range(10, self.height, self.height // 20):
            pygame.draw.rect(
                self.window, GREY,
                (self.width // 2 - 1, i, 2, self.height // 40)
            )

        if draw_score:
            left_text = FONT_LARGE_DIGITAL.render(str(self.left_score), True, WHITE)
            right_text = FONT_LARGE_DIGITAL.render(str(self.right_score), True, WHITE)
            self.window.blit(left_text, (self.width // 4 - left_text.get_width() // 2, 20))
            self.window.blit(right_text, (3 * self.width // 4 - right_text.get_width() // 2, 20))

        if draw_hits:
            left_text = FONT_SMALL_DIGITAL.render(str(self.left_hits), True, WHITE)
            right_text = FONT_SMALL_DIGITAL.render(str(self.right_hits), True, WHITE)
            self.window.blit(left_text, (self.width // 4 - left_text.get_width() // 2, 20))
            self.window.blit(right_text, (3 * self.width // 4 - right_text.get_width() // 2, 20))

    def move_paddle(self, left=True, up=True):
        """
        Move a paddle up or down. Returns False if the move would go
        off screen (used by AI fitness penalty).
        """
        paddle = self.left_paddle if left else self.right_paddle
        vel = paddle.fixed_vel if hasattr(paddle, 'fixed_vel') else 4.5

        if up:
            if paddle.pos[1] - vel < 0:
                return False
            paddle.pos[1] -= vel
        else:
            if paddle.pos[1] + paddle.height + vel > self.height:
                return False
            paddle.pos[1] += vel

        return True

    def reset(self):
        """Reset the game to initial state."""
        self.ball.reset()
        self.left_paddle.reset()
        self.right_paddle.reset()
        self.left_score = 0
        self.right_score = 0
        self.left_hits = 0
        self.right_hits = 0
