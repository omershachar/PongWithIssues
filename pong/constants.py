"""
constants.py -- All game-wide settings and fixed values for PongWithIssues.
"""

# Colors in RGB
BLACK = (0, 0, 0)
DARK_GREY = (64, 64, 64)
GREY = (128, 128, 128)
LIGHT_GREY = (224, 224, 224)
WHITE = (255, 255, 255)

# Sizes
WIDTH, HEIGHT = 700, 500 # Board size
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7

# Physics
MAX_DEFLECTION_SPEED = 5  # Max vertical speed added from paddle hit
SPIN_FACTOR = 0.3

# Others
FPS = 60 # Frame per second
WINNING_SCORE = 3