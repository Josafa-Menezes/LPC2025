import pygame
import math


# Screen setup
def screen_setup(title):
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()
    return screen, clock, width, height


# Scoreboard setup
def scoreboard_setup(WIDTH):
    pygame.font.init()
    score_font = pygame.font.Font("assets/PressStart2P.ttf", 44)
    score1_pos = (WIDTH // 4, 30)
    score2_pos = (3 * WIDTH // 4, 30)
    return score_font, score1_pos, score2_pos


# upload images and sound
def load_image(IMAGE_PATH_1, IMAGE_PATH_2):
    bullet_sound = pygame.mixer.Sound("assets/bullet.wav")
    bullet = "assets/bullet.png"
    image_1 = pygame.image.load(IMAGE_PATH_1).convert_alpha()
    image_2 = pygame.image.load(IMAGE_PATH_2).convert_alpha()
    bullet_image = pygame.image.load(bullet).convert_alpha()
    bullet_sound = pygame.mixer.Sound("assets/bullet.wav")
    return image_1, image_2, bullet_image, bullet_sound


# Scale bullet image
def scale_bullet_image(img_bul):
    bul_SIZE = 4  # pixels
    bul_img_w, bul_img_h = img_bul.get_size()
    bul_scale = (bul_SIZE * 2) / max(bul_img_w, bul_img_h)
    bul_new_w = max(1, int(bul_img_w * bul_scale))
    bul_new_h = max(1, int(bul_img_h * bul_scale))
    bul_new_size = (bul_new_w, bul_new_h)
    bul_image = pygame.transform.smoothscale(img_bul, bul_new_size)
    return bul_image


class Bullet:
    def __init__(self, x, y, angle, image, max_distance_pixels):
        BUL_SPEED = 900.0
        self.x = x
        self.y = y
        self.angle = angle
        self.image = image
        self.original_image = image
        self.rad = math.radians(self.angle - 270)
        self.vel_x = math.sin(self.rad) * BUL_SPEED
        self.vel_y = -math.cos(self.rad) * BUL_SPEED
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.max_distance_pixels = max_distance_pixels
        self.traveled_distance = 0.0
        self.last_x = x
        self.last_y = y

    def update(self, dt, width, height):
        self.last_x = self.x
        self.last_y = self.y

        self.x += self.vel_x * dt
        self.y += self.vel_y * dt

        delta_x = self.x - self.last_x
        delta_y = self.y - self.last_y
        self.traveled_distance += math.hypot(delta_x, delta_y)

        # Wrap-around
        if self.x < 0:
            self.x += width
        elif self.x > width:
            self.x -= width
        if self.y < 0:
            self.y += height
        elif self.y > height:
            self.y -= height

        self.rect.center = (self.x, self.y)

        # Check if bullet has exceeded max_distance_pixels
        return self.traveled_distance < self.max_distance_pixels

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def get_rect(self):
        return self.rect
