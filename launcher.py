import asyncio
import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), './')))

if not pygame.get_init():
    pygame.init()

from pong.constants import *
from pong.menu import draw_menu, handle_menu_click, GAME_MODES, get_mode_box_rects
from pong.settings import GameSettings, SettingsMenu
from pong.touch import TouchHandler
from pong import audio
from versions.classic.main import main as run_classic
from versions.pongception.main import main as run_pongception
from versions.BETA.main import main as run_BETA
from versions.cursed.main import main as run_cursed
from versions.sandbox.main import main as run_sandbox

FONT_MENU = FONT_DEFAULT_DIGITAL
FONT_MENU_SMALL = FONT_SMALL_DIGITAL

NUM_MODES = len(GAME_MODES)

# Touch target rects for vs-AI submenu options
_VS_FRIEND_RECT = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 40)
_VS_AI_RECT = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 40)
_VS_BACK_RECT = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 40)

# Touch target for "Press SPACE to start" area
_START_RECT = pygame.Rect(0, HEIGHT - 180, WIDTH, 80)

# Touch target for settings hint area
_SETTINGS_RECT = pygame.Rect(0, HEIGHT - 250, WIDTH, 40)


def draw_vs_menu(win):
    """Draw the 'vs Friend / vs AI' sub-menu screen."""
    win.fill(BLACK)
    title = FONT_MENU.render("Choose Opponent", True, WHITE)
    opt1 = FONT_MENU_SMALL.render("vs Friend", True, GREY)
    opt2 = FONT_MENU_SMALL.render("vs AI", True, GREY)
    back = FONT_MENU_SMALL.render("Back", True, GREY)
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


async def launcher():
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PongWithIssues")
    set_window_icon()
    audio.init()
    clock = pygame.time.Clock()

    selected_mode = 0  # Classic = 0, Pongception = 1, BETA = 2, Sandbox = 3
    running = True
    in_settings = False

    # Game settings (load saved or use defaults)
    settings = GameSettings()
    settings.load()
    settings_menu = SettingsMenu(settings)
    # Apply loaded audio settings
    audio.set_volume(master=settings.master_volume, sfx=settings.sfx_volume)

    # Touch handler for menu
    touch = TouchHandler()
    mode_box_rects = get_mode_box_rects()

    while running:
        clock.tick(FPS)

        if in_settings:
            # Settings menu loop
            for event in pygame.event.get():
                touch.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                    break
                if settings_menu.handle_input(event, touch):
                    in_settings = False
            touch.clear_taps()
            settings_menu.draw(WIN)
        else:
            # Main menu loop
            start_game = False
            for event in pygame.event.get():
                touch.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                    break
                handle_menu_click(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        start_game = True
                    elif event.key == pygame.K_RIGHT:
                        selected_mode = (selected_mode + 1) % NUM_MODES
                    elif event.key == pygame.K_LEFT:
                        selected_mode = (selected_mode - 1) % NUM_MODES
                    elif event.key == pygame.K_s:
                        in_settings = True
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            # Touch: tap on mode boxes to select or start
            for tap_x, tap_y in touch.taps:
                for i, rect in enumerate(mode_box_rects):
                    if rect.collidepoint(tap_x, tap_y):
                        if i == selected_mode:
                            start_game = True
                        else:
                            selected_mode = i
                        break
                # Tap on start area
                if _START_RECT.collidepoint(tap_x, tap_y):
                    start_game = True
                # Tap on settings area
                if _SETTINGS_RECT.collidepoint(tap_x, tap_y):
                    in_settings = True

            touch.clear_taps()

            if start_game and running:
                vs_ai = None
                if selected_mode in (0, 1, 3):
                    # Modes with vs Friend / vs AI sub-menu
                    choosing = True
                    while choosing:
                        draw_vs_menu(WIN)
                        for sub_event in pygame.event.get():
                            touch.handle_event(sub_event)
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
                        # Touch: tap on submenu options
                        for tap_x, tap_y in touch.taps:
                            if _VS_FRIEND_RECT.collidepoint(tap_x, tap_y):
                                vs_ai = False
                                choosing = False
                            elif _VS_AI_RECT.collidepoint(tap_x, tap_y):
                                vs_ai = True
                                choosing = False
                            elif _VS_BACK_RECT.collidepoint(tap_x, tap_y):
                                choosing = False
                        touch.clear_taps()
                        await asyncio.sleep(0)
                    if vs_ai is None:
                        continue
                    if selected_mode == 0:
                        await run_classic(vs_ai=vs_ai, settings=settings)
                    elif selected_mode == 1:
                        await run_pongception(vs_ai=vs_ai, settings=settings)
                    elif selected_mode == 3:
                        await run_cursed(vs_ai=vs_ai, settings=settings)
                elif selected_mode == 2:
                    await run_BETA()
                elif selected_mode == 4:
                    await run_sandbox(settings=settings)
                # Reset display after returning from game
                WIN = pygame.display.set_mode((WIDTH, HEIGHT))
                set_window_icon()

            draw_menu(WIN, selected_mode)

        await asyncio.sleep(0)

    pygame.quit()

if __name__ == '__main__':
    asyncio.run(launcher())
