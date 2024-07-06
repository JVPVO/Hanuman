import pytmx
import pygame
from pytmx.util_pygame import load_pygame

def load_map(filename):
    """ Carrega o mapa TMX usando pytmx. """
    tmx_data = load_pygame(filename)
    return tmx_data

def draw_map_tiles(tmx_data, scale, desvio, surf):
    """ Desenha o mapa no Pygame surface com um fator de escala, ajustando pela câmera. """
    display = pygame.display.get_surface()
    tile_width = tmx_data.tilewidth
    tile_height = tmx_data.tileheight
    
    scaled_tile_width = int(tile_width * scale)
    scaled_tile_height = int(tile_height * scale)

    for layer in tmx_data.visible_layers:
        if not isinstance(layer, pytmx.pytmx.TiledObjectGroup):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    # Redimensiona o tile com base na escala
                    tile = pygame.transform.scale(tile, (scaled_tile_width, scaled_tile_height))
                    
                    # Calcula a posição correta com a escala aplicada
                    pos_x = x * scaled_tile_width
                    pos_y = y * scaled_tile_height
                    

                    pos_com_desvio = pygame.math.Vector2(pos_x,pos_y) + desvio

                    # Aplica o deslocamento da câmera
                    surf.blit(tile, pos_com_desvio)

