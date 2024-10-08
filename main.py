
#TODO resolver importsss
#NOTE o arco do inimigo fica bugado na base porque o gameloop daqui tá diferente (não atualizei ainda)

from inimigos import *
from mapa_WIP import *
import pygame
from player import Player
from camera import EverythingScreen

from objects_mannager import Objects, Barrier
from menus import *
from salas import ConjuntoDeSalas


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))


         # Carregue seu mapa TMX aqui
        self.tmx_data = load_map('assets/base.tmx')

        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight
        # Defina o fator de escala (por exemplo, 2 para dobrar o tamanho)
        self.scale = 3
        
        self.portal = [None] #vai ser definido lá embaixo (isso que leva o player pra dungeon) (é uma lista pra poder ser alterado dentro de funções)
        #talvez eu possa fazer uma classe pra ele depois

        self.ui = HealthBar()

        # Main game loop
        self.running = True

        self.acabou_de_voltar = False
        
        self.time_elapsed = 0
        self.tempo_antes = pygame.time.get_ticks()

        self.camera_group = EverythingScreen()
        self.drawables_alone = pygame.sprite.Group()

        self.collision_sprites = pygame.sprite.Group()
        #Grupo de inimigos para serem renderizados e removidos da tela quando necessário
        self.inimigos_grupo = pygame.sprite.Group()

        #grupo de portas
        self.portas_grupo = pygame.sprite.Group()

        self.spawn = ((self.map_width//2)*self.scale, (self.map_height//2)*self.scale) #centro do mapa
        self.player = Player(self.spawn[0], self.spawn[1], self.collision_sprites, self.camera_group, self.ui, self.scale)


        #Grupo de números indicadores de dano, só usados quando o inimigo vai ser removido do grupo de iteração
        self.damage_numbers = []

    def setup_base(self):
        for group in (self.camera_group, self.collision_sprites):
            group.empty()
            self.camera_group.add(self.player)

        for obj in self.tmx_data.get_layer_by_name('objetos_nc'): #adcio0na os objetos (já com a escala) no grupo
            imagem = pygame.transform.scale(obj.image, (obj.width*self.scale, obj.height*self.scale))
            atual = Objects((obj.x*self.scale, obj.y*self.scale), imagem, (self.camera_group))
            #por enquanto vai ser sem colisao direto no obj


        for obj in self.tmx_data.get_layer_by_name('colisao_b'):
            Barrier((obj.x*self.scale, obj.y*self.scale), pygame.Surface((obj.width*self.scale, obj.height*self.scale)), (self.collision_sprites)) #, self.all_sprites pra debug
            #só no colision pra n ficar visivel (TODO n tem uma colisão não retangular)

        
        for obj in self.tmx_data.get_layer_by_name('colisao_objs'):
            Barrier((obj.x*self.scale, obj.y*self.scale), pygame.Surface((obj.width*self.scale, obj.height*self.scale)), (self.collision_sprites)) #, self.all_sprites pra debug
            #só no colision pra n ficar visivel (TODO n tem uma colisão não retangular)

        for obj in self.tmx_data.get_layer_by_name('portal'):
            self.portal = [Barrier((obj.x*self.scale, obj.y*self.scale), pygame.Surface((obj.width*self.scale, obj.height*self.scale)), (self.collision_sprites))] #, self.all_sprites pra debug
            self.player.quem_portal = self.portal

 

    def main(self):
        cont = 0
        while self.running:
            key_pressed = pygame.key.get_pressed()
            
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.MOUSEWHEEL:
                    self.camera_group.scale += event.y * 0.1
                    if self.camera_group.scale < 0:
                        self.camera_group.scale = 1

            self.player.handle_keys(key_pressed, (self.inimigos_grupo, self.camera_group), self.camera_group.desvio, self.camera_group.scale_offset, self.time_elapsed/1000)
            cont += 1
            

            self.player.sprite.update()

            

            self.camera_group.draw(self.player,self.tmx_data, self.drawables_alone) 
            self.ui.draw()

            self.player.update_damage_numbers()
            self.player.draw_damage_numbers(self.camera_group.desvio)

            self.damage_numbers = [dn for dn in self.damage_numbers if dn.update()]

        
            for damage_number in self.damage_numbers:
                damage_number.draw(self.camera_group.desvio) #NOTE


            if key_pressed[pygame.K_t]:
                self.ui.health = 100
                self.player.health = 100
            

            if key_pressed[pygame.K_m] or self.portal[0]==True: #inicia a dungeon
                self.start_dungeon()
                self.player.stop = False
                self.time_elapsed = 0
                cont = 0
                continue

            

            
            for inimigo in self.inimigos_grupo:
                #inimigo.draw(self.screen, self.camera)
                inimigo.sprite.update()
                inimigo.movement(self.player.rect.x, self.player.rect.y, self.time_elapsed/1000)
                inimigo.update_damage_numbers()
                inimigo.draw_damage_numbers(self.camera_group.desvio) 
                for i in range(len(self.player.weapon[self.player.selected_weapon].shoot)):
                    if inimigo.colisao(self.player.weapon[self.player.selected_weapon].shoot[i]):
                        #O último hit do inimigo não é desenhado já que o desenho tá associado ao grupo de inimigos e a gente remove ele do grupo
                        #Solução tlvz seja fzr o indicador de dano ser desenhado por fora? mas é tanto import que mds do céu
                        #Vou jogar pra um lista e iterar as funções da lista, solução meio boba e simplista mas a vida tem dessas
                        for dn in inimigo.damage_numbers:
                            self.damage_numbers.append(dn)
                        inimigo.kill()
                        
                
                if self.player.colisao(inimigo):
                    if self.ui.health > 0:
                        self.player.take_damage(inimigo.ataque)
                        self.ui.health = self.player.health

            pygame.display.flip()
            
            #a atualizacao do tempo tem que ser aqui no final do loop já que a ideia do delta time é "tempo passado entre frames"
            agora = pygame.time.get_ticks()
            self.time_elapsed = agora - self.tempo_antes
            self.tempo_antes = agora

        pygame.quit()
    
    def start_dungeon(self):
        for grupo in [self.camera_group, self.collision_sprites, self.inimigos_grupo, self.portas_grupo, self.drawables_alone]:
            grupo.empty()

        grupo_de_salas = ConjuntoDeSalas(self.scale,self.ui, self.camera_group,self.collision_sprites, self.drawables_alone, self.player, self.camera_group.scale_offset)
        grupo_de_salas.sala_game_loop() #agora vai pro gameloop da sala
        grupo_de_salas.tempo_antes = pygame.time.get_ticks() #pra começar a contar o tempo do gameloop da sala agora só (é bom fazer isso por causa do delta time)
    
        self.acabou_de_voltar = True
    
        self.player.health = 100
        self.ui.health = 100
        self.player.max_health = 100
        self.ui.max_health = 100

        self.setup_base() #quando voltar pra base tem que resetar tudo
        self.tempo_antes = pygame.time.get_ticks() #pra corrigir o bug do delta time
        self.player.rect.x, self.player.rect.y = self.spawn[0], self.spawn[1] #volta pra posicao inicial


if __name__ == '__main__':
    jogo = Game()
    jogo.setup_base()
    jogo.main()
    
