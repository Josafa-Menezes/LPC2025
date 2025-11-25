import math
from random import uniform

import pygame as pg

import config as C
import sounds
from sprites import Asteroid, Ship, UFO
from utils import Vec, rand_edge_pos, rand_unit_vec


class World:
    def __init__(self) -> None:
        # Main sprite groups
        self.ship = Ship(Vec(C.WIDTH / 2, C.HEIGHT / 2))
        self.bullets = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()

        self.all_sprites.add(self.ship)

        # Game state
        self.score = 0
        self.lives = C.START_LIVES
        self.wave = 0
        self.wave_cool = C.WAVE_DELAY
        self.safe = C.SAFE_SPAWN_TIME
        self.ufo_timer = C.UFO_SPAWN_EVERY

        # Start first wave
        self.start_wave()

    def start_wave(self) -> None:
        """Start a new asteroid wave."""
        self.wave += 1
        count = 3 + self.wave
        for _ in range(count):
            pos = rand_edge_pos()
            while (pos - self.ship.pos).length() < 150:
                pos = rand_edge_pos()
            ang = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel = Vec(math.cos(ang), math.sin(ang)) * speed
            self.spawn_asteroid(pos, vel, "L")

    def spawn_asteroid(self, pos: Vec, vel: Vec, size: str) -> None:
        """Spawn a new asteroid of a given size."""
        asteroid = Asteroid(pos, vel, size)
        self.asteroids.add(asteroid)
        self.all_sprites.add(asteroid)

    def spawn_ufo(self) -> None:
        """Spawn a UFO at a random side of the screen."""
        small = uniform(0, 1) < 0.5
        
        # Define a posição de nascimento (esquerda ou direita)
        y = uniform(0, C.HEIGHT)
        x = 0 if uniform(0, 1) < 0.5 else C.WIDTH
        
        # Pega a posição atual do player (se estiver vivo) para usar na mira de movimento
        # Se o player estiver morto, mira no centro da tela
        target_pos = self.ship.pos if self.ship.alive else Vec(C.WIDTH/2, C.HEIGHT/2)
        
        # Passamos o target_pos para a classe UFO
        ufo = UFO(Vec(x, y), small, target_pos) 
        
        self.ufos.add(ufo)
        self.all_sprites.add(ufo)

    def try_fire(self) -> None:
        """Try to fire a bullet from the ship."""
        if len(self.bullets) >= C.MAX_BULLETS:
            return

        bullet = self.ship.fire()
        if bullet is None:
            return

        self.bullets.add(bullet)
        self.all_sprites.add(bullet)

        # Play shooting sound
        sounds.SHOT.play()

    def hyperspace(self) -> None:
        """Teleport the ship to a random position."""
        if not self.ship.alive:
            return

        self.ship.pos.xy = (
            uniform(0, C.WIDTH),
            uniform(0, C.HEIGHT),
        )
        self.ship.vel.xy = (0, 0)

    def update(self, dt: float, keys: pg.key.ScancodeWrapper) -> None:
        """Update world state."""
        # Update ship control and all sprite logic
        self.ship.control(keys, dt)
        self.all_sprites.update(dt)
        
        player_pos = self.ship.pos if self.ship.alive else None
        for ufo in self.ufos:
            # Chama a função fire() que criamos no sprites.py
            bullet = ufo.fire(player_pos)
            if bullet:
                self.enemy_bullets.add(bullet) # Adiciona no grupo de tiros inimigos
                self.all_sprites.add(bullet)   # Adiciona para desenhar na tela

        # Timers
        if self.safe > 0:
            self.safe -= dt
            self.ship.invuln = 0.5
        else:
            self.ship.invuln = max(self.ship.invuln - dt, 0.0)

        self.ufo_timer -= dt
        if self.ufo_timer <= 0:
            self.spawn_ufo()
            self.ufo_timer = C.UFO_SPAWN_EVERY

        self.handle_collisions()

        # Waves
        if not self.asteroids and self.wave_cool <= 0:
            self.start_wave()
            self.wave_cool = C.WAVE_DELAY
        elif not self.asteroids:
            self.wave_cool -= dt

    def handle_collisions(self) -> None:
        """Handle all collisions between objects."""
        
        # --- 1. Balas do Player vs Asteroides ---
        hits = pg.sprite.groupcollide(
            self.asteroids,
            self.bullets,
            False, # Asteroides não somem direto (usamos split_asteroid)
            True,  # Balas somem
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for asteroid, _ in hits.items():
            self.split_asteroid(asteroid)

        # --- 2. Colisões que matam o Player ---
        # Só checa se o player não estiver invulnerável (renascendo)
        if self.ship.invuln <= 0 and self.safe <= 0:
            
            # Player vs Asteroides
            for asteroid in self.asteroids:
                if (asteroid.pos - self.ship.pos).length() < (asteroid.r + self.ship.r):
                    self.ship_die()
                    break

            # Player vs UFOs
            if self.ship.alive:
                for ufo in self.ufos:
                    if (ufo.pos - self.ship.pos).length() < (ufo.r + self.ship.r):
                        self.ship_die()
                        break
            
            # Player vs Balas Inimigas (Enemy Bullets)
            if self.ship.alive:
                # Checa se alguma bala inimiga tocou no player
                hits = pg.sprite.spritecollide(
                    self.ship, 
                    self.enemy_bullets, 
                    True, # A bala some ao bater
                    collided=pg.sprite.collide_circle # Usa o raio/rect para colisão
                )
                if hits:
                    self.ship_die()

        # --- 3. Balas do Player vs UFOs ---
        # (Usa listas manuais para calcular a distância circular customizada)
        for ufo in list(self.ufos):
            for bullet in list(self.bullets):
                if (ufo.pos - bullet.pos).length() < (ufo.r + bullet.r):
                    score = (
                        C.UFO_SMALL["score"]
                        if ufo.small
                        else C.UFO_BIG["score"]
                    )
                    self.score += score
                    ufo.kill()
                    bullet.kill()

        # --- 4. UFOs vs Asteroides (Onde estava o erro) ---
        # Verifica colisão entre UFOs e Asteroides
        crashes = pg.sprite.groupcollide(
            self.ufos,
            self.asteroids,
            True,  # O UFO morre imediatamente
            False, # O Asteroide será dividido manualmente
            collided=lambda u, a: (u.pos - a.pos).length() < (u.r + a.r)
        )

        for ufo, asteroids_hit in crashes.items():
            # Para o som do UFO se ele morrer
            if hasattr(ufo, "channel") and ufo.channel:
                ufo.channel.stop()
            
            # Divide os asteroides que ele bateu
            for asteroid in asteroids_hit:
                self.split_asteroid(asteroid)

    def split_asteroid(self, asteroid: Asteroid) -> None:
        """Split an asteroid into smaller pieces and add score."""
        # Play asteroid break sound
        if asteroid.size == "L":
            sounds.BREAK_LARGE.play()
        else:
            sounds.BREAK_MEDIUM.play()

        self.score += C.AST_SIZES[asteroid.size]["score"]
        split_sizes = C.AST_SIZES[asteroid.size]["split"]

        pos = Vec(asteroid.pos)
        asteroid.kill()

        for size in split_sizes:
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * 1.2
            self.spawn_asteroid(pos, dirv * speed, size)

    def ship_die(self) -> None:
        """Handle ship death and lives."""
        if not self.ship.alive:
            return

        # Sound of ship explosion (reuse large break)
        sounds.BREAK_LARGE.play()

        self.lives -= 1
        self.ship.alive = False

        # Respawn or reset game
        if self.lives >= 0:
            self.ship.pos.xy = (C.WIDTH / 2, C.HEIGHT / 2)
            self.ship.vel.xy = (0, 0)
            self.ship.angle = -90.0
            self.ship.invuln = C.SAFE_SPAWN_TIME
            self.safe = C.SAFE_SPAWN_TIME
            self.ship.alive = True
        else:
            # Reset everything
            self.__init__()

    def draw(self, surf: pg.Surface, font: pg.font.Font) -> None:
        """Draw all sprites and HUD."""
        for spr in self.all_sprites:
            spr.draw(surf)

        pg.draw.line(
            surf,
            (60, 60, 60),
            (0, 50),
            (C.WIDTH, 50),
            width=1,
        )

        txt = f"SCORE {self.score:06d}   LIVES {self.lives}   WAVE {self.wave}"
        label = font.render(txt, True, C.WHITE)
        surf.blit(label, (10, 10))
