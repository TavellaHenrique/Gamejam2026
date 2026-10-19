
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
        self.player = Player(500, 100, 64, 80)
        self.npc = NonPlayableCharacter(48, 100, 64, 80)

        # Adiciona a instância do jogado a um grupo usando o agrupamento nativo do pygame
        self.all_characters = pygame.sprite.Group()
        self.all_characters.add(self.player)
        self.all_characters.add(self.npc)

        self.npcs = pygame.sprite.Group()
        self.npcs.add(self.npc)

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
            self.draw_start_screen(screen)

        elif self.state == self.PLAYING:
            self.draw_playing_scene(screen)

            player_previous_pos = self.player.rect.topleft

            self.all_characters.update(delta_time)
            self.all_characters.draw(screen)

            # Para debug
            self.draw_collision_areas(screen)

            if self.player.collision_area.colliderect(self.npc.collision_area):
                self.player.rect.topleft = player_previous_pos
                self.player.update_collision_area()

                self.draw_centralized_text(
                    screen,
                    "Aperte E para interagir",
                    self.default_font,
                    FONT_COLOR_DEFAULT_TEXT,
                    500
                )

    def draw_collision_areas(self, screen):
        npc: NonPlayableCharacter = None

        self.player.show_collision_area(screen, pygame.color.THECOLORS.get("green"))

        for npc in self.npcs.sprites():
            npc.show_collision_area(screen, pygame.color.THECOLORS.get("red"))

    # Função que coordena os elementos do menu inicial
    def draw_start_screen(self, screen: pygame.Surface):
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
    def draw_playing_scene(self, screen: pygame.Surface):
        screen.fill((200, 100, 100))

        self.draw_centralized_text(
            screen,
            "Cena 01",
            self.default_font,
            FONT_COLOR_DEFAULT_TEXT,
            100
        )