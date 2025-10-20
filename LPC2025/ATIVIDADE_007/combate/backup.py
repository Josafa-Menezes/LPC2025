import math
import pygame

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spaceship")
clock = pygame.time.Clock()

# upload images
IMAGE_PATH = "assets/airplaneGreen.png"
img = pygame.image.load(IMAGE_PATH).convert_alpha()

# scale of images
SHIP_SIZE = 40  # pixels
img_w, img_h = img.get_size()
scale = (SHIP_SIZE * 2) / max(img_w, img_h)
new_size = (max(1, int(img_w * scale)), max(1, int(img_h * scale)))
ship_image = pygame.transform.smoothscale(img, new_size)

# Ship state variables
x = WIDTH / 2
y = HEIGHT / 2
angle = 0.0  # degrees, 0 points up
speed = 180.0
initial_rad = math.radians(angle - 270)
vel_x = math.sin(initial_rad) * speed
vel_y = -math.cos(initial_rad) * speed

# Movement parameters (kept slower from prior change)
ROT_SPEED = 225.0   # degrees per second

# Brake mode
BRAKE = 0

running = True
while running:
    dt = clock.tick(60) / 1000.0  # delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Corrected rotation: left decreases angle, right increases angle
    if keys[pygame.K_LEFT]:
        angle -= ROT_SPEED * dt
    if keys[pygame.K_RIGHT]:
        angle += ROT_SPEED * dt

    # Keep angle between 0–360
    angle = angle % 360
    rad = math.radians(angle - 270)

    # Calculate direction vector (0 degrees points up)
    dir_x = math.sin(rad)
    dir_y = -math.cos(rad)

    # Movement
    vel_x = dir_x * speed
    vel_y = dir_y * speed

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
