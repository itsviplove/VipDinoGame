import pygame
import random
import sys
import os
from pygame import mixer

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.6
JUMP_HEIGHT = -12
INITIAL_SPEED = 10
MAX_SPEED = 20

# Image target sizes
DINO_SIZE = (60, 60)
CACTUS_SIZE = (40, 60)
BIRD_SIZE = (50, 30)
CLOUD_SIZE = (100, 40)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
RED = (255, 0, 0)

# Initialize Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("VIP Dino Game")
clock = pygame.time.Clock()

# Sound handling
SOUND_ENABLED = True
try:
    mixer.init()
    jump_sound = mixer.Sound("jump.wav") if os.path.exists("jump.wav") else None
    collision_sound = mixer.Sound("collision.wav") if os.path.exists("collision.wav") else None
    if os.path.exists("bg_music.mp3"):
        mixer.music.load("bg_music.mp3")
    else:
        mixer.music = None
except:
    SOUND_ENABLED = False


def load_image(path, size):
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        # Create placeholder rectangle if image not found
        surf = pygame.Surface(size)
        surf.fill(RED)
        return surf


# Load Assets with auto-resizing
dino_run = [
    load_image(f"dino_run_{i}.png", DINO_SIZE) for i in range(1, 3)
]
dino_jump = load_image("dino_jump.png", DINO_SIZE)
cactus_img = load_image("cactus.png", CACTUS_SIZE)
bird_img = load_image("bird.png", BIRD_SIZE)
cloud_img = load_image("cloud.png", CLOUD_SIZE)

# High Score System
HIGH_SCORE_FILE = "highscore.txt"


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read())
    except:
        return 0


def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))


class Dinosaur:
    def __init__(self):
        self.run_images = dino_run
        self.jump_image = dino_jump
        self.image = self.run_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 110
        self.vel_y = 0
        self.jumped = False
        self.animation_index = 0
        self.animation_timer = 0

    def jump(self):
        if not self.jumped:
            self.vel_y = JUMP_HEIGHT
            self.jumped = True
            if SOUND_ENABLED and jump_sound:
                jump_sound.play()

    def update(self):
        # Movement
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom >= SCREEN_HEIGHT - 100:
            self.rect.bottom = SCREEN_HEIGHT - 100
            self.jumped = False
            self.vel_y = 0

        # Animation
        if not self.jumped:
            self.animation_timer += 1
            if self.animation_timer >= 5:
                self.animation_index = (self.animation_index + 1) % len(self.run_images)
                self.image = self.run_images[self.animation_index]
                self.animation_timer = 0
        else:
            self.image = self.jump_image

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Obstacle:
    def __init__(self, type):
        self.type = type
        if type == "cactus":
            self.image = cactus_img
            self.rect = self.image.get_rect()
            self.rect.y = SCREEN_HEIGHT - 120
        else:  # Bird
            self.image = bird_img
            self.rect = self.image.get_rect()
            self.rect.y = SCREEN_HEIGHT - 180  # Higher position

        self.rect.x = SCREEN_WIDTH

    def update(self, speed):
        self.rect.x -= speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Cloud:
    def __init__(self):
        self.image = cloud_img
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = random.randint(50, SCREEN_HEIGHT - 200)
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def game_over_screen(score, high_score):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, BLACK)
    text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50))
    screen.blit(text, text_rect)

    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20))
    screen.blit(score_text, score_rect)

    hs_text = font.render(f"High Score: {high_score}", True, GREY)
    hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60))
    screen.blit(hs_text, hs_rect)

    restart_text = font.render("Press SPACE to restart", True, GREY)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100))
    screen.blit(restart_text, restart_rect)

    pygame.display.flip()


def main():
    # Game State
    dino = Dinosaur()
    obstacles = []
    clouds = []
    spawn_timer = 0
    cloud_timer = 0
    score = 0
    high_score = load_high_score()
    game_speed = INITIAL_SPEED

    if SOUND_ENABLED and mixer.music:
        mixer.music.play(-1)

    running = True
    game_active = True

    while running:
        screen.fill(WHITE)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        dino.jump()
                    else:
                        if SOUND_ENABLED and mixer.music:
                            mixer.music.play(-1)
                        main()

        if game_active:
            # Spawn obstacles
            spawn_timer += 1
            if spawn_timer >= random.randint(40, 100):
                obstacles.append(Obstacle("cactus" if random.random() < 0.7 else "bird"))
                spawn_timer = 0

            # Spawn clouds
            cloud_timer += 1
            if cloud_timer >= 100:
                clouds.append(Cloud())
                cloud_timer = 0

            # Update game elements
            dino.update()
            for obstacle in obstacles:
                obstacle.update(game_speed)
                if obstacle.rect.right < 0:
                    obstacles.remove(obstacle)

            for cloud in clouds:
                cloud.update()
                if cloud.rect.right < 0:
                    clouds.remove(cloud)

            # Speed increase
            score += 1
            if score % 500 == 0 and game_speed < MAX_SPEED:
                game_speed += 0.5

            # Collision detection
            for obstacle in obstacles:
                if dino.rect.colliderect(obstacle.rect):
                    if SOUND_ENABLED and collision_sound:
                        collision_sound.play()
                    if SOUND_ENABLED and mixer.music:
                        mixer.music.stop()
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)
                    game_active = False

            # Draw elements
            pygame.draw.line(screen, BLACK, (0, SCREEN_HEIGHT - 100),
                             (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 3)

            # Draw clouds
            for cloud in clouds:
                cloud.draw(screen)

            dino.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)

            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {score // 10}", True, BLACK)
            screen.blit(score_text, (10, 10))

            hs_text = font.render(f"High Score: {high_score // 10}", True, GREY)
            screen.blit(hs_text, (10, 50))

        else:
            game_over_screen(score // 10, high_score // 10)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    if SOUND_ENABLED:
        mixer.quit()


if __name__ == "__main__":
    main()