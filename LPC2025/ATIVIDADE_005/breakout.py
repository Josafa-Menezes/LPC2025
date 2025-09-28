import pygame
import math

pygame.init()

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

SCORE_MAX = 4

size = (1280, 720)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Breakout - PyGame Edition - 2025-09-27")

# score text
score_font = pygame.font.Font("assets/PressStart2P.ttf", 44)
score_text = score_font.render("000", True, COLOR_WHITE)
score_text_rect = score_text.get_rect()
score_text_rect_left = (680, 50)

# score
score = 0

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

# life text
life_text = score_font.render("000", True, COLOR_WHITE)
life_text_rect = life_text.get_rect()
life_text_rect_right = (600, 50)

# game loop
game_loop = True
game_clock = pygame.time.Clock()

while game_loop:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_loop = False
    pygame.display.flip()
    game_clock.tick(60)


pygame.quit()
