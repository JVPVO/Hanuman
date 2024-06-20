import pygame
from animation_Wip import *
from typing import List

class HealthBar():
    def __init__(self):
        #resolution = pygame.display.get_window_size()
        path = "assets/ui/health-bar/"
        self.healthbars = []
        self.nullbars = []
        self.health = 3
        initial_scale = 6
        #faz cada barrinha
        for i in range(1,4):
            self.healthbars.append(Animation(image_file=f"{path}{i}.png", total_frames=1, frame_height=16, frame_width=16))
            self.nullbars.append(Animation(image_file=f"{path}{i+6}.png", total_frames=1, frame_height=16, frame_width=16))
        self.healthbars: List[Animation]
        self.nullbars: List[Animation]
        #faz os rects para cada barrinha
        for idx, tile in enumerate(self.healthbars):
            tile.x = -6+(idx*96)
            tile.y = 1080 - 200
            tile.rect = pygame.Rect(tile.x, tile.y, 16, 16)
            tile.image = pygame.transform.scale_by(tile.image, initial_scale)
            tile.rect.width = int(16 * initial_scale) 
            tile.rect.height = int(16 * initial_scale) 
        for idx, tile in enumerate(self.nullbars):
            tile.x = -6+(idx*96)
            tile.y = 1080 - 200
            tile.rect = pygame.Rect(tile.x, tile.y, 16, 16)
            tile.image = pygame.transform.scale_by(tile.image, initial_scale)
            tile.rect.width = int(16 * initial_scale) 
            tile.rect.height = int(16 * initial_scale) 
    def draw(self, surface:pygame.Surface):
        for i in range(self.health):
            tile = self.healthbars[i]
            surface.blit(tile.image, (tile.x, tile.y))
        blocos =  3 - self.health 
        if blocos != 0:
            for i in range(blocos):
                tile = self.nullbars[-i]
                surface.blit(tile.image, (tile.x, tile.y))
        elif self.health == 0:
            for i in range(len(self.nullbars)):
                tile = self.nullbars[i]
                surface.blit(tile.image, (tile.x, tile.y))

        