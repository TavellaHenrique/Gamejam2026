
import pygame

from systems.animation import Animation
from systems.inventory import Inventory

class Player(pygame.sprite.Sprite):

    ANIMATION_8_DIRECTIONS = "8_directions"
    ANIMATION_5_DIRECTIONS = "5_directions"

    def __init__(
        self,
        position,
        speed=180,
        animation_mode=ANIMATION_8_DIRECTIONS
    ):
        self.position = pygame.Vector2(position)
        self.speed = speed

        self.animation_mode = animation_mode
        self.animation = Animation("idle")

        self.facing = pygame.Vector2(0, 1)

        self.get_animations()

        self.animation.set_image()

        self.image = self.animation.image
        self.rect = self.image.get_rect(
            center=(
                round(self.position.x),
                round(self.position.y)
            )
        )

        self.inventory = Inventory()

    def update(self, delta_time):
        # Calcula movimentação
        self.move(delta_time)

        # Seleciona animação correspondente
        self.update_player_animation(delta_time)

        # Atualiza quadro da animação
        self.animation.update(delta_time)

        # Sincroniza imagem e retângulo com a posição atual
        self.image = self.animation.image
        self.rect = self.image.get_rect(
            center=(
                round(self.position.x),
                round(self.position.y)
            )
        )

    def move(self, delta_time):
        keys = pygame.key.get_pressed()

        direction = pygame.Vector2(
            keys[pygame.K_d] - keys[pygame.K_a],
            keys[pygame.K_s] - keys[pygame.K_w]
        )

        if direction.length_squared() > 0:
            direction = direction.normalize()
            
            self.position += direction * self.speed * delta_time
            self.facing = direction

        self.rect.center = (
            round(self.position.x),
            round(self.position.y)
        )

    def update_player_animation(self, delta_time):
        keys = pygame.key.get_pressed()

        moving = any((
            keys[pygame.K_w],
            keys[pygame.K_a],
            keys[pygame.K_s],
            keys[pygame.K_d]
        ))

        if self.animation_mode == self.ANIMATION_8_DIRECTIONS:
            self.animate_8_directions(moving)
        elif self.animation_mode == self.ANIMATION_5_DIRECTIONS:
            self.animate_5_directions(moving)

    def animate_8_directions(self, moving):
        x = round(self.facing.x)
        y = round(self.facing.y)
        direction = self.get_direction_name(x, y)
        prefix = "walk" if moving else "idle"
        self.set_animation(f"{prefix}_{direction}")

    def animate_5_directions(self, moving):
        if not moving:
            self.set_animation("idle")
            return
        x = self.facing.x
        y = self.facing.y
        if abs(x) > abs(y):
            direction = "right" if x > 0 else "left"
        else:
            direction = "down" if y > 0 else "up"
        self.set_animation(f"walk_{direction}")

    @staticmethod
    def get_direction_name(x, y):
        directions = {
            (0, -1): "up",
            (0, 1): "down",
            (-1, 0): "left",
            (1, 0): "right",
            (-1, -1): "up_left",
            (1, -1): "up_right",
            (-1, 1): "down_left",
            (1, 1): "down_right"
        }

        return directions.get((x, y), "down")

    def set_animation(self, animation_name):
        if animation_name == self.animation.current_animation:
            return

        self.animation.play(animation_name)
    
    def get_animations(self):
        base_path = "assets/sprites/player/TheFemaleAdventurer"

        frame_settings = {
            "frame_width": 48,
            "frame_height": 64,
            "frame_count": 8,
            "scale": 4
        }

        def load_animation(path):
            return self.animation.get_sprites_from_spritesheet(
                path=f"{base_path}/{path}",
                **frame_settings
            )

        self.animation.animations = {
            # -- Idle --
            "idle": load_animation("Idle/Idle_Down.png"),
            "idle_up": load_animation("Idle/Idle_Up.png"),
            "idle_down": load_animation("Idle/Idle_Down.png"),
            "idle_left": load_animation("Idle/Idle_Left_Down.png"),
            "idle_right": load_animation("Idle/Idle_Right_Down.png"),
            "idle_up_left": load_animation("Idle/Idle_Up.png"),
            "idle_up_right": load_animation("Idle/Idle_Up.png"),
            "idle_down_left": load_animation("Idle/Idle_Left_Down.png"),
            "idle_down_right": load_animation("Idle/Idle_Right_Down.png"),

            # -- Walk --
            "walk_up": load_animation("Walk/walk_Up.png"),
            "walk_down": load_animation("Walk/walk_Down.png"),
            "walk_left": load_animation("Walk/walk_Left_Down.png"),
            "walk_right": load_animation("Walk/walk_Right_Down.png"),
            "walk_up_left": load_animation("Walk/walk_Left_Up.png"),
            "walk_up_right": load_animation("Walk/walk_Right_Up.png"),
            "walk_down_left": load_animation("Walk/walk_Left_Down.png"),
            "walk_down_right": load_animation("Walk/walk_Right_Down.png"),
        }