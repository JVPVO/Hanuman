# player.py
#TODO consertar dash na nova colisao e dash como atravesar parede
import pygame
from animation_Wip import Animation
from weapons import Weapon #,Bow
from menus import DamageNumber
#import do inimigos quando for chamar

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, collision_sprites, camera_grupo, ui, initial_scale=1):
        super().__init__(camera_grupo)
        self.sprite = Animation(image_file='assets/Idle-Sheet.png', total_frames=4, frame_width=19, frame_height=30)
        self.sprite.x, self.sprite.y = x, y
        
        self.rect = pygame.Rect(x, y, 19, 30)  # Tamanho do jogador, ajuste conforme necessário
        
        self.speed = 750 # Velocidade de movimento do jogador (pixels por segundo) CUIDADO QUE ESSE valor é sobrescrito no handle_keys 
        self.scale_factor = initial_scale
        
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500  # Cooldown de 500 milissegundos
        
        self.sprite.rescale_frames(initial_scale)
        self.rect.width = int(19 * initial_scale)  # Ajusta o rect
        self.rect.height = int(30 * initial_scale)  # Ajusta o rect
        self.y_sort = self.rect.y + self.rect.height
        self.hitbox_C =self.rect.inflate(-self.rect.width/3,-self.rect.height/2) #hitbox de colisao do player
        self.hitbox_C.bottom = self.rect.bottom

        self.rect_where_draw = self.rect.copy() #depois do primeiro draw já muda (preciso disso quando to lidando com referencial da tela)
        
        self.ui = ui

        self.camada = 1

        self.weapon = [Weapon('assets/Weapon.png', 70, 30, initial_scale)]
        self.selected_weapon = 0
        
        self.health = 100
        self.max_health = 100

        self.collision_sprites = collision_sprites #pro palyer checar se ta colidindo
        self.pos_anterior = (self.hitbox_C.x, self.hitbox_C.y)

        self.mode = 'idle'
        
        self.scaled = False
        
        self.dashing = False
        self.dash_speed = 1860  # Velocidade durante o dash
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

    def handle_keys(self, key_pressed, grupos, desvio, scaleoffset, deltatime):
        # Os grupos em questão sao o grupo de inimigos e o grupo da camera, respectivamente (vem da main.py)

        self.pos_anterior = (self.hitbox_C.x, self.hitbox_C.y)
        weapon = self.weapon[self.selected_weapon]
        firstPos = (self.rect.x, self.rect.y)
        mouse_pos = pygame.mouse.get_pos()

        if key_pressed[pygame.K_LCTRL]:
            self.speed = 94
        else:
            if self.speed == 94:
                self.dash(mouse_pos)
            self.speed = 750

        if self.dashing:
            if pygame.time.get_ticks() - self.dash_start_time <= self.dash_duration:
                dash_speed = self.dash_speed
                self.rect.x += self.dash_direction.x * dash_speed * deltatime
                self.rect.y += self.dash_direction.y * dash_speed * deltatime
            else:
                self.dashing = False

        if not self.dashing:
            if key_pressed[pygame.K_w]:
                self.rect.y -= self.speed * deltatime
    
            if key_pressed[pygame.K_s]:
                self.rect.y += self.speed * deltatime
            self.check_collision(1)
            
            if key_pressed[pygame.K_a]:
                self.sprite.rotate('l')
                self.rect.x -= self.speed * deltatime
            if key_pressed[pygame.K_d]:
                self.sprite.rotate('r')
                self.rect.x += self.speed * deltatime
            self.check_collision(0)
            


        if key_pressed[pygame.K_ESCAPE]:
            pygame.quit()
        #Todas abaixo são para debug
        if key_pressed[pygame.K_p]:
            self.scale(1.5)
        if key_pressed[pygame.K_o]:
            self.scale(0.5)
        if key_pressed[pygame.K_l]:
            if pygame.time.get_ticks() - self.last_scale_time > self.scale_cooldown:
                
                from inimigos import Rat  # Evitar import circular
                Rat(self.rect.x + 30, self.rect.y + 30, initial_scale=3, groups=(grupos[0], grupos[1]), projectile_group=grupos[2])
                #Skeleton(self.rect.x + 30, self.rect.y + 30, initial_scale=3, groups=(grupos[0], grupos[1]))
                self.last_scale_time = pygame.time.get_ticks()
        ########################################

        if firstPos[0] != self.rect.x or firstPos[1] != self.rect.y:
            if self.mode != 'run':
                self.mode = 'run'
                self.loader('run', self.animations['run'], frames=6)
        else:
            if self.mode != 'idle':
                self.mode = 'idle'
                self.loader('idle', self.animations['idle'], frames=4)


        self.y_sort = self.rect.y + self.rect.height
        weapon.update(self.rect, desvio, self.rect.height, key_pressed, scaleoffset) #NOTE
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
                

    def check_collision(self, direcao):
        '''Checa a colisao com objetos e resolve ela'''
        from inimigos import Dropaveis
        self.hitbox_C.centerx = self.rect.centerx
        self.hitbox_C.bottom = self.rect.bottom
        for objeto in self.collision_sprites:
            if self.hitbox_C.colliderect(objeto.rect):
                if isinstance(objeto, Dropaveis):
                    self.interacao_com_dropavel(objeto.funcao, objeto.intensidade)
                    objeto.kill()

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
        
    def interacao_com_dropavel(self, funcao, intensidade): #talvez adcionar um icone de interação
        if funcao == "vida":
            self.health += intensidade
            if self.health > self.max_health: self.health = self.max_health #impee de passar da vida maxima
            self.ui.health = self.health
        
        if funcao == "aumentar_vida_maxima":
            self.max_health += intensidade
            self.ui.max_health = self.max_health
            self.health = int(intensidade*0.2)
            self.ui.health = self.health


    def check_door_collision(self, portasgrupo):
        #quase que função duplicada, melhorar isso depois
        for objeto in portasgrupo:
            if self.hitbox_C.colliderect(objeto.rect):
                return objeto.tag
        return None


    def draw(self,tela, desvio):
        pos_ajustada = pygame.math.Vector2(self.rect.x, self.rect.y) + desvio
        self.rect_where_draw.x, self.rect_where_draw.y = pos_ajustada


        tela.blit(self.sprite.image, pos_ajustada)
        self.weapon[self.selected_weapon].draw(tela,desvio) 

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

    def draw_damage_numbers(self, desvio):
        for damage_number in self.damage_numbers:
            damage_number.draw(desvio)




