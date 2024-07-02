import pygame
import time
from animation_Wip import *

class HealthBar:
    def __init__(self):
        path = "assets/ui/health-bar/"
        initial_scale = 6
        self.scale = 3
        y_position = 1080 - 200
        
        # Load and scale the empty health bar
        self.empty_bar = self.load_and_scale_image(f"{path}Empty.png", initial_scale, y_position)
        
        # Load and scale the full health bar
        self.full_bar = self.load_and_scale_image(f"{path}Full.png", initial_scale, y_position)

        self.max_health = 100
        self.health = 100

        self.display = pygame.display.get_surface()

    def load_and_scale_image(self, image_file, scale, y_position):
        """Helper function to load and scale an image"""
        animation = Animation(image_file=image_file, total_frames=1, frame_height=16, frame_width=48)
        animation.x = 0
        animation.y = y_position
        animation.rect = pygame.Rect(animation.x, animation.y, 48, 16)
        animation.image = pygame.transform.scale_by(animation.image, scale)
        animation.rect.width = int(48 * scale)
        animation.rect.height = int(16 * scale)
        return animation

    def draw(self):
        surface = self.display
        """Draw the health bar on the given surface"""
        # Calculate the new width of the full health bar
        new_width = int((self.health / self.max_health) * self.full_bar.rect.width)
        if new_width < 0:
            new_width = 0
        # Create a subsurface of the full bar image to represent the current health
        current_health_image = pygame.transform.scale(self.full_bar.image, (new_width, self.full_bar.rect.height))
        
        # Draw the empty health bar
        surface.blit(self.empty_bar.image, (self.empty_bar.x, self.empty_bar.y))
        
        # Draw the full health bar scaled to the current health
        surface.blit(current_health_image, (self.full_bar.x, self.full_bar.y))

        # Faz um número na health bar
        font = pygame.font.Font(None, 48)
        image = font.render(f"{self.health}/{self.max_health}", True, (255,255,255))
        surface.blit(image, dest=(int(48*self.scale/2), int(887+(16*self.scale/2))))

class DamageNumber:
    def __init__(self, x, y, damage, duration=1.5, speed=1, color=(255, 0, 0), font_size=32):
        self.x = x
        self.y = y
        self.damage = damage
        self.duration = duration
        self.speed = speed
        self.color = color
        self.start_time = time.time()
        self.font = pygame.font.Font(None, font_size)
        self.image = self.font.render(str(damage), True, self.color)
        self.rect = self.image.get_rect(center=(self.x, self.y))

        self.display = pygame.display.get_surface()

    def update(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time < self.duration:
            self.y -= self.speed
            self.rect.y = self.y
        else:
            return False  # Signal that the damage number should be removed
        return True

    def draw(self, desvio):
        surface = self.display

        surface.blit(self.image, self.rect.topleft + desvio)

class Minimap:
    def __init__(self, mapa):
        self.pos = [-1,-1]
        self.tile_size = 16
        self.offset = (10,10)
        matriz = mapa
        self.room_img = pygame.image.load("assets/ui/map/room.png").convert_alpha()
        self.path_img = pygame.image.load("assets/ui/map/room.png").convert_alpha()
        self.room_img = pygame.transform.scale(self.room_img, (16, 16))
        self.path_img = pygame.transform.scale(self.path_img, (16,16))
        for l in range(len(matriz)):
            for c in range(len(matriz[l])):
                if matriz[l][c] != None:
                    matriz[l][c] = matriz[l][c].tipo
                else:
                    matriz[l][c] = 0
        self.mapa = matriz
    def updateMinimap(self, posicao):
        pos_atual = [posicao[0], posicao[1]]
        if self.pos != pos_atual:
            self.pos = pos_atual
            x, y = posicao[0], posicao[1]
            print("Changed rooms")

    def render(self, screen):
        minimap_width = len(self.mapa[0]) * self.tile_size
        minimap_height = len(self.mapa) * self.tile_size
        start_x = screen.get_width() - minimap_width - self.offset[0]
        start_y = self.offset[1]

        for linha in range(len(self.mapa)):
            for coluna in range(len(self.mapa[linha])):
                tile_x = start_x + coluna * self.tile_size
                tile_y = start_y + linha * self.tile_size
                if self.mapa[linha][coluna] > 0:
                    screen.blit(self.room_img, (tile_x, tile_y))
