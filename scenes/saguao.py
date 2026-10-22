import pygame

from entities.door import Door
from entities.npc import NPC
from items.item import Item
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
from systems.tilemap_scene import TilemapScene


class Saguao(TilemapScene):
    """Cena de jogo com a história demonstrativa e seus NPCs."""

    def __init__(self, game, player_spawn=None):
        """Configura o jogador compartilhado e os NPCs da cena."""
        super().__init__(
            game,
            "assets/tileset/saguao/saguao_base.jpg",
            player_spawn=player_spawn,
        )
        self.player = game.player
        self.cantina_door = Door(
            rect=self.map_rect((230, 0, 116, 95)),
            prompt="Cantina",
            interaction_margin=72,
            visible=False,
        )
        self.lab_door = Door(
            rect=self.map_rect((875, 10, 47, 86)),
            prompt="Laboratório",
            interaction_margin=72,
            visible=False,
        )
        self.elevator_door = Door(
            rect=self.map_rect((0, 442, 64, 116)),
            prompt="Elevador",
            interaction_margin=72,
            visible=False,
        )
        self.stairs_door = Door(
            rect=self.map_rect((750, 430, 200, 195)),
            prompt="Laboratório 1",
            interaction_margin=72,
            visible=False,
        )
        self.door = self.lab_door
        self.doors = (
            self.cantina_door,
            self.lab_door,
            self.elevator_door,
            self.stairs_door,
        )
        stair_obstacles = []
        for top in range(430, 640, 16):
            left = max(750, 960 - (top + 16 - 430))
            stair_obstacles.append((left, top, 960 - left, 16))

        self.environment_obstacles = tuple(
            self.map_rect(rect)
            for rect in (
                (0, 0, 230, 96),
                (346, 0, 529, 96),
                (922, 0, 38, 96),
                *stair_obstacles,
            )
        )
        self.map_objects = [
            *(
                self.create_map_object_from_example(
                    "assets/tileset/saguao/saguao_exemplo.jpeg",
                    (x, y, 24, 72),
                    (x, y),
                    collision_rect=(0, 0, 24, 72),
                    occlusion_y=36,
                )
                for x, y in (
                    (55, 205),
                    (290, 205),
                    (738, 205),
                    (55, 300),
                    (290, 300),
                    (738, 284),
                )
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/Vaso.png",
                (17, 103),
                collision_rect=(1, 5, 31, 67),
                occlusion_y=60,
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/Vaso.png",
                (433, 103),
                collision_rect=(2, 5, 31, 67),
                occlusion_y=60,
            ),
            self.create_map_object(
                "assets/tileset/scene_objects/vaso_2.png",
                (18, 566),
                collision_rect=(3, 22, 31, 32),
                occlusion_y=45,
            ),
            *(
                self.create_map_object(
                    "assets/tileset/scene_objects/banco.png",
                    (x, y),
                    collision_rect=(3, 2, 73, 25),
                    occlusion_y=16,
                )
                for x, y in (
                    (89, 165),
                    (185, 165),
                    (505, 165),
                    (617, 165),
                    (89, 381),
                    (505, 334),
                    (601, 334),
                )
            ),
        ]
        self.map_objects.extend(
            self.create_map_object(
                "assets/tileset/scene_objects/lixeira.png",
                position,
                collision_rect=(0, 0, 20, 32),
                occlusion_y=16,
            )
            for position in ((12, 376), (412, 344))
        )
        self.items = [
            Item(
                item_id="lab_key",
                name="Chave do laboratório",
                description="O professor vai pedir isso na história.",
                position=self.map_point((620, 420)),
                interaction_radius=54,
            ),
            Item(
                item_id="battery",
                name="Bateria",
                description="Um pequeno dispositivo de energia.",
                position=self.map_point((780, 260)),
                interaction_radius=45,
            ),
            Item(
                item_id="note",
                name="Bilhete",
                description="Mensagem antiga do laboratório.",
                position=self.map_point((320, 560)),
                interaction_radius=48,
            ),
        ]
        for item in self.items:
            if self.player.inventory.has_item(item.id):
                item.collected = True
                item.visible = False
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
                    position=self.map_point((500, 200)),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="diretor_saguao_2",
                    use_player_animations=True,
                    interactable=True
                ),
                self.create_student_npc(
                    "saguao_student_1",
                    (125, 215),
                    ("O saguão fica bem cheio antes do começo das aulas.",),
                ),
                self.create_student_npc(
                    "saguao_student_2",
                    (220, 215),
                    ("A sala do laboratório fica no fim do corredor.",),
                ),
                self.create_student_npc(
                    "saguao_student_3",
                    (545, 215),
                    ("Você já passou na cantina? O café de lá é bom.",),
                ),
                self.create_student_npc(
                    "saguao_student_4",
                    (690, 380),
                    ("Estou esperando meus colegas para a próxima aula.",),
                ),
                self.create_student_npc(
                    "saguao_walker_1",
                    (365, 410),
                    ("Com licença, estou procurando minha sala.",),
                ),
                self.create_student_npc(
                    "saguao_walker_2",
                    (680, 500),
                    ("Ainda tenho alguns minutos antes da aula.",),
                ),
            ],
            npc_scope=type(self),
            static_obstacles=self.get_scene_obstacles(),
        )
        self.npc_controller.configure_wandering(
            (
                self.npc_controller.get_npc("saguao_walker_1"),
                self.npc_controller.get_npc("saguao_walker_2"),
            ),
            bounds=self.bounds,
            obstacles=self.get_scene_obstacles(),
        )
        self.cutscene_controller = CutsceneController.create_story_cutscene(
            game,
            self.npc_controller,
            trigger(
                trigger_position=self.map_point((480, 400)),
                trigger_radius=16,
                visible=True,
                action=(
                    spawn_npc(
                        npc_id="estudante1",
                        display_name="estudante1",
                        position=self.map_point((440, 544)),
                        sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                        dialogue_id="estudante1",
                        use_player_animations=True,
                        animation_scale=3,
                        interactable=False,
                    ),
                    spawn_npc(
                        npc_id="estudante2",
                        display_name="estudante2",
                        position=self.map_point((500, 544)),
                        sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                        dialogue_id="estudante2",
                        use_player_animations=True,
                        animation_scale=3,
                        interactable=False,
                    ),
                    spawn_npc(
                        npc_id="estudante3",
                        display_name="estudante3",
                        position=self.map_point((550, 544)),
                        sprite_path="assets/sprites/player/TheFemaleAdventurer/Idle/Idle_Up.png",
                        dialogue_id="estudante3",
                        use_player_animations=True,
                        animation_scale=3,
                        interactable=False,
                    ),
                    dialogue_from_id("jogador_intro"),
                    dialogue_from_id("diretor_saguao_1"),
                    npc(
                        "diretor",
                        npc_arrival=self.map_point((885, 105)),
                    ),
                    fade_out("diretor", duration=0.50),
                    npcs(
                        {
                            "estudante1": self.map_point((805, 122)),
                            "estudante2": self.map_point((830, 122)),
                            "estudante3": self.map_point((855, 122)),
                        }
                    ),
                    fade_out("estudante1", duration=0.25),
                    fade_out("estudante2", duration=0.25),
                    fade_out("estudante3", duration=0.25),
                    player_destination(self.map_point((700, 400))),
                    player_destination(self.map_point((900, 400))),
                    player_destination(self.map_point((900, 150))),
                    change_scene(
                        lambda: Laboratorio6(game),
                        player_spawn=self.map_point((900, 150)),
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
            camera=self.camera,
        )
        self.cutscene_controller.start()

    def handle_event(self, event):
        """Delega falas da cutscene e encaminha outras interações."""
        if self.is_inventory_open():
            return

        if self.cutscene_controller.handle_event(event):
            return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.game.dialogue_manager.is_active
            and not self.cutscene_controller.locks_player_control
        ):
            for item in self.items:
                if item.can_interact(self.player):
                    item.pick_up(self.player)
                    return

            if self.lab_door.can_interact(self.player):
                self.game.scene_manager.transition_to(
                    lambda: Laboratorio6(self.game),
                    player_spawn=self.map_point((900, 150)),
                )
                return

            if self.cantina_door.can_interact(self.player):
                from scenes.cantina import Cantina

                self.game.scene_manager.transition_to(
                    lambda: Cantina(self.game),
                    player_spawn=self.map_point((480, 400)),
                )
                return

            if self.stairs_door.can_interact(self.player):
                from scenes.laboratorio1 import Laboratorio1

                self.game.scene_manager.transition_to(
                    lambda: Laboratorio1(self.game),
                    player_spawn=Laboratorio1._fit_demo_point((1000, 875)),
                )
                return

        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        """Atualiza a cutscene, os NPCs e o jogador."""
        for item in self.items:
            item.update()
        self.update_camera(delta_time, self.cutscene_controller)
        self.cutscene_controller.update(delta_time)
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=(),
        )

        self.player.update(
            delta_time,
            accept_input=(
                # Diálogos, cutscene e inventário bloqueiam o controle para não andar durante as falas.
                not self.game.inventory_open
                and not self.game.dialogue_manager.is_active
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
            obstacles=self.npc_controller.get_player_obstacles(),
        )

    def draw(self, screen):
        """Desenha o fundo, personagens e interface da cena."""
        world = self.begin_world_draw()
        for item in self.items:
            item.draw(world)
        self.cutscene_controller.draw_trigger(world)
        self.draw_scene_entities(world, self.npc_controller.npcs)
        self.render_world(screen)

        nearby_item = next((item for item in self.items if item.can_interact(self.player)), None)
        if nearby_item is not None:
            prompt = self.hint_font.render(
                f"Pressione E para coletar {nearby_item.name}",
                True,
                (255, 255, 255),
            )
            screen.blit(
                prompt,
                prompt.get_rect(
                    midbottom=(screen.get_width() // 2, screen.get_height() - 18)
                ),
            )

        if (
            self.cutscene_controller.waiting_for == "trigger"
            and nearby_item is None
            and not any(
                door.can_interact(self.player)
                for door in (self.cantina_door, self.lab_door, self.stairs_door)
            )
            and self.npc_controller.get_nearest_interactable_npc() is None
        ):
            hint = self.hint_font.render(
                "Caminhe até o círculo amarelo para iniciar a história",
                True,
                (255, 255, 255),
            )
            screen.blit(
                hint,
                hint.get_rect(
                    midbottom=(screen.get_width() // 2, screen.get_height() - 18)
                ),
            )

        self.draw_door_hint(
            screen,
            self.hint_font,
            self.player,
            (
                self.cantina_door,
                self.lab_door,
                self.stairs_door,
            ),
        )
        self.npc_controller.draw_ui(screen, camera=self.camera)
        self.cutscene_controller.draw_overlay(screen)
