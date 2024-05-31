import pygame
import math
from pygame.math import Vector2

pygame.init()
screen = pygame.display.set_mode((800, 600))
font = pygame.font.Font(pygame.font.get_default_font(), 20)

# A sprite group with a single sprite (sad)
sprites = pygame.sprite.Group()

# Circle as a sprite
r = 100
center = (400, 300)
circle = pygame.sprite.Sprite()
circle.image = pygame.surface.Surface((2 * r, 2 * r), pygame.SRCALPHA)
pygame.draw.circle(circle.image, "#ffaa33", (r, r), r, 1)
circle.rect = circle.image.get_rect(center=center)
sprites.add(circle)

# function for drawing lines
def line(point1, point2, color, surface=screen):
    pygame.draw.line(surface, color, point1, point2)


# function for rendering some text
def text(string, pos, surface=screen):
    surface.blit(font.render(string, True, "#ffffff"), pos)


def tangents_points(p, c, r):
    """Finds the points that define tangents to a circle
    of radius r and center c, passing through point p"""

    # translate center to origin
    # center C -> O = (0,0)
    # point P -> P0 = (x0, y0)
    p0 = Vector2(p) - Vector2(c)

    # distance between the center and the point
    d0 = p0.magnitude()
    
    # if p is inside the circle then there are no tangents and we exit the function
    if d0 < r:
        return c, c
    
    # distance between p0 and the tangent points
    dt = math.sqrt(d0**2 - r**2)

    # points on the circle
    t1 = c + (r**2 / d0**2) * p0 + (r * dt) / d0**2 * p0.rotate(90)
    t2 = c + (r**2 / d0**2) * p0 - (r * dt) / d0**2 * p0.rotate(90)

    return t1, t2


def vertex_angle(a, b, c):
    """Finds angle between lines ab and bc"""
    vec1 = Vector2(a) - Vector2(b)
    vec2 = Vector2(c) - Vector2(b)
    return vec1.angle_to(vec2) % 360


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Find points required for our drawings
    mouse_pos = pygame.mouse.get_pos()
    t1, t2 = tangents_points(p=mouse_pos, c=center, r=r)
    
    # angle between the tangent lines
    angle = vertex_angle(t1,mouse_pos,t2)

    # Clear screen
    screen.fill("#101005")

    # Draw a circle
    sprites.draw(screen)

    # draw line from center to mouse
    line(mouse_pos, center, "#1020ff")
    # draw lines from mouse to tangent points
    line(mouse_pos, t1, "#aa4444")
    line(mouse_pos, t2, "#aa4444")

    # display the angle
    text(f'Angle = {angle:.1f} degrees.', (10,10))

    pygame.display.flip()
    
# good bye
pygame.quit()