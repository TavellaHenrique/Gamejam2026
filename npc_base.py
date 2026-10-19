
import pygame

from character_base import CharacterBase

class NonPlayableCharacter(CharacterBase):
    def __init__(self, x, y):
        super().__init__()
    
        self.facing_direction = "down"
    
        self.get_animations()
    
        self.current_animation = "idle"
    
        self.set_image(x, y)

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