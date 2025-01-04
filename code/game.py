import pygame
import sys
from os.path import join
from random import randint


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))


    






# Initialize pygame
pygame.init()


# Setup dimensions of window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

is_game_running = True

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

pygame.display.set_caption('SpaceShooties')


while is_game_running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    display_surface.fill('Black')

    all_sprites = pygame.sprite.Group()

    # Create Player (spaceship)
    player = Player(all_sprites)
    all_sprites.add(player)

    all_sprites.draw(display_surface)

    # Update display
    pygame.display.update()







