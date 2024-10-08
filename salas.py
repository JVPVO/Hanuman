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
        self.player = player
        self.scale = scale
        
        self.finalizou = False
        self.how_many_cleared = 1  #vao ser sobrescritos no first setup (é um porque a loja já conta como uma sala)
        self.clear_goal = 0        #vao ser sobrescritos no first setup
        self.player.quem_portal = [False] #vai ser sobrescrito nos setups
        self.portal = self.player.quem_portal #linkou com player

        self.game_over_sound = pygame.mixer.Sound('assets\\dungeon_props\\game_over.wav')
        self.som_porta = pygame.mixer.Sound('assets\\dungeon_props\\door18.wav')
        self.teminou_som = pygame.mixer.Sound('assets\\dungeon_props\\achievement_00.wav')
        self.saiu = False

        self.salas_comuns_sprites = [f'assets\\dungeon_room_1_{i}.tmx' for i in range(5)] # só tem 5 salas por enquanto...
        self.salas_lojas = [f'assets\\dungeon_room_2_0.tmx'] #só tem 1 loja por enquanto
        self.salas_boss = [f'assets\\dungeon_room_3_0.tmx'] #só tem 1 sala de chefe por enquanto
        
        ##para o game loop
        self.screen = pygame.display.get_surface()
        self.inimigos_grupo = pygame.sprite.Group()
        self.portas_grupo = pygame.sprite.Group()
        self.collision_sprites = collision_sprites #é melhor usar o que já tem
        self.projectile_group = pygame.sprite.Group() #projeteis que podem dar dano no player
        
        self.drawables_alone = drawables_alone
        self.camera_group = camera_group
        self.ui = ui

        self.damage_numbers = []

        self.camera_group.add(self.player)


        self.time_elapsed = 0 
        self.tempo_antes = pygame.time.get_ticks()

        self.sala:Sala = self.first_setup()
        self.sala_atual_obj = self.sala #sala atual como objeto
        self.player.rect.x, self.player.rect.y = self.get_first_pos_player(self.sala, self.scale) #ele tem uma area pra nascer pela primeira vez

        self.drawables_alone.add(self.sala)

        self.sala.setup(self.scale, self.collision_sprites, self.portas_grupo, self.camera_group, self.inimigos_grupo, self.projectile_group, self.player, self.finalizou)

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
                    if self.camera_group.scale < 0:
                        self.camera_group.scale = 1

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

            #UI
            self.damage_numbers = [dn for dn in self.damage_numbers if dn.update()]

            self.minimap.updateMinimap((self.sala_atual[0], self.sala_atual[1]))
            self.minimap.render(self.screen)
            for damage_number in self.damage_numbers:
                damage_number.draw(self.camera_group.desvio) #NOTE


            #key handles
            if key_pressed[pygame.K_t]:
                self.ui.health = self.ui.max_health
                self.player.health = self.player.max_health
            
            if key_pressed[pygame.K_h]:
                self.sala.portas = (self.sala.portas+1)%2
 
            if key_pressed[pygame.K_e] or self.portal[0]==True:
                self.saiu = True #acaba com a brincadeira
                break
            
            if self.player.health <= 0:
                self.saiu = True
                
                self.game_over_sound.play(fade_ms=100)
                break

            #tudo relacionado a inimigo
            self.gerenciador_de_inimigos()
            
            for drop in self.sala_atual_obj.dropados:
                drop.animate()
            

            pygame.display.flip()
            agora = pygame.time.get_ticks()
            self.time_elapsed = agora - self.tempo_antes
            self.tempo_antes = agora

            
                

        for grupo in [self.camera_group, self.collision_sprites, self.inimigos_grupo, self.portas_grupo, self.drawables_alone]: #limpa tudo
            grupo.empty()
        self.player.stop = True

        return


    def first_setup(self):
        '''Setup da primeira sala + ciracao de todas as outras salas'''
        
        qntd_de_salas = 10
        self.molde, self.sala_atual = gerar_matriz(6, qntd_de_salas) #gera a matriz e define a primeira sala (matriz 6x6)
        self.clear_goal = qntd_de_salas
        
        linhas = len(self.molde)
        colunas = len(self.molde[0])
        self.matriz_salas = []
        for l in range(linhas):
            temp = []
            for c in range(colunas):
                if self.molde[l][c] == 0:
                    temp.append(None) #apeend em none
                elif self.molde[l][c] == 1:
                    sala_path = Path(random.choice(self.salas_comuns_sprites))
                    temp.append(Sala(sala_path, 1, (l,c), self.sprite_portas))
                elif self.molde[l][c] == 2:
                    sala_path = Path(random.choice(self.salas_lojas))
                    temp.append(Sala(sala_path, 2, (l,c), self.sprite_portas)) 
                elif self.molde[l][c] == 3:
                    sala_path = Path(random.choice(self.salas_boss))
                    temp.append(Sala(sala_path, 3, (l,c), self.sprite_portas)) #por enquanto tá igual o 1 mas qnd a gnt tiver o mapa das salas a gnt troca o tmx
            self.matriz_salas.append(temp)
        
        printar_matriz(self.matriz_salas) #NOTE debug
        print(f'posicao do player no mapa: {(self.sala_atual[0],self.sala_atual[1])} ')
        super_linkening(self.matriz_salas, linhas, colunas) #liga todas as salas como se fosse magica!!!!



        #Criando o minimapa junto com o conjunto de salas
        self.minimap = Minimap(mapa=self.molde)

        self.sala_atual_obj = self.matriz_salas[self.sala_atual[0]][self.sala_atual[1]]
        
        self.tempo_antes = pygame.time.get_ticks() #acredito que ajude no deltatime
        return self.sala_atual_obj #retorna a sala
    
    def gerenciador_de_inimigos(self):
        '''Tudo que envolve inimigos porvavelmente tá aqui'''
        #Só movi pra cá pra ficar mais organizado

        for inimigo in self.inimigos_grupo:
            #inimigo.draw(self.screen, self.camera)
            inimigo.sprite.update()
            inimigo.movement(self.player.hitbox_C.centerx, self.player.hitbox_C.centery, self.time_elapsed/1000, self.collision_sprites)
            inimigo.update_damage_numbers()
            inimigo.draw_damage_numbers(self.camera_group.desvio) 

            #Rato nao mira no player se ele nao tiver visao
            if isinstance(inimigo, Rat) and not inimigo.check_vision(self.player.hitbox_C.centerx, self.player.hitbox_C.centery, self.collision_sprites): #ta duplicado
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
                        self.how_many_cleared += 1
                        if self.how_many_cleared == self.clear_goal:
                            self.teminou_som.play(fade_ms=100) #la em cima da update no estado finalizado
                            
                   

                    #se o inimigo morre pode dropar algo
                    if random.randrange(100) < 20: #chance de drop 20 porcento
                        funcao, intensidade, asset = _gerador_pocao(pesos=[0.7, 0.3]) #(70% de vida e 30% de aumentar_vida_maxima)
                        Dropaveis(inimigo.rect, asset , (self.camera_group, self.sala_atual_obj.dropados, self.collision_sprites), funcao, intensidade, self.scale)
                    
            
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


    def mudanca_de_sala(self,player, dest, sala_de_agora, grupo_de_portas:pygame.sprite.Group, grupo_de_colisao:pygame.sprite.Group, camera_group, inimigos_grupo, drawble_alone):
        self.som_porta.play(fade_ms=100)
        drawble_alone.remove(sala_de_agora)
        grupo_de_colisao.empty()
        camera_group.empty()
        camera_group.add(player)
        inimigos_grupo.empty()

        
        nova_sala = sala_de_agora.ponteiro[dest]

        if self.clear_goal <= self.how_many_cleared:
            self.finalizou = True

        grupo_de_portas.empty()
        grupo_de_colisao.empty()
        self.projectile_group.empty()
        nova_sala.setup(self.scale, grupo_de_colisao, grupo_de_portas, camera_group, inimigos_grupo, self.projectile_group, self.player, self.finalizou) 
        player.rect.x, player.rect.y = nova_sala.posicoes_perto_portas[dest] #define a posicao do player com base de onde ele vem
        self.sala_atual = nova_sala.posicao_na_matriz

        #adciona o dropados a camera
        for elem in nova_sala.dropados:
            camera_group.add(elem)
        
        self.sala_atual_obj = nova_sala
        drawble_alone.add(nova_sala)
        return nova_sala
    
    def get_first_pos_player(self, sala_obj, scale):
        spawn_area_list = []
        tmx_data = sala_obj.tmx_data
        for obj in tmx_data.get_layer_by_name('first_start_pos_player'): #adciona a area em que os inimigos podem dar spawn a lista
            x_top, x_bot = obj.x*scale, (obj.x+obj.width)*scale #min e max de x
            y_top, y_bot = obj.y*scale, (obj.y+obj.height)*scale # min e max de y
            spawn_area_list.append((int(x_top), int(x_bot), int(y_top), int(y_bot)))

        return sala_obj.choose_area_to_spawn(spawn_area_list)


class Sala(pygame.sprite.Sprite):
    def __init__(self, tmx_path, tipo, pos_na_matriz, sprite_portas):
        super().__init__()

        self.tmx_data = load_map(tmx_path)
        self.ponteiro = {'cima':None, 'baixo':None, 'direita':None, 'esquerda':None} #cima baixo direita esquerda
        self.portas = 0 #vira 1 quando os inimigos morrem 
        self.ja_passou_setup = False
        self.tipo = tipo
        self.posicao_na_matriz = pos_na_matriz

        self.dropados = pygame.sprite.Group() #pra intens dropados
        
        self.posicoes_perto_portas = {'cima':None, 'baixo':None, 'direita':None, 'esquerda':None} #no setup é prenchida de forma contraria ao #self.ponteiro (pq só precisamos dessa posicao se estamos vindo de outro lugar) (tipo uma posicao relativa de novo)
        
        

        self.portas_object = sprite_portas #dps vai ser esse pra ficar otimizado #NOTE
        #self.portas_object = [Animation('assets\porta_cima.png',2, 80, 73), Animation('assets\porta_baixo.png',2, 85, 32),Animation('assets\porta_direita.png',2, 32,87),Animation('assets\porta_esquerda.png',2, 32, 87)]

    def draw(self, tmx_data, scale, desvio, tela):
        draw_map_tiles(tmx_data, scale, desvio, tela)
        #self.draw_portas(desvio) #já é dado draw pelo ALLSprites

    
    def setup(self, scale, colision_gourp, portas_group, camera_group, inimigos_group, projectile_group, player, cleared_all):
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
            #só no colision pra n ficar visivel (TODO n tem uma colisão não retangular)

        for obj in self.tmx_data.get_layer_by_name('colisao_objs'):
            Barrier((obj.x*scale, obj.y*scale), pygame.Surface((obj.width*scale, obj.height*scale)), (colision_gourp)) #, self.all_sprites pra debug
            #só no colision pra n ficar visivel (TODO n tem uma colisão não retangular)
        
        for obj in self.tmx_data.get_layer_by_name('objetos_nc'): #adcio0na os objetos (já com a escala) no grupo
            imagem = pygame.transform.scale(obj.image, (obj.width*scale, obj.height*scale))
            atual = Objects((obj.x*scale, obj.y*scale), imagem, (camera_group))
            #por enquanto vai ser sem colisao direto no obj
        
        if cleared_all:
            for obj in self.tmx_data.get_layer_by_name('portal'):
                portal = Barrier((obj.x*scale, obj.y*scale), pygame.Surface((obj.width*scale, obj.height*scale)), (colision_gourp)) #, self.all_sprites pra debug
                player.quem_portal[0] = portal
            #poe a imagem do portal na sala
            for obj in self.tmx_data.get_layer_by_name('portal_img'):
                imagem = pygame.transform.scale(obj.image, (obj.width*scale, obj.height*scale))
                Objects((obj.x*scale, obj.y*scale), imagem, (camera_group))

        spawn_area_list = []
        for obj in self.tmx_data.get_layer_by_name('spawn_en'): #adciona a area em que os inimigos podem dar spawn a lista (tambem é usado pros itens da loja)
            if self.tipo ==1:
                x_top, x_bot = obj.x*scale, (obj.x+obj.width)*scale #min e max de x
                y_top, y_bot = obj.y*scale, (obj.y+obj.height)*scale # min e max de y
                spawn_area_list.append((int(x_top), int(x_bot), int(y_top), int(y_bot)))
            
            elif self.tipo == 2: #quando for loja
                #usaremos as areas de spawn para os itens da loja
                x_center = (obj.x+obj.width/2)*scale
                y_center = (obj.y+obj.height/2)*scale
                spawn_area_list.append((x_center, y_center))
            elif self.tipo == 3: #quando for sala de chefe
                meio_x = (self.tmx_data.width * self.tmx_data.tilewidth * scale)/2
                meio_y = (self.tmx_data.height * self.tmx_data.tileheight * scale)/2
                break #por enquanto que nao tem area de inimigos
                #depois botar a area de inimigos
        
        if not self.ja_passou_setup: #evita de esqueletos nascerem de novo em salas zeradas (e itens de lojas também)
            
            if self.tipo == 1:
                for _ in range(random.randint(3,8)): 
                    x, y = self.choose_area_to_spawn(spawn_area_list)
                    s =Skeleton(x, y, initial_scale=scale, groups=(camera_group, inimigos_group))
                for _ in range(random.randint(0,2)):
                    x, y = self.choose_area_to_spawn(spawn_area_list)
                    r = Rat(x, y, initial_scale=scale, groups=(camera_group, inimigos_group), projectile_group=projectile_group)
            
            elif self.tipo == 2:
                self.portas = 1
                funcao, intensidade, asset = _gerador_pocao(tipo='loja')
                for c, zipado in enumerate(zip(funcao, intensidade, asset)): #tres itens na loja
                    func, intens, asset_path = zipado
                    x, y = spawn_area_list[c]
                    Loja((x,y), asset_path,(camera_group, self.dropados, colision_gourp), func,intens, self.dropados, scale) #cria um item do tipo loja
            
            elif self.tipo == 3:
                Boss(meio_x, meio_y, scale, (camera_group, inimigos_group), ((self.tmx_data.width * self.tmx_data.tilewidth * scale), (self.tmx_data.height * self.tmx_data.tileheight * scale)), projectile_group, colision_gourp)

                         


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
        
        



def _gerador_pocao(pesos:list=[], tipo='comum'):
        '''gera o efeito com base no tipo do coletavel'''
        if tipo == 'comum':
            funcoes = ['vida', 'aumentar_vida_maxima']
            escolhido = random.choices(funcoes, weights=pesos, k=1)[0] #escolhe uma das funcoes com base na probabilidade 
            intensidade = 0#vai ser sobrescrito
            asset = 'assets\\dungeon_props\\'#vai ser sobrescrito

            if escolhido == 'vida':
                intensidade = random.randint(10, 20)
                asset = 'assets\\dungeon_props\\dungeon_props_24.png'
            elif escolhido == 'aumentar_vida_maxima':
                intensidade = random.randint(5, 10)
                asset = 'assets\\dungeon_props\\novos_27.png'
        
        elif tipo == 'loja':
            funcoes = ['max_health', 'more_damage',  'more_speed', 'aumentar_vida_maxima']
            escolhido = random.sample(funcoes, 3)#escolhe 3 pra loja
            intensidade = []
            asset = [] #TODO ASSETS DECENTES tem uns de teste ali

            for cada in escolhido:
                if cada == 'max_health':
                    intensidade.append(None) #não tem intensidade
                    asset.append('assets\\dungeon_props\\item_loja_03.png')
                elif cada == 'more_damage':
                    intensidade.append(random.randint(5, 10)) #absoluto
                    asset.append('assets\\dungeon_props\\item_loja_06.png')
                elif cada == 'more_speed':
                    intensidade.append(random.randint(0, 45)) #em percentual
                    asset.append('assets\\dungeon_props\\item_loja_09.png')
                elif cada == 'aumentar_vida_maxima':
                    intensidade.append(random.randint(20, 40)) #absoluto
                    asset.append('assets\\dungeon_props\\novos_27.png')
        

        
        return escolhido, intensidade, asset



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
    a.first_setup()
