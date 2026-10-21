
import pygame

# O gerenciador coordena as cenas e o gerenciador de diálogo mantém as falas.
from scenes.scene_manager import SceneManager
from systems.dialogue_manager import DialogueManager
from scenes.main_menu import MainMenu

# Entidades compartilhadas podem ser acessadas por diferentes cenas do jogo.
from entities.player import Player
from entities.npc import NPC


class Game:
    """Mantém o estado compartilhado durante toda a execução do jogo."""

    def __init__(self):
        """Cria as entidades e os gerenciadores centrais antes da primeira cena."""
        # O jogador e o inventário pertencem ao jogo, não a uma cena específica.
        self.player_spawn_point = pygame.Vector2(500, 544)
        self.player = Player(self.player_spawn_point)
        self.inventory = None  # Inventory()
        # Conclusões ficam no Game para sobreviver à recriação das cenas.
        self.completed_cutscenes = set()
        self.removed_npcs = set()
        self.show_mouse_coordinates = False
        self.coordinates_font = pygame.font.Font(None, 24)

        # Os diálogos são carregados de um arquivo e podem ser consultados pelas cenas.
        self.dialogue_manager = DialogueManager(
            "data/dialogues.json"
        )

        # Começa no menu e permite trocar de cena sem encerrar o estado compartilhado.
        self.scene_manager = SceneManager(self)
        self.scene_manager.change_scene(MainMenu(self))

    def set_player_spawn_point(self, position):
        """Atualiza o ponto persistente onde o jogador deve surgir."""
        self.player_spawn_point.update(position)

    def handle_global_event(self, event):
        """Alterna a legenda de coordenadas quando K é pressionado fora de sequências."""
        if event.type != pygame.KEYDOWN or event.key != pygame.K_k:
            return False
        if self.dialogue_manager.is_active or self._is_cutscene_active():
            return False

        self.show_mouse_coordinates = not self.show_mouse_coordinates
        return True

    def draw_debug_overlay(self, screen):
        """Desenha a posição atual do mouse no canto superior esquerdo."""
        if not self.show_mouse_coordinates:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        label = self.coordinates_font.render(
            f"X: {mouse_x}  Y: {mouse_y}",
            True,
            (255, 255, 255),
        )
        label_rect = label.get_rect(topleft=(10, 10))
        background_rect = label_rect.inflate(12, 8)
        background = pygame.Surface(background_rect.size, pygame.SRCALPHA)
        background.fill((0, 0, 0, 180))
        screen.blit(background, background_rect)
        screen.blit(label, label_rect)

    def _is_cutscene_active(self):
        """Considera tanto a cutscene da cena quanto a interação roteirizada de NPC."""
        scene = self.scene_manager.current_scene
        if scene is None:
            return False

        cutscene_controller = getattr(scene, "cutscene_controller", None)
        if cutscene_controller is not None and cutscene_controller.is_active:
            return True

        npc_controller = getattr(scene, "npc_controller", None)
        interaction_cutscene = getattr(
            npc_controller,
            "interaction_cutscene",
            None,
        )
        return (
            interaction_cutscene is not None
            and interaction_cutscene.is_active
        )

    def is_cutscene_completed(self, cutscene_id):
        """Verifica se uma cutscene já terminou nesta execução do jogo."""
        return cutscene_id in self.completed_cutscenes

    def mark_cutscene_completed(self, cutscene_id):
        """Registra a conclusão para impedir que a cutscene seja repetida."""
        self.completed_cutscenes.add(cutscene_id)

    def is_npc_removed(self, npc_id):
        """Verifica se um NPC foi removido durante a execução atual."""
        return npc_id in self.removed_npcs

    def mark_npc_removed(self, npc_id):
        """Mantém removido um NPC quando a cena for recriada."""
        self.removed_npcs.add(npc_id)
