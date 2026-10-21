"""Representa uma porta visível com uma área de interação invisível."""

import pygame

from systems.trigger import Trigger


class Door:
    """Desenha uma porta e indica quando o jogador pode usá-la."""

    def __init__(self, rect, prompt, color=(120, 72, 36), interaction_margin=48):
        """Configura o retângulo visível e a área ampliada para interação."""
        self.rect = pygame.Rect(rect)
        self.interaction_rect = self.rect.inflate(
            interaction_margin * 2,
            interaction_margin * 2,
        )
        self.interaction_trigger = Trigger(rect=self.interaction_rect)
        self.prompt = prompt
        self.color = color
        self.font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            20,
        )

    def can_interact(self, player):
        """Retorna True quando o centro do jogador entra na área da porta."""
        return self.interaction_trigger.contains(player)

    def draw(self, screen, player):
        """Desenha o bloco opaco marrom, detalhes simples e o aviso de interação."""
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

        text = self.font.render(
            f"E - {self.prompt}",
            True,
            (255, 255, 255),
        )
        text_rect = text.get_rect(
            midbottom=(self.rect.centerx, self.rect.top - 8)
        )
        background_rect = text_rect.inflate(16, 10)
        background = pygame.Surface(
            background_rect.size,
            pygame.SRCALPHA,
        )
        background.fill((20, 24, 32, 210))
        screen.blit(background, background_rect.topleft)
        screen.blit(text, text_rect)
