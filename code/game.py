import pygame
import sys
from os.path import join
from random import randint, uniform


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.direction = pygame.Vector2()  # create (0,0) vector
        self.speed = 500

        # Cooldown for laser-shooting
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.COOLDOWN_DURATION = 400  # 400ms between lasers
    

    def laser_timer(self):

        # If the laser is already pressed, we start the cooldown timer
        if not self.can_shoot:
            # amount of time since the start of game
            current_time = pygame.time.get_ticks()

            if current_time - self.laser_shoot_time >= self.COOLDOWN_DURATION:
                self.can_shoot = True


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
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            
            # Create Laser sprite
            Laser(laser_surface, self.rect.midtop, (all_sprites, laser_sprites))


            self.can_shoot = False

            # Capture time that the player pressed space (shoot laser)
            self.laser_shoot_time = pygame.time.get_ticks()

        # Run the cooldown timer
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf

        # Randomize locations of the Star objects
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surface, position, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(midbottom = position)


    def update(self, dt):
        self.rect.centery -= 400 * dt

        # Remove lasers that are out of screen for efficiency
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surface, position, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center = position)
        self.speed = randint(400, 600)
        self.direction = pygame.Vector2( uniform(-0.5, 0.5) , 1)
        
        # Timer
        self.spawn_time = pygame.time.get_ticks()
        self.LIFETIME = 3000
        

    def update(self, dt):
        self.rect.center += self.speed * self.direction * dt

        # Destroy meteor sprites after 3s
        if pygame.time.get_ticks() - self.spawn_time >= self.LIFETIME:
            self.kill()



def collisions():
    # global is_game_running
    # Check for collisions between player and meteor
    if pygame.sprite.spritecollide(player, meteor_sprites, True):
        # is_game_running = False
        print('meteor collided with player')


    # Check for collisions between laser sprites and meteors
    for laser in laser_sprites:
        if (pygame.sprite.spritecollide(laser, meteor_sprites, dokill=True)):
            laser.kill()


################################# GENERAL SETUP #################################

# Initialize pygame
pygame.init()


# Setup dimensions of window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

is_game_running = True

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

pygame.display.set_caption('SpaceShooties')

clock = pygame.time.Clock()

# Create group to hold all sprites
all_sprites = pygame.sprite.Group()

# Meteor sprite group
meteor_sprites = pygame.sprite.Group()

# Laser sprites
laser_sprites = pygame.sprite.Group()

# Add Stars randomly to display_surface
star_surface = pygame.image.load(join('images','star.png')).convert_alpha()

# Add 20 stars with random coordinates to the display_surface
for _ in range(20):
    Star(all_sprites, star_surface)

# Create Player (spaceship) and attach it to the all_sprites group
player = Player(all_sprites)

# Lasers
laser_surface = pygame.image.load(join('images','laser.png')).convert_alpha()

# Meteors
meteor_surface = pygame.image.load(join('images','meteor.png')).convert_alpha()

# Meteor spawn event (spawns every 500ms)
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)



################################# MAIN GAME LOOP #################################

while is_game_running:
    dt = clock.tick() / 1000  # convert to s

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()

        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            # print(f"Spawning meteor at: x={x}, y={y}")
            Meteor(meteor_surface, (x, y), (all_sprites, meteor_sprites))


    # Update sprites
    all_sprites.update(dt)

    collisions()
        

    # Draw game
    display_surface.fill('Black')

    # Draw sprites in all_sprites group
    all_sprites.draw(display_surface)


    



    # Update display
    pygame.display.update()


pygame.quit()




