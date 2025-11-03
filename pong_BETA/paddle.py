from pong_BETA.physics_object import PhysicsObject
import numpy as np
import pygame

class Paddle(PhysicsObject):
    def __init__(self, x, y, width, height, mass=1000, is_right=False):
        super().__init__(mass, x, y)
        self.original_pos = np.array([x, y], dtype=float)
        self.width = width
        self.height = height
        self.MAX_VEL = 7
        self.ACC = 1.2
        self.is_right = is_right

    def draw(self, win):
        pygame.draw.rect(
            win, (255, 255, 255),
            (int(self.pos[0]), int(self.pos[1]), self.width, self.height)
        )

    def accelerate(self, up=None, right=None):
        # Apply acceleration: up/down and left/right
        if up is not None:
            if up:
                self.acc[1] -= self.ACC
            else:
                self.acc[1] += self.ACC
        if right is not None:
            if right:
                self.acc[0] += self.ACC
            else:
                self.acc[0] -= self.ACC

    def update(self):
        self.vel += self.acc
        self.acc[:] = 0
        self.vel[1] = np.clip(self.vel[1], -self.MAX_VEL, self.MAX_VEL)
        self.vel[0] = np.clip(self.vel[0], -self.MAX_VEL, self.MAX_VEL)
        self.pos += self.vel
        self.vel[1] *= 0.85
        self.vel[0] *= 0.85

        from pong.constants import HEIGHT, WIDTH
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.vel[1] = 0
        elif self.pos[1] + self.height > HEIGHT:
            self.pos[1] = HEIGHT - self.height
            self.vel[1] = 0

        # Net crossing prevention
        if not self.is_right:
            # Left paddle
            if self.pos[0] < 0:
                self.pos[0] = 0
                self.vel[0] = 0
            elif self.pos[0] + self.width > WIDTH // 2:
                self.pos[0] = WIDTH // 2 - self.width
                self.vel[0] = 0
        else:
            # Right paddle
            if self.pos[0] < WIDTH // 2:
                self.pos[0] = WIDTH // 2
                self.vel[0] = 0
            elif self.pos[0] + self.width > WIDTH:
                self.pos[0] = WIDTH - self.width
                self.vel[0] = 0

    def reset(self):
        self.pos = self.original_pos.copy()
        self.vel[:] = 0
        self.acc[:] = 0
