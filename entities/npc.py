
import pygame
from systems.animation import Animation


class NPC(pygame.sprite.Sprite):

    def __init__(
        self,
        npc_id,
        position,
        sprite_path,
        dialogue_id,
        frame_width=48,
        frame_height=64,
        frame_count=8,
        scale=4,
        interaction_radius=60
    ):
        super().__init__()

        self.npc_id = npc_id
        self.dialogue_id = dialogue_id
        self.position = pygame.Vector2(position)
        self.interaction_radius = interaction_radius

        self.animation = Animation("idle")

        self.animation.animations = {
            "idle": self.animation.get_sprites_from_spritesheet(
                path=sprite_path,
                frame_width=frame_width,
                frame_height=frame_height,
                frame_count=frame_count,
                scale=scale
            )
        }

        self.animation.set_image()

        self.image = self.animation.image
        self.rect = self.image.get_rect(
            center=(
                round(self.position.x),
                round(self.position.y)
            )
        )

    def update(self, delta_time):
        # O NPC não se desloca, apenas anima.
        self.animation.update(delta_time)

        self.image = self.animation.image

        self.rect = self.image.get_rect(
            center=(
                round(self.position.x),
                round(self.position.y)
            )
        )

    def can_interact(self, player):
        distance = self.position.distance_to(player.position)

        return distance <= self.interaction_radius
