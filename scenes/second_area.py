"""Cena de demonstração conectada à cena principal por uma porta."""

import pygame

from config import SCREEN_HEIGHT, SCREEN_WIDTH
from entities.door import Door
from entities.npc import NPC
from scenes.scene import Scene
from systems.npc_controller import NPCController


class SecondArea(Scene):
    """Área com porta, jogador e NPCs ambulantes."""

    def __init__(self, game, player_spawn=(145, 300)):
        """Cria a área e inicializa dois NPCs ambulantes."""
        super().__init__(game)
        self.player = game.player
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
            rect=(42, 245, 56, 112),
            prompt="Voltar para a área anterior",
        )
        ambient_lines = game.dialogue_manager.get_lines("falas_aleatorias")
        self.npcs = [
            NPC(
                npc_id="estudante_area_2_a",
                display_name="Estudante",
                position=(320, 190),
                sprite_path="assets/sprites/npcs/Idle_Down.png",
                dialogue_id="poema",
                ambient_radius=220,
                ambient_lines=ambient_lines,
                use_player_animations=True,
                interactable=False,
            ),
            NPC(
                npc_id="estudante_area_2_b",
                display_name="Estudante",
                position=(700, 420),
                sprite_path="assets/sprites/npcs/Idle_Down.png",
                dialogue_id="poema",
                ambient_radius=220,
                ambient_lines=ambient_lines,
                use_player_animations=True,
                interactable=False,
            ),
        ]
        self.npc_controller = NPCController(game, npcs=self.npcs)
        self.npc_controller.configure_wandering(
            self.npcs,
            self.bounds,
            obstacles=(self.door.rect,),
        )

    def handle_event(self, event):
        """Inicia o fade para a cena principal ao interagir com a porta."""
        if (
            # O jogador precisa usar o comando de interação.
            event.type == pygame.KEYDOWN
            # A porta responde à tecla E.
            and event.key == pygame.K_e
            # A área de interação só vale quando o jogador está próximo.
            and self.door.can_interact(self.player)
        ):
            from scenes.game_scene import GameScene

            self.game.scene_manager.transition_to(
                lambda: GameScene(self.game, player_spawn=(840, 300))
            )

    def update(self, delta_time):
        """Move entidades com colisão e escolhe destinos dos NPCs a cada cinco segundos."""
        self.player.update(
            delta_time,
            bounds=self.bounds,
            obstacles=self.npc_controller.get_player_obstacles(
                (self.door.rect,)
            ),
        )
        self.npc_controller.update(delta_time)

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
