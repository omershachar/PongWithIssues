"""
main(BETA) -- Main file containing the essentials for a sandbox environment and debugging
"""

import sys
import os
import pygame

# Allow running from subdirectories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import time, math, numpy as np
from pong.constants import *
from pong_BETA.physics_object import *
from pong_BETA.object_manage import Box, _draw_grid, _draw_info, PLAY_W, IMPULSE, FORCE_MAG, FIXED_DT, BG_INFO, BG_PLAY, REST_E, INFO_W

def main():
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("PongWithIssues — BETA Sandbox")

    clock = pygame.time.Clock()

    # Sandbox object
    box = Box(
        pos=(PLAY_W/2, HEIGHT/2),
        size=36,
        color=WHITE,
        mass=1.0,
        gravity=(0.0, 0.0),   # start no gravity
        max_speed=800.0,
        damping=0.25          # mild air drag
    )
    gravity_on = False

    # Fixed-timestep accumulator
    acc = 0.0
    last = time.perf_counter()

    running = True
    while running:
        # --- events (once per frame) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                elif event.key == pygame.K_r:
                    box.pos[:] = (PLAY_W/2, HEIGHT/2)
                    box.vel[:] = (0.0, 0.0)
                elif event.key == pygame.K_q:
                    box.apply_impulse((-IMPULSE, 0))
                elif event.key == pygame.K_e:
                    box.apply_impulse((+IMPULSE, 0))
                elif event.key == pygame.K_w:
                    box.apply_impulse((0, -IMPULSE))
                elif event.key == pygame.K_s:
                    # Note: this 'S' is impulse; arrows also apply continuous force
                    box.apply_impulse((0, +IMPULSE))
                elif event.key == pygame.K_g:
                    gravity_on = not gravity_on
                    box.gravity[:] = (0.0, 900.0) if gravity_on else (0.0, 0.0)
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):  # '+'
                    box.damping = min(5.0, box.damping + 0.05)
                elif event.key == pygame.K_MINUS:
                    box.damping = max(0.0, box.damping - 0.05)
                elif event.key == pygame.K_LEFTBRACKET:
                    box.max_speed = (box.max_speed or 1000.0) - 50.0
                    if box.max_speed < 50.0: box.max_speed = 50.0
                elif event.key == pygame.K_RIGHTBRACKET:
                    box.max_speed = (box.max_speed or 0.0) + 50.0
                elif event.key == pygame.K_m:
                    box.mass = min(10.0, box.mass + 0.5)
                elif event.key == pygame.K_COMMA:
                    box.mass = max(0.1, box.mass - 0.5)

        # Continuous input → forces
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            box.add_force((-FORCE_MAG, 0))
        if keys[pygame.K_RIGHT]:
            box.add_force((+FORCE_MAG, 0))
        if keys[pygame.K_UP]:
            box.add_force((0, -FORCE_MAG))
        if keys[pygame.K_DOWN]:
            box.add_force((0, +FORCE_MAG))

        # --- fixed-step physics ---
        now = time.perf_counter()
        acc += now - last
        last = now
        steps = 0
        while acc >= FIXED_DT:
            box.integrate(FIXED_DT)
            box.play_bounds_bounce((0,0), (PLAY_W, HEIGHT), e=REST_E)
            acc -= FIXED_DT
            steps += 1
            if steps > 5:  # avoid spiral of death
                acc = 0.0
                break

        # --- draw ---
        WIN.fill(BG_PLAY, rect=pygame.Rect(0,0,PLAY_W,HEIGHT))
        _draw_grid(WIN)
        pygame.draw.rect(WIN, BG_INFO, pygame.Rect(PLAY_W,0,INFO_W,HEIGHT))
        box.draw(WIN)
        _draw_info(WIN, box, damping=box.damping, max_speed=box.max_speed, gravity_on=gravity_on)

        # divider
        pygame.draw.line(WIN, (60,70,90), (PLAY_W,0), (PLAY_W,HEIGHT), 2)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
