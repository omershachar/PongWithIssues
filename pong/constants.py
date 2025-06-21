"""
constants.py -- All game-wide settings and fixed values for PongWithIssues.
"""

import numpy as np
import pygame
pygame.font.init()

# -------------------- Fonts --------------------

# Digital fonts (custom)
FONT_SMALL_DIGITAL  = pygame.font.Font("pong/FONTS/digital-7.ttf", 20)
FONT_MEDIUM_DIGITAL  = pygame.font.Font("pong/FONTS/digital-7.ttf", 30)
FONT_DEFAULT_DIGITAL = pygame.font.Font("pong/FONTS/digital-7.ttf", 35)
FONT_LARGE_DIGITAL  = pygame.font.Font("pong/FONTS/digital-7.ttf", 45)
FONT_BIG_DIGITAL    = pygame.font.Font("pong/FONTS/digital-7.ttf", 65)
FONT_TITLE_DIGITAL  = pygame.font.Font("pong/FONTS/digital-7.ttf", 80)
ASCII_FONT = pygame.font.Font("pong/FONTS/LiberationMono-Bold.ttf", 24)

# Fallback system fonts (name + size tuples)
FONT_SMALL      = ("comicsans", 25)
FONT_DEFAULT    = ("comicsans", 40)
FONT_LARGE      = ("comicsans", 50)
FONT_BIG        = ("comicsans", 65)
FONT_TITLE      = ("comicsans", 90)
FONT_DATA       = ("consolas", 20)
FONT_DATA_LARGE = ("consolas", 30)

# -------------------- ASCII Title --------------------

PONG_ASCII = """
 _____     _____    _   _    ____     _ 
|  __ \   / ___ \  | \ | |  / ___|   | |
| |__| | | /   \ | |  \| | | |  _    | |
|  ___/  | \___/ | | |\  | | |_| |   |_|
|_|       \_____/  |_| \_|  \____|   (_)
"""

PONG_ASCII_3D = """

██████╗   ██████╗  ███╗   ██╗  ██████╗   ██╗
██╔══██╗ ██╔═══██╗ ████╗  ██║ ██╔════╝   ██║
██████╔╝ ██║   ██║ ██╔██╗ ██║ ██║  ███╗  ██║
██╔═══╝  ██║   ██║ ██║╚██╗██║ ██║   ██║  ╚═╝
██║      ╚██████╔╝ ██║ ╚████║ ╚██████╔╝  ██╗
╚═╝       ╚═════╝  ╚═╝  ╚═══╝  ╚═════╝   ╚═╝
"""

# -------------------- Colors (RGB) --------------------

BLACK         = (0, 0, 0)
DARK_GREY     = (64, 64, 64)
GREY          = (128, 128, 128)
LIGHT_GREY    = (224, 224, 224)
WHITE         = (255, 255, 255)
PURPLE        = (122, 118, 229)
LIGHT_PURPLE  = (185, 183, 232)
LIGHT_RED     = (255, 204, 203) 
RED           = (255, 0, 0)
DARK_RED      = (139, 0, 0)
YELLOW        = (255, 255, 0)

# ----- Fire Colors -----
DARK_ORANGE      = (170, 65, 0)
ORANGE           = (255, 140, 0)
LIGHT_ORANGE     = (255, 180, 50)
GOLD             = (255, 215, 0)
DARK_YELLOW      = (200, 180, 20)
BRIGHT_YELLOW    = (255, 255, 100)
FIERY_RED        = (255, 40, 0)
SCARLET          = (255, 36, 0)
CRIMSON          = (220, 20, 60)
CHERRY           = (255, 70, 70)
AMBER            = (255, 191, 0)
FLAME            = (255, 87, 34)
TANGERINE        = (255, 120, 0)

# ---- Transition colors for smoother fire gradients ----
ORANGE_RED       = (255, 69, 0)
TOMATO           = (255, 99, 71)
DARK_GOLD        = (218, 165, 32)
MELLOW_YELLOW    = (255, 239, 120)
PEACH            = (255, 229, 180)

# -------------------- Screen & Coordinates --------------------

WIDTH, HEIGHT = 800, 800
GAME_MARGIN_X = 10
GAME_FOOTER = np.array([WIDTH // 2, HEIGHT - 30], dtype=int)
MIDDLE_BOARD = np.array([WIDTH // 2, HEIGHT // 2], dtype=int)

MENU_MARGIN_Y = 45
MENU_SUBTITLES_Y = MENU_MARGIN_Y + 300
MENU_FOOTER = HEIGHT - MENU_MARGIN_Y

# -------------------- Paddle Settings --------------------

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 85
PADDLE_SIZE = np.array([PADDLE_WIDTH, PADDLE_HEIGHT], dtype=int)

ORIGINAL_LEFT_PADDLE_POS = np.array([GAME_MARGIN_X, HEIGHT // 2 - PADDLE_HEIGHT // 2], dtype=int)
ORIGINAL_RIGHT_PADDLE_POS = np.array([WIDTH - GAME_MARGIN_X - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2], dtype=int)

PADDLE_DEFAULT_VEL = 4.5
PADDLE_MAX_VEL = 8
PADDLE_DEFAULT_ACC = np.array([0, 1.5], dtype=float)

# -------------------- Ball Settings --------------------

BALL_RADIUS = 7
BALL_DEFAULT_VEL = np.array([5, 0], dtype=float)

# -------------------- Physics Constants --------------------

GRAVITY = 9.81
SPIN_FACTOR = 0.3                # Multiplier for paddle spin effect
MAX_DEFLECTION_SPEED = 5         # Max vertical speed after deflection
FRICTION_COEFFICIENT = 0.4       # Not currently used, placeholder

# -------------------- Game Settings --------------------

FPS = 60
WINNING_SCORE = 3

# Game states
MENU = 0
PLAYING = 1
