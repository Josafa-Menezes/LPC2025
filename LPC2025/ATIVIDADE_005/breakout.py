import pygame
import math

pygame.init()

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

SCORE_MAX = 4

size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Breakout - PyGame Edition - 2025-09-27")

# Fonts
font_path = "assets/PressStart2P.ttf"

score_font = pygame.font.Font(font_path, 44)
victory_font = pygame.font.Font(font_path, 100)
game_over_font = pygame.font.Font(font_path, 100)
paused_font = pygame.font.Font(font_path, 70)


# UI Rects (will be updated dynamically)
score_text_rect = pygame.Rect((0, 0), (1, 1))
life_text_rect = pygame.Rect((0, 0), (1, 1))


# Victory text
victory_text = victory_font.render("VICTORY", True, COLOR_WHITE)
victory_text_rect = victory_text.get_rect(center=(size[0]/2, size[1]/2))

# Game Over text
game_over_text = game_over_font.render("GAME OVER", True, COLOR_WHITE)
game_over_text_rect = game_over_text.get_rect(center=(size[0]/2, size[1]/2))

# Player
player = pygame.image.load("assets/player.png")
player_y = 300
player_move_up = False
player_move_down = False
player_speed = 10

# Ball
ball = pygame.image.load("assets/ball.png")
initial_ball_speed = 5
ball_dx = initial_ball_speed
ball_dy = initial_ball_speed
acceleration_factor = 1.05

# When the ball hits the paddle tip, it can leave up to this angle.
MAX_BOUNCE_ANGLE = math.radians(60)

# Game state variables
score = 0
lives = 3

# Game States
GAME_STATE_PLAYING = 0
GAME_STATE_PAUSED = 1
GAME_STATE_VICTORY = 2
GAME_STATE_GAME_OVER = 3

game_state = GAME_STATE_PLAYING

# game loop
game_loop = True
game_clock = pygame.time.Clock()

# Initial ball position (centered)
ball_x = size[0] / 2 - ball.get_width() / 2
ball_y = size[1] / 2 - ball.get_height() / 2

while game_loop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_loop = False

        # Key presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_move_up = True
            if event.key == pygame.K_DOWN:
                player_move_down = True

            # Pause/Unpause
            if event.key == pygame.K_SPACE:
                if game_state == GAME_STATE_PLAYING:
                    game_state = GAME_STATE_PAUSED
                elif game_state == GAME_STATE_PAUSED:
                    game_state = GAME_STATE_PLAYING

            # Restart game (from Game Over or Victory)
            if game_state in (GAME_STATE_GAME_OVER, GAME_STATE_VICTORY) and \
               event.key == pygame.K_r:
                score = 0
                lives = 3
                ball_x = size[0] / 2 - ball.get_width() / 2
                ball_y = size[1] / 2 - ball.get_height() / 2
                ball_dx = initial_ball_speed
                ball_dy = initial_ball_speed
                player_y = 300
                game_state = GAME_STATE_PLAYING

        # Key releases
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player_move_up = False
            if event.key == pygame.K_DOWN:
                player_move_down = False

    # Clear screen at the beginning of each frame
    screen.fill(COLOR_BLACK)

    # --- Game Logic based on State ---
    if game_state == GAME_STATE_PLAYING:
        # Player movement
        if player_move_up:
            player_y -= player_speed
        if player_move_down:
            player_y += player_speed

        # Player boundary check
        if player_y < 0:
            player_y = 0
        if player_y > size[1] - player.get_height():
            player_y = size[1] - player.get_height()

        # Ball collision with walls
        if ball_x + ball.get_width() > size[0]:
            ball_dx *= -1
        elif ball_x < 0:
            ball_dx *= -1

        if ball_y < 0:
            ball_dy *= -1

        # Check if ball went out of bounds
        # (lost a life - going off the right side)
        if ball_x > size[0]:
            lives -= 1
            if lives <= 0:
                game_state = GAME_STATE_GAME_OVER
            else:
                # Reset ball position and speed for next life
                ball_x = size[0] / 2 - ball.get_width() / 2
                ball_y = size[1] / 2 - ball.get_height() / 2
                ball_dx = initial_ball_speed * (1 if ball_dx > 0 else -1)
                ball_dy = initial_ball_speed * (1 if ball_dy > 0 else -1)

        # Create rects for collision
        ball_rect = pygame.Rect(ball_x, ball_y,
                                ball.get_width(), ball.get_height())
        player_rect = pygame.Rect(50, player_y,
                                  player.get_width(), player.get_height())

        # COLLISION: Ball with Paddle (Vertical paddle logic)
        if ball_rect.colliderect(player_rect):
            # Push ball outside the paddle to avoid 'sticking'
            ball_x = player_rect.right
            # Calculate centers for angle
            ball_center_y = ball_y + ball.get_height() / 2
            paddle_center_y = player_y + player.get_height() / 2

            relative_intersect = ball_center_y - paddle_center_y
            normalized = relative_intersect / (player.get_height() / 2)

            # Clamp normalized value to [-1, 1]
            normalized = max(-1, min(1, normalized))

            bounce_angle = normalized * MAX_BOUNCE_ANGLE

            # Recalculate ball velocity components based
            # on angle and current speed magnitude
            current_speed = math.hypot(ball_dx, ball_dy)
            ball_dx = current_speed * math.cos(bounce_angle)
            ball_dy = current_speed * math.sin(bounce_angle)

            # Ensure ball always goes to the right
            # after hitting the left paddle
            if ball_dx <= 0:
                ball_dx = abs(ball_dx)

            # Apply acceleration
            ball_dx *= acceleration_factor
            ball_dy *= acceleration_factor

        # Ball movement
        ball_x += ball_dx
        ball_y += ball_dy

        # Check for victory condition (e.g., score threshold)
        if score >= SCORE_MAX:
            game_state = GAME_STATE_VICTORY

        # --- Drawing for PLAYING state ---
        screen.blit(ball, (ball_x, ball_y))
        screen.blit(player, (50, player_y))

        # Update and draw score HUD
        score
