import pygame

pygame.init()
pygame.display.set_caption("Pong!") # Windows title

# Constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WIDTH, HEIGHT = 700, 500 # Board size
PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7

FPS = 60 # Frame Per Second

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

class Paddle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    # Fields - Paddle
    COLOR = WHITE # Paddles color
    VEL = 4 # Velocity of the paddle
    
    # Functions - Paddle
    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL
# End of class Paddle

class Ball:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.x_vel = self.MAX_VEL
        self.y_vel = 0

    # Fields - Ball
    MAX_VEL = 5
    COLOR = WHITE

    # Functions - Ball
    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y,), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel
# End of class Ball

# Function for managing the ball movement and collision
def handle_ball_collision(ball, left_paddle, right_paddle):
    if ball.y + ball.radius >= HEIGHT: # Check if the ball has reach the bottom of the board
        ball.y_vel *= -1 # Changing the ball bouncing direction downwards
    elif ball.y - ball.radius <= 0: # Check if the ball has reach the top of the board
        ball.y_vel *= -1 # Changing the ball bouncing direction downwards
    
    if ball.x_vel < 0: # Ball is moving to the left
        if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height: # Ball is in the right paddle height range
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width: # Ball is in the right paddle width range
                ball.x_vel *= -1 # Collision! Changing the ball direction to the right

                # Vertical movement logic
                middle_y = left_paddle.y + left_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (left_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel


    if ball.x_vel > 0: # Ball is moving to the right
        if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height: # Ball is in the right paddle height range
            if ball.x + ball.radius >= right_paddle.x: # Ball is in the right paddle width range
                ball.x_vel *= -1 # Collision! Changing the ball direction to the left

                # Vertical movement logic
                middle_y = right_paddle.y + right_paddle.height / 2
                difference_in_y = middle_y - ball.y
                reduction_factor = (right_paddle.height / 2) / ball.MAX_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1 * y_vel

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
    run = True
    clock = pygame.time.Clock()

    left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

    ball = Ball(WIDTH // 2, HEIGHT // 2, BALL_RADIUS)

    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle,right_paddle], ball)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        Keys = pygame.key.get_pressed()
        
        ball.move()
        handle_ball_collision(ball, left_paddle, right_paddle)

        handle_paddle_movement(Keys, left_paddle, right_paddle)
    pygame.quit()
# End of main()

if __name__ == '__main__':
    main()