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

        self.mode = 'idle'
        self.scaled = False

        if not self.scaled:
            self.sprite.rescale_frames(initial_scale)
            self.rect.width = int(32 * initial_scale) #ajusta o rect
            self.rect.height = int(32 * initial_scale) #ajusta o rect
            self.scaled = True
        self.animations = {'idle': 'Skeleton-Idle.png', 'run': 'Skeleton_Run-Sheet.png'}
        self.processed = {'idle': True, 'run': False}
        self.spritesheets = {'idle': self.sprite}
    def draw(self, surface:pygame.Surface, camera):
        main.draw(self, surface, camera)
    def loader(self, file, x, y, frames):
        if not self.processed[self.mode]:
            objeto = main.Animation(image_file=f'assets/{file}', total_frames=frames, frame_width=32, frame_height=32)
            objeto.x, objeto.y = x, y
            objeto.rescale_frames(3)
            self.spritesheets[self.mode] = objeto
            self.processed[self.mode] = True
        print(id(self.sprite))
        self.sprite = self.spritesheets[self.mode]
        self.sprite.x, self.sprite.y = x,y
    def movement(self, playerX, playerY):
        firstPos = (self.sprite.x, self.sprite.y)
        if self.sprite.x > playerX+5: 
            self.sprite.x -= self.speed
            self.sprite.rotate('l')
        elif self.sprite.x < playerX-5: 
            self.sprite.x += self.speed
            self.sprite.rotate('r')
        if self.sprite.y > playerY+5: self.sprite.y -= self.speed
        elif self.sprite.y < playerY-5: self.sprite.y += self.speed
        self.rect.x = self.sprite.x
        self.rect.y = self.sprite.y
        #Ele basicamente testa se houve algum movimento com a invocação da função, se houve, ele realiza a mudança da animação pra uma de corrida
        #Se não houve nenhum movimento ele volta pra animação idle
        if firstPos[0] != self.sprite.x or firstPos[1] != self.sprite.y:
            if self.mode != 'run':
                self.mode = 'run'
                file = self.animations['run']
                self.loader(file, self.sprite.x, self.sprite.y, frames=5)
        else:
            if self.mode != 'idle':
                self.mode = 'idle'
                file = self.animations['idle']
                self.loader(file, self.sprite.x, self.sprite.y, frames=4)
    def colisao(self, alvo):
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