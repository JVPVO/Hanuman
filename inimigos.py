
#lembrete (lembra que aqui em vez de usar rect.x é melhor usar o sprite.x (serve pro y tbm))

import pygame
from pygame.sprite import *
from animation_Wip import Animation
from menus import DamageNumber
from weapons import Bow

class Skeleton(pygame.sprite.Sprite):
    def __init__(self, x, y, initial_scale, groups):
        super().__init__(groups)
        #TODO Fazer um json que tem o nome dos inimigos e cada uma das sprites sheets deles, por enquanto vou deixar vazio e hard-coded no código
        self.sprite = Animation(image_file='assets/Skeleton-Idle.png', total_frames=4, frame_width=32, frame_height=32)
        
        self.sprite.x, self.sprite.y = x, y #nao é utilado mais (se usa esse buga com a colisao nova)
        self.rect = pygame.Rect(x, y, 32, 32)  # Tamanho do inimigo, ajuste conforme necessário
    
        self.speed = 188  # Velocidade de movimento do inimigo
        self.scale_factor = initial_scale
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500  # Cooldown de 500 milissegundos
        
        self.camada = 1
        self.y_sort = self.rect.y
        
        self.vendo = False #se o inimigo tá vendo o player

        self.ataque = 5 #Dano do inimigo
        self.health = 30 #Vida do inimigo
        self.invencibilidade = 300 #Cooldown de 300 milissegundos para cada ataque individual
        self.ataquesRecebidos = {}

        self.mode = 'idle'
        self.scaled = False

        self.pos_anterior = (self.rect.x, self.rect.y)

        if not self.scaled:
            self.sprite.rescale_frames(initial_scale)
            self.rect.width = int(32 * initial_scale) #ajusta o rect
            self.rect.height = int(32 * initial_scale) #ajusta o rect
            self.scaled = True
    
        self.animations = {'idle': 'Skeleton-Idle.png', 'run': 'Skeleton_Run-Sheet.png'}
        self.processed = {'idle': True, 'run': False}
        self.spritesheets = {'idle': self.sprite}

        self.hitbox_C =self.rect.inflate(-self.rect.width/3,-self.rect.height/2) #hitbox de colisao 
        self.hitbox_C.bottom = self.rect.bottom

        self.damage_numbers = []
    
    #FUNÇÃO MAIS IMPORTANTE DA NOSSA VIDA, RENDERIZA O PERSONAGEM COM A CÂMERA E É GLOBAL ENTÃO NÃO PRECISA BOTAR PRA TODA HORA                    
    def draw(self, surface:pygame.Surface, camera):
        surface.blit(self.sprite.image, camera.apply(pygame.Rect(self.rect.x, self.rect.y, self.rect.width, self.rect.height)))
    
    def loader(self, file, x, y, frames):
        if not self.processed[self.mode]:
            objeto = Animation(image_file=f'assets/{file}', total_frames=frames, frame_width=32, frame_height=32)
            objeto.x, objeto.y = x, y
            objeto.rescale_frames(self.scale_factor)
            self.spritesheets[self.mode] = objeto
            self.processed[self.mode] = True
        self.sprite = self.spritesheets[self.mode]
        self.rect.x, self.rect.y = x,y
    
    def movement(self, playerX, playerY, deltatime, collision_sprites):
        firstPos = (self.rect.x, self.rect.y)
        

        campo_de_visao = not self.check_vision(playerX, playerY, collision_sprites)

        if campo_de_visao:
            if self.rect.x > playerX+5: 
                self.rect.x -= self.speed * deltatime
                self.sprite.rotate('l')
            elif self.rect.x < playerX-5: 
                self.rect.x += self.speed * deltatime
                self.sprite.rotate('r')
            self.colisao_com_objetos(collision_sprites,0)

            if self.rect.y > playerY+5: self.rect.y -= self.speed * deltatime
            elif self.rect.y < playerY-5: self.rect.y += self.speed * deltatime
            self.colisao_com_objetos(collision_sprites, 1)
            
            
        
        #Ele basicamente testa se houve algum movimento com a invocação da função, se houve, ele realiza a mudança da animação pra uma de corrida
        #Se não houve nenhum movimento ele volta pra animação idle
        if firstPos[0] != self.rect.x or firstPos[1] != self.rect.y:
            if self.mode != 'run':
                self.mode = 'run'
                file = self.animations['run']
                self.loader(file, self.rect.x, self.rect.y, frames=6)
        else:
            if self.mode != 'idle':
                self.mode = 'idle'
                file = self.animations['idle']
                self.loader(file, self.rect.x, self.rect.y, frames=4)
        self.y_sort = self.rect.y + self.rect.height



        self.pos_anterior = (self.hitbox_C.x, self.hitbox_C.y)

    def check_vision(self, px, py, collision_sprites):
        #px e py devem ser o x e y do hitbox do player
        for objeto in collision_sprites: #se for botar um inimigo colidivel no futro tem que tomar cuidado com isso (fazer um if)
            if objeto.rect.clipline((px, py),(self.rect.centerx, self.rect.centery)):
                return True #se tem algo colidindo com a linha entre o player e o inimigo, o inimigo não pode ver o player
        return False
    
    def colisao(self, alvo):
        if id(alvo) not in self.ataquesRecebidos:
            #depois botar um if aqui pra quando a colisao for unica (um if que destrua o projetil (precisaria disso pra uma flecha por exemplo))
            #mas por enquanto o player n tem arco ent tudo certo
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

    def colisao_com_objetos(self,colision_sprites, direcao): #0 é x, 1 é y
        '''Checa a colisao com objetos e resolve ela'''

        self.hitbox_C.centerx = self.rect.centerx
        self.hitbox_C.bottom = self.rect.bottom
        for objeto in colision_sprites:
            if self.hitbox_C.colliderect(objeto.rect):
                sentido = (self.hitbox_C.x - self.pos_anterior[0], self.hitbox_C.y - self.pos_anterior[1])
                if direcao == 0:
                    if sentido[0] > 0:
                        self.hitbox_C.right = objeto.rect.left
                    elif sentido[0] < 0:
                        self.hitbox_C.left = objeto.rect.right
                    self.rect.centerx = self.hitbox_C.centerx

                elif direcao == 1:
                    if sentido[1] > 0:
                        self.hitbox_C.bottom = objeto.rect.top 
                    elif sentido[1] < 0:
                        self.hitbox_C.top = objeto.rect.bottom 
                    self.rect.bottom = self.hitbox_C.bottom

        
     

    
    

class Rat(Skeleton):
    #Herda o modelo geral do esqueleto, mas vou mudar os ataques e etc (#TODO depois fazer uma calasse pro inimigo?)
    def __init__(self, x, y, initial_scale, groups, projectile_group):
        super().__init__(x, y, initial_scale, groups)
        self.sprite = Animation(image_file='assets/Rat-Idle-Sheet.png', total_frames=4, frame_width=32, frame_height=32)
        self.rect = pygame.Rect(x, y, 32, 32)  # Tamanho do inimigo, ajuste conforme necessário

        self.weapon = [Bow('assets/Cursed-Bow.png', 70, 30,projectile_group, initial_scale)]
        self.projectile_group = pygame.sprite.Group()

        self.scale_factor = initial_scale
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500  # Cooldown de 500 milissegundos


        self.speed = 60  # Velocidade de movimento do inimigo
        self.ataque = 8 #Dano do inimigo
        self.health = 15 #Vida do inimigo

        self.scaled = False 
        if not self.scaled:
            self.sprite.rescale_frames(initial_scale)
            self.rect.width = int(32 * initial_scale) #ajusta o rect
            self.rect.height = int(32 * initial_scale) #ajusta o rect
            self.scaled = True

        self.mode = 'idle'
        self.animations = {'idle': 'Rat-Idle-Sheet.png', 'run': 'Rat-Run-Sheet.png'}
        self.processed = {'idle': True, 'run': False}
        self.spritesheets = {'idle': self.sprite}

        
        self.camada = 1
        self.y_sort = self.rect.y

        self.invencibilidade = 300 #Cooldown de 300 milissegundos para cada ataque individual
        self.ataquesRecebidos = {}
  

        self.damage_numbers = []
        self.weapon[0].rect.x = self.rect.x - 10
        self.weapon[0].rect.y = self.rect.y - 10

        self.hitbox_C =self.rect.inflate(-self.rect.width/3,-self.rect.height/2) #hitbox de colisao 
        self.hitbox_C.bottom = self.rect.bottom

    
    def movement(self, playerX, playerY, deltatime, collision_sprites):
        #talvez ele possa dar um dash pra alguma direcao aleatoria se prender na parede
        firstPos = (self.rect.x, self.rect.y)
        
  

        campo_de_visao = not self.check_vision(playerX, playerY, collision_sprites)

        if campo_de_visao:
            if self.rect.x > playerX+10: 
                self.rect.x += self.speed * deltatime
                self.sprite.rotate('l')
            elif self.rect.x < playerX-10: 
                self.rect.x -= self.speed * deltatime
                self.sprite.rotate('r')
            self.colisao_com_objetos(collision_sprites, 0)
            
            if self.rect.y > playerY+10: self.rect.y += self.speed * deltatime
            elif self.rect.y < playerY-10: self.rect.y -= self.speed * deltatime
            self.colisao_com_objetos(collision_sprites, 1)


        
        #Ele basicamente testa se houve algum movimento com a invocação da função, se houve, ele realiza a mudança da animação pra uma de corrida
        #Se não houve nenhum movimento ele volta pra animação idle
        if firstPos[0] != self.rect.x or firstPos[1] != self.rect.y:
            if self.mode != 'run':
                self.mode = 'run'
                file = self.animations['run']
                self.loader(file, self.rect.x, self.rect.y, frames=6)
        else:
            if self.mode != 'idle':
                self.mode = 'idle'
                file = self.animations['idle']
                self.loader(file, self.rect.x, self.rect.y, frames=4)
        self.y_sort = self.rect.y + self.rect.height

        self.pos_anterior = (self.hitbox_C.x, self.hitbox_C.y)



    def loader(self, file, x, y, frames,): #n sei porque se nao tiver ele carrega a do esqueleto (???)
        if not self.processed[self.mode]:
            objeto = Animation(image_file=f'assets/{file}', total_frames=frames, frame_width=32, frame_height=32)
            objeto.x, objeto.y = x, y
            objeto.rescale_frames(self.scale_factor)
            self.spritesheets[self.mode] = objeto
            self.processed[self.mode] = True
        self.sprite = self.spritesheets[self.mode]
        self.rect.x, self.rect.y = x,y

    def weapon_use(self, desvio, sacaleoffset, player_rect):
        self.weapon[0].update(self.rect, desvio, self.rect.height, sacaleoffset, player_rect)

    def draw(self,tela, desvio): #na verdade esse draw é pro weapon
        self.weapon[0].draw(tela, desvio)

    
