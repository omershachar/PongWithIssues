import pygame
pygame.init()
pygame.display.set_caption("Pong!") # Windows title

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WIDTH, HEIGHT = 700, 500 # Board size
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100 # Paddles size
BALL_RADIUS = 7 # Ball size

FPS = 60 # Frame Per Second
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) # Not sure...

class Paddle: # Class for storing paddles attributes and methods

    # Constructor
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    # Fields
    COLOR = WHITE # Color of the paddles
    VEL = 4 # Velocity of the paddle
    
    # Functions
    def draw(self, win): # Function for displaying the paddle on the board
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True): # Function for moving the paddle vertically by its velocity
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL
# End of class Paddle

class Ball: # Class for storing ball attributes and methods

    # Constructor
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    # Fields - Ball
    COLOR = WHITE # Color of the ball
    MAX_VEL = 5 # Max velocity of the ball

    # Functions - Ball
    def draw(self, win): # Function for displaying the ball on the board
        pygame.draw.circle(win, self.COLOR, (self.x, self.y,), self.radius)

    def move(self): # Function for moving the ball around the board by its velocity
        self.x += self.x_vel
        self.y += self.y_vel
# End of class Ball


# Function for managing the ball movement and collision
def handle_ball_collision(ball, left_paddle, right_paddle):
    if ball.y + ball.radius >= HEIGHT: # Check if the ball has reach the bottom of the board
        ball.y_vel *= -1 # Changing the ball bouncing direction downwards
    elif ball.y - ball.radius <= 0: # Check if the ball has reach the top of the board
        ball.y_vel *= -1 # Changing the ball bouncing direction downwards
    
    # Ball is moving to the left
    if ball.x_vel < 0:
        # Ball is in the right paddle height range
        if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
            # Ball is in the right paddle width range
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                # Collision! Changing the ball direction to the right
                ball.x_vel *= -1

                # Vertical movement logic
                middle_y = left_paddle.y + left_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel

    # Ball is moving to the right
    if ball.x_vel > 0:
        # Ball is in the right paddle height range
        if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
            # Ball is in the right paddle width range
            if ball.x + ball.radius >= right_paddle.x:
                # Collision! Changing the ball direction to the left
                ball.x_vel *= -1

                # Vertical movement logic
                middle_y = right_paddle.y + right_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel
# End of handle_ball_collision()

# Functions for moving the paddles
def handle_paddle_movement(Keys, left_paddle, right_paddle):
    # Checking if the 'w' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_w] and left_paddle.y - left_paddle.VEL >= 0:
        left_paddle.move(up=True)
    # Checking if the 's' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_s] and left_paddle.y + left_paddle.VEL + left_paddle.height <= HEIGHT:
        left_paddle.move(up=False)

    # Checking if the 'UP' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
        right_paddle.move(up=True)
    # Checking if the 'DOWN' key was pressed, and making sure the paddle won't go out of the board
    if Keys[pygame.K_DOWN] and right_paddle.y + right_paddle.VEL + right_paddle.height <= HEIGHT:
        right_paddle.move(up=False)
# End of handle_paddle_movement()

# Function for drawing the board
def draw(win, paddles, ball):
    win.fill(BLACK)

    for paddle in paddles:
        paddle.draw(win)

    for i in range(10, HEIGHT, HEIGHT//20):
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//20))
    ball.draw(win)
    pygame.display.update()


def main():
    run = True # Endless loop variable
    clock = pygame.time.Clock()

    # Initializing the paddles and the ball on the board
    left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle,right_paddle], ball)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False # Breaking the loop
                break
        Keys = pygame.key.get_pressed() # Getting the pressed keys of the players
        
        ball.move()
        handle_ball_collision(ball, left_paddle, right_paddle)
        handle_paddle_movement(Keys, left_paddle, right_paddle)

    pygame.quit() # Exiting the game
# End of main()

if __name__ == '__main__':
    main()