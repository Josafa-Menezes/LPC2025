import pygame

# Initialization
pygame.init()

# Screen setup
screen_size = (850, 720)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Sprites")

# Background
background = pygame.image.load('assets/screen.png')
background = pygame.transform.scale(background, screen_size)


# Projectile Class
class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/shoot.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (499/8, 500/8))
        if direction == -1:  # Flip if shooting left
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 15 * direction
        self.direction = direction

    def update(self):
        self.rect.x += self.speed
        # Remove projectile if it goes off screen
        if self.rect.left > screen_size[0] or self.rect.right < 0:
            self.kill()


class main(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.sprites = []

        # Walking sprites
        self.walk_sprites = [
            pygame.image.load('assets/walk_1.png'),
            pygame.image.load('assets/walk_2.png'),
            pygame.image.load('assets/walk_3.png')
        ]
        # Sprite to stand still
        self.idle_sprites = [
            pygame.image.load('assets/stop.png')
        ]

        # Jump sprite
        self.jump_sprites = [
            (pygame.image.load('assets/jump.png'))
        ]

        # NEW SHOOTING SPRITES
        self.shoot_idle_sprites = [
            pygame.image.load('assets/shooting.png')
        ]
        self.shoot_walk_sprites = [
            pygame.image.load('assets/shoot_walking_1.png'),
            pygame.image.load('assets/shoot_walking_2.png'),
            pygame.image.load('assets/shoot_walking_3.png')
        ]
        self.jump_shoot_sprites = [
            pygame.image.load('assets/jump_shoot.png')
        ]

        self.action_state = "idle"
        self.current_frame = 0
        self.speed = 8
        self.direction = 1
        self.image = self.idle_sprites[self.current_frame]
        self.image = pygame.transform.scale(self.image, (499/5, 500/5))

        self.rect = self.image.get_rect()
        self.rect.topleft = 200, 530
        self.is_animating = False
        self.y_velocity = 0
        self.is_jumping = False
        self.is_shooting = False

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.y_velocity = -20
            if not self.is_shooting:
                self.action_state = "jumping"
            else:
                self.action_state = "jumping_shooting"
            self.is_animating = True
            self.current_frame = 0

    def walk(self, direction):
        if not self.is_jumping:
            self.is_animating = True
            self.direction = direction
            if not self.is_shooting:
                self.action_state = "walking"
            else:
                self.action_state = "shooting_walking"

    def stop(self):
        if not self.is_jumping and not self.is_shooting:
            self.is_animating = False
            self.current_frame = 0
            self.action_state = "idle"
        elif self.is_shooting and not self.is_jumping:
            self.is_animating = False
            self.current_frame = 0
            self.action_state = "shooting_idle"

    def shoot(self):
        # This method is called when 'Z' is pressed
        if not self.is_shooting:
            self.is_shooting = True
            if self.action_state == "idle":
                self.action_state = "shooting_idle"
            elif self.action_state == "walking":
                self.action_state = "shooting_walking"
            elif self.action_state == "jumping":
                self.action_state = "jumping_shooting"
            self.current_frame = 0
            proj_x = self.rect.centerx + (50 * self.direction)
            proj_y = self.rect.centery - 10
            return Projectile(proj_x, proj_y, self.direction)
        return None

    def reset_shoot(self):
        # Called when 'Z' is released
        self.is_shooting = False
        # Reset state based on current movement
        if self.is_jumping:
            self.action_state = "jumping"
        elif self.rect.x != self.old_x or self.rect.y != self.old_y:
            self.action_state = "walking"
        else:
            self.action_state = "idle"
        self.is_animating = False
        self.current_frame = 0

    def update(self):
        self.old_x = self.rect.x
        self.old_y = self.rect.y

        # Update vertical position due to gravity
        self.rect.y += self.y_velocity
        self.y_velocity += 1

        # Check for ground collision
        if self.rect.y >= 530:
            self.rect.y = 530
            self.y_velocity = 0
            if self.is_jumping:
                self.is_jumping = False
                if self.action_state in ["jumping", "jumping_shooting"]:
                    if self.is_shooting:
                        self.action_state = "shooting_idle"
                    else:
                        self.action_state = "idle"
                    self.is_animating = False
                    self.current_frame = 0

        # Select sprites based on current action state
        if self.action_state == "jumping":
            self.sprites = self.jump_sprites
        elif self.action_state == "walking":
            self.sprites = self.walk_sprites
        elif self.action_state == "shooting_idle":
            self.sprites = self.shoot_idle_sprites
        elif self.action_state == "shooting_walking":
            self.sprites = self.shoot_walk_sprites
        elif self.action_state == "jumping_shooting":
            self.sprites = self.jump_shoot_sprites
        else:  # "idle"
            self.sprites = self.idle_sprites

        # Animate if necessary
        if self.is_animating:
            self.current_frame = self.current_frame + 0.5
            if self.current_frame >= len(self.sprites):
                self.current_frame = 0
            self.image = self.sprites[int(self.current_frame)]
            self.image = pygame.transform.scale(self.image, (499/5, 500/5))

            # Flip sprite based on direction
            if self.direction == 1:
                self.image = pygame.transform.flip(self.image, True, False)
        else:  # If not animating, use the first sprite of the current state
            self.image = self.sprites[0]
            self.image = pygame.transform.scale(self.image, (499/5, 500/5))
            if self.direction == 1:
                self.image = pygame.transform.flip(self.image, True, False)


# Sprite Creation
all_sprites = pygame.sprite.Group()
megaman = main()
all_sprites.add(megaman)

projectiles = pygame.sprite.Group()

# Clock
clock = pygame.time.Clock()
FPS = 30

# MAIN LOOP
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                new_projectile = megaman.shoot()
                if new_projectile:
                    all_sprites.add(new_projectile)
                    projectiles.add(new_projectile)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_z:
                megaman.reset_shoot()

    keys = pygame.key.get_pressed()
    moving = False

    # Handle movement
    if keys[pygame.K_RIGHT]:
        megaman.rect.x += megaman.speed
        megaman.direction = 1
        megaman.walk(1)
        moving = True
    elif keys[pygame.K_LEFT]:
        megaman.rect.x -= megaman.speed
        megaman.direction = -1
        megaman.walk(-1)
        moving = True

    # Handle jumping (can be combined with shooting)
    if keys[pygame.K_SPACE]:
        megaman.jump()

    # If not moving and not jumping, and not actively shooting
    if not moving and not megaman.is_jumping and not megaman.is_shooting:
        megaman.stop()
    elif not moving and not megaman.is_jumping and megaman.is_shooting:
        megaman.action_state = "shooting_idle"
        megaman.is_animating = False
        megaman.current_frame = 0

    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    pygame.display.flip()
    all_sprites.update()

pygame.quit()
