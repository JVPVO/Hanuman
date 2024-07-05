#TODO colisao do esqueleto

import pygame
from pygame.sprite import *
from animation_Wip import Animation
from menus import DamageNumber

class Skeleton(pygame.sprite.Sprite):
    def __init__(self, x, y, initial_scale, groups):
        super().__init__(groups)
        #TODO Fazer um json que tem o nome dos inimigos e cada uma das sprites sheets deles, por enquanto vou deixar vazio e hard-coded no código
        self.sprite = Animation(image_file='assets/Skeleton-Idle.png', total_frames=4, frame_width=32, frame_height=32)
        
        self.sprite.x, self.sprite.y = x, y
        self.rect = pygame.Rect(x, y, 32, 32)  # Tamanho do inimigo, ajuste conforme necessário
    
        self.speed = 188  # Velocidade de movimento do inimigo
        self.scale_factor = initial_scale
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500  # Cooldown de 500 milissegundos
        
        self.camada = 1
        self.y_sort = self.rect.y

        self.ataque = 5
        self.health = 30
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
    

        self.damage_numbers = []
    
    #FUNÇÃO MAIS IMPORTANTE DA NOSSA VIDA, RENDERIZA O PERSONAGEM COM A CÂMERA E É GLOBAL ENTÃO NÃO PRECISA BOTAR PRA TODA HORA                    
    def draw(self, surface:pygame.Surface, camera):
        surface.blit(self.sprite.image, camera.apply(pygame.Rect(self.sprite.x, self.sprite.y, self.rect.width, self.rect.height)))
    
    def loader(self, file, x, y, frames):
        if not self.processed[self.mode]:
            objeto = Animation(image_file=f'assets/{file}', total_frames=frames, frame_width=32, frame_height=32)
            objeto.x, objeto.y = x, y
            objeto.rescale_frames(self.scale_factor)
            self.spritesheets[self.mode] = objeto
            self.processed[self.mode] = True
        self.sprite = self.spritesheets[self.mode]
        self.sprite.x, self.sprite.y = x,y
    
    def movement(self, playerX, playerY, deltatime):
        firstPos = (self.sprite.x, self.sprite.y)
        if self.sprite.x > playerX+5: 
            self.sprite.x -= self.speed * deltatime
            self.sprite.rotate('l')
        elif self.sprite.x < playerX-5: 
            self.sprite.x += self.speed * deltatime
            self.sprite.rotate('r')
        if self.sprite.y > playerY+5: self.sprite.y -= self.speed * deltatime
        elif self.sprite.y < playerY-5: self.sprite.y += self.speed * deltatime
        self.rect.x = self.sprite.x
        self.rect.y = self.sprite.y
        
        #Ele basicamente testa se houve algum movimento com a invocação da função, se houve, ele realiza a mudança da animação pra uma de corrida
        #Se não houve nenhum movimento ele volta pra animação idle
        if firstPos[0] != self.sprite.x or firstPos[1] != self.sprite.y:
            if self.mode != 'run':
                self.mode = 'run'
                file = self.animations['run']
                self.loader(file, self.sprite.x, self.sprite.y, frames=6)
        else:
            if self.mode != 'idle':
                self.mode = 'idle'
                file = self.animations['idle']
                self.loader(file, self.sprite.x, self.sprite.y, frames=4)
        self.y_sort = self.rect.y + self.rect.height
    
    def colisao(self, alvo):
        if id(alvo) not in self.ataquesRecebidos:
            if self.rect.colliderect(alvo.rot_image_rect):
                self.ataquesRecebidos[id(alvo)] = pygame.time.get_ticks()
                if self.health-alvo.dano > 0:
                    self.take_damage(alvo.dano)
                    return False
                else:
                    self.take_damage(alvo.dano)
                    return True
        #Isso existe pq em algum momento pode ter ataque AoE
        elif pygame.time.get_ticks() - self.ataquesRecebidos[id(alvo)] > self.invencibilidade:   
            if self.rect.colliderect(alvo.rot_image_rect):
                self.ataquesRecebidos[id(alvo)] = pygame.time.get_ticks()
                if self.health-alvo.dano > 0:
                    self.take_damage(alvo.dano)
                    return False
                else:
                    self.take_damage(alvo.dano)
                    return True
        return False
    def take_damage(self, dano):
        damage_number = DamageNumber(self.rect.centerx, self.rect.y, dano, color=(255,255,255))
        self.damage_numbers.append(damage_number)
        self.health -= dano

    def update_damage_numbers(self):
        self.damage_numbers = [dn for dn in self.damage_numbers if dn.update()]

    def draw_damage_numbers(self, desvio):
        for damage_number in self.damage_numbers:
            damage_number.draw(desvio)