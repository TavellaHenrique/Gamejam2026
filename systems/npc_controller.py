
import pygame

from ui.dialogue_box import DialogueBox

class NPCController:
    def __init__(self, game, npcs=()):
        self.player = game.player
        self.dialogue_manager = game.dialogue_manager

        self.npcs = pygame.sprite.Group(*npcs)

        self.dialogue_box = DialogueBox()
        self.active_speaker = ""

        self.prompt_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf", 20
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

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key != pygame.K_e:
            return

        if self.dialogue_manager.is_active:
            # Primeiro, tenta avançar a página atual.
            if self.dialogue_box.advance_page():
                return

            # Na última página, avança a fala.
            self.dialogue_manager.advance()

            if self.dialogue_manager.is_active:
                self.dialogue_box.show_text(
                    self.dialogue_manager.current_text
                )
            else:
                self.active_speaker = ""

            return

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

    def update(self, delta_time):
        self.npcs.update(delta_time)

    def draw_npcs(self, screen):
        self.npcs.draw(screen)

    def draw_ui(self, screen):
        if self.dialogue_manager.is_active:
            self.dialogue_box.draw(
                screen,
                speaker_name=self.active_speaker,
            )
            return

        npc = self.get_nearest_interactable_npc()

        if npc is None:
            return

        text = self.prompt_font.render(
            "E - Interagir",
            True,
            (255, 255, 255),
        )

        text_rect = text.get_rect(
            midbottom=(
                npc.rect.centerx,
                npc.rect.top + 80,
            )
        )

        background_rect = text_rect.inflate(16, 10)

        background = pygame.Surface(
            background_rect.size,
            pygame.SRCALPHA,
        )
        background.fill((20, 24, 32, 210))

        screen.blit(background, background_rect.topleft)
        screen.blit(text, text_rect)
