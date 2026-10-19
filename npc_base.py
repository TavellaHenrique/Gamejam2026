
import pygame

from animated_character import AnimatedCharacter
from character_collision import CharacterCollision

class NonPlayableCharacter(AnimatedCharacter, CharacterCollision):
    def __init__(self, pos_x, pos_y, collision_area_width, collision_area_height):
        super().__init__()
    
        self.facing_direction = "down"
    
        self.get_animations()
    
        self.current_animation = "idle"
    
        self.set_image(pos_x, pos_y)

        self.set_collision_area(collision_area_width, collision_area_height)

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