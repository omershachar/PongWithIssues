class PhysicsObject:
    def __init__(self, mass, x, y, x_vel=0, y_vel=0):
        self.mass = mass
        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel

    def momentum(self):
        return (self.mass * self.x_vel, self.mass * self.y_vel)

    def apply_impulse(self, impulse_x, impulse_y):
        self.x_vel += impulse_x / self.mass
        self.y_vel += impulse_y / self.mass


class Ball(PhysicsObject):
    def __init__(self, x, y, radius, mass=1):
        super().__init__(mass, x, y, x_vel=5, y_vel=0)
        self.trail = []  # stores past positions
        self.max_trail = 10  # max trail length
        self.radius = radius
        self.original_x = x
        self.original_y = y

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
        pygame.draw.circle(win, (255, 255, 255), (int(self.x), int(self.y)), self.radius)


    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def update(self):
        # Add current position to trail
        self.trail.insert(0, (int(self.x), int(self.y)))
        if len(self.trail) > self.max_trail:
            self.trail.pop()
        self.move()  # reuse existing move
        # optionally add decay/friction logic here

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.x_vel *= -1
        self.y_vel = 0.9

    @property
    def VEL(self):
        return (self.x_vel ** 2 + self.y_vel ** 2) ** 0.5


class Paddle(PhysicsObject):
    def __init__(self, x, y, width, height, mass=1000):
        super().__init__(mass, x, y)
        self.original_x = x
        self.original_y = y
        self.width = width
        self.height = height
        self.VEL = 0
        self.ACC = 1.2
        self.MAX_VEL = 7

    def draw(self, win):
        import pygame
        pygame.draw.rect(win, (255, 255, 255), (int(self.x), int(self.y), self.width, self.height))

    def accelerate(self, up=True):
        if up:
            self.y_vel -= self.ACC
        else:
            self.y_vel += self.ACC

        # Clamp velocity to max speed
        if self.y_vel > self.MAX_VEL:
            self.y_vel = self.MAX_VEL
        elif self.y_vel < -self.MAX_VEL:
            self.y_vel = -self.MAX_VEL

    def update(self):
        self.y += self.y_vel
        self.y_vel *= 0.85  # decay / friction
        # Clamp to screen bounds
        if self.y < 0:
            self.y = 0
            self.y_vel = 0
        elif self.y + self.height > 500:  # HEIGHT
            self.y = 500 - self.height
            self.y_vel = 0


    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0
