import pygame

from entities.door import Door
from entities.npc import NPC
from scenes.scene import Scene
from scenes.laboratorio6 import Laboratorio6
from systems.cutscene_controller import (
    CutsceneController,
    change_scene,
    dialogue,
    face_direction,
    fade_out,
    npc,
    npc_dialogue,
    npcs,
    player_destination,
    spawn_npc,
    time_passes,
    trigger,
    wait,
    dialogue_from_id,
)
from systems.npc_controller import NPCController


class Saguao(Scene):
    """Cena de jogo com a história demonstrativa e seus NPCs."""

    def __init__(self, game, player_spawn=None):
        """Configura o jogador compartilhado e os NPCs da cena."""
        super().__init__(game)

        self.player = game.player
        if player_spawn is None:
            player_spawn = game.player_spawn_point
        else:
            game.set_player_spawn_point(player_spawn)
        self.player.position.update(player_spawn)
        self.player.rect.center = player_spawn

        self.door = Door(
            rect=(900, 245, 56, 112),
            prompt="Segunda área",
        )
        self.door = Door(
            rect=(450, 0, 100, 40),
            prompt="Primeira área",
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
                    npc_id="diretor",
                    display_name="Diretor",
                    position=(500, 200),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="diretor_saguao_2",
                    use_player_animations=True,
                    interactable=True
                ),
            ],
            npc_scope=type(self),
        )
        self.cutscene_controller = CutsceneController.create_story_cutscene(
            game,
            self.npc_controller,
            trigger(
                trigger_position=(self.player.position),
                trigger_radius=16,
                visible=False,
                action=(
                    spawn_npc(
                        npc_id="estudante1",
                        display_name="estudante1",
                        position=(440, 544),
                        sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                        dialogue_id="estudante1",
                        use_player_animations=True,
                        interactable=False,
                    ),
                    spawn_npc(
                        npc_id="estudante2",
                        display_name="estudante2",
                        position=(500, 544),
                        sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                        dialogue_id="estudante2",
                        use_player_animations=True,
                        interactable=False,
                    ),
                    spawn_npc(
                        npc_id="estudante3",
                        display_name="estudante3",
                        position=(550, 544),
                        sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                        dialogue_id="estudante3",
                        use_player_animations=True,
                        interactable=False,
                    ),
                    dialogue_from_id("jogador_intro"),
                    dialogue_from_id("diretor_saguao_1"),
                    npc("diretor", npc_arrival=(500, 40)),
                    fade_out("diretor", duration=0.50),
                    npcs(
                        {
                            "estudante1": (450, 40),
                            "estudante2": (500, 40),
                            "estudante3": (550, 40),
                        }
                    ),
                    fade_out("estudante1", duration=0.25),
                    fade_out("estudante2", duration=0.25),
                    fade_out("estudante3", duration=0.25),
                    player_destination((500, 40)),
                    change_scene(
                        lambda: Laboratorio6(game),
                        player_spawn=(400, 500),
                        text="Passa um tempo",
                        fade_out_duration=0.5,
                        duration=1.5,
                        fade_in_duration=0.5,
                        font_size=44,
                    )
                    # Os três personagens se deslocam em paralelo após o trigger.
                    # npcs(
                    #     {
                    #         "estudante1": (520, 260),
                    #         "estudante2": (550, 260),
                    #         "estudante3": (590, 260),
                    #     }
                    # ),
                    # face_direction("professor1", "left"),
                    # face_direction("poeta", "right"),
                    # face_direction("cutscene_guest", "left"),
                    # face_direction("player", "right"),
                    # npc_dialogue(
                    #     "professor1",
                    #     "Você também ouviu o sino tocar? A torre está trancada há anos.",
                    # ),
                    # dialogue(
                    #     "Ouvi vindo da sala de arquivos.",
                    # ),
                    # dialogue(
                    #     "Talvez alguém tenha encontrado outra entrada.",
                    # ),
                    # time_passes(
                    #     text="Passa um tempo",
                    #     fade_out_duration=0.8,
                    #     duration=1.8,
                    #     fade_in_duration=0.8,
                    #     font_size=44,
                    # ),
                    # wait(0.75),
                    # # O visitante segue até a porta e desaparece em fade-out.
                    # npc("cutscene_guest", npc_arrival=(880, 300)),
                    # fade_out("cutscene_guest", duration=1.25),
                ),
            ),
            # wait(1),
            # player_destination((360, 240)),
            # trigger(
            #     trigger_position=(360, 240),
            #     trigger_radius=10,
            #     visible=False,
            #     action=(
            #         face_direction("weird_girl", "left"),
            #         face_direction("player", "right"),
            #         npc_dialogue(
            #             "weird_girl",
            #             "Olha! A porta lateral está aberta. Acho que o barulho veio de lá.",
            #         ),
            #         dialogue(
            #             "Vamos investigar juntos. Mas se ouvirmos outro sino, é melhor correr.",
            #         ),
            #     ),
            # ),
            # # A transição substitui o spawn global e inicia a cena seguinte nesse ponto.
            # change_scene(
            #     lambda: SecondArea(game),
            #     duration=0.8,
            #     player_spawn=(145, 300),
            # ),
            cutscene_id="game_scene_1",
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
            self.game.scene_manager.transition_to(
                lambda: Laboratorio6(self.game),
                player_spawn=(145, 300),
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
        self.npc_controller.draw_ui(screen)
        self.cutscene_controller.draw_overlay(screen)
