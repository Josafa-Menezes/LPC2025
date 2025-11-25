
import math
from random import uniform

import pygame as pg

import config as C
from utils import Vec, angle_to_vec, draw_circle, draw_poly, wrap_pos

import sounds


class Bullet(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.ttl = C.BULLET_TTL
        self.r = C.BULLET_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        draw_circle(surf, self.pos, self.r)


class Asteroid(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec, size: str):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.size = size  # 'L' | 'M' | 'S'
        self.r = C.AST_SIZES[size]["r"]
        self.poly = self._make_poly()
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def _make_poly(self):
        steps = 12 if self.size == "L" else 10 if self.size == "M" else 8
        pts = []
        for i in range(steps):
            ang = i * (360 / steps)
            jitter = uniform(0.75, 1.2)
            r = self.r * jitter
            v = Vec(math.cos(math.radians(ang)),
                    math.sin(math.radians(ang)))
            pts.append(v * r)
        return pts

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        pts = [(self.pos + p) for p in self.poly]
        pg.draw.polygon(surf, C.WHITE, pts, width=1)


class Ship(pg.sprite.Sprite):
    def __init__(self, pos: Vec):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(0, 0)
        self.angle = -90.0
        self.cool = 0.0
        self.invuln = 0.0
        self.alive = True
        self.r = C.SHIP_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def control(self, keys: pg.key.ScancodeWrapper, dt: float):
        if keys[pg.K_LEFT]:
            self.angle -= C.SHIP_TURN_SPEED * dt
        if keys[pg.K_RIGHT]:
            self.angle += C.SHIP_TURN_SPEED * dt
        if keys[pg.K_UP]:
            self.vel += angle_to_vec(self.angle) * C.SHIP_THRUST * dt
        self.vel *= C.SHIP_FRICTION

    def fire(self) -> Bullet | None:
        if self.cool > 0:
            return None
        dirv = angle_to_vec(self.angle)
        pos = self.pos + dirv * (self.r + 6)
        vel = self.vel + dirv * C.SHIP_BULLET_SPEED
        self.cool = C.SHIP_FIRE_RATE
        return Bullet(pos, vel)

    def hyperspace(self):
        self.pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))
        self.vel.xy = (0, 0)
        self.invuln = 1.0

    def update(self, dt: float):
        if self.cool > 0:
            self.cool -= dt
        if self.invuln > 0:
            self.invuln -= dt
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        dirv = angle_to_vec(self.angle)
        left = angle_to_vec(self.angle + 140)
        right = angle_to_vec(self.angle - 140)
        p1 = self.pos + dirv * self.r
        p2 = self.pos + left * self.r * 0.9
        p3 = self.pos + right * self.r * 0.9
        draw_poly(surf, [p1, p2, p3])
        if self.invuln > 0 and int(self.invuln * 10) % 2 == 0:
            draw_circle(surf, self.pos, self.r + 6)


# Em src/sprites.py

class UFO(pg.sprite.Sprite):
    def __init__(self, pos: Vec, small: bool, target_pos: Vec = None):
        super().__init__()
        self.pos = Vec(pos)
        self.small = small
        self.r = C.UFO_SMALL["r"] if small else C.UFO_BIG["r"]
        self.speed = C.UFO_SPEED
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

        # --- LÓGICA DE MOVIMENTO (AQUI ESTÁ A MUDANÇA) ---
        if self.small and target_pos is not None:
            # NAVE PEQUENA: "Trajectory Shot"
            # Calcula o vetor que aponta da nave inimiga para o jogador AGORA.
            desired_dir = target_pos - self.pos
            
            # Normaliza (transforma em tamanho 1, mantendo a direção)
            if desired_dir.length() > 0:
                desired_dir = desired_dir.normalize()
            else:
                desired_dir = Vec(1, 0) # Fallback se nascer exatamente em cima

            # Adiciona uma aleatoriedade (Jitter) para não ser uma linha reta perfeita "sniper"
            # Isso faz ela ir "na direção", mas talvez passe um pouco ao lado
            desired_dir.x += uniform(-0.2, 0.2)
            desired_dir.y += uniform(-0.2, 0.2)
            
            self.dir = desired_dir.normalize()
            
        else:
            # NAVE GRANDE (ou sem alvo):
            # Comportamento Clássico: horizontal com leve inclinação vertical aleatória
            # Se nasceu na esquerda (x < width/2), vai pra direita (1), senão pra esquerda (-1)
            direction_x = 1 if self.pos.x < C.WIDTH / 2 else -1
            direction_y = uniform(-0.5, 0.5) # Leve movimento vertical
            self.dir = Vec(direction_x, direction_y).normalize()
        # ----------------------------------------------------

        # Configuração do Tiro (Mantivemos igual)
        self.shoot_timer = uniform(0, 1.0)
        self.shoot_delay = C.UFO_FIRE_RATE_SMALL if small else C.UFO_FIRE_RATE_BIG

        # Som
        self.channel = pg.mixer.find_channel()
        if self.channel is not None:
            engine_sound = sounds.FLY_SMALL if self.small else sounds.FLY_BIG
            self.channel.play(engine_sound, loops=-1)

    # ... (O resto dos métodos update, fire, draw, kill continuam IGUAIS ao passo anterior) ...
    def update(self, dt: float):
        self.pos += self.dir * self.speed * dt
        self.pos = wrap_pos(self.pos)
        self.rect.center = self.pos
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

    def fire(self, target_pos: Vec = None) -> Bullet | None:
        if self.shoot_timer > 0: return None
        self.shoot_timer = self.shoot_delay
        angle = 0.0
        if self.small and target_pos is not None:
            diff = target_pos - self.pos
            angle = math.degrees(math.atan2(diff.y, diff.x)) + uniform(-5, 5)
        else:
            angle = uniform(0, 360)
        dirv = angle_to_vec(angle)
        spawn_pos = self.pos + dirv * (self.r + 10)
        vel = dirv * C.UFO_BULLET_SPEED
        return Bullet(spawn_pos, vel)

    def draw(self, surf: pg.Surface):
        w, h = self.r * 2, self.r
        rect = pg.Rect(0, 0, w, h)
        rect.center = self.pos
        pg.draw.ellipse(surf, C.WHITE, rect, width=1)
        cup = pg.Rect(0, 0, w * 0.5, h * 0.7)
        cup.center = (self.pos.x, self.pos.y - h * 0.3)
        pg.draw.ellipse(surf, C.WHITE, cup, width=1)

    def kill(self) -> None:
        if hasattr(self, "channel") and self.channel is not None:
            self.channel.stop()
        super().kill()
