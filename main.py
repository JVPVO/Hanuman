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

        

        # Main game loop
        self.running = True
        

        self.all_sprites = AllSprites(self.screen.get_width(), self.screen.get_height())
        self.collision_sprites = pygame.sprite.Group()
        #Grupo de inimigos para serem renderizados e removidos da tela quando necessário
        self.inimigos_grupo = pygame.sprite.Group()

    def setup(self):
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
            draw_map_tiles(self.screen, self.tmx_data, self.scale, self.camera)
            
            self.all_sprites.draw(self.player, self.camera) #player e inimigos estao aqui
            
            self.all_sprites.draw(self.player, self.camera)
            for inimigo in self.inimigos_grupo:
                #inimigo.draw(self.screen, self.camera)
                inimigo.sprite.update()
                inimigo.movement(self.player.sprite.x, self.player.sprite.y)
                for i in range(len(self.player.weapon[self.player.selected_weapon].shoot)):
                    if inimigo.colisao(self.player.weapon[self.player.selected_weapon].shoot[i]):
                        inimigo.kill()

            pygame.display.flip()

        pygame.quit()

if __name__ == '__main__':
    jogo = Game()
    jogo.setup()
    jogo.main()
    
