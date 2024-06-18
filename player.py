import pygame
from animation_Wip import Animation
from inimigos import Skeleton
from camera import Camera
from weapons import Weapon

class Player:
    def __init__(self, x, y, colision_sprite, initial_scale = 1):
        self.sprite = Animation(image_file='assets/Idle-Sheet.png', total_frames=4, frame_width=19, frame_height=30)
        self.sprite.x, self.sprite.y = x, y
        self.rect = pygame.Rect(x, y, 19, 30)  # Tamanho do jogador, ajuste conforme necessário
        self.speed = 8  # Velocidade de movimento do jogador
        self.scale_factor = initial_scale
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500  # Cooldown de 500 milissegundos

        self.sprite.rescale_frames(initial_scale)
        self.rect.width = int(19 * initial_scale) #ajusta o rect
        self.rect.height = int(30 * initial_scale) #ajusta o rect
        self.y_sort = self.rect.y+self.rect.height
        
        self.weapon = [Weapon('assets/Weapon.png',70, 30, initial_scale)]
        self.selected_weapon = 0
        self.colision_sprite = colision_sprite
        self.pos_anterior = (self.rect.x, self.rect.y)

        


    def handle_keys(self, key_pressed, camera:Camera, grupos:tuple): #inimigos = 0, allsprites = 1
        """Atualiza a posição do jogador com base nas teclas pressionadas."""
        self.pos_anterior = (self.rect.x, self.rect.y)
        
        weapon = self.weapon[self.selected_weapon]
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
            #NOTE Recomendado usar valores inteiros (não distorce o sprite do personagem)
            self.scale(1.5)  # Aumenta a escala em 50% 
        if key_pressed[pygame.K_o]:
            self.scale(0.5)  # Diminui a escala em 50%
        if key_pressed[pygame.K_ESCAPE]:
            pygame.quit()
        if key_pressed[pygame.K_l]:
            if pygame.time.get_ticks() - self.last_scale_time > self.scale_cooldown:
                Skeleton(self.sprite.x+30,self.sprite.y+30, initial_scale=3, groups=(grupos[0], grupos[1])) #assim adiciona no gurpo já
                self.last_scale_time = pygame.time.get_ticks()
        
        self.y_sort = self.rect.y+self.rect.height
        weapon.update(self.rect, camera, self.rect.height,key_pressed)
        self.sprite.x, self.sprite.y = self.rect.topleft
        
        self.check_colision()

    def scale(self, scale_factor):
        """Redimensiona o sprite do jogador."""
        now = pygame.time.get_ticks()
        if now - self.last_scale_time > self.scale_cooldown:
            self.last_scale_time = now
            self.scale_factor *= scale_factor
            if 0.1 < self.scale_factor < 10:  # Limita a escala a um intervalo razoável
                self.sprite.rescale_frames(self.scale_factor)
                self.rect.width = int(19 * self.scale_factor) #ajusta o rect
                self.rect.height = int(30 * self.scale_factor) #ajusta o rect


    def check_colision(self):
        for objeto in self.colision_sprite:
            eixox = self.rect.x + self.rect.width > objeto.hitbox.x and self.rect.x < objeto.hitbox.x + objeto.hitbox.width
            eixoy = self.rect.y + self.rect.height > objeto.hitbox.y and  self.rect.y+self.rect.height < objeto.hitbox.y + objeto.hitbox.height
            if eixox and eixoy:
                if eixox:
                    self.rect.x = self.pos_anterior[0]
                if eixoy:
                    self.rect.y = self.pos_anterior[1]
                

    def draw(self, surface:pygame.Surface, camera):
        """Desenha o jogador na superfície, ajustando pela posição da câmera."""
        adjusted_rect = camera.apply(self.rect)
        
        #surface.blit(pygame.Surface((self.rect.width,self.rect.height)), camera.apply(pygame.Rect(self.sprite.x, self.sprite.y, self.rect.width, self.rect.height))) 
        #debug ^

        surface.blit(self.sprite.image, adjusted_rect.topleft)
        

        self.weapon[self.selected_weapon].draw(surface, camera)