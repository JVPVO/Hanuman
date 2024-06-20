#TODO Colisão
#TODO implementar deltatime
#TODO implementar deltatime
#TODO resolver importsss
#falta voltar o que ela antes + draw player no grupo + colisao efetiva

from inimigos import *
from mapa_WIP import *
import pygame
from camera import Camera
from player import Player

from objects_mannager import AllSprites, Objects, Barrier
from menus import *
from salas import ConjuntoDeSalas, Sala


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
        
        self.camera = Camera(1920,1080) #tem que botar a msm resolucao da tela pro jogador ficar no meio da tela

        self.ui = HealthBar()

        # Main game loop
        self.running = True
        

        self.all_sprites = AllSprites(self.screen.get_width(), self.screen.get_height())
        self.collision_sprites = pygame.sprite.Group()
        #Grupo de inimigos para serem renderizados e removidos da tela quando necessário
        self.inimigos_grupo = pygame.sprite.Group()

        #Grupo de números indicadores de dano, só usados quando o inimigo vai ser removido do grupo de iteração
        self.damage_numbers = []

    def setup_base(self):
        for group in (self.all_sprites, self.collision_sprites):
            group.empty()

        for obj in self.tmx_data.get_layer_by_name('objetos_nc'): #adcio0na os objetos (já com a escala) no grupo
            imagem = pygame.transform.scale(obj.image, (obj.width*self.scale, obj.height*self.scale))
            atual = Objects((obj.x*self.scale, obj.y*self.scale), imagem, (self.all_sprites))
            #por enquanto vai ser sem colisao direto no obj
            



        for obj in self.tmx_data.get_layer_by_name('colisao_b'):
            Barrier((obj.x*self.scale, obj.y*self.scale), pygame.Surface((obj.width*self.scale, obj.height*self.scale)), (self.collision_sprites)) #, self.all_sprites pra debug
            #só no colision pra n ficar visivel (TODO n tem uma colisão não retangular)

        
        for obj in self.tmx_data.get_layer_by_name('colisao_objs'):
            Barrier((obj.x*self.scale, obj.y*self.scale), pygame.Surface((obj.width*self.scale, obj.height*self.scale)), (self.collision_sprites)) #, self.all_sprites pra debug
            #só no colision pra n ficar visivel (TODO n tem uma colisão não retangular)

        self.player = Player(100, 100, self.collision_sprites, self.scale)

    def setup_salas(self):
        todas_salas = ConjuntoDeSalas(self.scale)
        self.sala:Sala = todas_salas.new_setup()
        self.sala.setup(self.scale, self.collision_sprites)
        self.tmx_data = self.sala.tmx_data
        self.player = Player(100, 100, self.collision_sprites, self.scale)
        

    def main(self):
        while self.running:
            key_pressed = pygame.key.get_pressed()
            
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.player.handle_keys(key_pressed, self.camera, (self.inimigos_grupo, self.all_sprites))
            self.player.sprite.update()
            self.camera.update(self.player, self.map_height, self.map_width, self.scale)
            self.screen.fill((0, 0, 0))
            
            
            #draw_map_tiles(self.screen, self.tmx_data, self.scale, self.camera)
            self.sala.draw(self.screen, self.tmx_data, self.scale, self.camera)
            
            self.all_sprites.draw(self.player, self.camera) #player e inimigos estao aqui
            self.ui.draw(self.screen)

            self.player.update_damage_numbers()
            self.player.draw_damage_numbers(self.screen, self.camera)

            self.damage_numbers = [dn for dn in self.damage_numbers if dn.update()]
            for damage_number in self.damage_numbers:
                damage_number.draw(self.screen, self.camera) 

            if key_pressed[pygame.K_t]:
                self.ui.health = 100
                self.player.health = 100
            
            if key_pressed[pygame.K_h]:
                self.sala.portas = (self.sala.portas+1)%2

            for inimigo in self.inimigos_grupo:
                #inimigo.draw(self.screen, self.camera)
                inimigo.sprite.update()
                inimigo.movement(self.player.sprite.x, self.player.sprite.y)
                inimigo.update_damage_numbers()
                inimigo.draw_damage_numbers(self.screen, self.camera)
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


        pygame.quit()

if __name__ == '__main__':
    jogo = Game()
    #jogo.setup_base()
    jogo.setup_salas()
    jogo.main()
    
