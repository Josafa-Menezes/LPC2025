import math
import pygame
import core

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen, clock = core.screen_setup(WIDTH, HEIGHT, "Warplane Combat")

# Scoreboard setup
score_font = pygame.font.Font("assets/PressStart2P.ttf", 44)
score1_pos = (WIDTH // 4, 30)
score2_pos = (3 * WIDTH // 4, 30)

# upload images
PATH_green = "assets/airplaneGreen.png"
PATH_orange = "assets/airplaneOrange.png"
PATH_bullet = "assets/bullet.png"
img_G, img_OR, img_bul = core.load_image(PATH_green, PATH_orange, PATH_bullet)

# scale of images
airplane_SIZE = 40  # pixels
img_w, img_h = img_G.get_size()
scale = (airplane_SIZE * 2) / max(img_w, img_h)
new_size = (max(1, int(img_w * scale)), max(1, int(img_h * scale)))
airplane_green_image = pygame.transform.smoothscale(img_G, new_size)
airplane_orange_image = pygame.transform.smoothscale(img_OR, new_size)

# Scale bullet image
bul_SIZE = 15  # pixels
bul_img_w, bul_img_h = img_bul.get_size()
bul_scale = (bul_SIZE * 2) / max(bul_img_w, bul_img_h)
bul_new_w = max(1, int(bul_img_w * bul_scale))
bul_new_h = max(1, int(bul_img_h * bul_scale))
bul_new_size = (bul_new_w, bul_new_h)
bul_image = pygame.transform.smoothscale(img_bul, bul_new_size)

# state variables
initial_angle = 0.0
speed = 180.0
initial_rad = math.radians(initial_angle - 270)

# airplane 1
x_green = WIDTH / 2
y_green = HEIGHT / 2
vel_x_green = math.sin(initial_rad) * speed
vel_y_green = -math.cos(initial_rad) * speed
angle_Green = 0.0

# airplane 2
x_orange = WIDTH / 4
y_orange = HEIGHT / 4
vel_x_orange = math.sin(initial_rad) * speed
vel_y_orange = -math.cos(initial_rad) * speed
angle_orange = 0.0

# Movement parameters (kept slower from prior change)
ROT_SPEED = 225.0   # degrees per second
BUL_SPEED = 300.0

# Lists to hold active bullets
bullets_green = []
bullets_orange = []


running = True
while running:
    dt = clock.tick(60) / 1000.0  # delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Corrected rotation: left decreases angle, right increases angle
    # airplane green controls
    if keys[pygame.K_LEFT]:
        angle_Green -= ROT_SPEED * dt
    if keys[pygame.K_RIGHT]:
        angle_Green += ROT_SPEED * dt

    # airplane orange controls
    if keys[pygame.K_a]:
        angle_orange -= ROT_SPEED * dt
    if keys[pygame.K_d]:
        angle_orange += ROT_SPEED * dt

    # Keep angle between 0–360
    angle_Green = angle_Green % 360
    angle_orange = angle_orange % 360
    rad_green = math.radians(angle_Green - 270)
    rad_orange = math.radians(angle_orange - 270)

    # Calculate direction vector (0 degrees points up)
    dir_x_green = math.sin(rad_green)
    dir_y_green = -math.cos(rad_green)
    dir_x_orange = math.sin(rad_orange)
    dir_y_orange = -math.cos(rad_orange)

    # Movement
    # airplane green
    vel_x_green = dir_x_green * speed
    vel_y_green = dir_y_green * speed
    # airplane orange
    vel_x_orange = dir_x_orange * speed
    vel_y_orange = dir_y_orange * speed
    # Update position
    x_green += vel_x_green * dt
    y_green += vel_y_green * dt
    x_orange += vel_x_orange * dt
    y_orange += vel_y_orange * dt

    # Wrap around screen edges
    # airplane green
    if x_green < 0:
        x_green += WIDTH
    elif x_green > WIDTH:
        x_green -= WIDTH
    if y_green < 0:
        y_green += HEIGHT
    elif y_green > HEIGHT:
        y_green -= HEIGHT
    # airplane orange
    if x_orange < 0:
        x_orange += WIDTH
    elif x_orange > WIDTH:
        x_orange -= WIDTH
    if y_orange < 0:
        y_orange += HEIGHT
    elif y_orange > HEIGHT:
        y_orange -= HEIGHT

    # Render (background and rotated ship)
    screen.fill((0, 0, 170))
    # Use -angle so the sprite visually matches the movement direction
    # airplane green
    rotated1 = pygame.transform.rotate(airplane_green_image, -angle_Green)
    rect1 = rotated1.get_rect(center=(x_green, y_green))
    screen.blit(rotated1, rect1.topleft)
    # airplane orange
    rotated2 = pygame.transform.rotate(airplane_orange_image, -angle_orange)
    rect2 = rotated2.get_rect(center=(x_orange, y_orange))
    screen.blit(rotated2, rect2.topleft)

    # Render scores
    score_text_orange = score_font.render("0", True, (210, 105, 30))
    score_text_green = score_font.render("0", True, (0, 170, 0))
    screen.blit(score_text_orange, score1_pos)
    screen.blit(score_text_green, score2_pos)
    pygame.display.flip()

pygame.quit()
