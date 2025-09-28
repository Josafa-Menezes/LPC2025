import pygame

# --- Game Constants ---
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
# Other constants
BALL_RADIUS = 10
BALL_SPEED_X = 5
BALL_SPEED_Y = 5
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_SPEED = 7
FPS = 60


# --- Ball Class ---
class Ball(pygame.sprite.Sprite):
    """Represents the game's ball."""
    def __init__(self, x, y, radius, color, speed_x, speed_y):
        super().__init__()
        self.image = pygame.Surface([radius * 2, radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        """Updates the ball's position and handles wall collisions."""
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Collision with side walls
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.speed_x *= -1

        # Collision with top wall
        if self.rect.top <= 0:
            self.speed_y *= -1

        # Collision with bottom wall (lost a life)
        if self.rect.bottom >= SCREEN_HEIGHT:
            return True  # Signals that the ball went off-screen
        return False

    def reset_position(self, x, y):
        """Resets the ball's position to the center of the screen."""
        self.rect.center = (x, y)
        self.speed_x = BALL_SPEED_X
        self.speed_y = BALL_SPEED_Y


# --- Paddle Class ---
class Paddle(pygame.sprite.Sprite):
    """Represents the player-controlled paddle."""
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        """Updates the paddle's position based on keyboard input."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PADDLE_SPEED


# --- Game Functions ---
def draw_text(surface, text, size, x, y, color=WHITE):
    """Draws text on the screen."""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def main_game_loop():
    """Main function containing the game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Breakout Pygame")
    clock = pygame.time.Clock()

    # --- Game Variables ---
    score = 0
    lives = 3
    game_state = "MENU"  # States: "MENU", "PLAYING", "PAUSED", "GAME_OVER"

    # Sprite groups
    all_sprites = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    paddles = pygame.sprite.Group()

    # Create the ball
    ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                BALL_RADIUS, WHITE, BALL_SPEED_X, BALL_SPEED_Y)
    all_sprites.add(ball)
    balls.add(ball)

    # Create the paddle
    paddle = Paddle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30,
                    PADDLE_WIDTH, PADDLE_HEIGHT, BLUE)
    all_sprites.add(paddle)
    paddles.add(paddle)

    # --- Main Game Loop ---
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state == "MENU":
                        game_state = "PLAYING"
                        score = 0
                        lives = 3
                        ball.reset_position(
                            SCREEN_WIDTH // 2,
                            SCREEN_HEIGHT // 2
                        )
                    elif game_state == "PAUSED":
                        game_state = "PLAYING"
                    elif game_state == "PLAYING":
                        game_state = "PAUSED"
                elif event.key == pygame.K_r and game_state == "GAME_OVER":
                    game_state = "MENU"

        # --- Game Logic (based on state) ---
        if game_state == "PLAYING":
            # Update sprites
            all_sprites.update()

            # Ball logic and collisions
            ball_out = ball.update()
            if ball_out:
                lives -= 1
                if lives <= 0:
                    game_state = "GAME_OVER"
                else:
                    ball.reset_position(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

            # Ball collision with paddle
            if pygame.sprite.spritecollide(paddle, balls, False):
                ball.speed_y *= -1
                # Small adjustment to prevent the ball from getting stuck
                ball.rect.bottom = paddle.rect.top - 1

            # You will add block collision logic here later
            # For now, just as an example for scoring:
            # if block_hit:
            #     score += 10
            #     remove_block()

        # --- Drawing to the Screen ---
        screen.fill(BLACK)  # Fills the background with black

        if game_state == "MENU":
            draw_text(screen, "BREAKOUT", 74, SCREEN_WIDTH // 2,
                      SCREEN_HEIGHT // 4, GREEN)
            draw_text(screen, "Press SPACE to start", 36, SCREEN_WIDTH // 2,
                      SCREEN_HEIGHT // 2)
            draw_text(screen, "Left/Right Arrows to move paddle", 24,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
        elif game_state == "PLAYING":
            all_sprites.draw(screen)
            draw_text(screen, f"Score: {score}", 24, 70, 20)
            draw_text(screen, f"Lives: {lives}", 24, SCREEN_WIDTH - 50, 20)
        elif game_state == "PAUSED":
            all_sprites.draw(screen)  # Draws the game state before pausing
            draw_text(screen, "PAUSED", 74, SCREEN_WIDTH // 2,
                      SCREEN_HEIGHT // 2, YELLOW)
            draw_text(screen, "Press SPACE to continue", 36,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        elif game_state == "GAME_OVER":
            draw_text(screen, "GAME OVER", 74, SCREEN_WIDTH // 2,
                      SCREEN_HEIGHT // 4, RED)
            draw_text(screen, f"Your final score: {score}", 36,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            draw_text(screen, "Press 'R' to return to Menu", 24,
                      SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)

        # Update the screen
        pygame.display.flip()

        # Control the frame rate (FPS)
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main_game_loop()
