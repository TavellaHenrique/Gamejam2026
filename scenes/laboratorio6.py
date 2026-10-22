"""Cena de demonstração conectada à cena principal por uma porta."""

import pygame

from entities.door import Door
from entities.npc import NPC
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
from systems.tilemap_scene import LABORATORY_OBSTACLES, TilemapScene


def _create_saguao(game):
    from scenes.saguao import Saguao

    return Saguao(game)


class Laboratorio6(TilemapScene):
    """Área com porta, jogador e NPCs ambulantes."""

    def __init__(self, game, player_spawn=None):
        """Cria a área e inicializa dois NPCs ambulantes."""
        super().__init__(
            game,
            "assets/tileset/laboratorio/laboratorio_base.jpg",
            player_spawn=player_spawn,
        )
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            36,
        )
        self.door = Door(
            rect=self.map_rect((862, 10, 43, 87)),
            prompt="Saguão",
            interaction_margin=72,
            visible=False,
        )
        self.doors = (self.door,)
        self.environment_obstacles = tuple(
            self.map_rect(rect) for rect in LABORATORY_OBSTACLES
        )
        self.map_objects = self.create_laboratory_objects()
        self.hint_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            20,
        )
        self.npc_controller = NPCController(
            game,
            npcs=[
                NPC(
                    npc_id="thiago",
                    display_name="Prof Thiago",
                    position=self.map_point((700, 160)),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="thiago_lab6_2",
                    use_player_animations=True,
                    interactable=True,
                ),
                *(
                    NPC(
                        npc_id=npc_id,
                        display_name="",
                        position=self.map_point(position),
                        sprite_path=(
                            "assets/sprites/player/"
                            "TheFemaleAdventurer/Idle/Idle_Up.png"
                        ),
                        dialogue_id="",
                        frame_count=1,
                        scale=3,
                        interactable=False,
                    )
                    for npc_id, position in (
                        ("estudante6", (105, 285)),
                        ("estudante7", (273, 370)),
                        ("estudante8", (465, 285)),
                        ("estudante4", (658, 370)),
                        ("estudante5", (273, 515)),
                    )
                ),
            ],
            npc_scope=type(self),
            static_obstacles=self.get_scene_obstacles(),
        )
        self.cutscene_controller = CutsceneController.create_story_cutscene(
            game,
            self.npc_controller,
            trigger(
                trigger_position=self.player.position,
                trigger_radius=16,
                visible=False,
                action=(
                    dialogue_from_id("thiago_lab6_1"),
                    dialogue_from_id("jogador_intro_2"),
                    npc(
                        "thiago",
                        npc_arrival=self.map_point((700, 200)),
                    ),
                    face_direction("thiago", "down"),
                    # player_destination(self.map_point((700, 150))),
                    # player_destination(self.map_point((900, 150))),
                    # change_scene(
                    #     lambda: _create_saguao(game),
                    #     duration=0.5,
                    #     player_spawn=(450, 100),
                    # ),
                    # npc("professor1", npc_arrival=(500, 40)),
                    # fade_out("professor1", duration=0.50),
                    # npcs(
                    #     {
                    #         "estudante1": (450, 40),
                    #         "estudante2": (500, 40),
                    #         "estudante3": (550, 40),
                    #     }
                    # ),
                    # fade_out("estudante1", duration=0.25),
                    # fade_out("estudante2", duration=0.25),
                    # fade_out("estudante3", duration=0.25),
                    # player_destination((500, 40)),
                    # change_scene(
                    #     lambda: SecondArea(game),
                    #     duration=0.5,
                    #     player_spawn=(0, 100),
                    # ),
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
            cutscene_id="game_scene_2",
            bounds=self.bounds,
            camera=self.camera,
        )
        self.cutscene_controller.start()

    def handle_event(self, event):
        """Avança diálogos e inicia o retorno ao interagir com a porta."""
        if self.is_inventory_open():
            return
        if self.cutscene_controller.handle_event(event):
            return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.game.dialogue_manager.is_active
            and not self.cutscene_controller.is_active
            and self.door.can_interact(self.player)
        ):
            self.game.scene_manager.transition_to(
                lambda: _create_saguao(self.game),
                player_spawn=self.map_point((900, 150)),
            )
            return

        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        """Move entidades com colisão e escolhe destinos dos NPCs a cada cinco segundos."""
        self.update_camera(delta_time, self.cutscene_controller)
        self.cutscene_controller.update(delta_time)
        self.player.update(
            delta_time,
            accept_input=(
                # Diálogos, cutscene e inventário bloqueiam o controle do jogador.
                not self.game.inventory_open
                and not self.game.dialogue_manager.is_active
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
                self.get_door_obstacles()
            ),
        )
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=self.get_door_obstacles(),
        )

    def draw(self, screen):
        """Desenha o tileset, os personagens e a interface."""
        world = self.begin_world_draw()
        self.cutscene_controller.draw_trigger(world)
        self.draw_scene_entities(world, self.npc_controller.npcs)
        self.render_world(screen)

        title = self.title_font.render(
            "Laboratório",
            True,
            (255, 255, 255),
        )
        screen.blit(title, (24, 20))

        self.draw_door_hint(
            screen,
            self.hint_font,
            self.player,
            self.doors,
        )
        self.npc_controller.draw_ui(screen, camera=self.camera)
        self.cutscene_controller.draw_overlay(screen)
