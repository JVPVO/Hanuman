import pygame

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

