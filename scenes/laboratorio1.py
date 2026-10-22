import pygame

from entities.door import Door
from entities.npc import NPC
from scenes.saguao import Saguao
from systems.cutscene_controller import (
    CutsceneController,
    camera_move,
    change_scene,
    dialogue,
    dialogue_from_id,
    face_direction,
    fade_out,
    npc,
    npc_dialogue,
    player_destination,
    set_player_spawn_point,
    spawn_npc,
    time_passes,
    trigger,
    wait,
)
from systems.npc_controller import NPCController
from systems.tilemap_scene import LABORATORY_OBSTACLES, TilemapScene


class Laboratorio1(TilemapScene):
    """Demonstra câmera, cutscenes, gatilhos e interações com NPCs."""

    DEMO_WIDTH = 2400
    DEMO_HEIGHT = 1400

    @classmethod
    def _fit_demo_point(cls, position):
        """Maps former demo-world coordinates onto the enlarged tileset."""
        world_width = round(960 * cls.TILESET_SCALE)
        world_height = round(640 * cls.TILESET_SCALE)
        return (
            round(position[0] * world_width / cls.DEMO_WIDTH),
            round(position[1] * world_height / cls.DEMO_HEIGHT),
        )

    def __init__(self, game):
        spawn = self._fit_demo_point((1000, 875))
        super().__init__(
            game,
            "assets/tileset/laboratorio.jpeg",
            player_spawn=spawn,
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
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            28,
        )
        self.hint_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            22,
        )

        self.npc_controller = NPCController(
            game,
            npcs=(
                NPC(
                    npc_id="professor_lab1",
                    display_name="Professor",
                    position=self._fit_demo_point((1800, 700)),
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="diretor_demo_1",
                    use_player_animations=True,
                    animation_scale=3,
                    interactable=True,
                    ambient_lines=(
                        "Se quiser, posso explicar como os gatilhos funcionam.",
                    ), # frases aleatórias que o NPC fala quando o jogador se aproxima, sem interação
                ),
                *(
                    NPC(
                        npc_id=f"lab1_seated_{index}",
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
                    for index, position in enumerate(
                        ((105, 285), (273, 370), (465, 285), (658, 370)),
                        1,
                    )
                ),
            ),
            # define o escopo da classe para que o NPCController possa instanciar NPCs dinamicamente
            npc_scope=type(self),
            static_obstacles=self.environment_obstacles,
        )
        self.cutscene_controller = CutsceneController.create_story_cutscene(
            game,
            self.npc_controller,
            time_passes(
                "Demonstração de câmera e cutscenes",
                fade_out_duration=0.35,
                duration=0.8,
                fade_in_duration=0.45,
            ),
            dialogue_from_id("camera_demo_abertura"),
            # define a posição inicial da câmera e o zoom para a demonstração
            camera_move(
                self._fit_demo_point((1450, 700)),
                duration=1.5,
                zoom=self.camera.zoom,
            ),
            wait(0.4),
            dialogue_from_id("camera_demo_camera"),
            face_direction("professor_lab1", "left"),
            npc(
                "professor_lab1",
                npc_arrival=self._fit_demo_point((1800, 820)),
            ),
            spawn_npc(
                npc_id="assistente_demo_lab1",
                display_name="Assistente",
                position=self._fit_demo_point((1850, 420)),
                sprite_path="assets/sprites/npcs/Idle_Down.png",
                dialogue_id="camera_demo_interacao",
                use_player_animations=True,
                animation_scale=3,
                interactable=False,
            ),
            npc(
                "professor_lab1",
                npc_arrival=self._fit_demo_point((1900, 820)),
            ),
            npc(
                "assistente_demo_lab1",
                npc_arrival=self._fit_demo_point((1980, 420)),
            ),
            face_direction("professor_lab1", "left"),
            face_direction("assistente_demo_lab1", "left"),
            npc_dialogue(
                "assistente_demo_lab1",
                "Esta fala foi iniciada pelo ID do NPC, sem precisar abrir "
                "um diálogo de interação.",
            ),
            dialogue(
                "Esta é uma fala inline da cutscene, sem entrada no JSON.",
                speaker="Calouro",
            ),
            dialogue_from_id("camera_demo_movimento"),
            player_destination(self._fit_demo_point((1000, 740))),
            # define o ponto de spawn do jogador para que, ao reiniciar a cena, ele comece no mesmo local
            set_player_spawn_point(spawn),
            camera_move(
                self._fit_demo_point((960, 700)),
                duration=1.0,
                zoom=self.camera.zoom,
            ),
            dialogue_from_id("camera_demo_gatilho"),
            trigger(
                trigger_position=self._fit_demo_point((960, 740)),
                trigger_radius=48,
                visible=True,
                action=dialogue_from_id("camera_demo_gatilho_ativado"),
            ),
            npc(
                "professor_lab1",
                npc_arrival=self._fit_demo_point((1800, 700)),
            ),
            camera_move(
                self._fit_demo_point((1550, 650)),
                duration=1.0,
                zoom=self.camera.zoom,
            ),
            dialogue_from_id("camera_demo_fade"),
            fade_out("assistente_demo_lab1", duration=0.8),
            time_passes(
                "Fim da demonstração",
                fade_out_duration=0.35,
                duration=0.6,
                fade_in_duration=0.45,
            ),
            camera_move(
                self._fit_demo_point((820, 740)),
                duration=1.0,
                zoom=self.camera.zoom,
            ),
            dialogue_from_id("camera_demo_final"),
            change_scene(
                lambda: Laboratorio1(game),
                player_spawn=spawn,
                text="Retornando ao início da demonstração",
                fade_out_duration=0.35,
                duration=0.6,
                fade_in_duration=0.35,
            ),
            cutscene_id="camera_demo_lab1", # define um ID para a cutscene, permitindo que o jogo saiba se ela já foi concluída e não precise ser repetida
            bounds=self.bounds, # passa os limites do mundo para a cutscene para que ela possa controlar a câmera corretamente
            camera=self.camera, # passa a câmera para a cutscene para que ela possa controlar o movimento da câmera durante a demonstração
        )
        # inicia a cutscene automaticamente ao entrar na cena
        self.cutscene_controller.start()

    def handle_event(self, event):
        """Encaminha eventos à cutscene e ao sistema de interação dos NPCs."""
        if self.cutscene_controller.handle_event(event):
            return
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.cutscene_controller.is_active
            and not self.game.dialogue_manager.is_active
            and self.door.can_interact(self.player)
        ):
            self.game.scene_manager.transition_to(
                lambda: Saguao(self.game),
                player_spawn=Saguao.map_point((700, 520)),
            )
            return
        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        """Atualiza a câmera, a cutscene, entidades e controles do jogador."""
        # atualiza a câmera apenas se não estiver aguardando um movimento de câmera na cutscene
        self.update_camera(delta_time, self.cutscene_controller)
        
        # atualiza a cutscene, NPCs e jogador
        self.cutscene_controller.update(delta_time)
        
        # atualiza o controlador de NPCs, passando os limites do jogador e obstáculos para que ele possa gerenciar interações e movimentos
        player_obstacles = self.npc_controller.get_player_obstacles(
            self.get_door_obstacles()
        )
        
        # atualiza o controlador de NPCs, passando os limites do jogador e obstáculos para que ele possa gerenciar interações e movimentos
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=player_obstacles,
        )
        
        # atualiza o jogador, permitindo entrada apenas se não houver cutscene ativa, diálogo ativo ou interação com NPCs em andamento
        self.player.update(
            delta_time,
            accept_input=(
                not self.game.dialogue_manager.is_active
                and not self.cutscene_controller.locks_player_control
                and not self.npc_controller.interaction_cutscene.is_active
                and not self.npc_controller.is_approaching_npc
                and self.npc_controller.pending_interaction_npc is None
            ),
            bounds=self.bounds,
            obstacles=player_obstacles,
        )

    def draw(self, screen):
        """Desenha o mundo em coordenadas absolutas e a interface na viewport."""
        # desenha o mundo em coordenadas absolutas, permitindo que a câmera controle a posição e o zoom da cena
        world = self.begin_world_draw()
        self.cutscene_controller.draw_trigger(world)
        self.npc_controller.draw_npcs(world)
        world.blit(self.player.image, self.player.rect)
        self.render_world(screen)
        self.npc_controller.draw_ui(screen, camera=self.camera)
        if (
            not self.game.dialogue_manager.is_active
            and not self.game.dialogue_manager.is_ambient_active
            and self.npc_controller.get_nearest_interactable_npc() is not None
        ):
            hint = self.hint_font.render(
                "E - Interagir",
                True,
                (255, 255, 255),
            )
            screen.blit(
                hint,
                hint.get_rect(
                    midbottom=(screen.get_width() // 2, screen.get_height() - 18)
                ),
            )

        title = self.title_font.render(
            "Laboratório 1",
            True,
            (255, 255, 255),
        )
        screen.blit(title, (18, 14))
        if self.cutscene_controller.waiting_for == "trigger":
            hint = self.hint_font.render(
                "Demonstração: caminhe até o círculo amarelo (WASD)",
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
            self.doors,
        )
        self.cutscene_controller.draw_overlay(screen)
