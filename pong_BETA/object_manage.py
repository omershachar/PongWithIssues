"""
object_manage.py -- Handles objects general behavior, methods and monitoring.
"""

import math
from pong.constants import *
from pong_BETA.physics_object import *

INFO_W = 280            # right-side debug panel width
PLAY_W = WIDTH - INFO_W # sandbox area width
BG_PLAY = (12, 16, 24)
BG_INFO = (20, 24, 36)
GRID    = (28, 36, 52)

FORCE_MAG = 1400.0      # arrow key push (N≈px*kg/s^2)
IMPULSE   = 260.0       # Q/E/F impulses (N·s≈px*kg/s)
FIXED_DT  = 1/120       # physics step
REST_E    = 0.90        # bouncy walls in play area

# Fonts (use your constants’ tuples, e.g. FONT_SMALL = ('Consolas', 16))
FONT_INFO = pygame.font.SysFont(*FONT_SMALL)
FONT_HEAD = pygame.font.SysFont(*FONT_DEFAULT)

class Box(PhysicsObject):
    def __init__(self, pos=(PLAY_W/2, HEIGHT/2), size=32, **kw):
        super().__init__(pos=pos, **kw)
        self.size = size

    def draw(self, surf):
        x, y = int(self.pos[0]), int(self.pos[1])
        r = pygame.Rect(0,0,self.size,self.size)
        r.center = (x, y)
        pygame.draw.rect(surf, self.color, r, border_radius=6)

    def play_bounds_bounce(self, origin=(0,0), size=(PLAY_W, HEIGHT), e=1.0):
        # Bounce inside the left sandbox (exclude info panel)
        x0, y0 = origin
        w, h = size
        half = self.size/2
        bounced = False

        # Left/right
        if self.pos[0] - half < x0:
            self.pos[0] = x0 + half
            self.vel[0] = -self.vel[0] * e
            bounced = True
        elif self.pos[0] + half > x0 + w:
            self.pos[0] = x0 + w - half
            self.vel[0] = -self.vel[0] * e
            bounced = True

        # Top/bottom
        if self.pos[1] - half < y0:
            self.pos[1] = y0 + half
            self.vel[1] = -self.vel[1] * e
            bounced = True
        elif self.pos[1] + half > y0 + h:
            self.pos[1] = y0 + h - half
            self.vel[1] = -self.vel[1] * e
            bounced = True

        return bounced

def _draw_grid(surface):
    # light grid for visual sense of speed/acc
    for x in range(0, PLAY_W, 40):
        pygame.draw.line(surface, GRID, (x,0), (x,HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(surface, GRID, (0,y), (PLAY_W,y), 1)

def _draw_info(surface, box, damping, max_speed, gravity_on):
    panel = pygame.Rect(PLAY_W, 0, INFO_W, HEIGHT)
    pygame.draw.rect(surface, BG_INFO, panel)

    def line(y, text, head=False):
        font = FONT_HEAD if head else FONT_INFO
        s = font.render(text, True, LIGHT_PURPLE if head else WHITE)
        surface.blit(s, (PLAY_W + 16, y))

    line(16, "BETA Physics Sandbox", head=True)
    y = 56
    v = box.vel
    p = box.momentum
    speed = float(np.linalg.norm(v))
    pmag  = float(np.linalg.norm(p))
    r, th = box.polar

    stats = [
        f"pos: ({box.pos[0]:7.2f}, {box.pos[1]:7.2f})",
        f"vel: ({v[0]:7.2f}, {v[1]:7.2f})  |speed|={speed:7.2f}",
        f"mom: ({p[0]:7.2f}, {p[1]:7.2f})  |P|={pmag:7.2f}",
        f"polar: r={r:7.2f}, θ={math.degrees(th):7.2f}°",
        f"mass: {box.mass:.2f}",
        f"damping: {damping:.3f}/s",
        f"max_speed: {max_speed if max_speed else '∞'}",
        f"gravity: {'ON' if gravity_on else 'OFF'}  g={box.gravity}",
        f"restitution: {REST_E}",
    ]
    for s in stats:
        line(y, s); y += 24

    y += 8
    line(y, "Controls:", head=True); y += 32
    help_lines = [
        "Arrows: apply force",
        "Q/E: impulse (-x/+x)",
        "W/S: impulse (-y/+y)",
        "G: toggle gravity",
        "+/-: damping up/down",
        "[/]: max_speed up/down",
        "M/,: mass up/down",
        "R: reset box",
        "ESC: back to menu",
    ]
    for s in help_lines:
        line(y, s); y += 22

class ObjectsManage:
    """
    A class for managing the game objects
    """
    def __init__(self):
        self.objects = []

    def add(self, obj):
        self.objects.append(obj)

    def remove(self, obj):
        self.objects.remove(obj)

    def update(self, dt):
        for obj in self.objects:
            obj.integrate(dt)

        for i in range(len(self.objects)):
            for j in range(i + 1, len(self.objects)):
                self.objects[i].resolve_collision(self.objects[j])
