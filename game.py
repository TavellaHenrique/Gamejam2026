
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
        self.player = Player(200, 200)
        self.inventory = None  # Inventory()
        # Conclusões ficam no Game para sobreviver à recriação das cenas.
        self.completed_cutscenes = set()
        self.removed_npcs = set()

        # Os diálogos são carregados de um arquivo e podem ser consultados pelas cenas.
        self.dialogue_manager = DialogueManager(
            "data/dialogues.json"
        )

        # Começa no menu e permite trocar de cena sem encerrar o estado compartilhado.
        self.scene_manager = SceneManager(self)
        self.scene_manager.change_scene(MainMenu(self))

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
