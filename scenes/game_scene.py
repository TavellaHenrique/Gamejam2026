
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
        npc = self.get_nearest_interactable_npc()

        if npc is None:
            return

        self.active_speaker = npc.display_name
        self.dialogue_manager.start(npc.dialogue_id)

        self.dialogue_box.show_text(
            self.dialogue_manager.current_text
        )

    def get_nearest_interactable_npc(self):
        nearby_npcs = [
            npc for npc in self.npcs
            if npc.can_interact(self.player)
        ]

        if not nearby_npcs:
            return None

        return min(
            nearby_npcs,
            key=lambda npc: npc.position.distance_to(
                self.player.position
            ),
        )

    def draw_interaction_prompt(self, screen):
        if self.dialogue_manager.is_active:
            return

        npc = self.get_nearest_interactable_npc()

        if npc is None:
            return

        font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf", 20
        )
        text = font.render(
            "E - Interagir", True, (255, 255, 255)
        )

        text_rect = text.get_rect(
            midbottom=(
                npc.rect.centerx,
                npc.rect.top + 60,
            )
        )

        # Fundo escuro para facilitar a leitura.
        background_rect = text_rect.inflate(16, 10)
        background = pygame.Surface(
            background_rect.size, pygame.SRCALPHA
        )
        background.fill((20, 24, 32, 210))

        screen.blit(background, background_rect.topleft)
        screen.blit(text, text_rect)


    def draw(self, screen):
        screen.fill((35, 45, 55))

        self.npcs.draw(screen)
        screen.blit(self.player.image, self.player.rect)

        self.draw_interaction_prompt(screen)

        if self.dialogue_manager.is_active:
            self.dialogue_box.draw(
                screen,
                speaker_name=self.active_speaker,
            )

    def update(self, delta_time):
        if not self.dialogue_manager.is_active:
            self.player.update(delta_time)

        self.npcs.update(delta_time)
