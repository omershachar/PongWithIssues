import pygame
pygame.init()
pygame.display.set_caption("Pong!")

# Fields and constants
WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

FPS = 60 #Frame Per Second

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100 # Paddles dimensions

class Paddle:

    # Fields
    COLOR = WHITE # Paddles color
    VEL = 4 # Velocity of the paddle
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    # Functions: draw() and move()
    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL
# End of Paddle class


# Function for moving the paddles
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
def draw(win, paddles):
    win.fill(BLACK)
    for paddle in paddles:
        paddle.draw(win)
    pygame.display.update()


def main():
    run = True
    clock = pygame.time.Clock()

    left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

    while run:
        clock.tick(FPS)
        draw(WIN, [left_paddle,right_paddle])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        Keys = pygame.key.get_pressed()
        handle_paddle_movement(Keys, left_paddle, right_paddle)

    pygame.quit()

if __name__ == '__main__':
    main()