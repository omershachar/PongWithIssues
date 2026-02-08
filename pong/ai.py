"""
ai.py -- AI opponent for controlling a paddle in Pong.
Supports 10 difficulty levels (1-10) with spin-aware trajectory prediction.

Difficulty ranges from 1 (Beginner) to 10 (Impossible):
  - Lower levels: slow reactions, no prediction, ignores spin, imprecise
  - Higher levels: instant reactions, accurate prediction with spin, precise

Parameters per level:
  reaction_distance  -- how early the AI starts reacting (fraction of screen width)
  prediction_skill   -- blend between tracking current Y vs predicted arrival Y
  spin_awareness     -- how much ball spin is factored into prediction (Magnus effect)
  dead_zone_factor   -- fraction of paddle height used as dead zone (larger = lazier)
  noise              -- random offset in pixels added to target (lower = more precise)
  return_speed       -- how aggressively the AI returns to center when ball is away
"""

import numpy as np
from pong.constants import HEIGHT, WIDTH, BALL_RADIUS


# ----- Difficulty level names (for UI display) -----

DIFFICULTY_NAMES = {
    1: "Beginner",
    2: "Novice",
    3: "Easy",
    4: "Below Avg",
    5: "Average",
    6: "Above Avg",
    7: "Good",
    8: "Hard",
    9: "Expert",
    10: "Impossible",
}


# ----- Parameter presets for each difficulty level -----

DIFFICULTY_PRESETS = {
    1: {   # Beginner -- barely competent, fun for new players
        'reaction_distance': 0.25,
        'prediction_skill':  0.0,
        'spin_awareness':    0.0,
        'dead_zone_factor':  0.50,
        'noise':             70,
        'return_speed':      0.30,
    },
    2: {   # Novice -- reacts late, doesn't predict
        'reaction_distance': 0.35,
        'prediction_skill':  0.0,
        'spin_awareness':    0.0,
        'dead_zone_factor':  0.44,
        'noise':             55,
        'return_speed':      0.35,
    },
    3: {   # Easy -- starts predicting slightly, still no spin sense
        'reaction_distance': 0.45,
        'prediction_skill':  0.15,
        'spin_awareness':    0.0,
        'dead_zone_factor':  0.38,
        'noise':             40,
        'return_speed':      0.40,
    },
    4: {   # Below Average -- some prediction, notices spin a little
        'reaction_distance': 0.55,
        'prediction_skill':  0.30,
        'spin_awareness':    0.15,
        'dead_zone_factor':  0.32,
        'noise':             30,
        'return_speed':      0.50,
    },
    5: {   # Average -- decent tracking, moderate spin awareness
        'reaction_distance': 0.65,
        'prediction_skill':  0.45,
        'spin_awareness':    0.30,
        'dead_zone_factor':  0.25,
        'noise':             22,
        'return_speed':      0.55,
    },
    6: {   # Above Average -- good prediction, respects spin
        'reaction_distance': 0.75,
        'prediction_skill':  0.60,
        'spin_awareness':    0.45,
        'dead_zone_factor':  0.20,
        'noise':             15,
        'return_speed':      0.60,
    },
    7: {   # Good -- strong prediction, reads spin well
        'reaction_distance': 0.85,
        'prediction_skill':  0.75,
        'spin_awareness':    0.60,
        'dead_zone_factor':  0.15,
        'noise':             10,
        'return_speed':      0.70,
    },
    8: {   # Hard -- very accurate, strong spin compensation
        'reaction_distance': 0.92,
        'prediction_skill':  0.85,
        'spin_awareness':    0.78,
        'dead_zone_factor':  0.10,
        'noise':              5,
        'return_speed':      0.80,
    },
    9: {   # Expert -- near-perfect prediction with spin
        'reaction_distance': 1.0,
        'prediction_skill':  0.95,
        'spin_awareness':    0.90,
        'dead_zone_factor':  0.06,
        'noise':              2,
        'return_speed':      0.90,
    },
    10: {  # Impossible -- perfect play, reads spin perfectly
        'reaction_distance': 1.0,
        'prediction_skill':  1.0,
        'spin_awareness':    1.0,
        'dead_zone_factor':  0.03,
        'noise':              0,
        'return_speed':      1.0,
    },
}


# ----- Trajectory prediction -----

def _predict_ball_y(ball, target_x, spin_awareness=1.0):
    """
    Predict the ball's Y position when it reaches target_x.
    Simulates the trajectory frame-by-frame, including:
      - Magnus effect (spin curving the ball vertically)
      - Wall bounces (top and bottom)

    Args:
        ball: The ball object (needs .pos, .vel, .spin, .radius).
        target_x (float): The x-coordinate to predict arrival at.
        spin_awareness (float): 0.0-1.0 -- how much spin is factored in.

    Returns:
        float: Predicted Y position when ball reaches target_x.
    """
    sim_x  = float(ball.pos[0])
    sim_y  = float(ball.pos[1])
    sim_vx = float(ball.vel[0])
    sim_vy = float(ball.vel[1])
    spin   = float(getattr(ball, 'spin', 0)) * spin_awareness
    radius = getattr(ball, 'radius', BALL_RADIUS)

    # Ball not moving horizontally -- just return current Y
    if abs(sim_vx) < 0.01:
        return sim_y

    max_steps = 600  # ~10 seconds at 60fps, safety limit

    for _ in range(max_steps):
        # Magnus effect: spin curves the ball vertically
        sim_vy += spin * 0.1

        # Advance position
        sim_x += sim_vx
        sim_y += sim_vy

        # Wall bounces (top and bottom)
        if sim_y + radius >= HEIGHT:
            sim_y = HEIGHT - radius
            sim_vy *= -1
        elif sim_y - radius <= 0:
            sim_y = radius
            sim_vy *= -1

        # Did we reach the target?
        if sim_vx > 0 and sim_x >= target_x:
            return sim_y
        elif sim_vx < 0 and sim_x <= target_x:
            return sim_y

    return sim_y  # fallback


# ----- Main AI function -----

def ai_move_paddle(paddle, ball, difficulty=5):
    """
    Moves a paddle to track the ball using acceleration-based movement.
    Supports 10 difficulty levels with spin-aware trajectory prediction.

    The AI controls the *right* paddle (reacts when ball.vel[0] > 0).

    Args:
        paddle (Paddle): The AI-controlled paddle.
        ball (Ball): The ball to track.
        difficulty (int): 1 to 10 -- higher means stronger AI.
    """
    # Clamp to valid range
    level = max(1, min(10, int(round(difficulty))))
    params = DIFFICULTY_PRESETS[level]

    paddle_center = paddle.pos[1] + paddle.height / 2
    dead_zone = paddle.height * params['dead_zone_factor']

    # Is ball approaching the AI paddle? (right side)
    ball_approaching = ball.vel[0] > 0

    # Ball progress across screen (0.0 = left edge, 1.0 = right edge)
    ball_progress = ball.pos[0] / WIDTH

    if ball_approaching and ball_progress >= (1.0 - params['reaction_distance']):
        # ---- Ball is approaching and within reaction zone ----

        # Determine target Y based on prediction skill
        if params['prediction_skill'] > 0:
            predicted_y = _predict_ball_y(
                ball,
                paddle.pos[0],
                spin_awareness=params['spin_awareness']
            )
            # Blend between raw ball Y and predicted arrival Y
            target_y = (
                ball.pos[1]
                + (predicted_y - ball.pos[1]) * params['prediction_skill']
            )
        else:
            # No prediction: just track current ball Y
            target_y = ball.pos[1]

        # Add imprecision noise (deterministic per approach to avoid jitter)
        if params['noise'] > 0:
            # Stable noise that changes only when ball position shifts significantly
            chunk = max(1, int(60 - level * 5))  # higher level = finer chunks
            noise_seed = (int(ball.pos[0]) // chunk * 7 + int(abs(ball.vel[1]) * 10)) % 1000
            noise_offset = (noise_seed / 500.0 - 1.0) * params['noise']
            target_y += noise_offset

        diff = target_y - paddle_center

        if abs(diff) > dead_zone:
            paddle.accelerate(up=(diff < 0))
    else:
        # ---- Ball moving away or not yet in reaction zone ----
        # Drift toward center of the screen
        center = HEIGHT / 2
        diff = center - paddle_center
        return_dead = dead_zone * (2.5 - params['return_speed'] * 1.5)

        if abs(diff) > return_dead:
            paddle.accelerate(up=(diff < 0))
