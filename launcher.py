import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), './')))
pygame.init()

from pong.constants import *
from pong.menu import draw_menu, handle_menu_click, GAME_MODES
from pong.settings import GameSettings, SettingsMenu
from versions.classic.main import main as run_classic
from versions.pongception.main import main as run_pongception
from versions.BETA.main import main as run_BETA
from versions.sandbox.main import main as run_sandbox

FONT_MENU = pygame.font.SysFont(*FONT_DEFAULT)
FONT_MENU_SMALL = pygame.font.SysFont(*FONT_SMALL)

NUM_MODES = len(GAME_MODES)


def set_window_icon():
    """Set the window icon if available."""
    icon_paths = [
        os.path.join(os.path.dirname(__file__), 'assets', 'icon_32x32.png'),
        os.path.join(os.path.dirname(__file__), 'assets', 'icon.png'),
    ]
    for path in icon_paths:
        if os.path.exists(path):
            try:
                icon = pygame.image.load(path)
                pygame.display.set_icon(icon)
                return
            except pygame.error:
                pass


def launcher():
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PongWithIssues")
    set_window_icon()
    clock = pygame.time.Clock()

    selected_mode = 0  # Classic = 0, Pongception = 1, BETA = 2, Sandbox = 3
    running = True
    in_settings = False

    # Game settings (can be customized in settings menu)
    settings = GameSettings()
    settings_menu = SettingsMenu(settings)

    while running:
        clock.tick(FPS)

        if in_settings:
            # Settings menu loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
                if settings_menu.handle_input(event):
                    in_settings = False
            settings_menu.draw(WIN)
        else:
            # Main menu loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return
                handle_menu_click(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if selected_mode == 0:
                            run_classic()
                        elif selected_mode == 1:
                            run_pongception()
                        elif selected_mode == 2:
                            run_BETA()
                        elif selected_mode == 3:
                            run_sandbox()
                        # Reset display after returning from game
                        WIN = pygame.display.set_mode((WIDTH, HEIGHT))
                        set_window_icon()

                    elif event.key == pygame.K_RIGHT:
                        selected_mode = (selected_mode + 1) % NUM_MODES
                    elif event.key == pygame.K_LEFT:
                        selected_mode = (selected_mode - 1) % NUM_MODES

                    elif event.key == pygame.K_s:
                        in_settings = True

                    elif event.key == pygame.K_ESCAPE:
                        running = False

            draw_menu(WIN, selected_mode)

    pygame.quit()

if __name__ == '__main__':
    launcher()
