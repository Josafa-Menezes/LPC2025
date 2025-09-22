# Jucimar Jr
# 2024

import pygame
import math

pygame.init()

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

SCORE_MAX = 4

size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("MyPong - PyGame Edition - 2024-09-02")

# score text
score_font = pygame.font.Font("assets/PressStart2P.ttf", 44)
score_text = score_font.render("00 x 00", True, COLOR_WHITE, COLOR_BLACK)
score_text_rect = score_text.get_rect()
score_text_rect.center = (680, 50)

# victory text
victory_font = pygame.font.Font("assets/PressStart2P.ttf", 100)
victory_text = victory_font.render("VICTORY", True, COLOR_WHITE, COLOR_BLACK)
victory_text_rect = score_text.get_rect()
victory_text_rect.center = (450, 350)

# sound effects
bounce_sound_effect = pygame.mixer.Sound("assets/bounce.wav")
scoring_sound_effect = pygame.mixer.Sound(
    "assets/258020__kodack__arcade-bleep-sound.wav"
)

# player 1
player_1 = pygame.image.load("assets/player.png")
player_1_y = 300
player_1_move_up = False
player_1_move_down = False

# player 2 - robot
player_2 = pygame.image.load("assets/player.png")
player_2_y = 300

# ball
ball = pygame.image.load("assets/ball.png")
ball_x = 640
ball_y = 360
initial_ball_speed = 5
ball_dx = initial_ball_speed
ball_dy = initial_ball_speed
acceleration_factor = 1.10

# When the ball hits the paddle tip, it can leave up to this angle.
# Adjust if desired (e.g., 45°, 60°, 75°).
MAX_BOUNCE_ANGLE = math.radians(60)

# score
score_1 = 0
score_2 = 0

# game loop
game_loop = True
game_clock = pygame.time.Clock()

while game_loop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_loop = False

        # keystroke events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_1_move_up = True
            if event.key == pygame.K_DOWN:
                player_1_move_down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player_1_move_up = False
            if event.key == pygame.K_DOWN:
                player_1_move_down = False

    # checking the victory condition
    if score_1 < SCORE_MAX and score_2 < SCORE_MAX:

        # clear screen
        screen.fill(COLOR_BLACK)

        # ball collision with the wall
        if ball_y > 700:
            ball_dy *= -1
            bounce_sound_effect.play()
            ball_dx *= acceleration_factor
            ball_dy *= acceleration_factor
        elif ball_y <= 0:
            ball_dy *= -1
            bounce_sound_effect.play()
            ball_dx *= acceleration_factor
            ball_dy *= acceleration_factor

        # create rects for collision
        ball_rect = pygame.Rect(
            ball_x, ball_y, ball.get_width(), ball.get_height()
        )
        player_1_rect = pygame.Rect(
            50, player_1_y, player_1.get_width(), player_1.get_height()
        )
        player_2_rect = pygame.Rect(
            1180, player_2_y, player_2.get_width(), player_2.get_height()
        )

        # COLLISION: left paddle now calculates bounce angle
        if ball_rect.colliderect(player_1_rect):
            # calculate centers (uses actual image heights)
            ball_center_y = ball_y + ball.get_height() / 2
            paddle_center_y = player_1_y + player_1.get_height() / 2

            # negative = hit upper half, positive = lower half
            relative_intersect = ball_center_y - paddle_center_y

            # normalize to range [-1, 1]
            normalized = relative_intersect / (player_1.get_height() / 2)
            if normalized < -1:
                normalized = -1
            if normalized > 1:
                normalized = 1

            # map to angle between -MAX_BOUNCE_ANGLE and +MAX_BOUNCE_ANGLE
            bounce_angle = normalized * MAX_BOUNCE_ANGLE

            # keep speed magnitude and recompute components
            speed = math.hypot(ball_dx, ball_dy)
            direction = 1  # left side => ball goes to the right
            ball_dx = direction * speed * math.cos(bounce_angle)
            ball_dy = speed * math.sin(bounce_angle)

            # push ball outside the paddle to avoid 'sticking'
            ball_x = player_1_rect.right
            bounce_sound_effect.play()

        # COLLISION: right paddle now calculates bounce angle
        if ball_rect.colliderect(player_2_rect):
            # calculate centers (uses actual image heights)
            ball_center_y = ball_y + ball.get_height() / 2
            paddle_center_y = player_2_y + player_2.get_height() / 2

            relative_intersect = ball_center_y - paddle_center_y
            normalized = relative_intersect / (player_2.get_height() / 2)
            if normalized < -1:
                normalized = -1
            if normalized > 1:
                normalized = 1

            bounce_angle = normalized * MAX_BOUNCE_ANGLE
            speed = math.hypot(ball_dx, ball_dy)
            direction = -1  # right side => ball goes to the left
            ball_dx = direction * speed * math.cos(bounce_angle)
            ball_dy = speed * math.sin(bounce_angle)

            # push ball outside the paddle to avoid 'sticking'
            ball_x = player_2_rect.left - ball.get_width()
            bounce_sound_effect.play()

        # scoring points
        if ball_x < -50:
            ball_x = 640
            ball_y = 360
            ball_dy *= -1
            ball_dx *= -1
            score_2 += 1
            scoring_sound_effect.play()
            ball_dx = initial_ball_speed * (1 if ball_dx > 0 else -1)
            ball_dy = initial_ball_speed * (1 if ball_dy > 0 else -1)
        elif ball_x > 1320:
            ball_x = 640
            ball_y = 360
            ball_dy *= -1
            ball_dx *= -1
            score_1 += 1
            scoring_sound_effect.play()
            ball_dx = initial_ball_speed * (1 if ball_dx > 0 else -1)
            ball_dy = initial_ball_speed * (1 if ball_dy > 0 else -1)

        # ball movement
        ball_x = ball_x + ball_dx
        ball_y = ball_y + ball_dy

        # player 1 up movement
        if player_1_move_up:
            player_1_y -= 5

        # player 1 down movement
        if player_1_move_down:
            player_1_y += 5

        # player 1 collides with upper wall
        if player_1_y <= 0:
            player_1_y = 0

        # player 1 collides with lower wall
        elif player_1_y >= 570:
            player_1_y = 570

        # player 2 "Artificial Intelligence"
        if ball_y > player_2_y + 75:
            player_2_y += 7
        elif ball_y < player_2_y + 75:
            player_2_y -= 7
        if player_2_y <= 0:
            player_2_y = 0
        elif player_2_y >= 570:
            player_2_y = 570

        # update score hud
        score_text = score_font.render(
            str(score_1) + " x " + str(score_2),
            True,
            COLOR_WHITE,
            COLOR_BLACK,
        )

        # drawing objects
        screen.blit(ball, (ball_x, ball_y))
        screen.blit(player_1, (50, player_1_y))
        screen.blit(player_2, (1180, player_2_y))
        screen.blit(score_text, score_text_rect)
    else:
        # drawing victory
        screen.fill(COLOR_BLACK)
        screen.blit(score_text, score_text_rect)
        screen.blit(victory_text, victory_text_rect)

    # update screen
    pygame.display.flip()
    game_clock.tick(60)

pygame.quit()
