import pygame
import os
import sys

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Megaman X")

# Clock setup
clock = pygame.time.Clock()


def load_images_from_folder(folder_path, scale_factor=2):
    images = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".png"):
            path = os.path.join(folder_path, filename)
            image = pygame.image.load(path).convert_alpha()

            # Scale up the sprite for better visibility
            width = int(image.get_width() * scale_factor)
            height = int(image.get_height() * scale_factor)
            image = pygame.transform.scale(image, (width, height))

            images.append(image)
    return images


# Get absolute path for assets folder
ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

# Load background image
background_path = os.path.join(ASSETS_PATH, "screen", "fundo_megaman.png")
background = pygame.image.load(background_path).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Load animations
animations = {
    "stop": load_images_from_folder(os.path.join(ASSETS_PATH, "stop")),
    "run": load_images_from_folder(os.path.join(ASSETS_PATH, "run")),
    "shoot": load_images_from_folder(os.path.join(ASSETS_PATH, "shoot")),
    "jump": load_images_from_folder(os.path.join(ASSETS_PATH, "jump")),
    "run_shoot": load_images_from_folder(
        os.path.join(ASSETS_PATH, "run_shoot")),
    "jump_shoot": load_images_from_folder(
        os.path.join(ASSETS_PATH, "jump_shoot")),
}

# Load bullet image
bullet_path = os.path.join(ASSETS_PATH, "bullet", "bullet_mega.png")
bullet_img = pygame.image.load(bullet_path).convert_alpha()

# Load bullet sound
bullet_sound_path = os.path.join(ASSETS_PATH, "sound", "bullet.wav")
bullet_sound = pygame.mixer.Sound(bullet_sound_path)

BULLET_SIZE = 25
bullet_img = pygame.transform.scale(bullet_img, (BULLET_SIZE, BULLET_SIZE))

# Player variables
action = "stop"
frame_index = 0
player_x = 200
player_y = 270
speed = 9
facing_right = True

# Jump variables
is_jumping = False
jump_speed = -15
gravity = 1
vertical_velocity = 0
ground_y = 270

# Bullets list
bullets = []
bullet_speed = 18
shoot_cooldown = 0

ARM_X_FROM_LEFT = 62
ARM_Y_FROM_TOP = 28

# Main loop
running = True
while running:
    # Draw background
    screen.blit(background, (0, 0))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key handling
    keys = pygame.key.get_pressed()
    moving = False

    # Movement logic
    if keys[pygame.K_RIGHT]:
        player_x += speed
        facing_right = True
        moving = True
    if keys[pygame.K_LEFT]:
        player_x -= speed
        facing_right = False
        moving = True

    # Jumping logic
    if not is_jumping:
        if keys[pygame.K_SPACE]:
            is_jumping = True
            vertical_velocity = jump_speed
    else:
        vertical_velocity += gravity
        player_y += vertical_velocity

        # Stop falling when reaching the ground
        if player_y >= ground_y:
            player_y = ground_y
            is_jumping = False

    # Prevent Megaman from leaving the screen
    current_frames = animations["stop"]
    current_width = current_frames[0].get_width()

    if player_x < 0:
        player_x = 0
    if player_x + current_width > WIDTH:
        player_x = WIDTH - current_width

    # Action selection logic
    if is_jumping and keys[pygame.K_z]:
        action = "run_shoot"
    elif moving and keys[pygame.K_z]:
        action = "jump_shoot"
    elif is_jumping:
        action = "jump"
    elif keys[pygame.K_z]:
        action = "shoot"
    elif moving:
        action = "run"
    else:
        action = "stop"

    # Shooting logic
    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    if keys[pygame.K_z] and shoot_cooldown == 0:
        # Compute spawn at the muzzle, aligned for both directions
        if facing_right:
            bullet_x = player_x + ARM_X_FROM_LEFT
        else:
            # Mirror the X offset when facing left
            bullet_offset = current_width - ARM_X_FROM_LEFT - BULLET_SIZE
            bullet_x = player_x + bullet_offset
        bullet_y = player_y + ARM_Y_FROM_TOP

        direction = 1 if facing_right else -1
        bullets.append({"x": bullet_x, "y": bullet_y, "dir": direction})
        bullet_sound.play()
        shoot_cooldown = 10  # Delay between shots

    # Update bullet positions
    for bullet in bullets[:]:
        bullet["x"] += bullet_speed * bullet["dir"]

        # Remove bullet if it goes off-screen
        if bullet["x"] < -50 or bullet["x"] > WIDTH + 50:
            bullets.remove(bullet)

    # Update animation frame
    frames = animations[action]
    frame_index += 0.3
    if frame_index >= len(frames):
        frame_index = 0

    current_image = frames[int(frame_index)]

    # Flip image when facing left
    if not facing_right:
        current_image = pygame.transform.flip(current_image, True, False)

    # Draw player
    screen.blit(current_image, (player_x, player_y))

    # Draw bullets
    for bullet in bullets:
        if bullet["dir"] == 1:
            screen.blit(bullet_img, (bullet["x"], bullet["y"]))
        else:
            flipped_bullet = pygame.transform.flip(bullet_img, True, False)
            screen.blit(flipped_bullet, (bullet["x"], bullet["y"]))

    # Update display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
