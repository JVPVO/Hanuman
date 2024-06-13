import pytmx
import pygame
from pytmx.util_pygame import load_pygame

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

