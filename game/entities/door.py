"""Representa uma porta visível com uma área de interação invisível."""

import pygame

from game.systems.trigger import Trigger
from game.ui.text import draw_prompt


class Door:
    """Desenha uma porta e indica quando o jogador pode usá-la."""

    def __init__(
        self,
        rect,
        prompt,
        color=(120, 72, 36),
        interaction_margin=48,
        visible=True,
    ):
        """Configura o retângulo visível e a área ampliada para interação."""
        self.rect = pygame.Rect(rect)
        self.interaction_rect = self.rect.inflate(
            interaction_margin * 2,
            interaction_margin * 2,
        )
        self.interaction_trigger = Trigger(rect=self.interaction_rect)
        self.prompt = prompt
        self.color = color
        self.visible = visible
        self.font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            20,
        )

    def can_interact(self, player):
        """Retorna True quando o centro do jogador entra na área da porta."""
        return self.interaction_trigger.contains(player)

    def draw(self, screen, player):
        """Desenha o bloco opaco marrom, detalhes simples e o aviso de interação."""
        if self.visible:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, (65, 38, 22), self.rect, width=4)

            knob_rect = pygame.Rect(
                self.rect.right - 16,
                self.rect.centery - 4,
                8,
                8,
            )
            pygame.draw.rect(screen, (220, 180, 70), knob_rect)

        if not self.can_interact(player):
            return

        draw_prompt(
            screen,
            f"E - {self.prompt}",
            self.font,
            position=(self.rect.centerx, self.rect.top - 8),
            align="midbottom",
        )
