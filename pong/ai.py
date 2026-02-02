"""
ai.py -- Simple AI opponent for controlling a paddle.
"""

from pong.constants import HEIGHT


def ai_move_paddle(paddle, ball, difficulty=0.7):
    """
    Moves a paddle to track the ball using acceleration-based movement.

    Args:
        paddle (Paddle): The AI-controlled paddle.
        ball (Ball): The ball to track.
        difficulty (float): 0.0 to 1.0 -- higher means tighter tracking.
    """
    paddle_center = paddle.pos[1] + paddle.height / 2
    dead_zone = paddle.height * (0.35 - 0.25 * difficulty)

    # Only actively track when ball is moving toward the AI paddle
    if ball.vel[0] > 0:
        diff = ball.pos[1] - paddle_center
        if abs(diff) > dead_zone:
            paddle.accelerate(up=(diff < 0))
    else:
        # Drift toward center when ball moves away
        center = HEIGHT / 2
        diff = center - paddle_center
        if abs(diff) > dead_zone * 2:
            paddle.accelerate(up=(diff < 0))
