import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from entities.npc import NPC
from scenes.scene import Scene
from systems.camera_manager import CameraManager
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


class Laboratorio1(Scene):
    """Demonstra câmera, cutscenes, gatilhos e interações com NPCs."""

    WORLD_WIDTH = 2400
    WORLD_HEIGHT = 1400

    def __init__(self, game):
        super().__init__(game)
        self.player = game.player
        spawn = (760, 700)
        game.set_player_spawn_point(spawn)
        self.player.position.update(spawn)
        self.player.rect.center = spawn

        display = pygame.display.get_surface()
        screen_width, screen_height = (
            display.get_size()
            if display is not None
            else (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        # configura a câmera
        self.camera = CameraManager(
            self.WORLD_WIDTH,
            self.WORLD_HEIGHT,
            screen_width,
            screen_height,
            zoom=1.0,
        )
        # câmera segue o jogador, atualizando a cada milissegundo
        self.camera.follow(self.player)
        self.camera.update(0)
        # define o limite do mundo para que a câmera não ultrapasse os limites da cena
        self.bounds = pygame.Rect(
            0,
            0,
            self.WORLD_WIDTH,
            self.WORLD_HEIGHT,
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
                    position=(1600, 700), # cria um NPC fora da tela, mas dentro do mundo
                    sprite_path="assets/sprites/npcs/Idle_Down.png",
                    dialogue_id="diretor_demo_1",
                    use_player_animations=True,
                    interactable=True,
                    ambient_lines=(
                        "Se quiser, posso explicar como os gatilhos funcionam.",
                    ), # frases aleatórias que o NPC fala quando o jogador se aproxima, sem interação
                ),
            ),
            # define o escopo da classe para que o NPCController possa instanciar NPCs dinamicamente
            npc_scope=type(self),
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
            camera_move((1450, 700), duration=1.5, zoom=1.2),
            wait(0.4),
            dialogue_from_id("camera_demo_camera"),
            face_direction("professor_lab1", "left"),
            npc("professor_lab1", npc_arrival=(1620, 820)),
            spawn_npc(
                npc_id="assistente_demo_lab1",
                display_name="Assistente",
                position=(1850, 420),
                sprite_path="assets/sprites/npcs/Idle_Down.png",
                dialogue_id="camera_demo_interacao",
                use_player_animations=True,
                interactable=False,
            ),
            npc("professor_lab1", npc_arrival=(1700, 820)),
            npc("assistente_demo_lab1", npc_arrival=(1980, 420)),
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
            player_destination((820, 740)),
            # define o ponto de spawn do jogador para que, ao reiniciar a cena, ele comece no mesmo local
            set_player_spawn_point(spawn),
            camera_move((960, 700), duration=1.0, zoom=1.1),
            dialogue_from_id("camera_demo_gatilho"),
            trigger(
                trigger_position=(960, 740),
                trigger_radius=32,
                visible=True,
                action=dialogue_from_id("camera_demo_gatilho_ativado"),
            ),
            npc("professor_lab1", npc_arrival=(1500, 700)),
            camera_move((1550, 650), duration=1.0, zoom=1.2),
            dialogue_from_id("camera_demo_fade"),
            fade_out("assistente_demo_lab1", duration=0.8),
            time_passes(
                "Fim da demonstração",
                fade_out_duration=0.35,
                duration=0.6,
                fade_in_duration=0.45,
            ),
            camera_move(
                (820, 740),
                duration=1.0,
                zoom=1.0,
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
        self.npc_controller.handle_event(event)

    def update(self, delta_time):
        """Atualiza a câmera, a cutscene, entidades e controles do jogador."""
        # atualiza a câmera apenas se não estiver aguardando um movimento de câmera na cutscene
        if self.cutscene_controller.waiting_for != "camera_movement":
            self.camera.update(delta_time)
        
        # atualiza a cutscene, NPCs e jogador
        self.cutscene_controller.update(delta_time)
        
        # atualiza o controlador de NPCs, passando os limites do jogador e obstáculos para que ele possa gerenciar interações e movimentos
        player_obstacles = self.npc_controller.get_player_obstacles()
        
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
        ) # atualiza a câmera para seguir o jogador apenas se não houver cutscene ativa, permitindo que a cutscene controle a câmera durante movimentos de câmera ou diálogos
        if not self.cutscene_controller.is_active:
            self.camera.follow(self.player)

    def draw(self, screen):
        """Desenha o mundo em coordenadas absolutas e a interface na viewport."""
        # desenha o mundo em coordenadas absolutas, permitindo que a câmera controle a posição e o zoom da cena
        world = self.camera.world_surface # cria uma superfície do tamanho do mundo para desenhar os elementos da cena
        world.fill((43, 58, 56)) # cor de fundo do laboratório
        self._draw_map(world) # desenha o piso e os detalhes do laboratório no canvas do mundo
        self.cutscene_controller.draw_trigger(world) # desenha o gatilho da cutscene no mundo, permitindo que o jogador veja onde ele deve ir para ativar a cutscene
        self.npc_controller.draw_npcs(world) # desenha os NPCs no mundo, permitindo que eles sejam renderizados na posição correta em relação ao jogador e à câmera
        world.blit(self.player.image, self.player.rect) # desenha o jogador no mundo, permitindo que ele seja renderizado na posição correta em relação aos NPCs e à câmera

        self.camera.render(screen) # renderiza a superfície do mundo na tela, aplicando o zoom e a posição da câmera
        self.game.dialogue_manager.draw(screen) # desenha o diálogo na tela, permitindo que ele seja renderizado acima do mundo e da interface
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

        # desenha o título da cena e o zoom atual da câmera no canto superior esquerdo da tela
        title = self.title_font.render(
            f"Laboratório 1  |  Zoom {self.camera.zoom:.2f}x",
            True,
            (255, 255, 255),
        )
        screen.blit(title, (18, 14))
        if self.cutscene_controller.waiting_for == "trigger": # desenha uma dica para o jogador ir até o gatilho da cutscene, caso a cutscene esteja aguardando o jogador ativar o gatilho
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
        self.cutscene_controller.draw_overlay(screen) # desenha a sobreposição da cutscene na tela, permitindo que ela seja renderizada acima do mundo e da interface

    def _draw_map(self, surface):
        """Desenha o piso e os detalhes do laboratório no canvas do mundo."""
        pygame.draw.rect(
            surface,
            (71, 82, 76),
            pygame.Rect(
                80,
                80,
                self.WORLD_WIDTH - 160,
                self.WORLD_HEIGHT - 160,
            ),
        )
        pygame.draw.rect(
            surface,
            (117, 106, 78),
            pygame.Rect(1120, 400, 420, 600),
        )
        for x in range(100, self.WORLD_WIDTH, 80):
            pygame.draw.line(
                surface,
                (78, 90, 82),
                (x, 90),
                (x, self.WORLD_HEIGHT - 90),
                1,
            )
        for y in range(100, self.WORLD_HEIGHT, 80):
            pygame.draw.line(
                surface,
                (78, 90, 82),
                (90, y),
                (self.WORLD_WIDTH - 90, y),
                1,
            )
        for x in (300, 650, 1850, 2100):
            pygame.draw.rect(
                surface,
                (48, 72, 78),
                pygame.Rect(x, 260, 170, 90),
                border_radius=8,
            )
            pygame.draw.rect(
                surface,
                (48, 72, 78),
                pygame.Rect(x, 1030, 170, 90),
                border_radius=8,
            )
