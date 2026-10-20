
from scenes.scene_manager import SceneManager
from scenes.main_menu import MainMenu

from entities.player import Player

class Game:
    def __init__(self):
        self.player = Player(200, 200)
        self.inventory = None # Inventory()
        self.dialogue_manager = None # DialogueManager()

        self.scene_manager = SceneManager(self)

        self.scene_manager.change_scene(MainMenu(self))
