import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), './')))
pygame.init()

from pong.constants import *
from pong.menu import draw_menu
from versions.classic.main import main as run_classic
from versions.pongception.main import main as run_pongception
from versions.BETA.main import main as run_BETA

FONT_MENU = pygame.font.SysFont(*FONT_DEFAULT)
FONT_MENU_SMALL = pygame.font.SysFont(*FONT_SMALL)

def launcher():
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PongWithIssues")
    clock = pygame.time.Clock()

    selected_mode = 0  # Classic = 0, Pongception = 1, Setting = 2
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if selected_mode == 0:
                        run_classic()
                        WIN = pygame.display.set_mode((WIDTH, HEIGHT))
                    elif selected_mode == 1:
                        run_pongception()
                        WIN = pygame.display.set_mode((WIDTH, HEIGHT))
                    elif selected_mode == 2:
                        run_BETA()
                        WIN = pygame.display.set_mode((WIDTH, HEIGHT))

                elif event.key in [pygame.K_RIGHT]:
                    selected_mode = (selected_mode + 1) % 3
                elif event.key in [pygame.K_LEFT]:
                    selected_mode = (selected_mode - 1) % 3

                elif event.key == pygame.K_ESCAPE:
                    running = False
        draw_menu(WIN, selected_mode)

    pygame.quit()

if __name__ == '__main__':
    launcher()
