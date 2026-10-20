
import pygame

from scenes.scene_manager import SceneManager
from systems.dialogue_manager import DialogueManager
from scenes.main_menu import MainMenu

from entities.player import Player
from entities.npc import NPC


class Game:
    def __init__(self):
        self.player = Player(200, 200)
        self.inventory = None  # Inventory()

        self.dialogue_manager = DialogueManager(
            "data/dialogues.json"
        )

        self.npcs = pygame.sprite.Group()
        self.create_npcs()

        self.scene_manager = SceneManager(self)
        self.scene_manager.change_scene(MainMenu(self))

    def create_npcs(self):
        self.npcs.add(
            NPC(
                npc_id="weird_girl",
                display_name="Garota estranha",
                position=(600, 300),
                sprite_path="assets/sprites/npcs/Idle_Down.png",
                dialogue_id="weird_girl_intro"
            ),
            NPC(
                npc_id="poeta",
                display_name="Poeta",
                position=(200, 100),
                sprite_path="assets/sprites/npcs/Idle_Down.png",
                dialogue_id="poema"
            )
        )
