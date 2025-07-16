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
flash_time = None


MUSIC_TRACKS = {
    "game": "bg_game.mp3",
    "menu": "bg_pause.mp3",     # Shared by menu, pause, and game over
    "pause": "bg_pause.mp3",
    "gameover": "bg_pause.mp3"
}

# === Load Assets ===
car_options = [
    {"name": "McQueen", "image": pygame.transform.scale(pygame.image.load("mcqueen.png"), (100, 60))},
    {"name": "Sally", "image": pygame.transform.scale(pygame.image.load("sally.png"), (100, 60))},
    {"name": "Doc Hudson", "image": pygame.transform.scale(pygame.image.load("doc.png"), (100, 60))},
    {"name": "Tow Mater", "image": pygame.transform.scale(pygame.image.load("mater.png"), (100, 60))},
    {"name": "Yellow Car", "image": pygame.transform.scale(pygame.image.load("yellowcar.png"), (100, 60))},
    {"name": "Hippie Bus", "image": pygame.transform.scale(pygame.image.load("hippie.png"), (100, 60))},
    {"name": "Guido", "image": pygame.transform.scale(pygame.image.load("guido.png"), (100, 60))},
    {"name": "Pink Car", "image": pygame.transform.scale(pygame.image.load("pinkcar.png"), (100, 60))},
]

power_shield_img = pygame.transform.scale(pygame.image.load("power_shield.png"), (40, 40))
power_slow_img = pygame.transform.scale(pygame.image.load("power_slow.png"), (40, 40))
power_magnet_img = pygame.transform.scale(pygame.image.load("power_magnet.png"), (40, 40))
power_double_img = pygame.transform.scale(pygame.image.load("power_double.png"), (40, 40))

coin_img = pygame.transform.scale(pygame.image.load("coin.png"), (40, 40))

pickup_message = ""
pickup_timer = 0  # milliseconds

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
coin_pickup_sound = load_sound("coin_pickup.mp3")
powerup_pickup_sound = load_sound("powerup_pickup.mp3")

# === Fonts & Screen ===
font = pygame.font.Font("pixelfont.otf", 36)
small_font = pygame.font.Font("pixelfont.otf", 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lightning McQueen Dodge – Cone Chaos")
clock = pygame.time.Clock()

# === Music Playback ===
def play_music(track_key, fade_ms=0):
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(MUSIC_TRACKS[track_key])
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1)
    except (pygame.error, KeyError):
        print(f"⚠️ Couldn't play music for '{track_key}'")


# === Pause Menu ===
pause_options = ["Resume", "Restart", "Main Menu", "Quit"]
pause_index = 0

def draw_pause_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))

    title = font.render("Game Paused", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 100))

    for i, option in enumerate(pause_options):
        color = YELLOW if i == pause_index else WHITE
        text = font.render(option, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40 + i * 40))

    score_text = small_font.render(f"Score: {score}", True, YELLOW)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 140))


# === Car Selection & Menu ===
def show_menu_and_car_select():
    play_music("menu")
    while True:
        screen.fill(BG_COLOR)
        title = font.render("Cars – Cone Chaos", True, WHITE)
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
        info = small_font.render("<- / -> to change car, ENTER to start", True, WHITE)

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

# === PowerUps and Coins ===
POWER_UP_TYPES = {
    "shield": {"image": "power_shield.png", "duration": 8},
    "slow": {"image": "power_slow.png", "duration": 5},
    "magnet": {"image": "power_magnet.png", "duration": 6},
    }

class PowerUp:
    def __init__(self, kind):
        self.kind = kind
        self.image = pygame.transform.scale(pygame.image.load(POWER_UP_TYPES[kind]["image"]), (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(WIDTH + 50, WIDTH + 300)
        self.rect.y = random.randint(50, HEIGHT - 50)
        self.speed = 3

    def move(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Coin:
    def __init__(self):
        self.image = pygame.transform.scale(pygame.image.load("coin.png"), (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(WIDTH + 50, WIDTH + 400)
        self.rect.y = random.randint(50, HEIGHT - 50)
        self.speed = 4

    def move(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# === Game Logic ===
def reset_game(player_img):
    return Car(player_img), [Obstacle(5)], Frank(), 0, 5, 100

False, False

# === Game Logic ===
def reset_game(player_img):
    return Car(player_img), [Obstacle(5)], Frank(), 0, 5, 100

coins = []
powerups = []
active_effects = {}  # {'shield': end_time, 'speed': end_time, ...}

def activate_powerup(kind, now):
    global pickup_message, pickup_timer

    duration = POWER_UP_TYPES[kind]["duration"]
    if duration > 0:
        active_effects[kind] = now + duration * 1000
        pickup_message = f"{kind.upper()} Activated!"
        pickup_timer = now + 2000

    if powerup_pickup_sound:
        powerup_pickup_sound.play()

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

    now = pygame.time.get_ticks()
    expired = [k for k in active_effects if now > active_effects[k]]
    for k in expired:
        del active_effects[k]

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
            coins.clear()
            powerups.clear()
            active_effects.clear()
            game_over = False
            last_game_over = False
            play_music("game")

    if not paused and not game_over:
        player.move(keys)
        player.draw()
        frank.update()
        frank.draw()

        slow_factor = 0.5 if 'slow' in active_effects else 1.0

        if player.rect.left <= frank.rect.right and 'invisible' not in active_effects:
            if crash_sound: crash_sound.play()
            play_music("gameover")
            game_over = True

        for o in obstacles:
            o.rect.x -= int(o.speed * slow_factor)
            o.draw()
            if player.rect.colliderect(o.rect) and 'shield' not in active_effects:
                if crash_sound: crash_sound.play()
                play_music("gameover")
                game_over = True
                flash_time = pygame.time.get_ticks()

        obstacles = [o for o in obstacles if o.rect.right > frank.rect.right]
        if random.randint(0, spawn_rate) < 2:
            obstacles.append(Obstacle(difficulty))

        # Spawn coins and powerups
        if random.randint(0, 500) < 2:
            coins.append(Coin())
        if random.randint(0, 800) < 2:
            kind = random.choice(list(POWER_UP_TYPES.keys()))
            powerups.append(PowerUp(kind))

        # Handle coins
        for coin in coins[:]:
            coin.move()
            coin.draw(screen)
            # Magnet effect: attract nearby coins/powerups
            if 'magnet' in active_effects:
                magnet_radius = 150
                magnet_speed = 3

                for coin in coins:
                    dx = player.rect.centerx - coin.rect.centerx
                    dy = player.rect.centery - coin.rect.centery
                    distance = math.hypot(dx, dy)
                    if distance < magnet_radius:
                        angle = math.atan2(dy, dx)
                        coin.rect.x += int(magnet_speed * math.cos(angle))
                        coin.rect.y += int(magnet_speed * math.sin(angle))

                for p in powerups:
                    dx = player.rect.centerx - p.rect.centerx
                    dy = player.rect.centery - p.rect.centery
                    distance = math.hypot(dx, dy)
                    if distance < magnet_radius:
                        angle = math.atan2(dy, dx)
                        p.rect.x += int(magnet_speed * math.cos(angle))
                        p.rect.y += int(magnet_speed * math.sin(angle))
            if player.rect.colliderect(coin.rect):
                coins.remove(coin)
                score += 10
                if coin_pickup_sound:
                    coin_pickup_sound.play()

        # Handle powerups
        for p in powerups[:]:
            p.move()
            p.draw(screen)
            if player.rect.colliderect(p.rect):
                activate_powerup(p.kind, now)
                powerups.remove(p)

        if pygame.time.get_ticks() % 200 < 17:  # roughly every 200ms
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
                        coins.clear()
                        powerups.clear()
                        active_effects.clear()
                        paused = False
                        game_over = False
                        play_music("game")
                    elif selected == "Main Menu":
                        player_img = show_menu_and_car_select()
                        player, obstacles, frank, score, difficulty, spawn_rate = reset_game(player_img)
                        coins.clear()
                        powerups.clear()
                        active_effects.clear()
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

        msg = font.render("Game Over! Press R to restart", True, WHITE)
        score_msg = small_font.render(f"Final Score: {score}", True, YELLOW)
        screen.blit(score_msg, (WIDTH // 2 - score_msg.get_width() // 2, HEIGHT // 2 + 40))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))

    # Show all active effects as messages
    for i, effect in enumerate(active_effects):
        msg = font.render(f"{effect.upper()} ACTIVE", True, YELLOW)
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT - 50 - i * 30))

    if flash_time and pygame.time.get_ticks() - flash_time < 200:
        flash_overlay = pygame.Surface((WIDTH, HEIGHT))
        flash_overlay.fill((255, 0, 0))
        flash_overlay.set_alpha(80)
        screen.blit(flash_overlay, (0, 0))

    pygame.display.flip()

