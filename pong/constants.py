"""
constants.py -- All game-wide settings and fixed values for PongWithIssues.
"""

import numpy as np
import pygame
pygame.font.init()

FONT_SMALL_DIGITAL = pygame.font.Font("pong/FONTS/digital-7.ttf", 20)
FONT_DEFAULT_DIGITAL = pygame.font.Font("pong/FONTS/digital-7.ttf", 35)
FONT_LARGE_DIGITAL = pygame.font.Font("pong/FONTS/digital-7.ttf", 45)
FONT_BIG_DIGITAL = pygame.font.Font("pong/FONTS/digital-7.ttf", 65)
FONT_TITLE_DIGITAL = pygame.font.SysFont("pong/FONTS/digital-7.ttf", 80)

# Fonts (in a tuple)
FONT_SMALL = ("comicsans", 25)
FONT_DEFAULT = ("comicsans", 40)
FONT_LARGE = ("comicsans", 50)
FONT_BIG = ("comicsans", 65)
FONT_TITLE = ("comicsans", 90)

PONG_ASCII = """
 _____    ____    _   _    ____     _ 
|  __ \  |  _ \  | \ | |  / ___|   | |
| |__| | | | | | |  \| | | |  _    | |
|  ___/  | |_| | | |\  | | |_| |   |_|
|_|      |____/  |_| \_|  \____|   (_)
"""

# Colors in RGB
BLACK = (0, 0, 0)
DARK_GREY = (64, 64, 64)
GREY = (128, 128, 128)
LIGHT_GREY = (224, 224, 224)
WHITE = (255, 255, 255)
PURPLE = (122, 118, 229)
LIGHT_PURPLE = (185, 183, 232)


# Sizes and coordinates
WIDTH, HEIGHT = 800, 800 # Board size
WIDTH_LAUNCHER, HEIGHT_LAUNCHER = 600, 400
MARGIN = 10
MIDDLE_BOARD = np.array([WIDTH // 2, HEIGHT // 2], dtype=int)

PADDLE_WIDTH, PADDLE_HEIGHT = 15, 85
PADDLE_SIZE = np.array([PADDLE_WIDTH,PADDLE_HEIGHT], dtype=int)
ORIGINAL_LEFT_PADDLE_POS = np.array([MARGIN, HEIGHT//2 - PADDLE_HEIGHT//2], dtype=int)
ORIGINAL_RIGHT_PADDLE_POS = np.array([WIDTH - MARGIN - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2], dtype=int)

BALL_RADIUS = 7

# Velocities
PADDLE_DEFAULT_VEL = 4
PADDLE_MAX_VEL = 8
PADDLE_DEFAULT_ACC = np.array([0, 1.5], dtype=float)
BALL_DEFAULT_VEL = (5,0)
BALL_DEFAULT_VEL = np.array([5, 0], dtype=float)

# Physics
GRAVITY = 9.81
MAX_DEFLECTION_SPEED = 5  # Max vertical speed added from paddle hit
SPIN_FACTOR = 0.3
FRICTION_COEFFICIENT = 0.4

# Others
FPS = 60 # Frame per second
WINNING_SCORE = 3
MENU = 0
PLAYING = 1