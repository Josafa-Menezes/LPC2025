import pygame
import math


# Screen and Clock Setup
def screen_setup(title):
    # Initialize game screen and clock.
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()
    return screen, clock, width, height


def scoreboard_setup(width):
    # Prepare font and positions for score display.
    pygame.font.init()
    score_font = pygame.font.Font("assets/PressStart2P.ttf", 44)
    score1_pos = (width // 4, 30)
    score2_pos = (3 * width // 4, 30)
    return score_font, score1_pos, score2_pos


# Image and Sound Loading
def load_image(image_path_1, image_path_2):
    # Load player and bullet images plus sound.
    bullet_sound = pygame.mixer.Sound("assets/bullet.wav")
    bullet = "assets/bullet.png"
    image_1 = pygame.image.load(image_path_1).convert_alpha()
    image_2 = pygame.image.load(image_path_2).convert_alpha()
    bullet_image = pygame.image.load(bullet).convert_alpha()
    return image_1, image_2, bullet_image, bullet_sound


def scale_bullet_image(img_bul):
    # Scale bullet image proportionally to a small size.
    bul_size = 4  # pixels
    bul_img_w, bul_img_h = img_bul.get_size()
    bul_scale = (bul_size * 2) / max(bul_img_w, bul_img_h)
    bul_new_w = max(1, int(bul_img_w * bul_scale))
    bul_new_h = max(1, int(bul_img_h * bul_scale))
    bul_new_size = (bul_new_w, bul_new_h)
    bul_image = pygame.transform.smoothscale(img_bul, bul_new_size)
    return bul_image


# Movement and Drawing Helpers
def move_in_direction(x, y, angle, speed, dt,
                      wrap=False, width=None, height=None):
    # Move an object in the direction of its angle.
    # Optionally wraps around screen borders.
    rad = math.radians(angle)
    x += math.sin(rad) * speed * dt
    y -= math.cos(rad) * speed * dt

    if wrap and width and height:
        x %= width
        y %= height

    return x, y


def draw_rotated_image(screen, image, angle, x, y):
    # Rotate an image around its center and draw it.
    rotated = pygame.transform.rotate(image, -angle)
    rect = rotated.get_rect(center=(x, y))
    screen.blit(rotated, rect.topleft)
    return rect


def render_score(screen, font, pos1, pos2, score1, score2, color1, color2):
    # Render two player scores on the screen.
    text1 = font.render(str(score1), True, color1)
    text2 = font.render(str(score2), True, color2)
    screen.blit(text1, pos1)
    screen.blit(text2, pos2)


# Bullet Class
class Bullet:
    # Represents a bullet fired by a player.

    def __init__(self, x, y, angle, image, max_distance_pixels):
        bul_speed = 900.0
        self.x = x
        self.y = y
        self.angle = angle
        self.image = image
        self.original_image = image
        self.rad = math.radians(self.angle - 270)
        self.vel_x = math.sin(self.rad) * bul_speed
        self.vel_y = -math.cos(self.rad) * bul_speed
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.max_distance_pixels = max_distance_pixels
        self.traveled_distance = 0.0
        self.last_x = x
        self.last_y = y

    def update(self, dt, width, height):
        # Update bullet position and return False if it exceeded max distance.
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
        return self.traveled_distance < self.max_distance_pixels

    def draw(self, screen):
        # Draw bullet image.
        screen.blit(self.image, self.rect.topleft)

    def get_rect(self):
        # Return bullet rectangle for collision detection.
        return self.rect
