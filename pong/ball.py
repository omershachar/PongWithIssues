"""
ball.py -- Class for storing ball attributes and methods
"""

import pygame
import numpy as np
from pong.physics_object import PhysicsObject

class Ball(PhysicsObject):
    def __init__(self, x, y, radius, mass=1):
        super().__init__(mass, x, y, x_vel=5, y_vel=0)
        self.spin = 0
        self.trail = []  # stores past positions
        self.max_trail = 10  # max trail length
        self.radius = radius
        self.original_pos = np.array([x, y], dtype=float)
# End of class Ball

class BallClassic:
    def __init__(self, x, y, radius, color, vel_x, vel_y):
        self.pos = np.array([x,y], dtype=float)
        self.original_pos = np.array([x, y], dtype=float)
        self.radius = radius
        self.color = color
        self.vel = np.array([vel_x, vel_y], dtype=float)

    # Functions
    def draw(self, win): # Drawing the ball on the board
        pygame.draw.circle(win, self.color, self.pos, self.radius)

    def move(self): # Moving the ball around the board by its current velocity
        self.pos += self.vel

    def bounce_box(self, width, height):
        if self.pos[0] <= 0 or self.pos[0] >= width:
            self.vel *= [-1,1]
        if self.pos[1] <= 0 or self.pos[1] >= height:
            self.vel *= [1,-1]

    def reset(self): # Resetting the ball position to its original position
        self.pos[:] = self.original_pos[:]
        self.vel *= [-1, 0]
# End of class BallClassic

class BallPongception(PhysicsObject):
    def __init__(self, x, y, radius, mass=1):
        super().__init__(mass, x, y, x_vel=5, y_vel=0)
        self.spin = 0
        self.trail = []  # stores past positions
        self.max_trail = 10  # max trail length
        self.radius = radius
        self.original_pos = np.array([x, y], dtype=float)

    def draw(self, win):
        import pygame
        # draw trail
        for i, pos in enumerate(self.trail):
            alpha = max(50, 255 - i * 20)
            radius = max(1, self.radius - i // 2)
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 255, alpha), (radius, radius), radius)
            win.blit(surface, (pos[0] - radius, pos[1] - radius))

        # draw main ball
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
        self.trail.insert(0, (int(self.pos[0]), int(self.pos[1])))
        if len(self.trail) > self.max_trail:
            self.trail.pop()
        self.move()

    def reset(self):
        self.pos = self.original_pos.copy()
        self.vel = np.array([-self.vel[0], 0.9], dtype=float)  # Reverse x, set y_vel

    @property
    def speed(self):
        return np.linalg.norm(self.vel)
# End of class BallPongception