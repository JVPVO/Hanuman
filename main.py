#TODO Colisão
#TODO implementar deltatime
#TODO implementar deltatime

from inimigos import *
from mapa_WIP import *
import pygame
from camera import Camera
from player import Player


#FUNÇÃO MAIS IMPORTANTE DA NOSSA VIDA, RENDERIZA O PERSONAGEM COM A CÂMERA E É GLOBAL ENTÃO NÃO PRECISA BOTAR PRA TODA HORA                    
def draw(self, surface:pygame.Surface, camera):
        surface.blit(self.sprite.image, camera.apply(pygame.Rect(self.sprite.x, self.sprite.y, self.rect.width, self.rect.height)))
def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))

    # Carregue seu mapa TMX aqui
    tmx_data = load_map('assets/base.tmx')

    map_width = tmx_data.width * tmx_data.tilewidth
    map_height = tmx_data.height * tmx_data.tileheight
    # Defina o fator de escala (por exemplo, 2 para dobrar o tamanho)
    scale = 3
    player = Player(100, 100, scale)
    camera = Camera(1920,1080) #tem que botar a msm resolucao da tela pro jogador ficar no meio da tela

    #Lista de inimigos para serem renderizados e removidos da tela quando necessário, TODO trocar por um sprite group
    inimigos = []
    #espada = Weapon(70, 30, scale)
    # Main game loop
    running = True
    while running:
        key_pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.handle_keys(key_pressed, camera, inimigos)
        player.sprite.update()
        camera.update(player, map_height, map_width, scale)

        screen.fill((0, 0, 0))
        draw_map(screen, tmx_data, scale, camera)
        player.draw(screen, camera)
        for inimigo in inimigos:
            inimigo.draw(screen, camera)
            inimigo.sprite.update()
            inimigo.movement(player.sprite.x, player.sprite.y)
            for i in range(len(player.weapon[player.selected_weapon].shoot)):
                if inimigo.colisao(player.weapon[player.selected_weapon].shoot[i]):
                    inimigos.remove(inimigo)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
    
