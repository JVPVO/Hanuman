import main
import pygame
from pygame.sprite import *

class Skeleton():
    def __init__(self, x, y, initial_scale):
        #TODO Fazer um json que tem o nome dos inimigos e cada uma das sprites sheets deles, por enquanto vou deixar vazio e hard-coded no código
        self.sprite = main.Animation(image_file='assets/Skeleton-Idle.png', total_frames=4, frame_width=32, frame_height=32)
        self.sprite.x, self.sprite.y = x, y
        self.rect = pygame.Rect(x, y, 19, 30)  # Tamanho do jogador, ajuste conforme necessário
        self.speed = 8  # Velocidade de movimento do jogador
        self.scale_factor = initial_scale
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500  # Cooldown de 500 milissegundos

        self.sprite.rescale_frames(initial_scale)
        self.rect.width = int(19 * initial_scale) #ajusta o rect
        self.rect.height = int(30 * initial_scale) #ajusta o rect
        self.scale(initial_scale)
    def draw(self, surface:pygame.Surface):
        surface.blit(self.sprite.image, (self.sprite.x, self.sprite.y))
    def scale(self, scale_factor):
        """Redimensiona o sprite do jogador."""
        now = pygame.time.get_ticks()
        if now - self.last_scale_time > self.scale_cooldown:
            self.last_scale_time = now
            self.scale_factor *= scale_factor
            if 0.1 < self.scale_factor < 10:  # Limita a escala a um intervalo razoável
                self.sprite.rescale_frames(self.scale_factor)
                self.rect.width = int(32 * self.scale_factor) #ajusta o rect
                self.rect.height = int(32 * self.scale_factor) #ajusta o rect