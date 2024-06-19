import pygame
from pygame.sprite import Group
from settings import camadas_obj_mundo
from player import Player
from inimigos import Skeleton


class AllSprites(pygame.sprite.Group):
    def __init__(self, window_widith, window_height):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.window_widith = window_widith
        self.window_height = window_height


		
    def draw(self, player, camera):

        bg_sprites = [sprite for sprite in self if sprite.camada < camadas_obj_mundo['main']]
        main_sprites = sorted([sprite for sprite in self if sprite.camada == camadas_obj_mundo['main']]+[player], key = lambda sprite: sprite.y_sort)
        fg_sprites = [sprite for sprite in self if sprite.camada > camadas_obj_mundo['main']]

        for layer in (bg_sprites, main_sprites, fg_sprites):
            for sprite in layer:
                if isinstance(sprite, Player) or isinstance(sprite, Skeleton):
                    sprite.draw(self.display_surface, camera)
                else:
                    self.display_surface.blit(sprite.image, camera.apply(pygame.Rect(sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rect.height)))
        
		
class Objects(pygame.sprite.Sprite):
    def __init__(self, pos, image, groups, camada=camadas_obj_mundo['main']):
        super().__init__(groups)
        self.image = image # pygame.image.load(image).convert_alpha()
        self.camada = camada
        self.rect = self.image.get_rect(topleft = pos)
        self.y_sort = self.rect.y + 0.85*self.rect.height
        self.hitbox = pygame.Rect(self.rect.x+(self.rect.width*0.6/2), self.rect.y+self.rect.height*0.6, self.rect.width*0.6, self.rect.height*0.4)
        #nao vou usar esse hitbox por enquanto, só quando precisar de colisão dinamica (e isso em cima talvez um inflate fica melhor)

class Barrier(Objects):
    def __init__(self, pos, image, groups, camada=camadas_obj_mundo['main']):
        super().__init__(pos, image, groups, camada)
        self.hitbox = self.rect.copy()