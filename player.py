import pygame

from animated_character import AnimatedCharacter
from character_collision import CharacterCollision

class Player(AnimatedCharacter, CharacterCollision):
    IDLE = "idle"
    WALKING = "walking"

    def __init__(self, pos_x, pos_y, collision_area_width, collision_area_height):
        super().__init__()

        self.state = self.IDLE

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
            "walk_up":
                self.get_sprites_from_sheet(
                    path="assets/character/The Female Adventurer - Free/Walk/walk_Up.png",
                    frame_width = 48,
                    frame_height = 64,
                    frame_count = 8,
                    scale = 4
                ),
            "walk_down":
                self.get_sprites_from_sheet(
                    path="assets/character/The Female Adventurer - Free/Walk/walk_Down.png",
                    frame_width = 48,
                    frame_height = 64,
                    frame_count = 8,
                    scale = 4
                ),
            "walk_left":
                self.get_sprites_from_sheet(
                    path="assets/character/The Female Adventurer - Free/Walk/walk_Left_Down.png",
                    frame_width = 48,
                    frame_height = 64,
                    frame_count = 8,
                    scale = 4
                ),
            "walk_right":
                self.get_sprites_from_sheet(
                    path="assets/character/The Female Adventurer - Free/Walk/walk_Right_Down.png",
                    frame_width = 48,
                    frame_height = 64,
                    frame_count = 8,
                    scale = 4
                )
        }
    
    def update(self, delta_time):
        keys = pygame.key.get_pressed()

        if (
            keys[pygame.K_a] or
            keys[pygame.K_d] or
            keys[pygame.K_s] or
            keys[pygame.K_w]
        ):
            self.state = self.WALKING

            if keys[pygame.K_a]:
                self.rect.x -= self.speed
                self.facing_direction = "left"
            if keys[pygame.K_d]:
                self.rect.x += self.speed
                self.facing_direction = "right"
            if keys[pygame.K_s]:
                self.rect.y += self.speed
                self.facing_direction = "down"
            if keys[pygame.K_w]:
                self.rect.y -= self.speed
                self.facing_direction = "up"

        else:
            self.state = self.IDLE

        self.update_collision_area()
        self.update_animation()
        super().update(delta_time)

    def update_animation(self):
        match (self.state):
            case Player.IDLE:
                self.current_animation = "idle"
            case Player.WALKING:
                self.current_animation = f"walk_{self.facing_direction}"