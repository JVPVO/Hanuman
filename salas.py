import pygame
from mapa_WIP import load_map, draw_map_tiles
from animation_Wip import Animation
from matriz_otimizada import gerar_matriz, super_linkening
from objects_mannager import Barrier, Objects

from inimigos import *
from menus import *

import random
from pathlib import Path

class ConjuntoDeSalas:
    def __init__(self, scale, ui, camera_group, collision_sprites, drawables_alone, player, scaleoffset):
        self.sprite_portas = [Porta(Path('assets\\porta_cima.png'),2, 90, 73,scale), Porta(Path('assets\\porta_baixo.png'),2, 85, 32,scale),Porta(Path('assets\\porta_direita.png'),2, 32,87,scale),Porta(Path('assets\\porta_esquerda.png'),2, 32, 87,scale)]
        self.sala_atual = (0,0)
        self.scale = scale
        self.finalizou = False

        self.saiu = False

        ##para o game loop
        self.screen = pygame.display.get_surface()
        self.inimigos_grupo = pygame.sprite.Group()
        self.portas_grupo = pygame.sprite.Group()
        self.collision_sprites = collision_sprites #é melhor usar o que já tem
        self.projectile_group = pygame.sprite.Group() #projeteis que podem dar dano no player
        
        self.drawables_alone = drawables_alone
        self.camera_group = camera_group
        self.player = player
        self.ui = ui

        self.damage_numbers = []

        self.camera_group.add(self.player)


        self.time_elapsed = 0 
        self.tempo_antes = pygame.time.get_ticks()

        self.sala:Sala = self.new_setup()
        self.player.rect.x, self.player.rect.y = 100, 100

        self.drawables_alone.add(self.sala)

        self.sala.setup(self.scale, self.collision_sprites, self.portas_grupo, self.camera_group, self.inimigos_grupo, self.projectile_group)

        self.tmx_data = self.sala.tmx_data
        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight

        self.scaleoffset = scaleoffset

        #minimap é criado no new_setup



    def sala_game_loop(self):
        while not self.saiu:
            key_pressed = pygame.key.get_pressed()
            self.screen.fill((0, 0, 0))
            
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.MOUSEWHEEL:
                    self.camera_group.scale += event.y * 0.1

            self.player.handle_keys(key_pressed, (self.inimigos_grupo, self.camera_group, self.projectile_group), self.camera_group.desvio, self.scaleoffset, self.time_elapsed/1000)
            
            #mover isso pra outro lugar dps
            if self.sala.portas == 1:
                qual_porta = self.player.check_door_collision(self.portas_grupo)
                if qual_porta != None:
                    self.sala = self.mudanca_de_sala(self.player, qual_porta, self.sala, self.portas_grupo, self.collision_sprites,self.camera_group, self.inimigos_grupo, self.drawables_alone)
                    self.tmx_data = self.sala.tmx_data
                    self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
                    self.map_height = self.tmx_data.height * self.tmx_data.tileheight

            self.player.sprite.update()
            
            
            

            self.camera_group.draw(self.player,self.tmx_data, self.drawables_alone) #NOTE datatmx desativado por causa do sala.draw
            self.ui.draw()

            self.player.update_damage_numbers()
            self.player.draw_damage_numbers(self.camera_group.desvio)

            self.damage_numbers = [dn for dn in self.damage_numbers if dn.update()]

            self.minimap.updateMinimap((self.sala_atual[0], self.sala_atual[1]))
            self.minimap.render(self.screen)
            for damage_number in self.damage_numbers:
                damage_number.draw(self.camera_group.desvio) #NOTE


            if key_pressed[pygame.K_t]:
                self.ui.health = 100
                self.player.health = 100
            
            if key_pressed[pygame.K_h]:
                self.sala.portas = (self.sala.portas+1)%2
            
            if key_pressed[pygame.K_e]:
                self.saiu = True #acaba com a brincadeira

            
            for inimigo in self.inimigos_grupo:
                #inimigo.draw(self.screen, self.camera)
                inimigo.sprite.update()
                inimigo.movement(self.player.rect.x, self.player.rect.y, self.time_elapsed/1000, self.collision_sprites)
                inimigo.update_damage_numbers()
                inimigo.draw_damage_numbers(self.camera_group.desvio) 

                if isinstance(inimigo, Rat):
                    inimigo.weapon[0].update(inimigo.rect, self.camera_group.desvio, inimigo.rect.height, self.scaleoffset, self.player.rect) 

                for i in range(len(self.player.weapon[self.player.selected_weapon].shoot)):
                    if inimigo.colisao(self.player.weapon[self.player.selected_weapon].shoot[i]):
                        #O último hit do inimigo não é desenhado já que o desenho tá associado ao grupo de inimigos e a gente remove ele do grupo
                        #Solução tlvz seja fzr o indicador de dano ser desenhado por fora? mas é tanto import que mds do céu
                        #Vou jogar pra um lista e iterar as funções da lista, solução meio boba e simplista mas a vida tem dessas
                        for dn in inimigo.damage_numbers:
                            self.damage_numbers.append(dn)
                        inimigo.kill()
                        if len(self.inimigos_grupo) == 0:
                            self.sala.portas = 1
                
                if self.player.colisao(inimigo):
                    if self.ui.health > 0:
                        self.player.take_damage(inimigo.ataque)
                        self.ui.health = self.player.health
                
                if len(self.projectile_group) != 0:
                    for proj in self.projectile_group:
                        if proj.rot_image_rect.colliderect(self.player.rect):
                            self.player.take_damage(proj.dano)
                            self.ui.health = self.player.health
                            proj.hitted = True
                            proj.kill()

            
            
            pygame.display.flip()
            agora = pygame.time.get_ticks()
            self.time_elapsed = agora - self.tempo_antes
            self.tempo_antes = agora


        for grupo in [self.camera_group, self.collision_sprites, self.inimigos_grupo, self.portas_grupo, self.drawables_alone]: #limpa tudo
            grupo.empty()

        return




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
                    temp.append(Sala(Path('assets\\dungeon_room_1_0.tmx'), 1, (l,c), self.sprite_portas))
                elif self.molde[l][c] == 2:
                    temp.append(Sala(Path('assets\\dungeon_room_1_0.tmx'), 2, (l,c), self.sprite_portas)) #por enquanto tá igual o 1 mas qnd a gnt tiver o mapa das salas a gnt troca o tmx
                elif self.molde[l][c] == 3:
                    temp.append(Sala(Path('assets\\dungeon_room_1_0.tmx'), 3, (l,c), self.sprite_portas)) #por enquanto tá igual o 1 mas qnd a gnt tiver o mapa das salas a gnt troca o tmx
            self.matriz_salas.append(temp)
        
        printar_matriz(self.matriz_salas) #NOTE debug
        print(f'posicao do player no mapa: {(self.sala_atual[0],self.sala_atual[1])} ')
        super_linkening(self.matriz_salas, linhas, colunas) #liga todas as salas como se fosse magica!!!!



        #Criando o minimapa junto com o conjunto de salas
        self.minimap = Minimap(mapa=self.molde)
        
        return self.matriz_salas[self.sala_atual[0]][self.sala_atual[1]] #retorna a sala
    
    def mudanca_de_sala(self,player, dest, sala_de_agora, grupo_de_portas:pygame.sprite.Group, grupo_de_colisao:pygame.sprite.Group, all_sprite_gorup, inimigos_grupo, drawble_alone):
        drawble_alone.remove(sala_de_agora)
        
        nova_sala = sala_de_agora.ponteiro[dest]
        grupo_de_portas.empty()
        grupo_de_colisao.empty()
        nova_sala.setup(self.scale, grupo_de_colisao, grupo_de_portas, all_sprite_gorup, inimigos_grupo) 
        player.rect.x, player.rect.y = nova_sala.posicoes_perto_portas[dest] #define a posicao do player com base de onde ele vem
        self.sala_atual = nova_sala.posicao_na_matriz

        drawble_alone.add(nova_sala)
        return nova_sala




class Sala(pygame.sprite.Sprite):
    def __init__(self, tmx_path, tipo, pos_na_matriz, sprite_portas):
        super().__init__()

        self.tmx_data = load_map(tmx_path)
        self.ponteiro = {'cima':None, 'baixo':None, 'direita':None, 'esquerda':None} #cima baixo direita esquerda
        self.portas = 0 #vira 1 quando os inimigos morrem
        self.ja_passou_setup = False
        self.tipo = tipo
        self.posicao_na_matriz = pos_na_matriz
        
        self.posicoes_perto_portas = {'cima':None, 'baixo':None, 'direita':None, 'esquerda':None} #no setup é prenchida de forma contraria ao #self.ponteiro (pq só precisamos dessa posicao se estamos vindo de outro lugar) (tipo uma posicao relativa de novo)
        
        

        self.portas_object = sprite_portas #dps vai ser esse pra ficar otimizado #NOTE
        #self.portas_object = [Animation('assets\porta_cima.png',2, 80, 73), Animation('assets\porta_baixo.png',2, 85, 32),Animation('assets\porta_direita.png',2, 32,87),Animation('assets\porta_esquerda.png',2, 32, 87)]

    def draw(self, tmx_data, scale, desvio, tela):
        draw_map_tiles(tmx_data, scale, desvio, tela)
        #self.draw_portas(desvio) #já é dado draw pelo ALLSprites

    
    def setup(self, scale, colision_gourp, portas_group, camera_group, inimigos_group, projectile_group):
        colision_gourp.empty()
       
        #depois ajeitar essa bagunca embaixo #TODO
        for obj in self.tmx_data.get_layer_by_name('portas'):
            if obj.name == 'cima':
                self.portas_object[0].rect.x, self.portas_object[0].rect.y = obj.x*scale, obj.y*scale
                self.portas_object[0].y_sort = obj.y*scale
                self.posicoes_perto_portas['baixo'] = (obj.x*scale, obj.y*scale+35)
            elif obj.name == 'baixo':
                self.portas_object[1].rect.x, self.portas_object[1].rect.y = obj.x*scale, obj.y*scale
                self.portas_object[1].y_sort = obj.y*scale
                self.posicoes_perto_portas['cima'] = (obj.x*scale, obj.y*scale-35)
            elif obj.name == 'direita':
                self.portas_object[2].rect.x, self.portas_object[2].rect.y = obj.x*scale, obj.y*scale
                self.portas_object[2].y_sort = obj.y*scale
                self.posicoes_perto_portas['esquerda'] = (obj.x*scale-35, obj.y*scale)

            elif obj.name == 'esquerda':
                self.portas_object[3].rect.x, self.portas_object[3].rect.y = obj.x*scale, obj.y*scale
                self.portas_object[3].y_sort = obj.y*scale
                self.posicoes_perto_portas['direita'] = (obj.x*scale+35, obj.y*scale)

        
        
        for obj in self.tmx_data.get_layer_by_name('portas_entrada'):
            if self.ponteiro[obj.name] != None:
                Barrier((obj.x*scale, obj.y*scale), pygame.Surface((obj.width*scale, obj.height*scale)), (portas_group), obj.name) #, self.all_sprites pra debug

        
        for obj in self.tmx_data.get_layer_by_name('colisao_b'):
            Barrier((obj.x*scale, obj.y*scale), pygame.Surface((obj.width*scale, obj.height*scale)), (colision_gourp)) #, self.all_sprites pra debug
            print('a')
            #só no colision pra n ficar visivel (TODO n tem uma colisão não retangular)

        for obj in self.tmx_data.get_layer_by_name('colisao_objs'):
            Barrier((obj.x*scale, obj.y*scale), pygame.Surface((obj.width*scale, obj.height*scale)), (colision_gourp)) #, self.all_sprites pra debug
            #só no colision pra n ficar visivel (TODO n tem uma colisão não retangular)
        
        for obj in self.tmx_data.get_layer_by_name('objetos_nc'): #adcio0na os objetos (já com a escala) no grupo
            imagem = pygame.transform.scale(obj.image, (obj.width*scale, obj.height*scale))
            atual = Objects((obj.x*scale, obj.y*scale), imagem, (camera_group))
            #por enquanto vai ser sem colisao direto no obj

        
        spawn_area_list = []
        for obj in self.tmx_data.get_layer_by_name('spawn_en'): #adciona a area em que os inimigos podem dar spawn a lista
            x_top, x_bot = obj.x*scale, (obj.x+obj.width)*scale #min e max de x
            y_top, y_bot = obj.y*scale, (obj.y+obj.height)*scale # min e max de y
            spawn_area_list.append((int(x_top), int(x_bot), int(y_top), int(y_bot)))
        
        if not self.ja_passou_setup: #evita de esqueletos nascerem de novo em salas zeradas

            for _ in range(random.randint(3,8)): 
                x, y = self.choose_area_to_spawn(spawn_area_list)
                s =Skeleton(x, y, initial_scale=scale, groups=(camera_group, inimigos_group))
            for _ in range(random.randint(0,2)):
                x, y = self.choose_area_to_spawn(spawn_area_list)
                r = Rat(x, y, initial_scale=scale, groups=(camera_group, inimigos_group), projectile_group=projectile_group)

        self.ja_passou_setup = True
    

    def choose_area_to_spawn(self, spawn_area_list):
        '''Escolhe uma area aleatoria e uma posicao aleatoria dentro da area'''
        area = random.choice(spawn_area_list)
        x = random.randint(area[0], area[1])
        y = random.randint(area[2], area[3])
        return x, y

    def draw(self,surf, desvio):
        #esse draw é só nas portas, o resto é feito pelo draw do da funcao do mapa que é chamada lá na camera
        for elem, pos in zip(self.portas_object, self.ponteiro.keys()):
            if self.ponteiro[pos] != None:
                pos_com_desvio = pygame.math.Vector2(elem.rect.x, elem.rect.y) + desvio
                surf.blit(elem.sprite.frames[self.portas], pos_com_desvio)


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
