import math
import os
import pygame
from dataclasses import dataclass

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

WIN_SCORE = 5
TANK_SIZE = 48
TANK_SPEED = 160
TANK_ROT_SPEED = 180

BULLET_SPEED = 380
BULLET_LIFETIME = 2.0
BULLET_RADIUS = 4
BULLET_COOLDOWN = 0.35

SPIN_SPEED = 800
SPIN_DURATION = 1.0

OBSTACLES = [
    pygame.Rect(300, 150, 60, 200),
    pygame.Rect(540, 150, 60, 200),
    pygame.Rect(160, 420, 120, 30),
    pygame.Rect(620, 420, 120, 30),
]

# Colors
BG_COLOR = (24, 24, 36)
WHITE = (255, 255, 255)
P1_COLOR = (80, 200, 120)
P2_COLOR = (250, 0, 0)
OBST_COLOR = (100, 100, 120)
TEXT_COLOR = (220, 220, 220)
FLASH_COLOR = (255, 200, 50)

# Initialization
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Combat - Atari style (fan remake)")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 64)

# Load images safely
base_path = os.path.dirname(__file__)
tank_p1_path = os.path.join(base_path, "assets", "tank_p1.png")
tank_p2_path = os.path.join(base_path, "assets", "tank_p2.png")

tank_img_p1 = pygame.image.load(tank_p1_path).convert_alpha()
tank_img_p2 = pygame.image.load(tank_p2_path).convert_alpha()
tank_img_p1 = pygame.transform.smoothscale(
    tank_img_p1, (TANK_SIZE, TANK_SIZE)
)
tank_img_p2 = pygame.transform.smoothscale(
    tank_img_p2, (TANK_SIZE, TANK_SIZE)
)


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    owner: int
    life: float

    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - BULLET_RADIUS),
            int(self.y - BULLET_RADIUS),
            BULLET_RADIUS * 2,
            BULLET_RADIUS * 2,
        )


class Tank:
    def __init__(self, x, y, angle_deg, color, controls, name="Tank"):
        self.x = float(x)
        self.y = float(y)
        self.prev_x = float(x)
        self.prev_y = float(y)
        self.angle = float(angle_deg)
        self.color = color
        self.controls = controls
        self.name = name
        self.cooldown = 0.0
        self.score = 0
        self.spinning = False
        self.spin_timer = 0.0

    def update(self, dt, keys):
        self.prev_x = self.x
        self.prev_y = self.y

        if self.spinning:
            self.angle += SPIN_SPEED * dt
            self.spin_timer -= dt
            if self.spin_timer <= 0:
                self.spinning = False
            return

        if keys[self.controls["left"]]:
            self.angle -= TANK_ROT_SPEED * dt
        if keys[self.controls["right"]]:
            self.angle += TANK_ROT_SPEED * dt
        self.angle %= 360

        brake = 0
        if keys[self.controls["forward"]]:
            brake += 1
        if keys[self.controls["back"]]:
            brake -= 1

        rad = math.radians(self.angle)
        dir_x = math.sin(rad)
        dir_y = -math.cos(rad)

        self.x += dir_x * TANK_SPEED * brake * dt
        self.y += dir_y * TANK_SPEED * brake * dt

        self.x = max(TANK_SIZE // 2,
                     min(SCREEN_WIDTH - TANK_SIZE // 2, self.x))
        self.y = max(TANK_SIZE // 2,
                     min(SCREEN_HEIGHT - TANK_SIZE // 2, self.y))

        if self.cooldown > 0:
            self.cooldown -= dt

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - TANK_SIZE / 2),
            int(self.y - TANK_SIZE / 2),
            TANK_SIZE,
            TANK_SIZE,
        )

    def shoot(self):
        if self.spinning or self.cooldown > 0:
            return None

        rad = math.radians(self.angle)
        dir_x = math.sin(rad)
        dir_y = -math.cos(rad)

        bx = self.x + dir_x * (TANK_SIZE / 2 + BULLET_RADIUS + 2)
        by = self.y + dir_y * (TANK_SIZE / 2 + BULLET_RADIUS + 2)
        vx = dir_x * BULLET_SPEED
        vy = dir_y * BULLET_SPEED

        self.cooldown = BULLET_COOLDOWN
        owner_id = 1 if self.color == P1_COLOR else 2
        return Bullet(bx, by, vx, vy, owner_id, BULLET_LIFETIME)

    def hit(self):
        self.spinning = True
        self.spin_timer = SPIN_DURATION


def draw_tank(surface, tank: Tank):
    image = tank_img_p1 if tank.color == P1_COLOR else tank_img_p2
    rotated = pygame.transform.rotate(image, -tank.angle)
    rect = rotated.get_rect(center=(tank.x, tank.y))
    surface.blit(rotated, rect.topleft)


def bullet_hits_obstacle(bullet: Bullet) -> bool:
    rect = bullet.rect()
    return any(rect.colliderect(ob) for ob in OBSTACLES)


def resolve_collisions(t1: Tank, t2: Tank):
    for tank in [t1, t2]:
        rect = tank.get_rect()
        for ob in OBSTACLES:
            if rect.colliderect(ob):
                dx_left = rect.right - ob.left
                dx_right = ob.right - rect.left
                dy_top = rect.bottom - ob.top
                dy_bottom = ob.bottom - rect.top

                min_dx = min(dx_left, dx_right)
                min_dy = min(dy_top, dy_bottom)

                if min_dx < min_dy:
                    if dx_left < dx_right:
                        tank.x -= dx_left
                    else:
                        tank.x += dx_right
                else:
                    if dy_top < dy_bottom:
                        tank.y -= dy_top
                    else:
                        tank.y += dy_bottom

                rect = tank.get_rect()

        tank.x = max(TANK_SIZE / 2,
                     min(SCREEN_WIDTH - TANK_SIZE / 2, tank.x))
        tank.y = max(TANK_SIZE / 2,
                     min(SCREEN_HEIGHT - TANK_SIZE / 2, tank.y))

    if t1.get_rect().colliderect(t2.get_rect()):
        t1.x = t1.prev_x
        t1.y = t1.prev_y
        t2.x = t2.prev_x
        t2.y = t2.prev_y


# Controls
controls_p1 = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "forward": pygame.K_w,
    "back": pygame.K_s,
    "shoot": pygame.K_SPACE,
}

controls_p2 = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "forward": pygame.K_UP,
    "back": pygame.K_DOWN,
    "shoot": pygame.K_RCTRL,
}

# Objects
p1 = Tank(120, SCREEN_HEIGHT // 2, 0, P1_COLOR, controls_p1, "Player 1")
p2 = Tank(SCREEN_WIDTH - 120, SCREEN_HEIGHT // 2, 180,
          P2_COLOR, controls_p2, "Player 2")

bullets = []
flash_time = 0.0
winner = None
game_state = "PLAYING"

# Main loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and game_state == "PLAYING":
            if event.key == p1.controls["shoot"]:
                bullet = p1.shoot()
                if bullet:
                    bullets.append(bullet)

            if event.key == p2.controls["shoot"]:
                bullet = p2.shoot()
                if bullet:
                    bullets.append(bullet)

    if game_state == "PLAYING":
        flash_time = max(0.0, flash_time - dt)
        p1.update(dt, keys)
        p2.update(dt, keys)
        resolve_collisions(p1, p2)

        for bullet in bullets[:]:
            bullet.life -= dt
            bullet.x += bullet.vx * dt
            bullet.y += bullet.vy * dt

            if bullet_hits_obstacle(bullet):
                bullets.remove(bullet)
                continue

            if (
                bullet.x < -10
                or bullet.x > SCREEN_WIDTH + 10
                or bullet.y < -10
                or bullet.y > SCREEN_HEIGHT + 10
                or bullet.life <= 0
            ):
                bullets.remove(bullet)
                continue

            if not p1.spinning and bullet.owner == 2:
                if p1.get_rect().collidepoint(int(bullet.x), int(bullet.y)):
                    p1.hit()
                    p2.score += 1
                    bullets.remove(bullet)
                    flash_time = 0.18
                    continue

            if not p2.spinning and bullet.owner == 1:
                if p2.get_rect().collidepoint(int(bullet.x), int(bullet.y)):
                    p2.hit()
                    p1.score += 1
                    bullets.remove(bullet)
                    flash_time = 0.18
                    continue

        if p1.score >= WIN_SCORE or p2.score >= WIN_SCORE:
            winner = "Player 1" if p1.score >= WIN_SCORE else "Player 2"
            game_state = "MATCH_OVER"

    screen.fill(BG_COLOR)

    for ob in OBSTACLES:
        pygame.draw.rect(screen, OBST_COLOR, ob)

    for bullet in bullets:
        pygame.draw.circle(screen, WHITE,
                           (int(bullet.x), int(bullet.y)), BULLET_RADIUS)

    draw_tank(screen, p1)
    draw_tank(screen, p2)

    score_text = font.render(
        f"P1: {p1.score}     P2: {p2.score}", True, TEXT_COLOR
    )
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 80, 8))

    if game_state == "MATCH_OVER":
        over = big_font.render(f"{winner} wins!", True, FLASH_COLOR)
        screen.blit(over, (SCREEN_WIDTH // 2 - over.get_width() // 2, 260))

        info = font.render("Press R to restart", True, TEXT_COLOR)
        screen.blit(info, (SCREEN_WIDTH // 2 - info.get_width() // 2, 320))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            p1.score = 0
            p2.score = 0
            game_state = "PLAYING"

    elif flash_time > 0:
        flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = int(140 * (flash_time / 0.18))
        flash.fill((255, 255, 255, alpha))
        screen.blit(flash, (0, 0))

    pygame.display.flip()

pygame.quit()
