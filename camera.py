import pygame

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0

    def apply(self, rect):
        """Aplica o deslocamento da câmera a um retângulo pygame.Rect para renderizar na posição correta."""
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


    