
import pygame

from entities.door import Door
from scenes.scene import Scene
from systems.cutscene import Cutscene
from systems.npc_controller import NPCController
from entities.npc import NPC


class GameScene(Scene):
    """Cena de jogo que atualiza e desenha o jogador e os NPCs."""

    def __init__(self, game, player_spawn=None):
        """Configura o jogador compartilhado e os NPCs presentes nesta cena."""
        super().__init__(game)

        self.player = game.player
        if player_spawn is not None:
            self.player.position.update(player_spawn)
            self.player.rect.center = player_spawn

        self.door = Door(
            rect=(900, 245, 56, 112),
            prompt="Entrar na próxima área",
        )
        self.cutscene = Cutscene()
        self.cutscene_hint_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            20,
        )
        self.cutscene_npc = NPC(
            npc_id="poeta",
            display_name="Poeta",
            position=(200, 100),
            sprite_path="assets/sprites/npcs/Idle_Down.png",
            dialogue_id="poema",
            use_player_animations=True,
        )
        self.ambient_npc = NPC(
            npc_id="estudante",
            display_name="Estudante",
            position=(420, 380),
            sprite_path="assets/sprites/npcs/Idle_Down.png",
            dialogue_id="poema",
            ambient_radius=180,
            ambient_lines=game.dialogue_manager.dialogues[
                "falas_aleatorias"
            ],
            use_player_animations=True,
            interactable=False,
        )

        # O controlador centraliza a atualização, interação e desenho dos NPCs.
        self.npc_controller = NPCController(
            game,
            npcs=[
                NPC(
                    npc_id="weird_girl",
                    display_name="Garota estranha",
                    position=(600, 300),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="weird_girl_intro",
                    use_player_animations=True,
                ),
                self.cutscene_npc,
                self.ambient_npc,
            ]
        )
    
    def handle_event(self, event):
        """Inicia o exemplo de cutscene com C e encaminha eventos aos NPCs."""
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and self.door.can_interact(self.player)
            and not self.npc_controller.dialogue_manager.is_active
            and not self.cutscene.is_active
        ):
            from scenes.second_area import SecondArea

            self.game.scene_manager.transition_to(
                lambda: SecondArea(self.game, player_spawn=(145, 300))
            )
            return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_c
            and not self.cutscene.is_active
            and not self.npc_controller.dialogue_manager.is_active
        ):
            # O terceiro NPC percorre dois segmentos com a animação de caminhada.
            self.cutscene.start(
                self.ambient_npc,
                [(520, 380), (520, 460)],
            )

        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        """Atualiza o jogador quando não há diálogo e mantém os NPCs animados."""
        cutscene_was_active = self.cutscene.is_active
        self.cutscene.update(delta_time)
        self.npc_controller.update(delta_time)

        if not self.npc_controller.dialogue_manager.is_active:
            self.player.update(
                delta_time,
                accept_input=(
                    not cutscene_was_active
                    and not self.npc_controller.interaction_cutscene.is_active
                    and not self.npc_controller.is_approaching_npc
                    and self.npc_controller.pending_interaction_npc is None
                ),
            )

    def draw(self, screen):
        """Desenha o fundo, personagens e interface da cena."""
        screen.fill((35, 45, 55))

        self.door.draw(screen, self.player)

        # Desenha os personagens sobre o cenário e a interface acima deles.
        self.npc_controller.draw_npcs(screen)
        screen.blit(self.player.image, self.player.rect)
        cutscene_hint = self.cutscene_hint_font.render(
            "C - Mover o terceiro NPC com animação",
            True,
            (255, 255, 255),
        )
        screen.blit(cutscene_hint, (20, 20))
        self.npc_controller.draw_ui(screen)
