import pygame

class Menu():
    window_width, window_height = pygame.display.get_window_size()
    rect_width = window_width * 0.7
    rect_height = window_height * 0.1
    rect_x = (window_width - rect_width) / 2
    rect_y = window_height - rect_height
    #Outline
    outline = pygame.Rect()
    #Interior