import math
import pygame

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spaceship")
clock = pygame.time.Clock()

# PLACE YOUR IMAGE HERE (change the path if needed)
IMAGE_PATH = "assets/nave.png"  # your image here

# Load player image (no os/sys usage)
try:
    img = pygame.image.load(IMAGE_PATH).convert_alpha()
except Exception as e:
    print(f"Failed to load image '{IMAGE_PATH}': {e}")
    pygame.quit()
    raise SystemExit

# Optional scaling. Remove this part if you want the original size.
SHIP_SIZE = 40  # reference size (pixels)
img_w, img_h = img.get_size()
scale = (SHIP_SIZE * 2) / max(img_w, img_h)
new_size = (max(1, int(img_w * scale)), max(1, int(img_h * scale)))
ship_image = pygame.transform.smoothscale(img, new_size)

# Ship state variables
x = WIDTH / 2
y = HEIGHT / 2
angle = 0.0  # degrees, 0 points up
vel_x = 0.0
vel_y = 0.0

# Movement parameters (kept slower from prior change)
ROT_SPEED = 90.0   # degrees per second
THRUST = 120.0     # units per second

# Brake mode: 0 = continuous thrust, 1 = thrust only when pressed
BRAKE = 0

running = True
while running:
    dt = clock.tick(60) / 1000.0  # delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                BRAKE = 1 - BRAKE  # toggle brake mode

    keys = pygame.key.get_pressed()

    # Corrected rotation: left decreases angle, right increases angle
    if keys[pygame.K_LEFT]:
        angle -= ROT_SPEED * dt
    if keys[pygame.K_RIGHT]:
        angle += ROT_SPEED * dt

    # Keep angle between 0–360
    angle = angle % 360
    rad = math.radians(angle)

    # Calculate direction vector (0 degrees points up)
    dir_x = math.sin(rad)
    dir_y = -math.cos(rad)

    up_pressed = keys[pygame.K_UP]

    # Movement logic
    if BRAKE == 0:
        if up_pressed:
            vel_x += dir_x * THRUST * dt
            vel_y += dir_y * THRUST * dt
        # optional gentle drag to slow over time (uncomment to enable)
        # vel_x *= 0.995
        # vel_y *= 0.995
    else:
        if up_pressed:
            # set a constant velocity in the facing direction (units/sec)
            vel_x = dir_x * THRUST
            vel_y = dir_y * THRUST
        else:
            vel_x = 0.0
            vel_y = 0.0

    # Update position
    x += vel_x * dt
    y += vel_y * dt

    # Wrap around screen edges
    if x < 0:
        x += WIDTH
    elif x > WIDTH:
        x -= WIDTH
    if y < 0:
        y += HEIGHT
    elif y > HEIGHT:
        y -= HEIGHT

    # Render (background and rotated ship)
    screen.fill((10, 10, 30))
    # Use -angle so the sprite visually matches the movement direction
    rotated = pygame.transform.rotate(ship_image, -angle)
    rect = rotated.get_rect(center=(x, y))
    screen.blit(rotated, rect.topleft)

    pygame.display.flip()

pygame.quit()
