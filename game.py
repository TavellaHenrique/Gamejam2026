
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

        self.scene_manager = SceneManager(self)
        self.scene_manager.change_scene(MainMenu(self))
