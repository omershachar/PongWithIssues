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


def draw_vs_menu(win):
    """Draw the 'vs Friend / vs AI' sub-menu screen."""
    win.fill(BLACK)
    title = FONT_MENU.render("Choose Opponent", True, WHITE)
    opt1 = FONT_MENU_SMALL.render("[1] vs Friend", True, GREY)
    opt2 = FONT_MENU_SMALL.render("[2] vs AI", True, GREY)
    back = FONT_MENU_SMALL.render("[ESC] Back", True, GREY)
    win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 80))
    win.blit(opt1, (WIDTH // 2 - opt1.get_width() // 2, HEIGHT // 2 - 20))
    win.blit(opt2, (WIDTH // 2 - opt2.get_width() // 2, HEIGHT // 2 + 20))
    win.blit(back, (WIDTH // 2 - back.get_width() // 2, HEIGHT // 2 + 70))
    pygame.display.update()


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
                        vs_ai = None
                        if selected_mode in (0, 1):
                            # Show vs Friend / vs AI sub-menu
                            choosing = True
                            while choosing:
                                draw_vs_menu(WIN)
                                for sub_event in pygame.event.get():
                                    if sub_event.type == pygame.QUIT:
                                        pygame.quit()
                                        return
                                    if sub_event.type == pygame.KEYDOWN:
                                        if sub_event.key == pygame.K_1:
                                            vs_ai = False
                                            choosing = False
                                        elif sub_event.key == pygame.K_2:
                                            vs_ai = True
                                            choosing = False
                                        elif sub_event.key == pygame.K_ESCAPE:
                                            choosing = False
                            if vs_ai is None:
                                continue
                            if selected_mode == 0:
                                run_classic(vs_ai=vs_ai)
                            else:
                                run_pongception(vs_ai=vs_ai)
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
