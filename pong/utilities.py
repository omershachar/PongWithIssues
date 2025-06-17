"""
utilities.py -- File for containing all environment and design methods for the classic version.
"""

import pygame
import numpy as np
from pong.constants import *

# Function for drawing the board
def draw(win, paddles, ball, left_score, right_score, score_font):
    win.fill(BLACK)

    left_score_text = score_font.render(f"{left_score}", 1, LIGHT_PURPLE)
    right_score_text = score_font.render(f"{right_score}", 1, LIGHT_PURPLE)
    win.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()//2, 20))
    win.blit(right_score_text, (WIDTH * (3/4) - right_score_text.get_width()//2, 20))

    for paddle in paddles:
        paddle.draw(win)

    for i in range(10, HEIGHT-10, HEIGHT//20): # Drawing the net
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, LIGHT_PURPLE, (WIDTH//2, i, 3, WIDTH//70))
    ball.draw(win)
    pygame.display.update()

def reset(ball, left_paddle, right_paddle):
    ball.reset()
    left_paddle.reset()
    right_paddle.reset()
    return 0, 0
    
"""
physics_objects_classic -- Section containing all physics methods for the game objects collision and movement.
"""

def handle_ball_collision(ball, left_paddle, right_paddle, board_height):
    if ball.pos[1] + ball.radius >= board_height: # Check if the ball has reached the bottom of the board
        ball.vel[1] *= -1 # Changing the ball bouncing direction downwards
    elif ball.pos[1] - ball.radius <= 0: # Check if the ball has reached the top of the board
        ball.vel[1] *= -1 # Changing the ball bouncing direction downwards
    
    # Ball is moving to the left
    if ball.vel[0] < 0:
        # Ball is in the left paddle height range
        if ball.pos[1] >= left_paddle.y and ball.pos[1] <= left_paddle.y + left_paddle.height:
            # Ball is in the left paddle width range
            if ball.pos[0] - ball.radius <= left_paddle.x + left_paddle.width:
                # Collision! Changing the ball direction to the left
                ball.vel[0] *= -1

                # Vertical movement logic
                middle_y = left_paddle.y + left_paddle.height / 2
                difference_in_y = middle_y - ball.pos[1]
                reduction_factor = (left_paddle.height / 2) / abs(ball.vel[0]) # !!
                y_vel = difference_in_y / reduction_factor
                ball.vel[1] = -1 * y_vel

    # Ball is moving to the right
    if ball.vel[0] > 0:
        # Ball is in the right paddle height range
        if ball.pos[1] >= right_paddle.y and ball.pos[1] <= right_paddle.y + right_paddle.height:
            # Ball is in the right paddle width range
            if ball.pos[0] + ball.radius >= right_paddle.x:
                # Collision! Changing the ball direction to the left
                ball.vel[0] *= -1

                # Vertical movement logic
                middle_y = right_paddle.y + right_paddle.height / 2
                difference_in_y = middle_y - ball.pos[1]
                reduction_factor = (right_paddle.height / 2) / abs(ball.vel[0]) # !!
                y_vel = difference_in_y / reduction_factor
                ball.vel[1] = -1 * y_vel
# End of handle_ball_collision()

def handle_paddle_movement(Keys, left_paddle, right_paddle, board_height):
    # Checking if the 'w' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_w] and left_paddle.y - left_paddle.vel >= 0:
        left_paddle.move(up=True)
    # Checking if the 's' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_s] and left_paddle.y + left_paddle.vel + left_paddle.height <= board_height:
        left_paddle.move(up=False)

    # Checking if the 'UP' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_UP] and right_paddle.y - right_paddle.vel >= 0:
        right_paddle.move(up=True)
    # Checking if the 'DOWN' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_DOWN] and right_paddle.y + right_paddle.vel + right_paddle.height <= board_height:
        right_paddle.move(up=False)
# End of handle_paddle_movement()