import pygame
import sys
import subprocess
import os

VERSIONS = [
    ("Classic Pong", "classic/main.py"),
    ("Pongception", "pongception/main.py"),
]

def launcher_version(script_path):
    subprocess.run(
        [sys.executable, f"versions/{script_path}"], cwd=os.path.dirname(os.path.abspath(__file__))
        )

pygame.init()
WIDTH, HEIGHT = 600, 400
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
PURPLE = (122, 118, 229)
FONT = pygame.font.SysFont("comicsans", 40)
SMALL = pygame.font.SysFont("comicsans", 25)
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PongWithIssues Launcher")

def draw_menu(selected):
    win.fill(BLACK)
    title = FONT.render("Select Pong Version", True, PURPLE)
    win.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    for i, (name, _) in enumerate(VERSIONS):
        color = PURPLE if i == selected else WHITE
        label = SMALL.render(f"{name}", True, color)
        win.blit(label, (WIDTH//2 - label.get_width()//2, 150 + i*60))
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
