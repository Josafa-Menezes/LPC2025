import math
import pygame
import core

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

# Colors
BG_COLOR = (24, 24, 36)
WHITE = (255, 255, 255)
P1_COLOR = (80, 200, 120)
P2_COLOR = (250, 0, 0)
OBST_COLOR = (100, 100, 120)
FLASH_COLOR = (255, 200, 50)

# Initialization
pygame.init()
pygame.mixer.init()
screen, clock, WIDTH, HEIGHT = core.screen_setup("Combat")

# Load tank and bullet images + sound
img_t1, img_t2, img_bullet, bullet_sound = core.load_image(
    "assets/tank_p1.png", "assets/tank_p2.png"
)
bullet_image = core.scale_bullet_image(img_bullet)

tank_img_p1 = pygame.transform.smoothscale(img_t1, (TANK_SIZE, TANK_SIZE))
tank_img_p2 = pygame.transform.smoothscale(img_t2, (TANK_SIZE, TANK_SIZE))

# Scoreboard setup (same style as warplane)
score_font, score1_pos, score2_pos = core.scoreboard_setup(WIDTH)
COLOR_P1 = (0, 200, 100)
COLOR_P2 = (220, 60, 60)

# Obstacles
OBSTACLES = [
    pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 60, 200),
    pygame.Rect(WIDTH // 2 + 90, HEIGHT // 2 - 100, 60, 200),
    pygame.Rect(WIDTH // 2 - 260, HEIGHT // 2 + 160, 120, 30),
    pygame.Rect(WIDTH // 2 + 140, HEIGHT // 2 + 160, 120, 30),
]


class Bullet:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        owner: int,
        life: float,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.owner = owner
        self.life = life

    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - bullet_image.get_width() / 2),
            int(self.y - bullet_image.get_height() / 2),
            bullet_image.get_width(),
            bullet_image.get_height(),
        )

    def draw(self, surface):
        surface.blit(
            bullet_image,
            (self.x - bullet_image.get_width() / 2,
             self.y - bullet_image.get_height() / 2),
        )


class Tank:
    # Tank object with rotation, shooting, and collision.

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
        # Update position, rotation, and cooldown.
        self.prev_x, self.prev_y = self.x, self.y

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

        move_dir = 0
        if keys[self.controls["forward"]]:
            move_dir += 1
        if keys[self.controls["back"]]:
            move_dir -= 1

        if move_dir != 0:
            self.x, self.y = core.move_in_direction(
                self.x, self.y, self.angle, TANK_SPEED * move_dir, dt
            )

        # Keep tank inside screen
        self.x = max(TANK_SIZE // 2, min(WIDTH - TANK_SIZE // 2, self.x))
        self.y = max(TANK_SIZE // 2, min(HEIGHT - TANK_SIZE // 2, self.y))

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
        # Fire a bullet if possible.
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
        bullet_sound.play()  # Fire sound
        return Bullet(bx, by, vx, vy, owner_id, BULLET_LIFETIME)

    def hit(self):
        # Trigger spin animation when hit.
        self.spinning = True
        self.spin_timer = SPIN_DURATION


def draw_tank(surface, tank: Tank):
    # Draw tank rotated according to its angle.
    image = tank_img_p1 if tank.color == P1_COLOR else tank_img_p2
    core.draw_rotated_image(surface, image, tank.angle, tank.x, tank.y)


def bullet_hits_obstacle(bullet: Bullet) -> bool:
    # Check if a bullet hits any obstacle.
    rect = bullet.rect()
    return any(rect.colliderect(ob) for ob in OBSTACLES)


def resolve_collisions(t1: Tank, t2: Tank):
    # Prevent tanks from overlapping obstacles or each other.
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

        tank.x = max(TANK_SIZE / 2, min(WIDTH - TANK_SIZE / 2, tank.x))
        tank.y = max(TANK_SIZE / 2, min(HEIGHT - TANK_SIZE / 2, tank.y))

    if t1.get_rect().colliderect(t2.get_rect()):
        t1.x, t1.y = t1.prev_x, t1.prev_y
        t2.x, t2.y = t2.prev_x, t2.prev_y


# Game Setup
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

p1 = Tank(120, HEIGHT // 2, 0, P1_COLOR, controls_p1, "Player 1")
p2 = Tank(WIDTH - 120, HEIGHT // 2, 180, P2_COLOR, controls_p2, "Player 2")

bullets = []
flash_time = 0.0
winner = None
game_state = "PLAYING"


# Main Game Loop
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
                or bullet.x > WIDTH + 10
                or bullet.y < -10
                or bullet.y > HEIGHT + 10
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

    # Drawing
    screen.fill(BG_COLOR)

    for ob in OBSTACLES:
        pygame.draw.rect(screen, OBST_COLOR, ob)

    for bullet in bullets:
        bullet.draw(screen)

    draw_tank(screen, p1)
    draw_tank(screen, p2)

    # Score display
    core.render_score(
        screen, score_font, score1_pos, score2_pos,
        p1.score, p2.score, COLOR_P1, COLOR_P2
    )

    if game_state == "MATCH_OVER":
        over = score_font.render(f"{winner} WINS!", True, FLASH_COLOR)
        screen.blit(over,
                    (WIDTH // 2 - over.get_width() // 2, HEIGHT // 2 - 40))
        info = score_font.render("PRESS R TO RESTART", True, WHITE)
        screen.blit(info,
                    (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 20))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            p1.score = 0
            p2.score = 0
            game_state = "PLAYING"

    elif flash_time > 0:
        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = int(140 * (flash_time / 0.18))
        flash.fill((255, 255, 255, alpha))
        screen.blit(flash, (0, 0))

    pygame.display.flip()

pygame.quit()
