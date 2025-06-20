"""
utilities.py -- File for containing all environment and design methods for the game.
"""

import pygame
import numpy as np
from pong.constants import *

def draw(win, paddles, ball, left_score, right_score, score_font):
    """
    Renders all visual game elements to the window:
    - Background
    - Player scores
    - Paddles
    - Net
    - Ball

    Args:
        win (pygame.Surface): The surface to draw on.
        paddles (list): List of Paddle objects.
        ball (Ball): The Ball object.
        left_score (int): Left player's score.
        right_score (int): Right player's score.
        score_font (pygame.font.Font): Font used to render scores.
    """
    win.fill(BLACK)

    # Draw scores
    left_score_text = score_font.render(f"{left_score}", True, LIGHT_PURPLE)
    right_score_text = score_font.render(f"{right_score}", True, LIGHT_PURPLE)
    win.blit(left_score_text, (WIDTH // 4 - left_score_text.get_width() // 2, 20))
    win.blit(right_score_text, (WIDTH * 3 // 4 - right_score_text.get_width() // 2, 20))

    # Draw paddles and ball
    for paddle in paddles:
        paddle.draw(win)
    ball.draw(win)

    # Draw dashed net
    net_width = 6
    net_height = 28
    gap = 18
    net_segment = pygame.Surface((net_width, net_height), pygame.SRCALPHA)
    net_segment.fill(LIGHT_PURPLE)
    net_segment.set_alpha(120)
    for y in range(0, HEIGHT, net_height + gap):
        win.blit(net_segment, (WIDTH // 2 - net_width // 2, y))

    pygame.display.update()

def reset(ball, left_paddle, right_paddle):
    """
    Reset all game objects.
    """
    ball.reset()
    left_paddle.reset()
    right_paddle.reset()
    return 0, 0
    
def handle_score(ball, left_score, right_score):
    if ball.pos[0] < 0:
        right_score = right_score + 1
        ball.reset()
    elif ball.pos[0] > WIDTH:
        left_score = left_score + 1
        ball.reset()
    return left_score, right_score
    
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