import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 480
BALL_SPEED = [5, 5]
WHITE = (255, 255, 255)
FPS = 60

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")

# Initialize paddles and ball
player_paddle = pygame.Rect(50, HEIGHT // 2 - 30, 10, 60)
opponent_paddle = pygame.Rect(WIDTH - 60, HEIGHT // 2 - 30, 10, 60)
ball = pygame.Rect(WIDTH // 2 - 15, HEIGHT // 2 - 15, 20, 20)

# Initialize scores
player_score = 0
opponent_score = 0
font = pygame.font.Font(None, 36)

# Game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player_paddle.y -= 5
    if keys[pygame.K_DOWN]:
        player_paddle.y += 5

    # Ball movement
    ball.x += BALL_SPEED[0]
    ball.y += BALL_SPEED[1]

    # Ball collision with walls
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        BALL_SPEED[1] = -BALL_SPEED[1]

    # Ball collision with paddles
    if ball.colliderect(player_paddle) or ball.colliderect(opponent_paddle):
        BALL_SPEED[0] = -BALL_SPEED[0]

    # Ball out of bounds
    if ball.left <= 0 or ball.right >= WIDTH:
        if ball.left <= 0:
            opponent_score += 1
        else:
            player_score += 1
        ball.x = WIDTH // 2 - 15
        ball.y = HEIGHT // 2 - 15
        BALL_SPEED[0] = -BALL_SPEED[0]

    # Drawing
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, WHITE, player_paddle)
    pygame.draw.rect(screen, WHITE, opponent_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    player_text = font.render(str(player_score), True, WHITE)
    opponent_text = font.render(str(opponent_score), True, WHITE)
    screen.blit(player_text, (WIDTH // 4, 50))
    screen.blit(opponent_text, (3 * WIDTH // 4 - 36, 50))

    pygame.display.flip()
    clock.tick(FPS)
cmd