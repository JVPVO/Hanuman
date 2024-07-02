import pygame
from mapa_WIP import draw_map_tiles
from settings import camadas_obj_mundo
from inimigos import Skeleton
from player import Player


class EverythingScreen(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.tela = pygame.display.get_surface()
        
        ##desvio com vetor de desvio (pra camera)
        self.desvio = pygame.math.Vector2()


    def draw(self, tmx_data):#NOTE datatmx desativado por causa do sala.draw
        #chao
        
        #blit no chao aqui
        #draw_map_tiles(tmx_data, 3, self.desvio) #NOTE desativado por causa do sala.draw


        bg_sprites = [sprite for sprite in self if sprite.camada < camadas_obj_mundo['bg']]
        main_sprites = sorted([sprite for sprite in self if sprite.camada == camadas_obj_mundo['main']], key = lambda sprite: sprite.y_sort)
        top_sprites = [sprite for sprite in self if sprite.camada > camadas_obj_mundo['top']]

        
        #objetos
        for layer in (bg_sprites, main_sprites, top_sprites):
            for elem in layer: #elem = sprite pra maioria dos casos
                if isinstance(elem, Player):
                    elem.draw(self.tela,self.desvio)
                elif isinstance(elem, Skeleton):#depois eu posso adicionar no grupo ai n precisa desse if (adcionar a imagem)#NOTE
                    pos_com_desvio = elem.rect.topleft + self.desvio
                    self.tela.blit(elem.sprite.image, pos_com_desvio)
                else:
                    pos_com_desvio = elem.rect.topleft + self.desvio
                    self.tela.blit(elem.image, pos_com_desvio)

    


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def apply(self, rect):
        """Desloca o rect pra deixar em relacao a camera"""
        return rect.move(self.camera.topleft)
    
    def update(self, target, map_height, map_width, scale):
        """Atualiza a posição da câmera para seguir o alvo (jogador)."""
        x =  int(self.width / 2) -target.rect.x
        y =  int(self.height / 2) -target.rect.y
        # NOTE DEBUG print(y, x, self.height, target.rect.y, map_height, self.height-(map_height)*scale) #map height padrao é 480
        

        # Limitar a câmera para não mostrar áreas fora do mapa SE O MAPA FOR MAIOR QUE A CAMERA SOMENTE
        if map_width*scale >= self.width: #maior que a res da tela
            x = min(0, x)  # esquerda #-1252
            x = max(self.width-map_width*scale, x)  # direita
            
        
        if map_height*scale >= self.height: #maior que a res da tela
            y = min(0, y)  # topo
            y = max(self.height-map_height*scale, y)  # baixo

        self.x = x
        self.y = y

        self.camera = pygame.Rect(x, y, self.width, self.height)


    