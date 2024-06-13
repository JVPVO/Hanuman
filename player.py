import pygame
from camera import Camera
from weapons import Weapon
from inimigos import *

class Animation:
    def __init__(self, image_file, total_frames, frame_width, frame_height, animation_speed=0.2):
        self.sprite_sheet = pygame.image.load(image_file).convert_alpha() #faz um png com bordas mais suaves (colisao mais realista (nao colide com parte transparente))
        self.total_frames = total_frames
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.animation_speed = animation_speed
        self.current_frame = 0
        self.frames = self.__load_frames__()
        self.last_update = pygame.time.get_ticks()
        self.image = self.frames[self.current_frame]
        self.x, self.y = 0, 0
        self.scale_factor = 1
        self.last_rotation = pygame.time.get_ticks()
        self.orientation = 0 #começa virado pra direita (0 é direita e 1 é esquerda)

    
    def __load_frames__(self):
        '''Separa os frames do sprite em uma lista'''
        frames = []
        for i in range(self.total_frames):
            frame = self.sprite_sheet.subsurface(pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height))
            frames.append(frame)
        return frames

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 1000 * self.animation_speed: #pra animacao ficar trocando no tempo especificado
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % self.total_frames #para sempre ser uma valor dentro de [0, totalframes-1]
            self.image = self.frames[self.current_frame] #finalmente rroca a imagem pra frame atual

    def draw(self, surface): #NOTE essa funcao nunca é usada no nosso codigo (a que é usada é o Draw do player)
        surface.blit(self.image, (self.x, self.y)) #desenha na posicao especificada

    def rescale_frames(self, scale_factor):
        """Redimensiona os frames do sprite com base no fator de escala absoluto."""
        self.scale_factor = scale_factor
        self.frames = [pygame.transform.scale(frame, (int(self.frame_width * scale_factor), int(self.frame_height * scale_factor))) for frame in self.frames]
    
    def rotate(self,orientation_dest, cooldown = 80):
        orientation_dest = 0 if orientation_dest == 'r' else 1 #converte pra numero
        
        if self.orientation != orientation_dest: #só muda a orientação se ta diferente
            now = pygame.time.get_ticks()
            if now - self.last_rotation > cooldown:
                self.orientation = (self.orientation+1) % 2 #troca orientação
                self.last_rotation = pygame.time.get_ticks()
                self.frames = [pygame.transform.flip(frame, True, False) for frame in self.frames]#rotaciona no eixo x
                self.image = self.frames[self.current_frame]


class Player:
    def __init__(self, x, y, initial_scale = 1):
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
        
        self.weapon = [Weapon('assets/Weapon.png',70, 30, initial_scale)]
        self.selected_weapon = 0


    def handle_keys(self, key_pressed, camera:Camera, inimigos):
        """Atualiza a posição do jogador com base nas teclas pressionadas."""
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
                inimigos.append(Skeleton(self.sprite.x+30,self.sprite.y+30, initial_scale=3))
                self.last_scale_time = pygame.time.get_ticks()
        
        weapon.update(self.rect, camera, self.rect.height,key_pressed)
        self.sprite.x, self.sprite.y = self.rect.topleft

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

    def draw(self, surface:pygame.Surface, camera):
        """Desenha o jogador na superfície, ajustando pela posição da câmera."""
        adjusted_rect = camera.apply(self.rect)
        
        #surface.blit(pygame.Surface((self.rect.width,self.rect.height)), camera.apply(pygame.Rect(self.sprite.x, self.sprite.y, self.rect.width, self.rect.height))) 
        #debug ^

        surface.blit(self.sprite.image, adjusted_rect.topleft)
        

        self.weapon[self.selected_weapon].draw(surface, camera)