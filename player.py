import pygame

from animated_character import AnimatedCharacter
from collision_area import CollisionArea

class Player(AnimatedCharacter):
    IDLE = "idle"
    WALKING = "walking"

    def __init__(self, pos_x, pos_y, collision_area_width, collision_area_height):
        super().__init__()

        self.state = self.IDLE

        self.facing_direction = "down"

        self.get_animations()

        self.current_animation = "idle"

        self.set_image(pos_x, pos_y)

        self.collision_area = CollisionArea(self, collision_area_height, collision_area_height)

        self.position = pygame.Vector2(pos_x, pos_y)

        self.speed = 240

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

        self.direction = pygame.Vector2(
            keys[pygame.K_d] - keys[pygame.K_a],
            keys[pygame.K_s] - keys[pygame.K_w]
        )

        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()
            self.state = self.WALKING

            if abs(self.direction.x) > abs(self.direction.y):
                self.facing_direction = (
                    "right" if self.direction.x > 0 else "left"
                )
            else:
                self.facing_direction = (
                    "down" if self.direction.y > 0 else "up"
                )

            self.position += self.direction * self.speed * delta_time

            self.rect.topleft = (
                round(self.position.x),
                round(self.position.y)
            )
        else:
            self.state = self.IDLE

        self.collision_area.update()
        self.update_animation()
        
        super().update(delta_time)

    def update_animation(self):
        match (self.state):
            case Player.IDLE:
                self.current_animation = "idle"
            case Player.WALKING:
                self.current_animation = f"walk_{self.facing_direction}"
