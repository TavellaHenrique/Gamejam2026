
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
    DIALOG = "dialog"

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

    # Coordena as chamadas dos elementos visuais da tela
    def draw(self, screen: pygame.Surface, delta_time):

        match (self.state):
            case self.START_MENU:
                # Delega para a função que coordena os elementos da tela inicial
                self.draw_start_screen(screen)

            case self.PLAYING:
                # Coordena os elementos de uma cena (por enquanto, há apenas uma)
                self.draw_playing_scene(screen)

                # Guarda a posição do jogador antes do movimento
                player_previous_pos = self.player.rect.topleft

                # Atualiza os elementos (inclui movimento e animações)
                self.all_characters.update(delta_time)
                self.all_characters.draw(screen)

                # [Debug] Exibe as áreas de colisão dos elementos
                self.draw_collision_areas(screen)

                # Lida com colisões e suas consequências
                self.handle_collision(screen, player_previous_pos)

            case self.DIALOG:
                self.draw_centralized_text(
                    screen,
                    "Pressione ENTER para encerrar o diálogo",
                    self.default_font,
                    FONT_COLOR_DEFAULT_TEXT,
                    screen.get_height()//2
                )

    def draw_collision_areas(self, screen):
        npc: NonPlayableCharacter = None

        self.player.show_collision_area(screen, pygame.color.THECOLORS.get("green"))

        for npc in self.npcs.sprites():
            npc.show_collision_area(screen, pygame.color.THECOLORS.get("red"))
            npc.show_interaction_area(screen, pygame.color.THECOLORS.get("yellow"))

    def handle_collision(self, screen, player_previous_pos):
        # Verificação de colisões entre jogador e npcs
        npc: NonPlayableCharacter = None
        for npc in self.npcs.sprites():
            # Colisão entre áreas sólidas
            if self.player.collision_area.colliderect(npc.collision_area):
                self.player.rect.topleft = player_previous_pos
                self.player.update_collision_area()
        
            # Colisão do jogador com uma área de interação
            if self.player.collision_area.colliderect(npc.interaction_area):
                self.draw_text(
                    screen,
                    "Aperte E para interagir",
                    self.default_font,
                    FONT_COLOR_DEFAULT_TEXT,
                    npc.rect.centerx,
                    npc.collision_area.top - 20
                )
        
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e]:
                    self.state = Game.DIALOG

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

    # Função genérica que gera na tela um texto
    def draw_text(
        self,
        screen: pygame.Surface,
        text: str,
        font: pygame.Font,
        color: pygame.Color,
        x: int,
        y: int,
    ):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(x, y))
        screen.blit(surface, rect)