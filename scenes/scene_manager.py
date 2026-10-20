
from scenes.scene import Scene

class SceneManager:
    def __init__(self, game):
        self.game = game
        self.current_scene = None

    def change_scene(self, new_scene: Scene):
        if self.current_scene is not None:
            self.current_scene.on_exit()

        self.current_scene = new_scene
        self.current_scene.on_enter()

    def handle_event(self, event):
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self, delta_time):
        if self.current_scene:
            self.current_scene.update(delta_time)

    def draw(self, screen):
        if self.current_scene:
            self.current_scene.draw(screen)