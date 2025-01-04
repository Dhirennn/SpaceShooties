import pygame
import sys
from os.path import join
from random import randint


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.direction = pygame.Vector2()  # create (0,0) vector
        self.speed = 300
    

    def update(self, dt):
        # print('hi')
        keys = pygame.key.get_pressed()

        # Update x and y values of player's direction vector
        # based on right/left arrows
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

        # Normalize to maintain constant speed diagonally
        self.direction = self.direction.normalize() if self.direction else self.direction

        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE]:
            print('laser boom')





# Initialize pygame
pygame.init()


# Setup dimensions of window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

is_game_running = True

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

pygame.display.set_caption('SpaceShooties')

clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()

# Create Player (spaceship)
player = Player(all_sprites)

while is_game_running:
    dt = clock.tick() / 1000  # convert to s

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()


    # Update sprites
    all_sprites.update(dt)

    # Draw game
    display_surface.fill('Black')

    # Draw sprites in all_sprites group
    all_sprites.draw(display_surface)

    # Update display
    pygame.display.update()


pygame.quit()




