
import pygame

class CollisionArea:
    def __init__(self, body: pygame.sprite.Sprite, width, height):
        self.body = body

        self.rect = pygame.Rect(
            0,
            0,
            width,
            height
        )
        self.rect.center = self.body.rect.center

    def update(self):
        self.rect.center = self.body.rect.center

    def show(self, screen, color: pygame.Color):
        pygame.draw.rect(screen, color, self.rect, 2)
        pygame.draw.circle(screen, color, self.rect.center, 5)
