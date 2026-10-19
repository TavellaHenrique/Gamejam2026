
# -- Importações --
import pygame

from config import(
    BG_COLOR_START_MENU,
    FONT_COLOR_DEFAULT_TEXT
)

from player import Player
from npc_base import NonPlayableCharacter

class Game:
    # -- Estados do jogo e texto correspondente --
    START_MENU = "start_menu"
    PLAYING = "playing"

    def __init__(self):
        # Define a fonte padrão 
        self.default_font = pygame.font.Font(None, 36)

        # Define o estado inicial do jogo
        self.state = self.START_MENU

        # Cria uma instância de Player, que representa o jogador
        self.player = Player(100, 100)

        self.npc = NonPlayableCharacter(200, 200)

        # Adiciona a instância do jogado a um grupo usando o agrupamento nativo do pygame
        self.all_sprites = pygame.sprite.Group(self.player)
        self.all_sprites.add(self.npc)

    # Função genérica que gera na tela um texto horizontalmente centralizado
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
    def draw(self, screen: pygame.Surface, delta_time):

        if self.state == self.START_MENU:
            self.drawStartScreen(screen)

        elif self.state == self.PLAYING:
            self.drawPlayingScene(screen)
            self.all_sprites.update(delta_time)
            self.all_sprites.draw(screen)

    # Função que coordena os elementos do menu inicial
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

    # Função que coordena os elementos de uma cena
    def drawPlayingScene(self, screen: pygame.Surface):
        screen.fill((200, 100, 100))

        self.draw_centralized_text(
            screen,
            "Cena 01",
            self.default_font,
            FONT_COLOR_DEFAULT_TEXT,
            100
        )