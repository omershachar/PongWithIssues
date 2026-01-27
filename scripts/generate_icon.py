"""
Generate a simple Pong game icon programmatically.
Creates both PNG and ICO formats.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import pygame
pygame.init()

# Icon sizes for different platforms
ICON_SIZES = [16, 32, 48, 64, 128, 256]

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (122, 118, 229)
LIGHT_PURPLE = (185, 183, 232)


def create_icon(size):
    """Create a simple Pong icon at the given size."""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # Transparent background

    # Background circle
    pygame.draw.circle(surface, PURPLE, (size // 2, size // 2), size // 2 - 2)
    pygame.draw.circle(surface, BLACK, (size // 2, size // 2), size // 2 - 4)

    # Scale factors
    paddle_width = max(2, size // 16)
    paddle_height = max(4, size // 4)
    ball_radius = max(2, size // 12)
    margin = max(2, size // 8)

    # Left paddle
    left_paddle_x = margin
    left_paddle_y = (size - paddle_height) // 2
    pygame.draw.rect(surface, LIGHT_PURPLE,
                     (left_paddle_x, left_paddle_y, paddle_width, paddle_height))

    # Right paddle
    right_paddle_x = size - margin - paddle_width
    right_paddle_y = (size - paddle_height) // 2
    pygame.draw.rect(surface, LIGHT_PURPLE,
                     (right_paddle_x, right_paddle_y, paddle_width, paddle_height))

    # Ball
    ball_x = size // 2
    ball_y = size // 2
    pygame.draw.circle(surface, WHITE, (ball_x, ball_y), ball_radius)

    # Center line (dashed effect)
    center_x = size // 2
    dash_height = max(2, size // 16)
    dash_gap = max(2, size // 12)
    y = margin
    while y < size - margin:
        pygame.draw.line(surface, (80, 80, 80),
                        (center_x, y), (center_x, min(y + dash_height, size - margin)), 1)
        y += dash_height + dash_gap

    return surface


def main():
    output_dir = os.path.join(os.path.dirname(__file__), '../assets')
    os.makedirs(output_dir, exist_ok=True)

    # Generate PNG icons at various sizes
    for size in ICON_SIZES:
        icon = create_icon(size)
        filename = os.path.join(output_dir, f'icon_{size}x{size}.png')
        pygame.image.save(icon, filename)
        print(f'Created: {filename}')

    # Create main icon (256x256)
    main_icon = create_icon(256)
    main_icon_path = os.path.join(output_dir, 'icon.png')
    pygame.image.save(main_icon, main_icon_path)
    print(f'Created: {main_icon_path}')

    # Create favicon for web (32x32)
    favicon = create_icon(32)
    favicon_path = os.path.join(output_dir, 'favicon.png')
    pygame.image.save(favicon, favicon_path)
    print(f'Created: {favicon_path}')

    print('\nIcon generation complete!')
    print('Note: To create .ico file, use an online converter or PIL:')
    print('  pip install Pillow')
    print('  from PIL import Image')
    print('  img = Image.open("assets/icon.png")')
    print('  img.save("assets/icon.ico", format="ICO", sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])')


if __name__ == '__main__':
    main()
