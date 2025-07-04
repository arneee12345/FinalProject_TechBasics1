import pygame
import random
import sys

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
FPS = 60

# Load images
player_img = pygame.image.load("cachow.png")
player_img = pygame.transform.scale(player_img, (100, 60))

obstacle_img = pygame.image.load("cone.png")
obstacle_img = pygame.transform.scale(obstacle_img, (50, 60))

# Load crash sound
try:
    crash_sound = pygame.mixer.Sound("crash.mp3")
except pygame.error:
    print("⚠️ Couldn't load crash.mp3. Sound disabled.")
    crash_sound = None

# Colors
WHITE = (255, 255, 255)
BG_COLOR = (30, 30, 30)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lightning McQueen Dodge – Cone Chaos")
clock = pygame.time.Clock()

# Car class
class Car:
    def __init__(self):
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = HEIGHT // 2
        self.speed = 5

    def move(self, keys):
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

# Obstacle class
class Obstacle:
    def __init__(self, speed):
        self.image = obstacle_img
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH + random.randint(0, 200)
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.speed = speed

    def move(self):
        self.rect.x -= self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

def reset_game():
    player = Car()
    obstacles = [Obstacle(5)]
    score = 0
    difficulty = 5
    spawn_rate = 100  # lower = spawns more often
    return player, obstacles, score, difficulty, spawn_rate

# Start game
player, obstacles, score, difficulty, spawn_rate = reset_game()
font = pygame.font.SysFont(None, 36)
game_over = False

# Main loop
while True:
    clock.tick(FPS)
    screen.fill(BG_COLOR)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            player, obstacles, score, difficulty, spawn_rate = reset_game()
            game_over = False

    if not game_over:
        # Move player
        player.move(keys)
        player.draw()

        # Move and draw obstacles
        for obstacle in obstacles:
            obstacle.move()
            obstacle.draw()
            if player.rect.colliderect(obstacle.rect):
                if crash_sound:
                    crash_sound.play()
                game_over = True

        # Remove off-screen obstacles
        obstacles = [o for o in obstacles if o.rect.x > -o.rect.width]

        # Spawn new obstacles randomly
        if random.randint(0, spawn_rate) < 2:
            obstacles.append(Obstacle(difficulty))

        # Increase difficulty
        score += 1
        if score % 200 == 0 and spawn_rate > 30:
            difficulty += 1
            spawn_rate -= 5  # more frequent spawns

        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

    else:
        game_over_text = font.render("You hit a cone! Press R to restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 200, HEIGHT // 2))

    pygame.display.flip()


