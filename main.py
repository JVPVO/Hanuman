import pygame
import pytmx
from pytmx.util_pygame import load_pygame

def load_map(filename):
    """ Carrega o mapa TMX usando pytmx. """
    tmx_data = load_pygame(filename)
    return tmx_data

def draw_map(surface, tmx_data, scale):
    """ Desenha o mapa no Pygame surface com um fator de escala. """
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
                    surface.blit(tile, (pos_x, pos_y))

def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))

    # Carregue seu mapa TMX aqui
    tmx_data = load_map('assets/testes.tmx')

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        draw_map(screen, tmx_data, scale=5)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
