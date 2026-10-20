
import pygame

from scenes.scene import Scene

from ui.dialogue_box import DialogueBox

class GameScene(Scene):

    def __init__(self, game):
        super().__init__(game)

        self.player = game.player
        self.npcs = game.npcs
        self.dialogue_manager = game.dialogue_manager

        self.dialogue_box = DialogueBox()
        self.active_speaker = ""
    
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_e:
            if self.dialogue_manager.is_active:
                # Primeiro, tenta avançar a página.
                if self.dialogue_box.advance_page():
                    return

                # Na última página: avança a fala.
                self.dialogue_manager.advance()

                if self.dialogue_manager.is_active:
                    self.dialogue_box.show_text(
                        self.dialogue_manager.current_text
                    )
                else:
                    self.active_speaker = ""

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
            ),
        )

        self.active_speaker = npc.display_name
        self.dialogue_manager.start(npc.dialogue_id)

        self.dialogue_box.show_text(
            self.dialogue_manager.current_text
        )


    def draw(self, screen):
        screen.fill((35, 45, 55))

        self.npcs.draw(screen)
        screen.blit(self.player.image, self.player.rect)

        if self.dialogue_manager.is_active:
            self.dialogue_box.draw(
                screen,
                speaker_name=self.active_speaker,
            )

    def update(self, delta_time):
        if not self.dialogue_manager.is_active:
            self.player.update(delta_time)

        self.npcs.update(delta_time)
