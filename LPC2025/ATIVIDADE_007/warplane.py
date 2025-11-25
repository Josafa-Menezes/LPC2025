import math
import pygame
import core
from core import Bullet

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen setup
screen, clock, WIDTH, HEIGHT = core.screen_setup("Warplane Combat")

# Scoreboard setup
score_font, score1_pos, score2_pos = core.scoreboard_setup(WIDTH)

# upload images
PATH_green = "assets/airplaneGreen.png"
PATH_orange = "assets/airplaneOrange.png"
img_G, img_OR, img_bul, sound_bullet = core.load_image(PATH_green, PATH_orange)
img_cloud = pygame.image.load("assets/nuvem.png").convert_alpha()

# scale of airplane
airplane_SIZE = 40  # pixels
img_w, img_h = img_G.get_size()
scale = (airplane_SIZE * 2) / max(img_w, img_h)
new_size = (max(1, int(img_w * scale)), max(1, int(img_h * scale)))
airplane_green_image = pygame.transform.smoothscale(img_G, new_size)
airplane_orange_image = pygame.transform.smoothscale(img_OR, new_size)

# cloud setup
cloud_rect = img_cloud.get_rect()
# cloud 1
pos_cloud_1_x = WIDTH // 4
pos_cloud_1_y = HEIGHT // 2
cloud_rect_1 = cloud_rect.copy()
cloud_rect_1.center = (pos_cloud_1_x, pos_cloud_1_y)
# cloud 2
pos_cloud_2_x = WIDTH * 3 // 4
pos_cloud_2_y = HEIGHT // 2
cloud_rect_2 = cloud_rect.copy()
cloud_rect_2.center = (pos_cloud_2_x, pos_cloud_2_y)

# Scale bullet image
bul_image = core.scale_bullet_image(img_bul)


# state variables
initial_angle = 0.0
speed = 180.0
initial_rad = math.radians(initial_angle - 270)

# airplane green
x_green_initial = WIDTH / 2
y_green_initial = HEIGHT / 2
x_green = x_green_initial
y_green = y_green_initial
vel_x_green = math.sin(initial_rad) * speed
vel_y_green = -math.cos(initial_rad) * speed
angle_Green = 0.0
green_hit_timer = 0.0
green_respawn_delay = 2.0

# airplane orange
x_orange_initial = WIDTH / 4
y_orange_initial = HEIGHT / 4
x_orange = x_orange_initial
y_orange = y_orange_initial
vel_x_orange = math.sin(initial_rad) * speed
vel_y_orange = -math.cos(initial_rad) * speed
angle_orange = 0.0
orange_hit_timer = 0.0
orange_respawn_delay = 2.0

# Movement parameters
ROT_SPEED = 225.0   # degrees per second
BULLET_MAX_TRAVEL_DISTANCE = 800

# Lists to hold active bullets
bullets_green = []
bullets_orange = []

# Score
score_green = 0
score_orange = 0

running = True
while running:
    dt = clock.tick(60) / 1000.0  # delta time in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            # Player Orange fires
            if event.key == pygame.K_s and not bullets_orange:
                # Offset bullet starting position slightly from airplane center
                sound_bullet.play()
                rad = math.radians(angle_orange - 270)
                offset = airplane_SIZE / 2
                bullet_start_x = x_orange + math.sin(rad) * offset
                bullet_start_y = y_orange - math.cos(rad) * offset
                bullets_orange.append(
                    Bullet(
                        bullet_start_x,
                        bullet_start_y,
                        angle_orange,
                        bul_image,
                        BULLET_MAX_TRAVEL_DISTANCE,
                    )
                )

            # Player Green fires
            if event.key == pygame.K_DOWN and not bullets_green:
                # Offset bullet starting position slightly from airplane center
                sound_bullet.play()
                bullet_offset = airplane_SIZE / 2
                rad = math.radians(angle_Green - 270)
                bullet_start_x = x_green + math.sin(rad) * bullet_offset
                bullet_start_y = y_green - math.cos(rad) * bullet_offset
                bullets_green.append(
                    Bullet(
                        bullet_start_x,
                        bullet_start_y,
                        angle_Green,
                        bul_image,
                        BULLET_MAX_TRAVEL_DISTANCE,
                    )
                )

    keys = pygame.key.get_pressed()

    # airplane green movement and respawn handling
    if green_hit_timer <= 0:
        if keys[pygame.K_LEFT]:
            angle_Green -= ROT_SPEED * dt
        if keys[pygame.K_RIGHT]:
            angle_Green += ROT_SPEED * dt
        angle_Green = angle_Green % 360
        rad_green = math.radians(angle_Green - 270)
        dir_x_green = math.sin(rad_green)
        dir_y_green = -math.cos(rad_green)
        vel_x_green = dir_x_green * speed
        vel_y_green = dir_y_green * speed
        x_green += vel_x_green * dt
        y_green += vel_y_green * dt

        # Wrap around screen edges
        if x_green < 0:
            x_green += WIDTH
        elif x_green > WIDTH:
            x_green -= WIDTH
        if y_green < 0:
            y_green += HEIGHT
        elif y_green > HEIGHT:
            y_green -= HEIGHT
    else:
        green_hit_timer -= dt
        angle_Green += ROT_SPEED * dt * 4
        angle_Green = angle_Green % 360
        if green_hit_timer <= 0:
            x_green = x_green_initial
            y_green = y_green_initial
            angle_Green = 0.0

    # airplane orange movement and respawn handling
    if orange_hit_timer <= 0:
        if keys[pygame.K_a]:
            angle_orange -= ROT_SPEED * dt
        if keys[pygame.K_d]:
            angle_orange += ROT_SPEED * dt
        angle_orange = angle_orange % 360
        rad_orange = math.radians(angle_orange - 270)
        dir_x_orange = math.sin(rad_orange)
        dir_y_orange = -math.cos(rad_orange)
        vel_x_orange = dir_x_orange * speed
        vel_y_orange = dir_y_orange * speed
        x_orange += vel_x_orange * dt
        y_orange += vel_y_orange * dt

        # Wrap around screen edges
        if x_orange < 0:
            x_orange += WIDTH
        elif x_orange > WIDTH:
            x_orange -= WIDTH
        if y_orange < 0:
            y_orange += HEIGHT
        elif y_orange > HEIGHT:
            y_orange -= HEIGHT
    else:
        orange_hit_timer -= dt
        angle_orange += ROT_SPEED * dt * 4
        angle_orange = angle_orange % 360
        if orange_hit_timer <= 0:
            x_orange = x_orange_initial
            y_orange = y_orange_initial
            angle_orange = 0.0

    # Update and draw bullets
    for bullet in bullets_green[:]:
        if not bullet.update(dt, WIDTH, HEIGHT):
            bullets_green.remove(bullet)

    for bullet in bullets_orange[:]:
        if not bullet.update(dt, WIDTH, HEIGHT):
            bullets_orange.remove(bullet)

    #  Collision Detection
    green_plane_rect = airplane_green_image.get_rect(
        center=(int(x_green), int(y_green))
    )
    orange_plane_rect = airplane_orange_image.get_rect(
        center=(int(x_orange), int(y_orange))
    )
    #  Collision: Bullets from GREEN hit ORANGE
    for bullet in bullets_green[:]:
        if bullet.get_rect().colliderect(orange_plane_rect):
            score_green += 1
            orange_hit_timer = orange_respawn_delay
            bullets_green.remove(bullet)
            break
    #  Collision: Bullets from ORANGE hit GREEN
    for bullet in bullets_orange[:]:
        if bullet.get_rect().colliderect(green_plane_rect):
            score_orange += 1
            green_hit_timer = green_respawn_delay
            bullets_orange.remove(bullet)
            break

    # Render (background and rotated ship)
    screen.fill((0, 0, 170))
    # airplane green
    rotated1 = pygame.transform.rotate(airplane_green_image, -angle_Green)
    rect1 = rotated1.get_rect(center=(x_green, y_green))
    screen.blit(rotated1, rect1.topleft)
    # airplane orange
    rotated2 = pygame.transform.rotate(airplane_orange_image, -angle_orange)
    rect2 = rotated2.get_rect(center=(x_orange, y_orange))
    screen.blit(rotated2, rect2.topleft)

    # Draw bullets
    for bullet in bullets_green:
        bullet.draw(screen)
    for bullet in bullets_orange:
        bullet.draw(screen)

    # Draw clouds
    screen.blit(img_cloud, cloud_rect_1)
    screen.blit(img_cloud, cloud_rect_2)

    # Render scores
    ORANGE_COLOR = (210, 105, 30)
    GREEN_COLOR = (0, 170, 0)
    score_text_orange = score_font.render(
        str(score_orange), True, ORANGE_COLOR
    )
    score_text_green = score_font.render(
        str(score_green), True, GREEN_COLOR
    )
    screen.blit(score_text_orange, score1_pos)
    screen.blit(score_text_green, score2_pos)
    pygame.display.flip()

pygame.quit()
