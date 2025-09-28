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
score_text = score_font.render("000", True, COLOR_WHITE, COLOR_BLACK)

# main loop create
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # quit
            running = False

pygame.quit()
