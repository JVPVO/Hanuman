#lembrete (lembra que aqui em vez de usar rect.x é melhor usar o sprite.x (serve pro y tbm))

import pygame
from animation_Wip import Animation
from menus import DamageNumber
from weapons import Bow

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, initial_scale, groups, image_file, total_frames, frame_width, frame_height):
        super().__init__(groups)
        #TODO Fazer um json que tem o nome dos inimigos e cada uma das sprites sheets deles, por enquanto vou deixar vazio e hard-coded no código

        self.sprite = Animation(image_file=image_file, total_frames=total_frames, frame_width=frame_width, frame_height=frame_height)
        
        self.rect = pygame.Rect(x, y, frame_width, frame_height)
        self.hitbox_C = self.rect.inflate(-self.rect.width/3, -self.rect.height/2)
        self.hitbox_C.bottom = self.rect.bottom
        
        self.speed = 0
        self.scale_factor = initial_scale
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500
        
        self.camada = 1
        self.y_sort = self.rect.y
        
        self.vendo = False
        self.ataque = 0
        self.health = 0
        self.invencibilidade = 300
        self.ataquesRecebidos = {}

        self.mode = 'idle'
        self.scaled = False
        self.pos_anterior = (self.rect.x, self.rect.y)

        self.animations = {}
        self.processed = {'idle': True, 'run':False}
        self.spritesheets = {'idle': self.sprite}

        self.damage_numbers = []

        if not self.scaled:
            self.sprite.rescale_frames(initial_scale)
            self.rect.width = int(frame_width * initial_scale)
            self.rect.height = int(frame_height * initial_scale)
            self.scaled = True

    
    def loader(self, file, x, y, frames):
        if not self.processed[self.mode]:
            objeto = Animation(image_file=f'assets/{file}', total_frames=frames, frame_width=32, frame_height=32)
            objeto.x, objeto.y = x, y
            objeto.rescale_frames(self.scale_factor)
            self.spritesheets[self.mode] = objeto
            self.processed[self.mode] = True
        self.sprite = self.spritesheets[self.mode]
        self.rect.x, self.rect.y = x, y
    
    def movement(self, playerX, playerY, deltatime, collision_sprites):
        firstPos = (self.rect.x, self.rect.y)
        
        campo_de_visao = not self.check_vision(playerX, playerY, collision_sprites)

        if campo_de_visao:
            if self.rect.x > playerX + 5:
                self.rect.x -= self.speed * deltatime
                self.sprite.rotate('l')
            elif self.rect.x < playerX - 5:
                self.rect.x += self.speed * deltatime
                self.sprite.rotate('r')
            self.colisao_com_objetos(collision_sprites, 0)
            

            if self.rect.y > playerY + 5:
                self.rect.y -= self.speed * deltatime
            elif self.rect.y < playerY - 5:
                self.rect.y += self.speed * deltatime
            self.colisao_com_objetos(collision_sprites, 1)
        
        self.update_animation(firstPos)
        self.y_sort = self.rect.y + self.rect.height
        self.pos_anterior = (self.hitbox_C.x, self.hitbox_C.y)

    def update_animation(self, firstPos):
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

    def check_vision(self, px, py, collision_sprites):
        '''Retorna TRUE se inimigo nao pode ver o player'''
        #px e py devem ser o x e y do hitbox do player
        for objeto in collision_sprites: #se for botar um inimigo colidivel no futuro tem que tomar cuidado com isso (fazer um if)
            if objeto.rect.clipline((px, py), (self.rect.centerx, self.rect.centery)):
                return True #se tem algo colidindo com a linha entre o player e o inimigo, o inimigo não pode ver o player
        return False
    
    def colisao(self, alvo):
        if id(alvo) not in self.ataquesRecebidos:
            if self.rect.colliderect(alvo.rot_image_rect):
                self.ataquesRecebidos[id(alvo)] = pygame.time.get_ticks()
                return self.apply_damage(alvo.dano)
        elif pygame.time.get_ticks() - self.ataquesRecebidos[id(alvo)] > self.invencibilidade:
            if self.rect.colliderect(alvo.rot_image_rect):
                self.ataquesRecebidos[id(alvo)] = pygame.time.get_ticks()
                return self.apply_damage(alvo.dano)
        return False

    def apply_damage(self, dano):
        if self.health - dano > 0:
            self.take_damage(dano)
            return False
        else:
            self.take_damage(dano)
            return True

    def take_damage(self, dano):
        damage_number = DamageNumber(self.rect.centerx, self.rect.y, dano, color=(255,255,255))
        self.damage_numbers.append(damage_number)
        self.health -= dano

    def update_damage_numbers(self):
        self.damage_numbers = [dn for dn in self.damage_numbers if dn.update()]

    def draw_damage_numbers(self, desvio):
        for damage_number in self.damage_numbers:
            damage_number.draw(desvio)

    def colisao_com_objetos(self, colision_sprites, direcao):
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


class Skeleton(Enemy):
    def __init__(self, x, y, initial_scale, groups):
        super().__init__(x, y, initial_scale, groups, 'assets/Skeleton-Idle.png', 4, 32, 32) # Tamanho do inimigo
        self.speed = 188 # Velocidade de movimento do inimigo
        self.ataque = 5
        self.health = 30
        self.animations = {'idle': 'Skeleton-Idle.png', 'run': 'Skeleton_Run-Sheet.png'}

class Rat(Enemy):
    def __init__(self, x, y, initial_scale, groups, projectile_group):
        super().__init__(x, y, initial_scale, groups, 'assets/Rat-Idle-Sheet.png', 4, 32, 32) # Tamanho do inimigo
        self.speed = 60 # Velocidade de movimento do inimigo
        self.ataque = 8
        self.health = 15
        self.animations = {'idle': 'Rat-Idle-Sheet.png', 'run': 'Rat-Run-Sheet.png'}

        self.weapon = [Bow('assets/Cursed-Bow.png', 70, 30, projectile_group, initial_scale)]
        self.projectile_group = pygame.sprite.Group()

        #posicao inicial da arma
        self.weapon[0].rect.x = self.rect.x - 10
        self.weapon[0].rect.y = self.rect.y - 10

    def movement(self, playerX, playerY, deltatime, collision_sprites):
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
            
            if self.rect.y > playerY+10:
                self.rect.y += self.speed * deltatime
            elif self.rect.y < playerY-10:
                self.rect.y -= self.speed * deltatime
            self.colisao_com_objetos(collision_sprites, 1)
        else:
            self.weapon[0].rect.x = self.rect.x - 10
            self.weapon[0].rect.y = self.rect.y - 10
            #so pra evitar o bug do arco nao ir
        
        self.update_animation(firstPos)
        self.y_sort = self.rect.y + self.rect.height
        self.pos_anterior = (self.hitbox_C.x, self.hitbox_C.y)

    def weapon_use(self, desvio, sacaleoffset, player_rect):
        self.weapon[0].update(self.rect, desvio, self.rect.height, sacaleoffset, player_rect)

    def draw(self, tela, desvio): #na verdade esse draw é só pro weapon
        self.weapon[0].draw(tela, desvio)



class Dropaveis(pygame.sprite.Sprite):
    def __init__(self, enemy_rect, sprite_img_path, groups, funcao, scale): #grupos deve ser o da camera e o de items da sala
        super().__init__(groups)
        self.posX = enemy_rect.centerx

        self.funcao = funcao

        self.Y_start = enemy_rect.centery
        self.image = pygame.image.load(sprite_img_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(self.posX, self.Y_start)) #posicao inicial no centro do inimigo
        self.camada = 1 #fica em cima de tudo até agora
        

        self.scale = scale #nao ta implemntado a escala dinamia ainda
        self.rect.width = int(self.rect.width*scale)
        self.rect.height = int(self.rect.height*scale)
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

        
        self.Y_max = enemy_rect.y
        self.Y_end = enemy_rect.bottom - self.rect.height
        self.y_sort = 0 #vai mudando enquanto se movimenta

        
        self.start = pygame.time.get_ticks()
        self.last_time = self.start
        self.animation_duration = 0.7 * 1000
        self.animation_ended = False
        self.vel = (self.Y_start-self.Y_max)/(self.animation_duration/2000) #nessa ordem pra ficar positivo
        #pela construcao dessa velocidade o movimento termina no segundo que determinamos, com a caida 2x mais rapida que a subida

        self.part = 0 #em qual parte da animacao ta (0 é subida, 1 é descida)
    
    def animate(self):
        if self.animation_ended: return
        
        agora = pygame.time.get_ticks()
        delta_time = ( agora - self.last_time)/1000 #n é exatamente um delta time mas ok
        if self.part == 0:
            self.rect.y -= self.vel * delta_time
            if self.rect.y <= self.Y_max: 
                self.part = 1 #troca pra segunda parte da animacao
                self.rect.y = self.Y_max
        else:
            self.rect.y += 2*self.vel * delta_time
            if self.rect.y >= self.Y_end: 
                self.animation_ended = True #fim da animacao
                self.rect.y = self.Y_end
        
        self.y_sort = self.rect.centery
        self.last_time = agora
        
