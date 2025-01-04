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
        self.COOLDOWN_DURATION = 0  # 400ms between lasers
    

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
            laser_sound.play()


            self.can_shoot = False

            # Capture time that the player pressed space (shoot laser)
            self.laser_shoot_time = pygame.time.get_ticks()

        # Run the cooldown timer
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.speed = 300

        # Randomize locations of the Star objects
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

    def update(self, dt):
        self.rect.centery += self.speed * dt

        if self.rect.top >= WINDOW_HEIGHT:
            self.rect.top = randint(0, WINDOW_WIDTH)
            self.rect.centery = 0


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
        self.original_image = surface
        self.image = self.original_image
        self.rect = self.image.get_frect(center = position)
        self.speed = randint(400, 600)
        self.direction = pygame.Vector2( uniform(-0.5, 0.5) , 1)
        
        # Timer
        self.spawn_time = pygame.time.get_ticks()
        self.LIFETIME = 3000

        self.rotation = 0
        self.rotation_speed = randint(40, 80)
        

    def update(self, dt):
        self.rect.center += self.speed * self.direction * dt

        # rotate meteors
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_frect(center = self.rect.center)

        # Destroy meteor sprites after 3s
        if pygame.time.get_ticks() - self.spawn_time >= self.LIFETIME:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self, dt):
        self.frame_index += 30 * dt

        if int(self.frame_index) < len(self.frames):
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            self.kill()


def display_score():
    current_time = pygame.time.get_ticks() // 100

    text_surface = font.render(f"Score: {score}", True, (240, 240, 240))

    text_rect = text_surface.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))

    pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 1, 10)


    # brb_surface = font.render('20-MIN BREAK, BRB! :D', True, (240, 240, 240))
    # brb_rect = brb_surface.get_frect(midbottom = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 200))

    # display_surface.blit(brb_surface, brb_rect)

    display_surface.blit(text_surface, text_rect)

def collisions():
    global score
    # global is_game_running
    # Check for collisions between player and meteor
    if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask):
        # is_game_running = False
        print('meteor collided with player')


    # Check for collisions between laser sprites and meteors
    for laser in laser_sprites:
        if (pygame.sprite.spritecollide(laser, meteor_sprites, dokill=True)):
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            score += 10


################################# GENERAL SETUP #################################

# Initialize pygame
pygame.init()


# Setup dimensions of window
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

is_game_running = True

score = 0

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
laser_sound = pygame.mixer.Sound(join('audio','laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio','explosion.wav'))
explosion_sound.set_volume(0.5)
# damage_sound = pygame.mixer.Sound(join('audio','damage.ogg'))
# damage_sound.set_volume(0.5)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)

# Meteors
meteor_surface = pygame.image.load(join('images','meteor.png')).convert_alpha()

# Explosion animation
explosion_frames = [pygame.image.load(join('images','explosion', f"{i}.png")).convert_alpha() for i in range(21)]
print(explosion_frames)

# Font
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)

# Meteor spawn event (spawns every 500ms)
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)



################################# MAIN GAME LOOP #################################

game_music.play(loops=-1)

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

    # Check for collisions
    collisions()
        

    # Draw game
    display_surface.fill('#3a2e3f')

    # Draw sprites in all_sprites group
    all_sprites.draw(display_surface)


    display_score()

    # Update display
    pygame.display.update()


pygame.quit()




