import main
import pygame
from pygame.sprite import *

class Skeleton():
    def __init__(self, x, y, initial_scale):
        #TODO Fazer um json que tem o nome dos inimigos e cada uma das sprites sheets deles, por enquanto vou deixar vazio e hard-coded no código
        self.sprite = main.Animation(image_file='assets/Skeleton-Idle.png', total_frames=4, frame_width=32, frame_height=32)
        self.sprite.x, self.sprite.y = x, y
        self.rect = pygame.Rect(x, y, 32, 32)  # Tamanho do jogador, ajuste conforme necessário
        self.speed = 2  # Velocidade de movimento do jogador
        self.scale_factor = initial_scale
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500  # Cooldown de 500 milissegundos
        self.health = 3
        self.invencibilidade = 300 #Cooldown de 300 milissegundos para cada ataque individual
        self.ataquesRecebidos = {}


        self.sprite.rescale_frames(initial_scale)
        self.rect.width = int(32 * initial_scale) #ajusta o rect
        self.rect.height = int(32 * initial_scale) #ajusta o rect

    def draw(self, surface:pygame.Surface, camera):
        main.draw(self, surface, camera)
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
    #implementar na hierarquia, não sei como ainda mas vou fazer assim que descobrir, mas enfim...
    def movement(self, playerX, playerY):
        if self.sprite.x > playerX+5: self.sprite.x -= self.speed
        elif self.sprite.x < playerX-5: self.sprite.x += self.speed
        if self.sprite.y > playerY+5: self.sprite.y -= self.speed
        elif self.sprite.y < playerY-5: self.sprite.y += self.speed
        self.rect.x = self.sprite.x
        self.rect.y = self.sprite.y
    def colisao(self, alvo):
        print(f"Analisando {id(alvo)}")
        print(self.ataquesRecebidos)
        print(f"Tempo atual: {pygame.time.get_ticks()}")
        print(f"Vida atual {self.health}")
        if id(alvo) not in self.ataquesRecebidos:
            if self.rect.colliderect(alvo.rot_image_rect):
                self.ataquesRecebidos[id(alvo)] = pygame.time.get_ticks()
                if self.health > 1:
                    self.health -= 1
                    return False
                else:
                    return True
        elif pygame.time.get_ticks() - self.ataquesRecebidos[id(alvo)] > self.invencibilidade:   
            if self.rect.colliderect(alvo.rot_image_rect):
                self.ataquesRecebidos[id(alvo)] = pygame.time.get_ticks()
                if self.health > 1:
                    self.health -= 1
                    return False
                else:
                    return True
        return False