
import pygame

from entities.door import Door
from entities.npc import NPC
from scenes.scene import Scene
from systems.cutscene_controller import (
    CutsceneController,
    dialogue,
    npc,
    npc_dialogue,
    player_destination,
    trigger,
    wait,
)
from systems.npc_controller import NPCController


class GameScene(Scene):
    """Cena de jogo com a história demonstrativa e seus NPCs."""

    def __init__(self, game, player_spawn=None):
        """Configura o jogador compartilhado e os NPCs da cena."""
        super().__init__(game)

        self.player = game.player
        if player_spawn is not None:
            self.player.position.update(player_spawn)
            self.player.rect.center = player_spawn

        self.door = Door(
            rect=(900, 245, 56, 112),
            prompt="Entrar na próxima área",
        )
        surface = pygame.display.get_surface()
        self.bounds = pygame.Rect(
            (0, 0),
            surface.get_size(),
        )
        self.hint_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            20,
        )
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
                NPC(
                    npc_id="poeta",
                    display_name="Poeta",
                    position=(200, 100),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="poema",
                    use_player_animations=True,
                ),
                NPC(
                    npc_id="estudante",
                    display_name="Estudante",
                    position=(420, 380),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="poema",
                    ambient_radius=180,
                    ambient_lines=game.dialogue_manager.get_lines(
                        "falas_aleatorias"
                    ),
                    use_player_animations=True,
                    interactable=False,
                ),
            ],
        )
        self.cutscene_controller = CutsceneController.create_story_cutscene(
            game,
            self.npc_controller,
            trigger(
                trigger_position=(280, 200),
                trigger_radius=32,
                visible=True,
                action=(
                    npc("weird_girl", npc_arrival=(520, 260)),
                    npc_dialogue(
                        "weird_girl",
                        "Você também ouviu o sino tocar? A torre está trancada há anos.",
                    ),
                    dialogue(
                        "Ouvi vindo da sala de arquivos. Talvez alguém tenha encontrado outra entrada.",
                        face_npc="weird_girl",
                    ),
                ),
            ),
            wait(1),
            player_destination((360, 240)),
            trigger(
                trigger_position=(360, 240),
                trigger_radius=10,
                visible=True,
                action=(
                    npc_dialogue(
                        "weird_girl",
                        "Olha! A porta lateral está aberta. Acho que o barulho veio de lá.",
                    ),
                    dialogue(
                        "Vamos investigar juntos. Mas se ouvirmos outro sino, é melhor correr.",
                        face_npc="weird_girl",
                    ),
                ),
            ),
            bounds=self.bounds,
        )
        self.cutscene_controller.start()

    def handle_event(self, event):
        """Delega falas da cutscene e encaminha outras interações."""
        if self.cutscene_controller.handle_event(event):
            return

        if (
            # O evento precisa ser o pressionamento da tecla de interação.
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            # A porta só pode ser usada quando o jogador está próximo.
            and self.door.can_interact(self.player)
            # Diálogo ou cutscene ativa impede a troca de cena.
            and not self.game.dialogue_manager.is_active
            and not self.cutscene_controller.is_active
        ):
            from scenes.second_area import SecondArea

            self.game.scene_manager.transition_to(
                lambda: SecondArea(self.game, player_spawn=(145, 300))
            )
            return

        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        """Atualiza a cutscene, os NPCs e o jogador."""
        self.cutscene_controller.update(delta_time)
        self.npc_controller.update(delta_time)

        self.player.update(
            delta_time,
            accept_input=(
                # Diálogos bloqueiam o controle para não andar durante as falas.
                not self.game.dialogue_manager.is_active
                # A cutscene bloqueia o teclado, exceto enquanto aguarda o gatilho.
                and not self.cutscene_controller.locks_player_control
                # A aproximação automática à conversa controla o jogador.
                and not self.npc_controller.interaction_cutscene.is_active
                # O jogador não deve se mover enquanto está sendo posicionado.
                and not self.npc_controller.is_approaching_npc
                # Uma interação pendente ainda está preparando a conversa.
                and self.npc_controller.pending_interaction_npc is None
            ),
            bounds=self.bounds,
            obstacles=self.npc_controller.get_player_obstacles(
                (self.door.rect,)
            ),
        )

    def draw(self, screen):
        """Desenha o fundo, personagens e interface da cena."""
        screen.fill((35, 45, 55))

        # Desenha os personagens sobre o cenário e a interface acima deles.
        self.door.draw(screen, self.player)
        self.cutscene_controller.draw_trigger(screen)
        self.npc_controller.draw_npcs(screen)
        screen.blit(self.player.image, self.player.rect)
        hint = self.hint_font.render(
            "Aproxime-se do círculo para iniciar a história",
            True,
            (255, 255, 255),
        )
        screen.blit(hint, (20, 20))
        self.npc_controller.draw_ui(screen)
