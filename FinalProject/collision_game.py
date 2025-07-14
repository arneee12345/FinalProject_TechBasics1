import pygame
import random
import sys
import math

# === Initialization ===
pygame.init()
pygame.mixer.init()

# === Settings ===
WIDTH, HEIGHT = 1000, 600
FPS = 60

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BG_COLOR = (30, 30, 30)
OVERLAY_COLOR = (0, 0, 0, 180)

music_volume = 0.15
sfx_volume = 0.1

MUSIC_TRACKS = {
    "game": "bg_game.mp3",
    "menu": "bg_pause.mp3",     # Shared by menu, pause, and game over
    "pause": "bg_pause.mp3",
    "gameover": "bg_pause.mp3"
}

# === Load Assets ===
car_options = [
    {"name": "McQueen", "image": pygame.transform.scale(pygame.image.load("cachow.png"), (100, 60))},
    {"name": "Sally", "image": pygame.transform.scale(pygame.image.load("sally.png"), (100, 60))},
    {"name": "Doc Hudson", "image": pygame.transform.scale(pygame.image.load("doc.png"), (100, 60))},
    {"name": "Tow Mater", "image": pygame.transform.scale(pygame.image.load("mater.png"), (100, 60))},
    {"name": "Blue Lightning McQueen", "image": pygame.transform.scale(pygame.image.load("lightningblue.png"), (100, 60))}
]

obstacle_img = pygame.transform.scale(pygame.image.load("cone.png"), (50, 60))
frank_img = pygame.transform.scale(pygame.image.load("frank.png"), (80, 60))

def load_sound(file):
    try:
        s = pygame.mixer.Sound(file)
        s.set_volume(sfx_volume)
        return s
    except pygame.error:
        return None

crash_sound = load_sound("crash.mp3")
frank_sound = load_sound("frank_sound.mp3")
pause_ding = load_sound("pause_ding.mp3")
select_sound = load_sound("select.mp3")

# === Fonts & Screen ===
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lightning McQueen Dodge – Cone Chaos")
clock = pygame.time.Clock()

# === Music Playback ===
def play_music(track_key, fade_ms=1000):
    try:
        pygame.mixer.music.fadeout(fade_ms)
        pygame.time.delay(fade_ms)
        pygame.mixer.music.load(MUSIC_TRACKS[track_key])
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1, fade_ms=fade_ms)
    except (pygame.error, KeyError):
        print(f"⚠️ Couldn't play music for '{track_key}'")

# === Pause Menu ===
pause_options = ["Resume", "Restart", "Main Menu", "Quit"]
pause_index = 0

def draw_pause_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))

    title = font.render("⏸ Game Paused", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))

    for i, option in enumerate(pause_options):
        color = YELLOW if i == pause_index else WHITE
        text = font.render(option, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40 + i * 40))

# === Car Selection & Menu ===
def show_menu_and_car_select():
    play_music("menu")
    while True:
        screen.fill(BG_COLOR)
        title = font.render("🚗 Lightning McQueen – Cone Chaos", True, WHITE)
        instructions = small_font.render("Press SPACE to start | ESC to quit", True, WHITE)

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT // 2 + 10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    break
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        else:
            continue
        break

    selected = 0
    while True:
        screen.fill(BG_COLOR)
        car = car_options[selected]
        label = font.render(f"Choose your car: {car['name']}", True, WHITE)
        info = small_font.render("← / → to change car, ENTER to start", True, WHITE)

        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(car["image"], (WIDTH // 2 - car["image"].get_width() // 2, HEIGHT // 2 - 20))
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 60))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected = (selected - 1) % len(car_options)
                    if select_sound: select_sound.play()
                elif event.key == pygame.K_RIGHT:
                    selected = (selected + 1) % len(car_options)
                    if select_sound: select_sound.play()
                elif event.key == pygame.K_RETURN:
                    return car["image"]

# === Game Classes ===
class Car:
    def __init__(self, image):
        self.image = image
        self.rect = self.image.get_rect(x=150, y=HEIGHT // 2)
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

class Obstacle:
    def __init__(self, speed):
        self.image = obstacle_img
        self.rect = self.image.get_rect(x=WIDTH + random.randint(0, 200),
                                        y=random.randint(0, HEIGHT - 60))
        self.speed = speed

    def move(self):
        self.rect.x -= self.speed

    def draw(self):
        screen.blit(self.image, self.rect)

class Frank:
    def __init__(self):
        self.image = frank_img
        self.rect = self.image.get_rect(x=10, y=HEIGHT // 2)
        self.frame = 0
        self.base_y = HEIGHT // 2
        self.shake_offset = 0
        self.sound_timer = random.randint(300, 500)

    def update(self):
        self.frame += 1
        self.rect.y = int(self.base_y + 150 * math.sin(self.frame * 0.02))
        self.shake_offset = -3 if self.frame % 10 < 5 else 3
        self.sound_timer -= 1

        if self.sound_timer <= 0 and frank_sound:
            frank_sound.play()
            self.sound_timer = random.randint(300, 500)

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y + self.shake_offset))

# === Game Logic ===
def reset_game(player_img):
    return Car(player_img), [Obstacle(5)], Frank(), 0, 5, 100

# === Game Start ===
player_img = show_menu_and_car_select()
play_music("game")
player, obstacles, frank, score, difficulty, spawn_rate = reset_game(player_img)
game_over, paused, last_game_over = False, False, False

# === Game Loop ===
while True:
    clock.tick(FPS)
    screen.fill(BG_COLOR)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
                if pause_ding: pause_ding.play()
                play_music("pause" if paused else "game")
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            player, obstacles, frank, score, difficulty, spawn_rate = reset_game(player_img)
            game_over = False
            last_game_over = False
            play_music("game")

    if not paused and not game_over:
        player.move(keys)
        player.draw()
        frank.update()
        frank.draw()

        if player.rect.left <= frank.rect.right:
            if crash_sound: crash_sound.play()
            play_music("gameover")
            game_over = True

        for o in obstacles:
            o.move()
            o.draw()
            if player.rect.colliderect(o.rect):
                if crash_sound: crash_sound.play()
                play_music("gameover")
                game_over = True

        obstacles = [o for o in obstacles if o.rect.right > frank.rect.right]
        if random.randint(0, spawn_rate) < 2:
            obstacles.append(Obstacle(difficulty))

        score += 1
        if score % 200 == 0 and spawn_rate > 30:
            difficulty += 1
            spawn_rate -= 5

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(small_font.render("Press 'P' to pause", True, WHITE), (WIDTH - 160, 10))

    elif paused:
        draw_pause_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
                    play_music("game")
                elif event.key == pygame.K_UP:
                    pause_index = (pause_index - 1) % len(pause_options)
                    if select_sound: select_sound.play()
                elif event.key == pygame.K_DOWN:
                    pause_index = (pause_index + 1) % len(pause_options)
                    if select_sound: select_sound.play()
                elif event.key == pygame.K_RETURN:
                    selected = pause_options[pause_index]
                    if selected == "Resume":
                        paused = False
                        play_music("game")
                    elif selected == "Restart":
                        player, obstacles, frank, score, difficulty, spawn_rate = reset_game(player_img)
                        paused = False
                        game_over = False
                        play_music("game")
                    elif selected == "Main Menu":
                        player_img = show_menu_and_car_select()
                        player, obstacles, frank, score, difficulty, spawn_rate = reset_game(player_img)
                        paused = False
                        game_over = False
                        play_music("menu")
                    elif selected == "Quit":
                        pygame.quit()
                        sys.exit()

    elif game_over:
        if not last_game_over:
            play_music("gameover")
            last_game_over = True

        msg = font.render("💥 Game Over! Press R to restart", True, WHITE)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))

    pygame.display.flip()






