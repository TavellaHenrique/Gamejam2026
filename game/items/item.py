import pygame

from game.systems.trigger import Trigger


class Item:
    """Representa um item colecionável do mundo com interação por proximidade."""

    def __init__(
        self,
        item_id,
        name,
        description="",
        image=None,
        image_path=None,
        position=(0, 0),
        interaction_radius=40,
        world_image_size=None,
    ):
        self.id = item_id
        self.item_id = item_id
        self.name = name
        self.description = description
        self.image = image
        self.image_path = image_path
        self.position = pygame.Vector2(position)
        self.interaction_radius = interaction_radius
        self.interaction_trigger = Trigger(
            position=self.position,
            radius=self.interaction_radius,
        )
        self.collected = False
        self.visible = True

        if self.image is None and self.image_path is not None:
            try:
                self.image = pygame.image.load(self.image_path).convert_alpha()
            except (FileNotFoundError, pygame.error):
                self.image = None

        self.world_image = self.image
        if self.image is not None and world_image_size is not None:
            self.world_image = pygame.transform.scale(
                self.image,
                world_image_size,
            )

    def update(self):
        """Sincroniza a área de interação com a posição do item."""
        self.interaction_trigger.position.update(self.position)

    def can_interact(self, player):
        """Indica se o jogador está dentro da área de coleta do item."""
        if self.collected or not self.visible:
            return False
        return self.interaction_trigger.contains(player)

    def pick_up(self, player):
        """Coleta o item e o adiciona ao inventário do jogador."""
        if self.collected or not self.visible:
            return False
        if not self.can_interact(player):
            return False

        if player.inventory.add_item(self):
            self.collected = True
            self.visible = False
            return True
        return False

    def draw(self, screen, color=(245, 220, 120), text_color=(255, 255, 255)):
        """Desenha o item. Se não houver sprite, usa um círculo visível como debug."""
        if not self.visible:
            return

        if self.world_image is not None:
            rect = self.world_image.get_rect(
                center=(round(self.position.x), round(self.position.y))
            )
            screen.blit(self.world_image, rect)
            return

        pygame.draw.circle(
            screen,
            color,
            (round(self.position.x), round(self.position.y)),
            round(self.interaction_radius),
            width=2,
        )
        pygame.draw.circle(
            screen,
            (245, 220, 120),
            (round(self.position.x), round(self.position.y)),
            max(6, round(self.interaction_radius * 0.3)),
            width=0,
        )

        font = pygame.font.Font(None, 18)
        label = font.render(self.name, True, text_color)
        screen.blit(
            label,
            (
                round(self.position.x) - label.get_width() // 2,
                round(self.position.y) - self.interaction_radius - 20,
            ),
        )