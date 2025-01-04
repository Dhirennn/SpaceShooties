import pygame
import sys
from os.path import join
from random import randint


pygame.init()

WIND0W_WIDTH = 1280
WINDOW_HEIGHT = 720


is_game_running = True

display_surface = pygame.display.set_mode((WIND0W_WIDTH, WINDOW_HEIGHT))

pygame.display.set_caption("SpaceShooties")


# Import graphics

# Spaceship
spaceship_surf = pygame.image.load(join('images','player.png')).convert_alpha()
spaceship_rect = spaceship_surf.get_frect(center=(WIND0W_WIDTH/2, WINDOW_HEIGHT/2))

# Stars
star_surf = pygame.image.load(join('images','star.png')).convert_alpha()
star_positions = [(randint(0, WIND0W_WIDTH), randint(0, WINDOW_HEIGHT)) for i in range(20)]

# Meteor
meteor_surf = pygame.image.load(join('images','meteor.png')).convert_alpha()
meteor_rect = meteor_surf.get_frect(center=(WIND0W_WIDTH/2, WINDOW_HEIGHT/2))

# Laser
laser_surf = pygame.image.load(join('images','laser.png')).convert_alpha()
laser_rect = laser_surf.get_frect(bottomleft=(20, WINDOW_HEIGHT - 20))



while is_game_running:

    # Event Loop
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            is_game_running = False
            sys.exit()

    display_surface.fill('Black')

    # Randomly place 20 stars on the surface
    for star_position in star_positions:
        display_surface.blit(star_surf, star_position)

    display_surface.blit(spaceship_surf, spaceship_rect)
    display_surface.blit(meteor_surf, meteor_rect)
    display_surface.blit(laser_surf, laser_rect)



    spaceship_rect.left += 0.5

    if spaceship_rect.right == WIND0W_WIDTH:
        spaceship_rect.left = 0

    # Draw the game
    pygame.display.update()

pygame.quit()
