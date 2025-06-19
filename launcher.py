import pygame
import sys
import subprocess
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), './')))
pygame.init()

from pong.constants import *
from pong.menu import draw_menu
from pong.paddle import PaddleClassic, Paddle
from pong.ball import BallClassic, Ball
from pong.utilities import reset
from pong.helpers import handle_ball_collision as physics_collision, handle_paddle_movement as physics_movement
from pong.utilities import handle_ball_collision as classic_collision, handle_paddle_movement as classic_movement

FONT_MENU = pygame.font.SysFont(*FONT_DEFAULT)
FONT_MENU_SMALL = pygame.font.SysFont(*FONT_SMALL)

# def run_classic():
#     classic_path = os.path.join(os.path.dirname(__file__), "versions", "classic", "main.py")
#     subprocess.run([sys.executable, classic_path])

def run_classic():
    pygame.quit()  # prevent window conflict
    classic_path = os.path.join(os.path.dirname(__file__), "versions", "classic", "main.py")
    subprocess.run([sys.executable, classic_path])
    pygame.init()  # re-init for return


def run_physics():
    physics_path = os.path.join(os.path.dirname(__file__), "versions", "pongception", "main.py")
    subprocess.run([sys.executable, physics_path])

def launcher():
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PongWithIssues")
    clock = pygame.time.Clock()

    selected_mode = 0  # 0 = Classic, 1 = Physics
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
                    else:
                        run_physics()
                elif event.key in [pygame.K_RIGHT, pygame.K_LEFT]:
                    selected_mode ^= 1  # toggle mode (0 ↔ 1)

        draw_menu(WIN, selected_mode)

    pygame.quit()

if __name__ == '__main__':
    launcher()



# VERSIONS = [
#     ("Classic Pong", "versions/classic/main.py"),
#     ("Pongception", "versions/pongception/main.py"),
#     ("BETA", "versions/BETA/main.py"),
# ]

# def launcher_version(script_path):
#     subprocess.run(
#         [sys.executable, script_path], cwd=os.path.dirname(os.path.abspath(__file__))
#         )

# pygame.init()

# win = pygame.display.set_mode((WIDTH_LAUNCHER, HEIGHT_LAUNCHER))
# pygame.display.set_caption("PongWithIssues Launcher")

# def draw_menu(selected):
#     win.fill(BLACK)
#     title = FONT_MENU.render("Select Pong Version", True, PURPLE)
#     win.blit(title, (WIDTH_LAUNCHER//2 - title.get_width()//2, 50))
#     for i, (name, _) in enumerate(VERSIONS):
#         color = PURPLE if i == selected else WHITE
#         label = FONT_MENU_SMALL.render(f"{name}", True, color)
#         win.blit(label, (WIDTH_LAUNCHER//2 - label.get_width()//2, 150 + i*60))
#     pygame.display.update()

# def main():
#     selected = 0
#     while True:
#         draw_menu(selected)
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_UP:
#                     selected = (selected - 1) % len(VERSIONS)
#                 elif event.key == pygame.K_DOWN:
#                     selected = (selected + 1) % len(VERSIONS)
#                 elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
#                     # Launch the selected version
#                     pygame.quit()
#                     script_path = VERSIONS[selected][1]
#                     launcher_version(script_path)
#                     sys.exit()
#         pygame.time.wait(50)

# if __name__ == "__main__":
#     main()
