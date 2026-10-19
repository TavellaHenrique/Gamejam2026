import pygame

from config import(
    BG_COLOR_START_MENU,
    FONT_COLOR_DEFAULT_TEXT
)

class Game:
    # -- Estados do jogo e versão textual correspondente --
    START_MENU = "start_menu"
    PLAYING = "playing"

    def __init__(self):
        self.default_font = pygame.font.Font(None, 36)
        self.state = self.START_MENU

    # Gera um elemento de texto horizontalmente centralizado
    def draw_centralized_text(
        self,
        screen: pygame.Surface,
        text: str,
        font: pygame.Font,
        color: pygame.Color,
        y: int,
    ):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(screen.get_width() // 2, y))
        screen.blit(surface, rect)

    # Coordena as chamadas dos elementos visuais da tela
    def draw(self, screen: pygame.Surface):

        if self.state == self.START_MENU:
            self.drawStartScreen(screen)

        elif self.state == self.PLAYING:
            self.drawPlayingScene(screen)

    def drawStartScreen(self, screen: pygame.Surface):
        screen.fill(BG_COLOR_START_MENU)

        self.draw_centralized_text(
            screen,
            "Fatec: Presas Abertas",
            self.default_font,
            FONT_COLOR_DEFAULT_TEXT,
            100
        )

        self.draw_centralized_text(
            screen,
            "Pressione ENTER para iniciar",
            self.default_font,
            FONT_COLOR_DEFAULT_TEXT,
            200
        )

    def drawPlayingScene(self, screen: pygame.Surface):
        screen.fill((200, 100, 100))

        self.draw_centralized_text(
            screen,
            "Cena 01",
            self.default_font,
            FONT_COLOR_DEFAULT_TEXT,
            100
        )