"""
paddle.py -- Class for storing paddles attributes and methods
"""

import pygame
import numpy as np

class Paddle:
    def __init__(self, x, y, width, height, color, vel):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel = vel
    
    # Functions
    def draw(self, win): # Drawing the paddle on the board
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))

    def move(self, up=True): # Moving the paddle vertically on the board by its fixed velocity
        if up:
            self.y -= self.vel
        else:
            self.y += self.vel
    
    def reset(self): # Resetting the paddle position to his original position
        self.x = self.original_x
        self.y = self.original_y
# End of class Paddle
