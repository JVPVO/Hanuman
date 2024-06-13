import pygame
from player import *

class HealthBar():
    def __init__():
        #resolution = pygame.display.get_window_size()
        path = "assets/ui/health-bar/"
        healthbars = []
        nullbars = []
        for i in range(1,4):
            healthbars.append(Animation(image_file=f"{path}{i}.png", total_frames=1, frame_height=16, frame_width=16))
            nullbars.append(Animation(image_file=f"{path}{i+6}.png", total_frames=1, frame_height=16, frame_width=16))
        for tile in healthbars:
            tile.x = 0 + 50
            tile.y = 200
        for tile in nullbars:
            tile.x = 0 + 50
            tile.y = 200