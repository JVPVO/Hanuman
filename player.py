import pygame
from animation_Wip import Animation
from inimigos import Skeleton
from camera import Camera
from weapons import Weapon
import math


class Player:
    def __init__(self, x, y, initial_scale=1):
        self.sprite = Animation(image_file='assets/Idle-Sheet.png', total_frames=4, frame_width=19, frame_height=30)
        self.sprite.x, self.sprite.y = x, y
        self.rect = pygame.Rect(x, y, 19, 30)  # Tamanho do jogador, ajuste conforme necessário
        self.speed = 8  # Velocidade de movimento do jogador
        self.scale_factor = initial_scale
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500  # Cooldown de 500 milissegundos
        
        self.weapon = [Weapon('assets/Weapon.png', 70, 30, initial_scale)]
        self.selected_weapon = 0
        self.health = 3
        
        self.mode = 'idle'
        self.scaled = False
        self.dashing = False
        self.dash_speed = 20  # Velocidade durante o dash
        self.dash_duration = 300  # Duração do dash em milissegundos
        self.dash_cooldown = 1000  # Tempo de cooldown do dash em milissegundos
        self.last_dash_time = pygame.time.get_ticks() - self.dash_cooldown
        self.dash_start_time = None
        self.dash_direction = pygame.Vector2(0, 0)
        
        if not self.scaled:
            self.sprite.rescale_frames(initial_scale)
            self.rect.width = int(19 * initial_scale)  # Ajusta o rect
            self.rect.height = int(32 * initial_scale)  # Ajusta o rect
            self.scaled = True
        
        self.animations = {'idle': 'Idle-Sheet.png', 'run': 'Run-Sheet.png'}
        self.processed = {'idle': True, 'run': False}
        self.spritesheets = {'idle': self.sprite}
    
    def loader(self, file, x, y, frames):
        if not self.processed[self.mode]:
            objeto = Animation(image_file=f'assets/{file}', total_frames=frames, frame_width=32, frame_height=32)
            objeto.x, objeto.y = x, y
            objeto.rescale_frames(3)
            self.spritesheets[self.mode] = objeto
            self.processed[self.mode] = True
        self.sprite = self.spritesheets[self.mode]
        self.sprite.x, self.sprite.y = x, y
    
    def dash(self, mouse_pos):
        #TODO botar efeito nessa porraaaaaaaaaaaa
        now = pygame.time.get_ticks()
        if now - self.last_dash_time >= self.dash_cooldown:
            self.dashing = True
            self.dash_start_time = now
            self.last_dash_time = now
            dash_vector = pygame.Vector2(mouse_pos) - pygame.Vector2(self.rect.center)
            self.dash_direction = dash_vector.normalize() if dash_vector.length() > 0 else pygame.Vector2(0, 0)
    
    def handle_keys(self, key_pressed, camera: Camera, inimigos):
        """Atualiza a posição do jogador com base nas teclas pressionadas."""
        weapon = self.weapon[self.selected_weapon]
        firstPos = (self.rect.x, self.rect.y)
        
        # Obter posição do mouse
        mouse_pos = pygame.mouse.get_pos()

        # Se a tecla LCTRL está pressionada, reduz a velocidade
        if key_pressed[pygame.K_LCTRL]:
            self.speed = 1
        else:
            # Se LCTRL foi solto, aciona o dash
            if self.speed == 1:
                self.dash(mouse_pos)
            self.speed = 8  # Reseta a velocidade para o valor normal

        # Atualizar velocidade de movimento durante o dash
        if self.dashing:
            if pygame.time.get_ticks() - self.dash_start_time <= self.dash_duration:
                dash_speed = self.dash_speed
                self.rect.x += self.dash_direction.x * dash_speed
                self.rect.y += self.dash_direction.y * dash_speed
            else:
                self.dashing = False

        # Movimentação do jogador
        if not self.dashing:  # Permitir movimento normal apenas se não estiver dashing
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

        # Outros controles
        if key_pressed[pygame.K_p]:
            self.scale(1.5)  # Aumenta a escala em 50%
        if key_pressed[pygame.K_o]:
            self.scale(0.5)  # Diminui a escala em 50%
        if key_pressed[pygame.K_ESCAPE]:
            pygame.quit()
        if key_pressed[pygame.K_l]:
            if pygame.time.get_ticks() - self.last_scale_time > self.scale_cooldown:
                inimigos.append(Skeleton(self.sprite.x + 30, self.sprite.y + 30, initial_scale=3))
                self.last_scale_time = pygame.time.get_ticks()
        
        if firstPos[0] != self.rect.x or firstPos[1] != self.rect.y:
            if self.mode != 'run':
                self.mode = 'run'
                file = self.animations['run']
                self.loader(file, self.sprite.x, self.sprite.y, frames=6)
        else:
            if self.mode != 'idle':
                self.mode = 'idle'
                file = self.animations['idle']
                self.loader(file, self.sprite.x, self.sprite.y, frames=4)
        weapon.update(self.rect, camera, self.rect.height, key_pressed)
        self.sprite.x, self.sprite.y = self.rect.topleft
    
    def scale(self, scale_factor):
        """Redimensiona o sprite do jogador."""
        now = pygame.time.get_ticks()
        if now - self.last_scale_time > self.scale_cooldown:
            self.last_scale_time = now
            self.scale_factor *= scale_factor
            if 0.1 < self.scale_factor < 10:  # Limita a escala a um intervalo razoável
                self.sprite.rescale_frames(self.scale_factor)
                self.rect.width = int(19 * self.scale_factor)  # Ajusta o rect
                self.rect.height = int(30 * self.scale_factor)  # Ajusta o rect
    
    def draw(self, surface: pygame.Surface, camera):
        """Desenha o jogador na superfície, ajustando pela posição da câmera."""
        adjusted_rect = camera.apply(self.rect)
        
        # surface.blit(pygame.Surface((self.rect.width,self.rect.height)), camera.apply(pygame.Rect(self.sprite.x, self.sprite.y, self.rect.width, self.rect.height)))
        # debug ^
        
        surface.blit(self.sprite.image, adjusted_rect.topleft)
        
        self.weapon[self.selected_weapon].draw(surface, camera)
    
    def colisao(self, alvo):
        return self.rect.colliderect(alvo.rect)
