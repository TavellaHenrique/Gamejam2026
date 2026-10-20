
from scenes.scene_manager import SceneManager
from scenes.main_menu import MainMenu

class Game:
    def __init__(self):
        self.player = None # Player()
        self.inventory = None # Inventory()
        self.dialogue_manager = None # DialogueManager()

        self.scene_manager = SceneManager(self)

        self.scene_manager.change_scene(MainMenu(self))