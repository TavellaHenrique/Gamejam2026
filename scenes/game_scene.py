
import pygame

from scenes.scene import Scene


class GameScene(Scene):

    def __init__(self, game):
        super().__init__(game)

        self.player = game.player
        self.npcs = game.npcs
        self.dialogue_manager = game.dialogue_manager

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_e:
            if self.dialogue_manager.is_active:
                self.dialogue_manager.advance()
            else:
                self.interact_with_nearest_npc()

    def interact_with_nearest_npc(self):
        nearby_npcs = [
            npc for npc in self.npcs
            if npc.can_interact(self.player)
        ]

        if not nearby_npcs:
            return

        npc = min(
            nearby_npcs,
            key=lambda item: item.position.distance_to(
                self.player.position
            )
        )

        self.dialogue_manager.start(npc.dialogue_id)

    def update(self, delta_time):
        if not self.dialogue_manager.is_active:
            self.player.update(delta_time)

        self.npcs.update(delta_time)

    def draw(self, screen):
        screen.fill((35, 45, 55))

        self.npcs.draw(screen)
        screen.blit(self.player.image, self.player.rect)

        # A caixa de diálogo será desenhada aqui
        # quando DialogueBox for implementada.
