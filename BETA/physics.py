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
        self.radius = radius
        self.original_x = x
        self.original_y = y

    def draw(self, win):
        import pygame
        pygame.draw.circle(win, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def update(self):
        self.move()  # reuse existing move
        # optionally add decay/friction logic here

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.x_vel *= -1
        self.y_vel = 0

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
        self.VEL = 4

    def draw(self, win):
        import pygame
        pygame.draw.rect(win, (255, 255, 255), (int(self.x), int(self.y), self.width, self.height))

    def move(self, up=True):
        if up:
            self.y_vel = -self.VEL
        else:
            self.y_vel = self.VEL

    def update(self):
        self.y += self.y_vel
        self.y_vel *= 0.8  # friction

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0
