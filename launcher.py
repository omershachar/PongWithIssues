import pygame
import sys
import subprocess
import os
from pong.constants import *

VERSIONS = [
    ("Classic Pong", "versions/classic/main.py"),
    ("Pongception", "versions/pongception/main.py"),
    ("BETA", "versions/BETA/main.py"),
]

def launcher_version(script_path):
    subprocess.run(
        [sys.executable, script_path], cwd=os.path.dirname(os.path.abspath(__file__))
        )

pygame.init()
FONT_MENU = pygame.font.SysFont(*FONT_DEFAULT)
FONT_MENU_SMALL = pygame.font.SysFont(*FONT_SMALL)
win = pygame.display.set_mode((WIDTH_LAUNCHER, HEIGHT_LAUNCHER))
pygame.display.set_caption("PongWithIssues Launcher")

def draw_menu(selected):
    win.fill(BLACK)
    title = FONT_MENU.render("Select Pong Version", True, PURPLE)
    win.blit(title, (WIDTH_LAUNCHER//2 - title.get_width()//2, 50))
    for i, (name, _) in enumerate(VERSIONS):
        color = PURPLE if i == selected else WHITE
        label = FONT_MENU_SMALL.render(f"{name}", True, color)
        win.blit(label, (WIDTH_LAUNCHER//2 - label.get_width()//2, 150 + i*60))
    pygame.display.update()

def main():
    selected = 0
    while True:
        draw_menu(selected)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(VERSIONS)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(VERSIONS)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    # Launch the selected version
                    pygame.quit()
                    script_path = VERSIONS[selected][1]
                    launcher_version(script_path)
                    sys.exit()
        pygame.time.wait(50)

if __name__ == "__main__":
    main()
