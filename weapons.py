
import pygame, math

class RotatableObjects():
    def __init__(self, img_file, x, y, initial_scale = 1):
        sprite = pygame.image.load(img_file).convert_alpha()
        sprite_width = sprite.get_width()
        sprite_height = sprite.get_height()

        self.scale = initial_scale

        self.x, self.y = x, y
        self.rect = sprite.get_rect(center = (x,y))
        
        self.sprite_width =  int(sprite_width * initial_scale)
        self.sprite_height = int(sprite_height  * initial_scale)
        
        self.sprite = pygame.transform.scale(sprite, (self.sprite_width, self.sprite_height))

        self.rect.width = self.sprite_width #ajusta o rect
        self.rect.height = self.sprite_height #ajusta o rect
            
        self.rotated_img = self.sprite
        self.rot_image_rect = self.rect


class Weapon(RotatableObjects):
    def __init__(self, img_file, x, y, initial_scale = 1):
        super().__init__(img_file, x, y, initial_scale)
        
        self.shots = 2
        self.shoot = []
        self.projectile_cooldown = 0.3 *1000
        self.last_shoot = pygame.time.get_ticks()
        self.last_direction = pygame.Vector2(0,0) #sempre normalizado (vetor unitário)
        
        

    def draw(self,tela, desvio):
        tam_s = len(self.shoot)
        for t in range(tam_s-1,-1,-1): #desenha, movimenta e deleta os projeteis
            self.shoot[t].draw(tela,desvio)
            delete_result = self.shoot[t].move(0.5)
            if delete_result:
                self.shoot.pop(t)

        
        tela.blit(self.rotated_img, self.rot_image_rect.topleft + desvio)
    
    def update(self, playerrect:pygame.Rect, desvio, ph, keypressed, scaleoffset):
        '''pPos_pComp = (player_x, player_y, player_width, player_height)'''
        #em progresso
        mx, my = pygame.mouse.get_pos()
        if pygame.time.get_ticks() - self.last_shoot  >= self.projectile_cooldown and keypressed[pygame.K_SPACE]:
            self.shots -= 1
            p = Projectile('assets\slash_demo.png', playerrect.centerx, playerrect.centery, mx, my, 0.1, self.rect, desvio, self.scale)
            self.shoot.append(p)
            self.last_shoot = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.last_shoot >= 50 and self.shots > 0:
            self.shots -= 1
            p = Projectile('assets\slash_demo.png', playerrect.centerx+20, playerrect.centery+20, mx, my, 0.1, self.rect, desvio, self.scale)
            self.shoot.append(p)
        
        self.set_pos(playerrect.centerx, playerrect.centery, mx, my, ph, desvio, scaleoffset)
        
        
    #pequena modificacao em relacao a versão original (rotação com refrencial espada-mouse -> rotação com refrencial player-espada)
    def update_rot(self, mx, my):
        
        dx = mx - self.rect.centerx 
        dy = my - self.rect.centery 
        #print(pygame.mouse.get_pos(), dx,dy)
        #print('player', mx, my) debug
        angle = math.degrees(math.atan2(dy, -dx)) - 90

        self.rotated_img = pygame.transform.rotate(self.sprite, angle)

    def set_pos(self, x, y, mx, my, player_height,desvio, scaleoffset): #talvez deixar esse scale offset quando der initi
        #em progresso
        self.rect = self.sprite.get_rect(center = (x,y))
        mouse = pygame.Vector2(mx, my)
        player= pygame.Vector2(x, y)

        result = mouse -desvio - player +scaleoffset #deslocamento da origem + correcao da camera (o scaleoffset é pra counterar o deslocamento que a camera faz no rect pra desenhar)

        #print(desvio)
        mag = result.magnitude()
        if mag > 2: #um valor pequeno para o "centro"
            result = result.normalize() * player_height *0.9
            final = result + player # voltando pra origem original
            
            self.rect.centerx = final.x
            self.rect.centery = final.y
            
            
            self.last_direction = result.normalize()
            self.update_rot(x, y)

        
        else: #se nao tiver saido do limite = a que tava antes (#NOTE tem um bug aqui)
            #talvez deixar atras do personagem?
            self.rect.centerx = x + self.last_direction.x * player_height 
            self.rect.centery = y + self.last_direction.y * player_height
        
        self.rot_image_rect = self.rotated_img.get_rect(center = self.rect.center)
            


class Projectile(RotatableObjects):     #ta repetido dá pra otimizar #NOTE   
    def __init__(self,img_file, x, y, mx, my, duration_time, player_rect, desvio, initial_scale=1):
        super().__init__(img_file, x, y, initial_scale)

        self.time_control = self.creation_time = pygame.time.get_ticks()
        
        self.lifespan = duration_time*1000

        self.mx, self.my = mx, my

        dx = mx - self.rect.centerx - desvio.x
        dy = my - self.rect.centery - desvio.y
        angle = math.degrees(math.atan2(-dy, dx))

        self.rotated_img = pygame.transform.rotate(self.sprite, angle)
        self.rot_image_rect = self.rotated_img.get_rect(center = self.rect.center)

        self.rect = self.sprite.get_rect(center = (x,y))
        
        mouse = pygame.Vector2(mx, my)
        player= pygame.Vector2(x, y)
        
        result = mouse - player - desvio #deslocamento da origem + correcao da camera
        self.result = result
        
        result = result.normalize() * player_rect.height *1.1
        final = result + player # voltando pra origem original
        
        self.rot_image_rect.centerx = final.x
        self.rot_image_rect.centery = final.y
        
        self.dano = 10


    def move(self, vel):
        agora = pygame.time.get_ticks()
        delta_time = agora - self.time_control
        self.time_control = agora

        
        direcao = self.result.normalize()
        
        self.rot_image_rect.centerx += (direcao.x * vel) * delta_time
        self.rot_image_rect.centery += (direcao.y * vel) * delta_time 

        if agora - self.creation_time >= self.lifespan:
            return True
        return False
    
    def draw(self,tela, desvio):
        tela.blit(self.rotated_img, self.rot_image_rect.topleft+desvio)


    
