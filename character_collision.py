
import pygame

class CharacterCollision:
    def __init__(self):
        self.collision_area: pygame.Rect = None
        self.rect: pygame.Rect = None

    def set_collision_area(self, collision_area_width, collision_area_height):
        self.collision_area = pygame.Rect(
            0, 0,
            collision_area_width,
            collision_area_height
        )
        self.collision_area.center = self.rect.center

    def update_collision_area(self):
        self.collision_area.center = self.rect.center

    def show_collision_area(self, screen, color: pygame.Color):
        pygame.draw.rect(screen, color, self.collision_area, 2)
        pygame.draw.circle(screen, color, self.rect.center, 5)
