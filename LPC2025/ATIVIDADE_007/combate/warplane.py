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
IMAGE_PATH_airplane1 = "assets/airplaneGreen.png"
airplane1 = pygame.image.load(IMAGE_PATH_airplane1).convert_alpha()
IMAGE_PATH_airplane2 = "assets/airplaneOrange.png"
airplane2 = pygame.image.load(IMAGE_PATH_airplane2).convert_alpha()

# scale of images
airplane_SIZE = 40  # pixels
img_w, img_h = airplane1.get_size()
scale = (airplane_SIZE * 2) / max(img_w, img_h)
new_size = (max(1, int(img_w * scale)), max(1, int(img_h * scale)))
airplane1_image = pygame.transform.smoothscale(airplane1, new_size)
airplane2_image = pygame.transform.smoothscale(airplane2, new_size)

# state variables
initial_angle = 0.0  # degrees, 0 points up
speed = 180.0
initial_rad = math.radians(initial_angle - 270)

# airplane 1
x1 = WIDTH / 2
y1 = HEIGHT / 2
vel_x1 = math.sin(initial_rad) * speed
vel_y1 = -math.cos(initial_rad) * speed
angle1 = 0.0

# airplane 2
x2 = WIDTH / 4
y2 = HEIGHT / 4
vel_x2 = math.sin(initial_rad) * speed
vel_y2 = -math.cos(initial_rad) * speed
angle2 = 0.0

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
    # airplane 1 controls
    if keys[pygame.K_LEFT]:
        angle1 -= ROT_SPEED * dt
    if keys[pygame.K_RIGHT]:
        angle1 += ROT_SPEED * dt

    # airplane 2 controls
    if keys[pygame.K_a]:
        angle2 -= ROT_SPEED * dt
    if keys[pygame.K_d]:
        angle2 += ROT_SPEED * dt

    # Keep angle between 0–360
    angle1 = angle1 % 360
    angle2 = angle2 % 360
    rad1 = math.radians(angle1 - 270)
    rad2 = math.radians(angle2 - 270)

    # Calculate direction vector (0 degrees points up)
    dir_x1 = math.sin(rad1)
    dir_y1 = -math.cos(rad1)
    dir_x2 = math.sin(rad2)
    dir_y2 = -math.cos(rad2)

    # Movement
    # airplane 1
    vel_x1 = dir_x1 * speed
    vel_y1 = dir_y1 * speed
    # airplane 2
    vel_x2 = dir_x2 * speed
    vel_y2 = dir_y2 * speed
    # Update position
    x1 += vel_x1 * dt
    y1 += vel_y1 * dt
    x2 += vel_x2 * dt
    y2 += vel_y2 * dt

    # Wrap around screen edges
    # airplane 1
    if x1 < 0:
        x1 += WIDTH
    elif x1 > WIDTH:
        x1 -= WIDTH
    if y1 < 0:
        y1 += HEIGHT
    elif y1 > HEIGHT:
        y1 -= HEIGHT
    # airplane 2
    if x2 < 0:
        x2 += WIDTH
    elif x2 > WIDTH:
        x2 -= WIDTH
    if y2 < 0:
        y2 += HEIGHT
    elif y2 > HEIGHT:
        y2 -= HEIGHT

    # Render (background and rotated ship)
    screen.fill((10, 10, 30))
    # Use -angle so the sprite visually matches the movement direction
    rotated1 = pygame.transform.rotate(airplane1_image, -angle1)
    rect1 = rotated1.get_rect(center=(x1, y1))
    screen.blit(rotated1, rect1.topleft)
    # airplane 2
    rotated2 = pygame.transform.rotate(airplane2_image, -angle2)
    rect2 = rotated2.get_rect(center=(x2, y2))
    screen.blit(rotated2, rect2.topleft)

    pygame.display.flip()

pygame.quit()
