from pong_BETA.physics_object import PhysicsObject
import numpy as np
import pygame

class Ball(PhysicsObject):
    def __init__(self, x, y, radius, mass=1):
        super().__init__(mass, x, y, x_vel=5, y_vel=0)
        self.spin = 0
        self.trail = []
        self.max_trail = 10
        self.radius = radius
        self.original_pos = np.array([x, y], dtype=float)
        self.prev_pos = self.original_pos.copy()
        self.last_hit_by = None

    def draw(self, win):
        for i, pos in enumerate(self.trail):
            alpha = max(50, 255 - i * 20)
            radius = max(1, self.radius - i // 2)
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 255, alpha), (radius, radius), radius)
            win.blit(surface, (pos[0] - radius, pos[1] - radius))
        pygame.draw.circle(win, (255, 255, 255), 
                           (int(self.pos[0]), int(self.pos[1])), self.radius)
        if abs(self.spin) > 0.2:
            import math
            direction = 0 if self.spin > 0 else math.pi
            arc_rect = pygame.Rect(int(self.pos[0] - self.radius), int(self.pos[1] - self.radius), self.radius * 2, self.radius * 2)
            pygame.draw.arc(win, (0, 255, 0), arc_rect, direction, direction + math.pi, 2)

    def move(self):
        self.vel[1] += self.spin * 0.1  # Magnus effect curve on y
        self.pos += self.vel

    def update(self):
        self.prev_pos = self.pos.copy()
        self.trail.insert(0, (int(self.pos[0]), int(self.pos[1])))
        if len(self.trail) > self.max_trail:
            self.trail.pop()
        self.move()

    def reset(self):
        self.pos = self.original_pos.copy()
        self.vel = np.array([5.0, 0.0], dtype=float)  # Always gentle, rightward
        self.prev_pos = self.pos.copy()
        self.spin = 0
        self.last_hit_by = None

    @property
    def speed(self):
        return np.linalg.norm(self.vel)
