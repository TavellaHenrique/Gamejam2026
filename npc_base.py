
import pygame

from animated_character import AnimatedCharacter
from collision_area import CollisionArea

class NonPlayableCharacter(AnimatedCharacter):
    def __init__(self, pos_x, pos_y, collision_area_width, collision_area_height):
        super().__init__()
    
        self.facing_direction = "down"
    
        self.get_animations()
    
        self.current_animation = "idle"
    
        self.set_image(pos_x, pos_y)

        self.collision_area = CollisionArea(self, collision_area_width, collision_area_height)

        interaction_area_width = 100
        interaction_area_height = 100

        self.interaction_area = pygame.Rect(
            0,
            0,
            interaction_area_width,
            interaction_area_height
        )
        self.interaction_area.center = self.rect.center

    def update(self, delta_time):
        self.update_interaction_area()
        super().update(delta_time)

    def update_interaction_area(self):
        self.interaction_area.center = self.rect.center

    def show_interaction_area(self, screen, color):
        pygame.draw.rect(screen, color, self.interaction_area, 2)

    def get_animations(self):
        self.animations = {
            "idle":
                self.get_sprites_from_sheet(
                    path="assets/character/The Female Adventurer - Free/Idle/Idle_Down.png",
                    frame_width = 48,
                    frame_height = 64,
                    frame_count = 8,
                    scale = 4
                ),
        }