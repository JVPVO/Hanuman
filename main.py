import pygame
import pytmx
from pytmx.util_pygame import load_pygame

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
        x = -target.rect.x + int(self.width / 2)
        y = -target.rect.y + int(self.height / 2)
        
        # Limitar a câmera para não mostrar áreas fora do mapa
        x = min(0, x)  # esquerda
        y = min(0, y)  # topo
        x = max(-(self.width - map_width), x)  # direita
        y = max(-(self.height - map_height), y)  # fundo
        
        self.camera = pygame.Rect(x, y, self.width, self.height)


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)  # Tamanho do jogador, ajuste conforme necessário
        self.speed = 2  # Velocidade de movimento do jogador
    
    def handle_keys(self, key_pressed):
        """Atualiza a posição do jogador com base nas teclas pressionadas."""
        if key_pressed[pygame.K_w]:
            self.rect.y -= self.speed
        if key_pressed[pygame.K_s]:
            self.rect.y += self.speed
        if key_pressed[pygame.K_a]:
            self.rect.x -= self.speed
        if key_pressed[pygame.K_d]:
            self.rect.x += self.speed

    def draw(self, surface, camera):
        """Desenha o jogador na superfície, ajustando pela posição da câmera."""
        # Ajusta o retângulo do jogador pela câmera antes de desenhar
        pygame.draw.rect(surface, (255, 0, 0), camera.apply(self.rect))

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
    tmx_data = load_map('assets/testes.tmx')
    global map_width, map_height
    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight

    # Defina o fator de escala (por exemplo, 2 para dobrar o tamanho)
    scale = 4
    player = Player(100, 100)
    camera = Camera(1280,720)

    # Main game loop
    running = True
    while running:
        key_pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.handle_keys(key_pressed)
        camera.update(player)

        screen.fill((0, 0, 0))
        draw_map(screen, tmx_data, scale, camera)
        player.draw(screen, camera)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
