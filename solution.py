import pygame
pygame.init()
pygame.display.set_caption("Pong!")

# Fields and constants
WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

FPS = 60 #Frame Per Second

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100

class Paddle:

    # Fields
    COLOR = WHITE
    VEL = 4 #Velocity of the paddle
    
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

def draw(win, paddles):
    win.fill(BLACK)

    for paddle in paddles:
        paddle.draw(win)
    
    pygame.display.update()

# Function for moving the paddles
def handle_paddle_movement(Keys, left_paddle, right_paddle):
    if Keys[pygame.K_w]:
        left_paddle.move(up=True)
    if Keys[pygame.K_s]:
        left_paddle.move(up=False)

    if Keys[pygame.K_UP]:
        right_paddle.move(up=True)
    if Keys[pygame.K_DOWN]:
        right_paddle.move(up=False)

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