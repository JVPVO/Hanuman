# player.py
import pygame
from animation_Wip import Animation
from inimigos import Skeleton
from camera import Camera
from weapons import Weapon
from menus import DamageNumber

class Player:
    def __init__(self, x, y, collision_sprites, initial_scale=1):
        self.sprite = Animation(image_file='assets/Idle-Sheet.png', total_frames=4, frame_width=19, frame_height=30)
        self.sprite.x, self.sprite.y = x, y
        self.rect = pygame.Rect(x, y, 19, 30)  # Tamanho do jogador, ajuste conforme necessário
        self.speed = 8  # Velocidade de movimento do jogador
        self.scale_factor = initial_scale
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500  # Cooldown de 500 milissegundos
        self.sprite.rescale_frames(initial_scale)
        self.rect.width = int(19 * initial_scale)  # Ajusta o rect
        self.rect.height = int(30 * initial_scale)  # Ajusta o rect
        self.y_sort = self.rect.y + self.rect.height

        self.weapon = [Weapon('assets/Weapon.png', 70, 30, initial_scale)]
        self.selected_weapon = 0
        self.health = 100
        self.collision_sprites = collision_sprites
        self.pos_anterior = (self.rect.x, self.rect.y)

        self.mode = 'idle'
        self.scaled = False
        self.dashing = False
        self.dash_speed = 20  # Velocidade durante o dash
        self.dash_duration = 300  # Duração do dash em milissegundos
        self.dash_cooldown = 1000  # Tempo de cooldown do dash em milissegundos
        self.last_dash_time = pygame.time.get_ticks() - self.dash_cooldown
        self.dash_start_time = None
        self.dash_direction = pygame.Vector2(0, 0)

        self.animations = {'idle': 'Idle-Sheet.png', 'run': 'Run-Sheet.png'}
        self.processed = {'idle': False, 'run': False}
        self.spritesheets = {'idle': self.sprite}

        self.loader('idle', self.animations['idle'], frames=4)
        self.loader('run', self.animations['run'], frames=6)

        self.damage_numbers = []
        self.last_hit = 0
    def loader(self, mode, file, frames):
        if not self.processed[mode]:
            if mode == 'idle':
                fWidth = 19
                fHeight = 30
            else:
                fWidth = 32
                fHeight = 32
            objeto = Animation(image_file=f'assets/{file}', total_frames=frames, frame_width=fWidth, frame_height=fHeight)
            objeto.x, objeto.y = self.sprite.x, self.sprite.y
            objeto.rescale_frames(self.scale_factor)
            self.spritesheets[mode] = objeto
            self.processed[mode] = True
        self.sprite = self.spritesheets[mode]

    def dash(self, mouse_pos):
        now = pygame.time.get_ticks()
        if now - self.last_dash_time >= self.dash_cooldown:
            self.dashing = True
            self.dash_start_time = now
            self.last_dash_time = now
            dash_vector = pygame.Vector2(mouse_pos) - pygame.Vector2(self.rect.center)
            self.dash_direction = dash_vector.normalize() if dash_vector.length() > 0 else pygame.Vector2(0, 0)

    def handle_keys(self, key_pressed, camera: Camera, grupos):
        self.pos_anterior = (self.rect.x, self.rect.y)
        weapon = self.weapon[self.selected_weapon]
        firstPos = (self.rect.x, self.rect.y)
        mouse_pos = pygame.mouse.get_pos()

        if key_pressed[pygame.K_LCTRL]:
            self.speed = 1
        else:
            if self.speed == 1:
                self.dash(mouse_pos)
            self.speed = 8

        if self.dashing:
            if pygame.time.get_ticks() - self.dash_start_time <= self.dash_duration:
                dash_speed = self.dash_speed
                self.rect.x += self.dash_direction.x * dash_speed
                self.rect.y += self.dash_direction.y * dash_speed
            else:
                self.dashing = False

        if not self.dashing:
            if key_pressed[pygame.K_w]:
                self.rect.y -= self.speed
            if key_pressed[pygame.K_s]:
                self.rect.y += self.speed
            if key_pressed[pygame.K_a]:
                self.sprite.rotate('l')
                self.rect.x -= self.speed
            if key_pressed[pygame.K_d]:
                self.sprite.rotate('r')
                self.rect.x += self.speed

        if key_pressed[pygame.K_p]:
            self.scale(1.5)
        if key_pressed[pygame.K_o]:
            self.scale(0.5)
        if key_pressed[pygame.K_ESCAPE]:
            pygame.quit()
        if key_pressed[pygame.K_l]:
            if pygame.time.get_ticks() - self.last_scale_time > self.scale_cooldown:
                Skeleton(self.sprite.x + 30, self.sprite.y + 30, initial_scale=3, groups=(grupos[0], grupos[1]))
                self.last_scale_time = pygame.time.get_ticks()

        if firstPos[0] != self.rect.x or firstPos[1] != self.rect.y:
            if self.mode != 'run':
                self.mode = 'run'
                self.loader('run', self.animations['run'], frames=6)
        else:
            if self.mode != 'idle':
                self.mode = 'idle'
                self.loader('idle', self.animations['idle'], frames=4)

        self.check_collision()
        self.y_sort = self.rect.y + self.rect.height
        weapon.update(self.rect, camera, self.rect.height, key_pressed)
        self.sprite.x, self.sprite.y = self.rect.topleft

    def scale(self, scale_factor):
        now = pygame.time.get_ticks()
        if now - self.last_scale_time > self.scale_cooldown:
            self.last_scale_time = now
            self.scale_factor *= scale_factor
            if 0.1 < self.scale_factor < 10:
                self.sprite.rescale_frames(self.scale_factor)
                self.rect.width = int(19 * self.scale_factor)
                self.rect.height = int(30 * self.scale_factor)

    def check_collision(self):
        for objeto in self.collision_sprites:
            eixox = self.rect.x + self.rect.width > objeto.hitbox.x and self.rect.x < objeto.hitbox.x + objeto.hitbox.width
            eixoy = self.rect.y + self.rect.height > objeto.hitbox.y and self.rect.y + self.rect.height < objeto.hitbox.y + objeto.hitbox.height
            if eixox and eixoy:
                if eixox:
                    self.rect.x = self.pos_anterior[0]
                if eixoy:
                    self.rect.y = self.pos_anterior[1]

    def draw(self, surface: pygame.Surface, camera):
        adjusted_rect = camera.apply(self.rect)
        surface.blit(self.sprite.image, adjusted_rect.topleft)
        self.weapon[self.selected_weapon].draw(surface, camera)

    def colisao(self, alvo):
        return self.rect.colliderect(alvo.rect)
    
    def take_damage(self, amount):
        if pygame.time.get_ticks() - self.last_hit > 200:
            self.health -= amount
            damage_number = DamageNumber(self.rect.centerx, self.rect.y, amount)
            self.damage_numbers.append(damage_number)
            self.last_hit = pygame.time.get_ticks()

    def update_damage_numbers(self):
        self.damage_numbers = [dn for dn in self.damage_numbers if dn.update()]

    def draw_damage_numbers(self, surface, camera):
        for damage_number in self.damage_numbers:
            damage_number.draw(surface, camera)

