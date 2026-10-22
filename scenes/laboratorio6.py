"""Cena de demonstração conectada à cena principal por uma porta."""

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
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
from scenes.scene import Scene
from systems.npc_controller import NPCController


def _create_saguao(game):
    from scenes.saguao import Saguao

    return Saguao(game)


class Laboratorio6(Scene):
    """Área com porta, jogador e NPCs ambulantes."""

    def __init__(self, game, player_spawn=None):
        """Cria a área e inicializa dois NPCs ambulantes."""
        super().__init__(game)
        self.player = game.player
        if player_spawn is None:
            player_spawn = game.player_spawn_point
        else:
            game.set_player_spawn_point(player_spawn)
        self.player.position.update(player_spawn)
        self.player.rect.center = player_spawn
        surface = pygame.display.get_surface()
        self.bounds = pygame.Rect(
            0,
            0,
            surface.get_width() if surface else SCREEN_WIDTH,
            surface.get_height() if surface else SCREEN_HEIGHT,
        )
        self.background_color = (48, 66, 58)
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            36,
        )
        self.door = Door(
            rect=(0, 100, 56, 112),
            prompt="Área anterior",
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
                    npc_id="thiago",
                    display_name="Prof Thiago",
                    position=(500, 200),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="thiago_lab6_2",
                    use_player_animations=True,
                    interactable = True
                ),
                NPC(
                    npc_id="estudante6",
                    display_name="",
                    position=(100, 500),
                    sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                    dialogue_id="",
                    use_player_animations=True,
                    interactable = False
                ),
                NPC(
                    npc_id="estudante7",
                    display_name="",
                    position=(200, 500),
                    sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                    dialogue_id="",
                    use_player_animations=True,
                    interactable = False
                ),
                NPC(
                    npc_id="estudante8",
                    display_name="",
                    position=(300, 500),
                    sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                    dialogue_id="",
                    use_player_animations=True,
                    interactable = False
                ), #400, 500 - player
                NPC(
                    npc_id="estudante4",
                    display_name="",
                    position=(500, 500),
                    sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                    dialogue_id="",
                    use_player_animations=True,
                    interactable = False
                ),
                NPC(
                    npc_id="estudante5",
                    display_name="",
                    position=(600, 500),
                    sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                    dialogue_id="",
                    use_player_animations=True,
                    interactable = False
                ),
            ],
            npc_scope=type(self),
        )
        self.cutscene_controller = CutsceneController.create_story_cutscene(
            game,
            self.npc_controller,
            trigger(
                trigger_position=(400, 500),
                trigger_radius=16,
                visible=False,
                action=(
                    dialogue_from_id("thiago_lab6_1"),
                    dialogue_from_id("jogador_intro_2"),
                    npc("thiago", npc_arrival=(700, 200)),
                    face_direction("thiago", "down"),
                    player_destination((400, 100)),
                    player_destination((40, 100)),
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
            and self.door.can_interact(self.player)
        ):
            self.game.scene_manager.transition_to(
                lambda: _create_saguao(self.game),
                player_spawn=(840, 300),
            )
            return

        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        """Move entidades com colisão e escolhe destinos dos NPCs a cada cinco segundos."""
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
                (self.door.rect,)
            ),
        )
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=(self.door.rect,),
        )

    def draw(self, screen):
        """Desenha o fundo, porta, NPCs, jogador e suas falas compactas."""
        screen.fill(self.background_color)

        title = self.title_font.render(
            "Segunda área",
            True,
            (255, 255, 255),
        )
        screen.blit(title, (24, 20))

        self.door.draw(screen, self.player)
        self.npc_controller.draw_npcs(screen)
        screen.blit(self.player.image, self.player.rect)
        self.npc_controller.draw_ui(screen)
        self.cutscene_controller.draw_overlay(screen)
