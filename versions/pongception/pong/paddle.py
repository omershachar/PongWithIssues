from pong.physics_object import PhysicsObject
import numpy as np

class Paddle(PhysicsObject):
    def __init__(self, x, y, width, height, mass=1000):
        super().__init__(mass, x, y)
        self.original_pos = np.array([x, y], dtype=float)
        self.width = width
        self.height = height
        self.acc = np.array([0.0, 0.0], dtype=float)
        self.MAX_VEL = 7
        self.ACC = 1.2

    def draw(self, win):
        import pygame
        pygame.draw.rect(win, (255, 255, 255), 
                         (int(self.pos[0]), int(self.pos[1]), self.width, self.height))

    def accelerate(self, up=True):
        if up:
            self.acc[1] -= self.ACC
        else:
            self.acc[1] += self.ACC

    def update(self):
        # Apply acceleration to velocity, then decay/friction
        self.vel += self.acc
        self.acc[:] = 0
        # Clamp vertical velocity
        if self.vel[1] > self.MAX_VEL:
            self.vel[1] = self.MAX_VEL
        elif self.vel[1] < -self.MAX_VEL:
            self.vel[1] = -self.MAX_VEL
        # Update position
        self.pos += self.vel
        self.vel[1] *= 0.85  # friction/decay only on y
        # Clamp to screen bounds (assuming HEIGHT is global or import)
        from pong.constants import HEIGHT
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.vel[1] = 0
        elif self.pos[1] + self.height > HEIGHT:
            self.pos[1] = HEIGHT - self.height
            self.vel[1] = 0

    def reset(self):
        self.pos = self.original_pos.copy()
        self.vel[:] = 0
        self.acc[:] = 0
