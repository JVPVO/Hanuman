import pygame
from mapa_WIP import draw_map_tiles
from settings import camadas_obj_mundo
from inimigos import Skeleton, Rat
from player import Player
from salas import Sala

class EverythingScreen(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.tela = pygame.display.get_surface()
        
        ##desvio com vetor de desvio (pra camera)
        self.desvio = pygame.math.Vector2()
        self.metadeTelaW, self.metadeTelaH = self.tela.get_width()//2, self.tela.get_height()//2

        self.bordas = {'esquerda': 600, 'direita': 600, 'cima': 300, 'baixo': 300}
        
        l, t = self.bordas['esquerda'], self.bordas['cima'] #esquerda e cima
        w = self.tela.get_width() - self.bordas['esquerda'] - self.bordas['direita'] #largura
        h = self.tela.get_height() - self.bordas['cima'] - self.bordas['baixo'] #altura

        self.camera_rect= pygame.Rect(l, t, w, h)

        self.scale = 1
        self.scale_surface_size = (1920,1080) #como se fosse o "zoom out maximo"
        self.scale_surface = pygame.Surface(self.scale_surface_size, pygame.SRCALPHA) #SRCALPHA para ter transparencia
        self.scale_rect = self.scale_surface.get_rect(center = (self.metadeTelaW, self.metadeTelaH))
        self.scale_surface_size_vector = pygame.math.Vector2(self.scale_surface_size)
        self.scale_offset = pygame.math.Vector2(self.scale_surface_size[0]//2-self.metadeTelaW, self.scale_surface_size[1]//2-self.metadeTelaH)

    

    def centralizar_player(self, target):
        '''Centraliza a camera no player'''
        #print(self.scale_offset.x, self.scale_offset.y) 
        self.desvio.x = self.metadeTelaW - target.rect.centerx + self.scale_offset.x
        self.desvio.y = self.metadeTelaH - target.rect.centery + self.scale_offset.y
        #print(self.desvio.x, self.desvio.y)

    def centralizar_bordas(self, target):
        '''Centraliza pela caixa (a borda)'''
        
        # se o player sair da camera pela esquerda ajusta a borda (e a câmera tambem)
        if target.rect.left < self.camera_rect.left: self.camera_rect.left = target.rect.left

        # se o player sair da camera pela direita ajusta a borda (e a câmera tambem)
        if target.rect.right > self.camera_rect.right: self.camera_rect.right = target.rect.right

        # se o player sair da camera por cima ajusta a borda (e a câmera tambem)
        if target.rect.top < self.camera_rect.top: self.camera_rect.top = target.rect.top

        # se o player sair da camera por baixo ajusta a borda (e a câmera tambem)
        if target.rect.bottom > self.camera_rect.bottom: self.camera_rect.bottom = target.rect.bottom

       
        #mesma ideia do centralizar player
        self.desvio.x = self.bordas['esquerda']  - self.camera_rect.left + self.scale_offset.x
        self.desvio.y = self.bordas['cima'] - self.camera_rect.top  + self.scale_offset.y

        
    def draw(self, player, tmx_data, drawable_alone:pygame.sprite.Group):#NOTE datatmx desativado por causa do sala.draw
        self.tela.fill((0, 0, 0))
        self.scale_surface.fill((0, 0, 0))

        #Se quiser trocar de um modo pra outro é só comentar e descomentar aqui!!
        self.centralizar_player(player)
        #self.centralizar_bordas(player)
        
        #chao
       
        #blit no chao aqui (por enquanto tá na sala.draw)
        draw_map_tiles(tmx_data, 3, self.desvio, self.scale_surface, self.scale_rect) #NOTE desativado por causa do sala.draw

    
        for elem in drawable_alone:
            elem.draw(self.scale_surface, self.desvio)


        bg_sprites = [sprite for sprite in self if sprite.camada < camadas_obj_mundo['bg']]
        main_sprites = sorted([sprite for sprite in self if sprite.camada == camadas_obj_mundo['main']], key = lambda sprite: sprite.y_sort)
        top_sprites = [sprite for sprite in self if sprite.camada > camadas_obj_mundo['top']]

        
        #objetos
        for layer in (bg_sprites, main_sprites, top_sprites):
            for elem in layer: #elem = sprite pra maioria dos casos
                if isinstance(elem, Player):
                    pygame.draw.rect(self.scale_surface, (255,255,255), (elem.rect.topleft + self.desvio, elem.rect.size), 2)
                    elem.draw(self.scale_surface,self.desvio)
                elif isinstance(elem, Rat): #tem que vir antes do skeleton pq rat herda de skeleton
                    pos_com_desvio = elem.rect.topleft + self.desvio
                    self.scale_surface.blit(elem.sprite.image, pos_com_desvio)
                    pygame.draw.rect(self.scale_surface, (255,255,255), (elem.rect.topleft + self.desvio, elem.rect.size), 2)
                    elem.draw(self.scale_surface, self.desvio) # só isso que muda em comparação com o esqueleto
                elif isinstance(elem, Skeleton):#depois eu posso adicionar no grupo ai n precisa desse if (adcionar a imagem)#NOTE
                    pos_com_desvio = elem.rect.topleft + self.desvio
                    self.scale_surface.blit(elem.sprite.image, pos_com_desvio)
                else:
                    pos_com_desvio = elem.rect.topleft + self.desvio
                    self.scale_surface.blit(elem.image, pos_com_desvio)


        
        scaled_surf = pygame.transform.scale(self.scale_surface, self.scale_surface_size_vector*self.scale)
        scaled_rect = scaled_surf.get_rect(center = (self.metadeTelaW, self.metadeTelaH))

        self.tela.blit(scaled_surf, scaled_rect)

        #pygame.draw.rect(self.tela, (255,0,0), self.camera_rect, 8) #ver onde estao as bordas (#debug)

    
#NOTE A camera do cara do video n tem aquilo de nao sair do mapa, teremos que implementar de novo depois (não é dificil pq temos a camera antiga ainda)

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


    