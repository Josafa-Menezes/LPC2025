import pygame
import random
import os

# Game Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BALL_RADIUS = 10
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_SPEED = 7
FPS = 60


# Ball Class
class Ball(pygame.sprite.Sprite):
    # Represents the game ball.

    def __init__(self, x, y, radius, color, speed_x, speed_y):
        super().__init__()
        self.radius = radius
        self.image = pygame.Surface([radius * 2, radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = color
        self.hit_cooldown = 0  # collision delay

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left <= 0:
            self.rect.left = 0
            self.speed_x *= -1
        if self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.speed_x *= -1
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speed_y *= -1

        # reduce cooldown each frame
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

    def reset_position(self, x, y,
                       speed_x=BALL_SPEED_X, speed_y=BALL_SPEED_Y):
        self.rect.center = (x, y)
        self.speed_x = speed_x if random.choice([True, False]) else -speed_x
        self.speed_y = -abs(speed_y)
        self.hit_cooldown = 0


# Paddle Class
class Paddle(pygame.sprite.Sprite):
    # Represents the paddle.

    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.width = width

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PADDLE_SPEED


# Block Class
class Block(pygame.sprite.Sprite):
    # Represents a block in the game.

    def __init__(self, x, y, width, height, color, row):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.row = row


# Utility Functions
def draw_text(surface, text, size, x, y, color=WHITE):
    # Draw text on the screen.
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def generate_blocks(rows, cols, start_x, start_y,
                    block_width, block_height, padding, colors=None):
    # Generate blocks for the game grid.
    blocks = pygame.sprite.Group()
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (block_width + padding)
            y = start_y + row * (block_height + padding)
            color = (colors[row % len(colors)]
                     if colors else (random.randint(50, 255),
                                     random.randint(50, 255),
                                     random.randint(50, 255)))
            block = Block(x, y, block_width, block_height, color, row)
            blocks.add(block)
    return blocks


# Main Game Loop
def main_game_loop():
    pygame.init()
    # initialize mixer (sound)
    try:
        pygame.mixer.init()
    except Exception as e:
        print("Warning: pygame.mixer.init() failed:", e)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout Pygame")
    clock = pygame.time.Clock()

    # sounds
    base_sound_path = (os.path.join(os.path.dirname(__file__), "assets")
                       if "__file__" in globals() else "sounds")
    paddle_sound_path = os.path.join(base_sound_path, "bullet.wav")
    block_sound_path = os.path.join(base_sound_path, "hit.wav")
    life_lost_sound_path = os.path.join(base_sound_path, "sound-damage.mp3")

    paddle_sound = None
    block_sound = None
    life_lost_sound = None

    # helper function to load sounds safely
    def safe_load_sound(path):
        try:
            if os.path.exists(path):
                s = pygame.mixer.Sound(path)
                return s
            else:
                return None
        except Exception as e:
            print(f"Warning while loading sound '{path}':", e)
            return None

    paddle_sound = safe_load_sound(paddle_sound_path)  # paddle hit sound
    block_sound = safe_load_sound(block_sound_path)  # block hit sound
    life_lost_sound = safe_load_sound(life_lost_sound_path)  # life lost sound

    # default volumes
    if paddle_sound:
        paddle_sound.set_volume(0.6)
    if block_sound:
        block_sound.set_volume(0.5)
    if life_lost_sound:
        life_lost_sound.set_volume(0.7)

    score = 0
    lives = 3
    level = 1
    game_state = "MENU"

    all_sprites = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    paddles = pygame.sprite.Group()
    blocks = pygame.sprite.Group()

    ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                BALL_RADIUS, WHITE, BALL_SPEED_X, -BALL_SPEED_Y)
    all_sprites.add(ball)
    balls.add(ball)

    paddle = Paddle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30,
                    PADDLE_WIDTH, PADDLE_HEIGHT, WHITE)
    all_sprites.add(paddle)
    paddles.add(paddle)

    rows = 5
    cols = 8
    padding = 8
    block_width = (SCREEN_WIDTH - (cols + 1) * padding) // cols
    block_height = 30
    start_x = padding
    start_y = 60
    colors = [(200, 50, 50), (200, 120, 50), (200, 200, 50),
              (50, 180, 50), (50, 120, 200)]
    blocks = generate_blocks(rows, cols, start_x, start_y,
                             block_width, block_height, padding, colors)
    for b in blocks:
        all_sprites.add(b)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state == "MENU":
                        game_state = "PLAYING"
                        score = 0
                        lives = 3
                        level = 1
                        blocks.empty()
                        blocks = generate_blocks(rows, cols, start_x, start_y,
                                                 block_width, block_height,
                                                 padding, colors)
                        all_sprites.empty()
                        all_sprites.add(ball, paddle)
                        for b in blocks:
                            all_sprites.add(b)
                        ball.reset_position(SCREEN_WIDTH // 2,
                                            SCREEN_HEIGHT // 2)
                    elif game_state == "PAUSED":
                        game_state = "PLAYING"
                    elif game_state == "PLAYING":
                        game_state = "PAUSED"
                elif event.key == pygame.K_r and (game_state == "GAME_OVER"
                                                  or game_state == "WIN"):
                    game_state = "MENU"

        if game_state == "PLAYING":
            all_sprites.update()

            if ball.rect.bottom >= SCREEN_HEIGHT:
                lives -= 1
                # play life lost sound
                if life_lost_sound:
                    try:
                        life_lost_sound.play()
                    except Exception:
                        pass
                if lives <= 0:
                    game_state = "GAME_OVER"
                else:
                    ball.reset_position(SCREEN_WIDTH // 2,
                                        SCREEN_HEIGHT // 2)

            # ball-paddle collision
            if pygame.sprite.spritecollide(paddle, balls, False):
                offset = ((ball.rect.centerx - paddle.rect.centerx)
                          / (paddle.width / 2))
                offset = max(-1, min(1, offset))
                base_speed = max(abs(ball.speed_x), BALL_SPEED_X)
                ball.speed_x = base_speed * offset
                ball.speed_y = (-abs(ball.speed_y)
                                if ball.speed_y > 0 else -abs(ball.speed_y))
                ball.rect.bottom = paddle.rect.top - 1

                # play paddle collision sound
                if paddle_sound and ball.hit_cooldown == 0:
                    try:
                        paddle_sound.play()
                    except Exception:
                        pass

            # ball-block collision
            hits = pygame.sprite.spritecollide(ball, blocks, dokill=True)
            if hits and ball.hit_cooldown == 0:
                ball.speed_y *= -1
                score += 10 * len(hits)

                # smoother speed multipliers
                for h in hits:
                    multipliers = [1.15, 1.1, 1.05, 1.02, 1.0]
                    row_index = min(h.row, len(multipliers) - 1)
                    m = multipliers[row_index]
                    ball.speed_x *= m
                    ball.speed_y *= m

                # play block collision sound
                if block_sound:
                    try:
                        block_sound.play()
                    except Exception:
                        pass

                ball.hit_cooldown = 10  # delay (~10 frames)

            if len(blocks) == 0:
                game_state = "WIN"

        # Drawing
        screen.fill(BLACK)
        if game_state == "MENU":
            draw_text(screen, "BREAKOUT", 74,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, GREEN)
            draw_text(screen, "Press SPACE to start", 36,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text(screen, "Left/Right Arrows to move paddle", 24,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        elif game_state == "PLAYING":
            all_sprites.draw(screen)
            draw_text(screen, f"Score: {score}", 24, 70, 20)
            draw_text(screen, f"Lives: {lives}", 24,
                      SCREEN_WIDTH - 70, 20)
            draw_text(screen, f"Level: {level}", 18,
                      SCREEN_WIDTH // 2, 20)
        elif game_state == "PAUSED":
            all_sprites.draw(screen)
            draw_text(screen, "PAUSED", 74,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, YELLOW)
            draw_text(screen, "Press SPACE to continue", 36,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        elif game_state == "GAME_OVER":
            draw_text(screen, "GAME OVER", 74,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, RED)
            draw_text(screen, f"Your final score: {score}", 36,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text(screen, "Press 'R' to return to Menu", 24,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        elif game_state == "WIN":
            all_sprites.draw(screen)
            draw_text(screen, "YOU WIN!", 74,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, GREEN)
            draw_text(screen, f"Final Score: {score}", 36,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text(screen, "Press 'R' to return to Menu", 24,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main_game_loop()
