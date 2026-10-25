import pygame

from game.entities.door import Door


class Elevator:
    """Elevador que abre uma lista de destinos navegável pelo teclado."""

    def __init__(self, rect, destinations):
        self.door = Door(
            rect=rect,
            prompt="escolher destino",
            color=(105, 115, 125),
            interaction_margin=72,
            visible=True,
        )
        self.destinations = tuple(destinations)
        self.is_open = False
        self.selected_index = 0
        self.font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            22,
        )
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            30,
        )
        panel_height = (
            72
            + len(self.destinations) * 46
            + max(0, len(self.destinations) - 1) * 12
            + 46
        )
        self.panel = pygame.Rect(0, 0, 440, panel_height)

    @property
    def rect(self):
        return self.door.rect

    def can_interact(self, player):
        return self.door.can_interact(player)

    def handle_event(self, event, player):
        """Retorna (consumido, destino) ao abrir ou escolher uma opção."""
        if self.is_open:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_index = (
                        self.selected_index - 1
                    ) % len(self.destinations)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_index = (
                        self.selected_index + 1
                    ) % len(self.destinations)
                elif event.key == pygame.K_e:
                    self.is_open = False
                    destination, _ = self.destinations[self.selected_index]
                    if destination == "cancel":
                        return True, None
                    return True, destination
            return True, None

        if (
            # Somente um evento de tecla pode abrir o menu.
            event.type == pygame.KEYDOWN
            # A tecla E é o comando para usar o elevador.
            and event.key == pygame.K_e
            # O jogador precisa estar dentro da área de interação.
            and self.can_interact(player)
        ):
            self.is_open = True
            self.selected_index = 0
            return True, None
        return False, None

    def draw_world(self, world, player):
        self.door.draw(world, player)

    def draw_menu(self, screen):
        if not self.is_open:
            return

        screen_width, screen_height = screen.get_size()
        self.panel.center = (screen_width // 2, screen_height // 2)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (30, 38, 48), self.panel)
        pygame.draw.rect(screen, (225, 205, 155), self.panel, width=3)

        title = self.title_font.render(
            "Elevador - escolha o destino",
            True,
            (255, 255, 255),
        )
        screen.blit(title, title.get_rect(midtop=(self.panel.centerx, self.panel.top + 16)))
        button_height = 46
        button_gap = 12
        button_width = self.panel.width - 48
        first_y = self.panel.top + 72
        for index, (_, label) in enumerate(self.destinations):
            button = pygame.Rect(
                self.panel.left + 24,
                first_y + index * (button_height + button_gap),
                button_width,
                button_height,
            )
            is_selected = index == self.selected_index
            fill_color = (
                (105, 126, 145) if is_selected else (72, 91, 108)
            )
            outline_color = (
                (255, 225, 145) if is_selected else (205, 215, 220)
            )
            pygame.draw.rect(screen, fill_color, button)
            pygame.draw.rect(screen, outline_color, button, width=2)
            text = self.font.render(label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=button.center))

        hint = self.font.render(
            "↑/↓ selecionar   E confirmar",
            True,
            (205, 215, 220),
        )
        screen.blit(
            hint,
            hint.get_rect(midbottom=(self.panel.centerx, self.panel.bottom - 10)),
        )
