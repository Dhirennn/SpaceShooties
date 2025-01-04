import pygame
import sys
from os.path import join
from random import randint, uniform

###############################################################################
#                               GLOBAL CONSTANTS                              #
###############################################################################

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
FPS = 60  # Frames per second

###############################################################################
#                               INITIAL SETUP                                 #
###############################################################################

pygame.init()
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('SpaceShooties')
clock = pygame.time.Clock()

# Load font
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
game_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 80)

# Load images
player_image = pygame.image.load(join('images', 'player.png')).convert_alpha()
star_surface = pygame.image.load(join('images', 'star.png')).convert_alpha()
laser_surface = pygame.image.load(join('images', 'laser.png')).convert_alpha()
meteor_surface = pygame.image.load(join('images', 'meteor.png')).convert_alpha()

# Load explosion frames
explosion_frames = [
    pygame.image.load(join('images','explosion', f"{i}.png")).convert_alpha()
    for i in range(21)
]

# Load sounds
laser_sound = pygame.mixer.Sound(join('audio','laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio','explosion.wav'))
explosion_sound.set_volume(0.5)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)
game_over_music = pygame.mixer.Sound(join('audio', 'No_Hope.wav'))
game_over_music.set_volume(0.8)

# Custom event for meteor spawn
METEOR_EVENT = pygame.event.custom_type()
pygame.time.set_timer(METEOR_EVENT, 500)


###############################################################################
#                                SPRITE CLASSES                               #
###############################################################################

class Player(pygame.sprite.Sprite):
    """The player-controlled spaceship."""

    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale_by(player_image, 1.2)
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 500

        # Laser cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.COOLDOWN_DURATION = 400

    def laser_timer(self):
        """Check and update laser cooldown."""
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.COOLDOWN_DURATION:
                self.can_shoot = True

    def update(self, dt):
        """Update the player's movement and handle laser firing."""
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction.length() != 0 else self.direction

        # Move player
        self.rect.center += self.direction * self.speed * dt

        # Check for laser firing
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surface, self.rect.midtop, (all_sprites, laser_sprites))
            laser_sound.play()
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    """Background stars that continuously move downward."""

    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.speed = 300
        self.rect = self.image.get_frect(
            center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT))
        )

    def update(self, dt):
        """Move the star downward and wrap back to top."""
        self.rect.centery += self.speed * dt
        if self.rect.top >= WINDOW_HEIGHT:
            self.rect.top = 0
            self.rect.centerx = randint(0, WINDOW_WIDTH)

class Laser(pygame.sprite.Sprite):
    """Player-fired laser that moves upward."""

    def __init__(self, surface, position, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(midbottom=position)

    def update(self, dt):
        """Move laser upward and remove it if it goes off-screen."""
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    """Randomly spawned meteors that move downward at an angle."""

    def __init__(self, surface, position, groups):
        super().__init__(groups)
        self.original_image = surface
        self.image = self.original_image
        self.rect = self.image.get_frect(center=position)
        self.speed = randint(400, 600)
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)

        # Rotation
        self.rotation = 0
        self.rotation_speed = randint(40, 80)

        # Lifetime (meteor is destroyed automatically after 3s)
        self.spawn_time = pygame.time.get_ticks()
        self.LIFETIME = 3000  # ms

    def update(self, dt):
        """Move and rotate the meteor, and remove it after lifetime."""
        self.rect.center += self.speed * self.direction * dt

        # Rotate meteors
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_frect(center=self.rect.center)

        # Remove meteor after lifetime
        if pygame.time.get_ticks() - self.spawn_time >= self.LIFETIME:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    """Animated explosion that plays frames and destroys itself after finishing."""

    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=pos)

    def update(self, dt):
        """Animate the explosion by cycling through frames."""
        self.frame_index += 30 * dt
        if int(self.frame_index) < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


###############################################################################
#                            GAME LOGIC FUNCTIONS                             #
###############################################################################

def display_score(score):
    """Display the current score in the bottom center of the screen."""
    text_surface = font.render(f"Score: {score}", True, (240, 240, 240))
    text_rect = text_surface.get_frect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))

    # Draw a semi-transparent rect behind the text
    pygame.draw.rect(display_surface, (240, 240, 240),
                     text_rect.inflate(20, 10).move(0, -8), width=1, border_radius=10)

    display_surface.blit(text_surface, text_rect)

def collisions(player, meteor_sprites, laser_sprites, explosion_frames):
    """
    Handle collisions between:
    - Player and Meteors
    - Lasers and Meteors

    Returns:
        hit_player (bool): True if the player is hit by a meteor, otherwise False.
        score_increase (int): The score increment from meteor-laser collisions.
    """
    # Player - Meteor collision
    hit_player = pygame.sprite.spritecollide(
        player, meteor_sprites, True, pygame.sprite.collide_mask
    )
    player_hit = len(hit_player) > 0  # True if any meteor collided

    # Laser - Meteor collision
    score_increase = 0
    for laser in laser_sprites:
        hit_meteors = pygame.sprite.spritecollide(
            laser, meteor_sprites, dokill=True
        )
        if hit_meteors:
            laser.kill()
            # Explosion at laser's position
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            explosion_sound.play()
            # Increase score for each meteor destroyed
            score_increase += 10 * len(hit_meteors)

    return player_hit, score_increase


def show_game_over_screen():
    """
    Display a 'Game Over' screen with options to restart or quit.
    Allows the player to press 'R' to restart or 'Q' to quit.
    """
    # Stop the game music
    game_music.stop()

    # Play the game over music
    game_over_music.play(loops=-1)

    # Simple "Game Over" loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart the game
                    return  # Exit this function to restart the game loop
                if event.key == pygame.K_q:  # Quit the game
                    pygame.quit()
                    sys.exit()

        # Fill background
        display_surface.fill('#1a1a1a')

        # Game Over text
        game_over_surface = font.render("GAME OVER", True, (240, 50, 50))
        game_over_rect = game_over_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 100))
        display_surface.blit(game_over_surface, game_over_rect)

        # Restart instructions
        restart_surface = font.render("Press R to Restart", True, (240, 240, 240))
        restart_rect = restart_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        display_surface.blit(restart_surface, restart_rect)

        # Quit instructions
        quit_surface = font.render("Press Q to Quit", True, (240, 240, 240))
        quit_rect = quit_surface.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 100))
        display_surface.blit(quit_surface, quit_rect)

        pygame.display.update()
        clock.tick(FPS)



def run_game():
    """
    Main function to run the game loop.
    - Initializes groups and sprites.
    - Runs the main loop for gameplay until player is hit.
    - Shows a game over screen afterward with options to restart or quit.
    """
    while True:  # Loop to allow restarting the game
        game_over_music.stop()
        # Initialize music
        game_music.play(loops=-1)

        # Create sprite groups
        global all_sprites, meteor_sprites, laser_sprites
        all_sprites = pygame.sprite.Group()
        meteor_sprites = pygame.sprite.Group()
        laser_sprites = pygame.sprite.Group()

        # Create Player
        player = Player(all_sprites)

        # Create initial stars
        for _ in range(20):
            Star(all_sprites, star_surface)

        # Reset score and running state
        score = 0
        is_game_running = True

        # Main game loop
        while is_game_running:
            dt = clock.tick(FPS) / 1000  # Delta time in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == METEOR_EVENT:
                    x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
                    Meteor(meteor_surface, (x, y), (all_sprites, meteor_sprites))

            # Update sprites
            all_sprites.update(dt)

            # Check collisions
            player_hit, score_increase = collisions(
                player, meteor_sprites, laser_sprites, explosion_frames
            )
            if player_hit:
                # Player is hit -> stop game
                is_game_running = False
            score += score_increase

            # Draw everything
            display_surface.fill('#3a2e3f')
            all_sprites.draw(display_surface)

            # Display the score
            display_score(score)

            # Display game name
            game_name_surface = game_font.render("SpaceShooties", True, (240, 240, 240))
            game_name_rect = game_name_surface.get_rect(midtop=(WINDOW_WIDTH / 2, 10))
            display_surface.blit(game_name_surface, game_name_rect)

            pygame.display.update()

        # If we exit the while loop, it means the player got hit -> game over
        show_game_over_screen()



###############################################################################
#                                   RUN GAME                                  #
###############################################################################

if __name__ == "__main__":
    # These two variables are declared here to align with your original code.
    # They get updated in run_game() and collisions().
    score = 0
    is_game_running = True

    run_game()

    # Once the user closes the Game Over screen, we exit.
    pygame.quit()
    sys.exit()
