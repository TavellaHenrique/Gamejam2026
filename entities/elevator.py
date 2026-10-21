import pygame

from entities.door import Door


class Elevator:
    """Porta de elevador que abre uma lista clicável de destinos."""

    def __init__(self, rect, destinations):
        self.door = Door(
            rect=rect,
            prompt="escolher destino",
            color=(105, 115, 125),
        )
        self.destinations = tuple(destinations)
        self.is_open = False
        self.font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            22,
        )
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            30,
        )
        self.panel = pygame.Rect(0, 0, 440, 280)
        self.buttons = []

    @property
    def rect(self):
        return self.door.rect

    def can_interact(self, player):
        return self.door.can_interact(player)

    def handle_event(self, event, player):
        """Retorna (consumido, destino) ao abrir ou escolher uma opção."""
        if not self.is_open:
            if (
                # Somente um evento de tecla pode abrir o menu.
                event.type == pygame.KEYDOWN
                # A tecla E é o comando para usar o elevador.
                and event.key == pygame.K_e
                # O jogador precisa estar dentro da área de interação.
                and self.can_interact(player)
            ):
                self.is_open = True
                return True, None
            return False, None

        # Só o evento de tecla Escape fecha o menu por teclado.
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
        ):
            self.is_open = False
            return True, None

        # Só cliques do mouse com botão esquerdo podem selecionar destinos.
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            for button, destination in self.buttons:
                if button.collidepoint(event.pos):
                    self.is_open = False
                    return True, destination

        # Com o menu aberto, cliques fora das opções não ativam NPCs ou portas.
        return True, None

    def draw(self, screen, player):
        self.door.draw(screen, player)
        if not self.is_open:
            return

        screen_width, screen_height = screen.get_size()
        self.panel.center = (screen_width // 2, screen_height // 2)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (30, 38, 48), self.panel)
        pygame.draw.rect(screen, (225, 205, 155), self.panel, width=3)

        title = self.title_font.render("Elevador - escolha o destino", True, (255, 255, 255))
        screen.blit(title, title.get_rect(midtop=(self.panel.centerx, self.panel.top + 16)))
        self.buttons = []
        button_height = 46
        button_gap = 12
        button_width = self.panel.width - 48
        first_y = self.panel.top + 72
        for index, (destination, label) in enumerate(self.destinations):
            button = pygame.Rect(
                self.panel.left + 24,
                first_y + index * (button_height + button_gap),
                button_width,
                button_height,
            )
            pygame.draw.rect(screen, (72, 91, 108), button)
            pygame.draw.rect(screen, (205, 215, 220), button, width=2)
            text = self.font.render(label, True, (255, 255, 255))
            screen.blit(text, text.get_rect(center=button.center))
            self.buttons.append((button, destination))
