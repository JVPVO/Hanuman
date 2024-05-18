import pygame
import pytmx
from pytmx.util_pygame import load_pygame

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

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
    
    def apply(self, rect):
        """Aplica o deslocamento da câmera a um retângulo pygame.Rect para renderizar na posição correta."""
        return rect.move(self.camera.topleft)
    
    def update(self, target):
        """Atualiza a posição da câmera para seguir o alvo (jogador)."""
        x =  int(self.width / 2) -target.rect.x
        y =  int(self.height / 2) -target.rect.y
        
        # Limitar a câmera para não mostrar áreas fora do mapa
        x = min(0, x)  # esquerda
        y = min(0, y)  # topo
        
        x = max((map_width - self.width), x)  # direita
        y = max((map_height - self.height), y)  # fundo

        
        self.camera = pygame.Rect(x, y, self.width, self.height)
        pass


class Player:
    def __init__(self, x, y):
        self.sprite = Animation(image_file='assets/Idle-Sheet.png', total_frames=4, frame_width=32, frame_height=32)
        self.sprite.x, self.sprite.y = x, y
        self.rect = pygame.Rect(x, y, 32, 32)  # Tamanho do jogador, ajuste conforme necessário
        self.speed = 8  # Velocidade de movimento do jogador
        self.scale_factor = 1
        self.last_scale_time = pygame.time.get_ticks()
        self.scale_cooldown = 500  # Cooldown de 500 milissegundos

    def handle_keys(self, key_pressed):
        """Atualiza a posição do jogador com base nas teclas pressionadas."""
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
        self.sprite.x, self.sprite.y = self.rect.topleft

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

    def draw(self, surface, camera):
        """Desenha o jogador na superfície, ajustando pela posição da câmera."""
        adjusted_rect = camera.apply(self.rect)
        surface.blit(self.sprite.image, adjusted_rect.topleft)
def load_map(filename):
    """ Carrega o mapa TMX usando pytmx. """
    tmx_data = load_pygame(filename)
    return tmx_data

def draw_map(surface, tmx_data, scale, camera):
    """ Desenha o mapa no Pygame surface com um fator de escala, ajustando pela câmera. """
    tile_width = tmx_data.tilewidth
    tile_height = tmx_data.tileheight
    
    scaled_tile_width = int(tile_width * scale)
    scaled_tile_height = int(tile_height * scale)

    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    # Redimensiona o tile com base na escala
                    tile = pygame.transform.scale(tile, (scaled_tile_width, scaled_tile_height))
                    # Calcula a posição correta com a escala aplicada
                    pos_x = x * scaled_tile_width
                    pos_y = y * scaled_tile_height
                    # Aplica o deslocamento da câmera
                    surface.blit(tile, camera.apply(pygame.Rect(pos_x, pos_y, scaled_tile_width, scaled_tile_height)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))

    # Carregue seu mapa TMX aqui
    tmx_data = load_map('assets/base.tmx')
    global map_width, map_height
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight

    # Defina o fator de escala (por exemplo, 2 para dobrar o tamanho)
    scale = 4
    player = Player(100, 100)
    camera = Camera(1920,1080) #tem que botar a msm resolucao da tela

    # Main game loop
    running = True
    while running:
        key_pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.handle_keys(key_pressed)
        player.sprite.update()
        camera.update(player)

        screen.fill((0, 0, 0))
        draw_map(screen, tmx_data, scale, camera)
        player.draw(screen, camera)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
