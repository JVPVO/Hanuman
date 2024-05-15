from pygame.surface import Surface
from pplay.window import Window
from pplay.gameimage import GameImage
from pytmx import load_pygame, TiledMap
from pygame.surface import Surface
import pygame

pygame.init()















janela = pygame.display.set_mode((1920,1080))





if __name__ == "__main__":
    print("Hanuman")
    tmxdata = load_pygame('assets/testes.tmx')
    chao = tmxdata.get_tile_image(0,0, layer=0)
    parede = tmxdata.get_tile_image(0,0, layer=1)
    while True:
        janela.blit(chao, (0,0))
        #janela.blit(parede, (0,0))