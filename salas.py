import pygame
from mapa_WIP import load_map, draw_map_tiles
from animation_Wip import Animation
from matriz_otimizada import gerar_matriz, super_linkening
from objects_mannager import Barrier

class ConjuntoDeSalas:
    def __init__(self, scale):
        self.sprite_portas = [Porta('assets\porta_cima.png',2, 90, 73,scale), Porta('assets\porta_baixo.png',2, 85, 32,scale),Porta('assets\porta_direita.png',2, 32,87,scale),Porta('assets\porta_esquerda.png',2, 32, 87,scale)]
        self.sala_atual = (0,0)


    def new_setup(self):
        self.molde, self.sala_atual = gerar_matriz(6, 10) #gera a matriz e define a primeira sala
        
        linhas = len(self.molde)
        colunas = len(self.molde[0])
        self.matriz_salas = []
        for l in range(linhas):
            temp = []
            for c in range(colunas):
                if self.molde[l][c] == 0:
                    temp.append(None) #apeend em none
                elif self.molde[l][c] == 1:
                    temp.append(Sala('assets\dungeon_model.tmx', 1, (l,c), self.sprite_portas))
                elif self.molde[l][c] == 2:
                    temp.append(Sala('assets\dungeon_model.tmx', 2, (l,c), self.sprite_portas)) #por enquanto tá igual o 1 mas qnd a gnt tiver o mapa das salas a gnt troca o tmx
                elif self.molde[l][c] == 3:
                    temp.append(Sala('assets\dungeon_model.tmx', 3, (l,c), self.sprite_portas)) #por enquanto tá igual o 1 mas qnd a gnt tiver o mapa das salas a gnt troca o tmx
            self.matriz_salas.append(temp)
        
        #printar_matriz(self.matriz_salas) #NOTE debug
        super_linkening(self.matriz_salas, linhas, colunas) #liga todas as salas como se fosse magica!!!!
        
        return self.matriz_salas[self.sala_atual[0]][self.sala_atual[1]] #retorna a sala
    


class Sala:
    def __init__(self, tmx_path, tipo, pos_na_matriz, sprite_portas):

        self.tmx_data = load_map(tmx_path)
        self.ponteiro = {'cima':None, 'baixo':None, 'direita':None, 'esquerda':None} #cima baixo direita esquerda
        self.portas = 0
        self.all_loaded = False
        self.display_surface = pygame.display.get_surface()
        self.tipo = tipo
        self.posicao_na_matriz = pos_na_matriz

        self.portas_object = sprite_portas #dps vai ser esse pra ficar otimizado #NOTE
        #self.portas_object = [Animation('assets\porta_cima.png',2, 80, 73), Animation('assets\porta_baixo.png',2, 85, 32),Animation('assets\porta_direita.png',2, 32,87),Animation('assets\porta_esquerda.png',2, 32, 87)]

    def draw(self, surface, tmx_data, scale, camera):
        draw_map_tiles(surface, tmx_data, scale, camera)
        self.draw_portas(camera) #já é dado draw pelo ALLSprites

    
    def setup(self, scale, colision_gourp):
        for obj in self.tmx_data.get_layer_by_name('portas'):
            if obj.name == 'cima':
                self.portas_object[0].rect.x, self.portas_object[0].rect.y = obj.x*scale, obj.y*scale
                self.portas_object[0].y_sort = obj.y*scale
            elif obj.name == 'baixo':
                self.portas_object[1].rect.x, self.portas_object[1].rect.y = obj.x*scale, obj.y*scale
                self.portas_object[1].y_sort = obj.y*scale
            elif obj.name == 'direita':
                self.portas_object[2].rect.x, self.portas_object[2].rect.y = obj.x*scale, obj.y*scale
                self.portas_object[2].y_sort = obj.y*scale
            elif obj.name == 'esquerda':
                self.portas_object[3].rect.x, self.portas_object[3].rect.y = obj.x*scale, obj.y*scale
                self.portas_object[3].y_sort = obj.y*scale
        
        for obj in self.tmx_data.get_layer_by_name('portas_entrada'):
            pass
        
        for obj in self.tmx_data.get_layer_by_name('colisao_b'):
            Barrier((obj.x*scale, obj.y*scale), pygame.Surface((obj.width*scale, obj.height*scale)), (colision_gourp)) #, self.all_sprites pra debug
            #só no colision pra n ficar visivel (TODO n tem uma colisão não retangular)
        
        self.all_loaded = True
    
    def draw_portas(self, camera):
        for elem in self.portas_object:
            self.display_surface.blit(elem.sprite.frames[self.portas], camera.apply(pygame.Rect(elem.rect.x, elem.rect.y, elem.rect.width, elem.rect.height)))


class Porta(pygame.sprite.Sprite):
    #Parecida com a Animation #TODO mudar dps
    def __init__(self, image_file, total_frames, frame_width, frame_height, scale):
        self.scale_factor = scale
        self.sprite = Animation(image_file,total_frames, frame_width, frame_height)
        self.rect = pygame.Rect(0, 0, frame_width* self.scale_factor, frame_height* self.scale_factor)  # Tamanho do jogador, ajuste conforme necessário

        self.total_frames = total_frames
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.current_frame = 0
        self.image = self.sprite.frames[self.current_frame]
        self.camada = 0
        self.y_sort = 0
        self.sprite.rescale_frames(self.scale_factor)
        
        
    


#####
##### FUNCAO DE DEBUG ABAIXO:
#####
def printar_matriz(matriz):
    '''Printa a matriz pra ver se ta td certo'''
    print('\033[0m')
    for l in range(len(matriz)):
        for c in range(len(matriz[l])):
            if matriz[l][c] != None:
                elem = matriz[l][c].tipo
            else:
                elem = 0

            if elem == 3:
                elem = f'\033[1;31m{elem:2}\033[0m'
            elif elem == 2:
                elem = f'\033[1;33m{elem:2}\033[0m'
            elif elem == 1:
                elem = f'\033[1;32m{elem:2}\033[0m'
            else:
                elem = f'\033[1;30m{elem:2}\033[0m'

            print(f'{elem}', end=' ')
        
        print('')
    print()
#####
##### 
#####

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    a = ConjuntoDeSalas()
    a.new_setup()
