from pong.constants import *
from pong.paddle import Paddle
from pong.ball import BallClassic as Ball
from pong.utilities import draw as draw_game, reset, handle_ball_collision
from pong.helpers import handle_paddle_movement


class GameWorld:
    def __init__(self):
        self.objects = []

    def add(self, obj):
        self.objects.append(obj)

    def update(self, dt):
        for obj in self.objects:
            obj.integrate(dt)

        for i in range(len(self.objects)):
            for j in range(i + 1, len(self.objects)):
                self.objects[i].resolve_collision(self.objects[j])
