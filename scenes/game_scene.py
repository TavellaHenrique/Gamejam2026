
import pygame

from scenes.scene import Scene
from systems.npc_controller import NPCController
from entities.npc import NPC

class GameScene(Scene):

    def __init__(self, game):
        super().__init__(game)

        self.player = game.player

        self.npc_controller = NPCController(
            game,
            npcs=[
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
            ]
        )
    
    def handle_event(self, event):
        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        if not self.npc_controller.dialogue_manager.is_active:
            self.player.update(delta_time)

        self.npc_controller.update(delta_time)

    def draw(self, screen):
        screen.fill((35, 45, 55))

        self.npc_controller.draw_npcs(screen)
        screen.blit(self.player.image, self.player.rect)
        self.npc_controller.draw_ui(screen)
