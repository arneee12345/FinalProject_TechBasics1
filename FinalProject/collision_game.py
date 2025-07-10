import pygame
import random
import sys
import math

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 1000, 600
FPS = 60

# Load images
player_img = pygame.image.load("cachow.png")
player_img = pygame.transform.scale(player_img, (100, 60))

obstacle_img = pygame.image.load("cone.png")
obstacle_img = pygame.transform.scale(obstacle_img, (50, 60))

frank_img = pygame.image.load("frank.png")
frank_img = pygame.transform.scale(frank_img, (80, 60))  # smaller Frank!

# Load sounds
try:
    crash_sound = pygame.mixer.Sound("crash.mp3")
except pygame.error:
    crash_sound = None
    print("⚠️ Couldn't load crash.mp3. Sound disabled.")

try:
    frank_sound = pygame.mixer.Sound("frank_sound.mp3")
except pygame.error:
    frank_sound = None
    print("⚠️ Couldn't load frank_sound.mp3. Frank sound disabled.")

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
        self.rect.x = 150
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

# Frank class
class Frank:
    def __init__(self):
        self.image = frank_img
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.frame = 0
        self.base_y = HEIGHT // 2
        self.shake_offset = 0
        self.sound_timer = random.randint(300, 500)  # ~5-8 seconds

    def update(self):
        self.frame += 1
        # Move up and down smoothly
        self.rect.y = int(self.base_y + 150 * math.sin(self.frame * 0.02))

        # Add jitter effect
        if self.frame % 10 < 5:
            self.shake_offset = -3
        else:
            self.shake_offset = 3

        # Sound occasionally
        self.sound_timer -= 1
        if self.sound_timer <= 0:
            if frank_sound:
                frank_sound.play()
            self.sound_timer = random.randint(300, 500)

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y + self.shake_offset))

# Reset game state
def reset_game():
    player = Car()
    obstacles = [Obstacle(5)]
    frank = Frank()
    score = 0
    difficulty = 5
    spawn_rate = 100
    return player, obstacles, frank, score, difficulty, spawn_rate

# Start game
player, obstacles, frank, score, difficulty, spawn_rate = reset_game()
font = pygame.font.SysFont(None, 36)
game_over = False

# Main game loop
while True:
    clock.tick(FPS)
    screen.fill(BG_COLOR)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            player, obstacles, frank, score, difficulty, spawn_rate = reset_game()
            game_over = False

    if not game_over:
        player.move(keys)
        player.draw()

        # Update & draw Frank
        frank.update()
        frank.draw()

        # End game if player gets too far left (catches by Frank)
        if player.rect.left <= frank.rect.right:
            if crash_sound:
                crash_sound.play()
            game_over = True

        # Obstacle logic
        for obstacle in obstacles:
            obstacle.move()
            obstacle.draw()
            if player.rect.colliderect(obstacle.rect):
                if crash_sound:
                    crash_sound.play()
                game_over = True

        # Remove cones that reach Frank's edge
        obstacles = [o for o in obstacles if o.rect.right > frank.rect.right]

        # Spawn new cones
        if random.randint(0, spawn_rate) < 2:
            obstacles.append(Obstacle(difficulty))

        # Score & difficulty
        score += 1
        if score % 200 == 0 and spawn_rate > 30:
            difficulty += 1
            spawn_rate -= 5

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))

    else:
        msg = font.render("💥 Game Over! Press R to restart", True, WHITE)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()




