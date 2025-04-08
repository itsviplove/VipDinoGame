import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.6
JUMP_HEIGHT = -12
OBSTACLE_SPEED = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)

# Initialize Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("VIP Dino Game")
clock = pygame.time.Clock()

# Load Assets
dino_img = pygame.image.load("images/dino.png")  # You need to provide a dino image
cactus_img = pygame.image.load("images/tree1.png")  # You need to provide a cactus image

class Dinosaur:
    def __init__(self):
        self.image = dino_img
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 110
        self.vel_y = 0
        self.jumped = False

    def jump(self):
        if not self.jumped:
            self.vel_y = JUMP_HEIGHT
            self.jumped = True

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom >= SCREEN_HEIGHT - 100:
            self.rect.bottom = SCREEN_HEIGHT - 100
            self.jumped = False
            self.vel_y = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Cactus:
    def __init__(self):
        self.image = cactus_img
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = SCREEN_HEIGHT - 120

    def update(self):
        self.rect.x -= OBSTACLE_SPEED

    def draw(self, screen):
        screen.blit(self.image, self.rect)

def game_over_screen(score):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, BLACK)
    text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50))
    screen.blit(text, text_rect)

    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
    screen.blit(score_text, score_rect)

    restart_text = font.render("Press SPACE to restart", True, GREY)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80))
    screen.blit(restart_text, restart_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

def main():
    dino = Dinosaur()
    obstacles = []
    spawn_timer = 0
    score = 0

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
                        main()

        if game_active:
            # Spawn obstacles
            spawn_timer += 1
            if spawn_timer >= random.randint(40, 100):
                obstacles.append(Cactus())
                spawn_timer = 0

            # Update game elements
            dino.update()
            for obstacle in obstacles:
                obstacle.update()
                if obstacle.rect.right < 0:
                    obstacles.remove(obstacle)

            # Collision detection
            for obstacle in obstacles:
                if dino.rect.colliderect(obstacle.rect):
                    game_active = False

            # Score
            score += 1

            # Draw elements
            pygame.draw.line(screen, BLACK, (0, SCREEN_HEIGHT - 100),
                           (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 3)
            dino.draw(screen)
            for obstacle in obstacles:
                obstacle.draw(screen)

            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {score//10}", True, BLACK)
            screen.blit(score_text, (10, 10))

        else:
            game_over_screen(score//10)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()