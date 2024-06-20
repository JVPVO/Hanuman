import pygame
from animation_Wip import *

class HealthBar:
    def __init__(self):
        path = "assets/ui/health-bar/"
        initial_scale = 6
        y_position = 1080 - 200
        
        # Load and scale the empty health bar
        self.empty_bar = self.load_and_scale_image(f"{path}Empty.png", initial_scale, y_position)
        
        # Load and scale the full health bar
        self.full_bar = self.load_and_scale_image(f"{path}Full.png", initial_scale, y_position)

        self.max_health = 100
        self.health = 100

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

    def draw(self, surface: pygame.Surface):
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
