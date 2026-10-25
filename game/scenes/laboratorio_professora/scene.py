"""Cena de exploração do laboratório da professora."""

import pygame

from game.entities.door import Door
from game.entities.npc import NPC
from game.items.item import Item
from game.scenes.saguao import Saguao
from game.scenes.laboratorio_professora.layout import (
    create_environment_obstacles,
    create_laboratory_objects,
)
from game.systems.cutscene_controller import (
    CutsceneController,
    face_direction,
    npc as cutscene_npc,
    player_destination,
    dialogue_from_id,
    time_passes_prompt,
)
from game.systems.npc_controller import NPCController
from game.systems.quests.quest_status import QuestStatus
from game.systems.tilemap_scene import TilemapScene
from game.ui.text import draw_prompt


class LaboratorioProfessora(TilemapScene):
    """Laboratório da Professora Amélia, suas missões e seus desfechos."""

    def __init__(self, game, player_spawn=None):
        """Monta o cenário, itens, personagens e estado da história."""
        super().__init__(
            game,
            "assets/tileset/laboratorio/laboratorio_base.jpg",
            player_spawn=player_spawn,
        )
        self.game.quest_manager.unlock_quest("find_the_key")
        self.door = Door(
            rect=self.map_rect((862, 10, 43, 87)),
            prompt="Saguão",
            interaction_margin=72,
            visible=False,
        )
        self.doors = (self.door,)
        self.environment_obstacles = create_environment_obstacles(self)
        self.map_objects = create_laboratory_objects(self)
        self.title_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            36,
        )
        self.hint_font = pygame.font.Font(
            "assets/fonts/typewcond_regular.otf",
            20,
        )
        self.ending_font = pygame.font.Font(None, 28)
        self.items = [
            Item(
                item_id="professora_pendrive",
                name="Pen-drive",
                description="O pen-drive usado pela Professora Amélia.",
                image_path=(
                    "assets/sprites/items/"
                    "vecteezy_pixel-art-usb-flashdisk-drive-icon.png"
                ),
                position=self.map_point((500, 225)),
                interaction_radius=48,
                world_image_size=(48, 48),
            ),
            Item(
                item_id="essence_stone",
                name="Pedra da Essência",
                description="Uma pedra de origem desconhecida.",
                position=self.map_point((700, 540)),
                interaction_radius=48,
            ),
        ]
        for item in self.items:
            if self.player.inventory.has_item(item.id):
                item.collected = True
                item.visible = False
        if (
            self.game.quest_manager.get_status("find_the_pendrive")
            != QuestStatus.ACTIVE
        ):
            self.items[0].visible = False
        self.dialogue_flow = None
        self.choice_active = False
        self.professora = NPC(
            npc_id="professora",
            display_name="Professora Amélia",
            position=self.map_point((700, 160)),
            sprite_path="assets/sprites/npcs/character2.png",
            dialogue_id="professora_introducao",
            interactable=True,
        )
        self.npc_controller = NPCController(
            game,
            npcs=(self.professora,),
            npc_scope=type(self),
            static_obstacles=self.get_scene_obstacles(),
        )
        self.lesson_cutscene = None
        self.lesson_followup_cutscene = None

    def handle_event(self, event):
        """Encaminha as interações, a investigação e a escolha do desfecho."""
        if self.is_inventory_open():
            return

        if self.game.ending is not None:
            return

        if self.choice_active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self._choose_ending("accepted")
                elif event.key == pygame.K_2:
                    self._choose_ending("refused")
            return

        if (
            self.lesson_cutscene is not None
            and self.lesson_cutscene.handle_event(event)
        ):
            return
        if (
            self.lesson_followup_cutscene is not None
            and self.lesson_followup_cutscene.handle_event(event)
        ):
            return

        was_dialogue_active = self.game.dialogue_manager.is_active
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not was_dialogue_active
        ):
            for item in self.items:
                if item.can_interact(self.player):
                    if item.pick_up(self.player):
                        if item.id == "professora_pendrive":
                            self.game.register_quest_event(
                                "collect_item",
                                item.id,
                            )
                            self.npc_controller.start_monologue(
                                "pensamento_encontra_chaveiro"
                            )
                    return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not was_dialogue_active
            and self.door.can_interact(self.player)
        ):
            self.game.scene_manager.transition_to(
                lambda: Saguao(self.game),
                player_spawn=Saguao.map_point((900, 150)),
            )
            return

        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
            and not self.game.dialogue_manager.is_active
        ):
            nearby_npc = self.npc_controller.get_nearest_interactable_npc()
            if nearby_npc is self.professora:
                self._update_story_quest_unlocks()
                quest_status = self.game.quest_manager.get_status(
                    "find_the_key"
                )
                necklace_status = self.game.quest_manager.get_status(
                    "find_lost_necklace"
                )
                if (
                    necklace_status == QuestStatus.LOCKED
                    and self.player.inventory.has_item("lost_necklace")
                ):
                    self.game.quest_manager.unlock_quest(
                        "find_lost_necklace"
                    )
                    self.game.start_quest("find_lost_necklace")
                    self.game.register_quest_event(
                        "collect_item",
                        "lost_necklace",
                    )
                    necklace_status = QuestStatus.ACTIVE
                pendrive_status = self.game.quest_manager.get_status(
                    "find_the_pendrive"
                )
                snack_status = self.game.quest_manager.get_status(
                    "eat_snacks"
                )
                if quest_status == QuestStatus.AVAIABLE:
                    self.game.start_quest("find_the_key")
                    self.professora.dialogue_id = "professora_introducao"
                elif (
                    quest_status == QuestStatus.ACTIVE
                    and self.player.inventory.has_item("lab_key")
                ):
                    self.professora.dialogue_id = (
                        "professora_chave_devolvida"
                    )
                    self.player.inventory.remove_item("lab_key")
                    self.game.register_quest_event(
                        "return_item",
                        "lab_key",
                    )
                    self.dialogue_flow = "key_return"
                elif (
                    necklace_status == QuestStatus.ACTIVE
                    and self.player.inventory.has_item("lost_necklace")
                ):
                    self.professora.dialogue_id = (
                        "professora_colar_encontrado"
                    )
                    self.dialogue_flow = "necklace_report"
                elif (
                    pendrive_status == QuestStatus.AVAIABLE
                    and "investigation_unlocked" in self.game.story_flags
                    and snack_status == QuestStatus.COMPLETED
                ):
                    self.game.start_quest("find_the_pendrive")
                    self.items[0].visible = True
                    self.professora.dialogue_id = (
                        "professora_missao_chaveiro"
                    )
                elif (
                    snack_status == QuestStatus.COMPLETED
                    and necklace_status != QuestStatus.COMPLETED
                    and not self.player.inventory.has_item("lost_necklace")
                ):
                    self.professora.dialogue_id = (
                        "professora_colar_pendente"
                    )
                elif (
                    "investigation_unlocked" in self.game.story_flags
                    and snack_status == QuestStatus.COMPLETED
                    and pendrive_status == QuestStatus.ACTIVE
                    and self.player.inventory.has_item(
                        "professora_pendrive"
                    )
                ):
                    self.professora.dialogue_id = (
                        "entrega_pendrive_professora"
                    )
                    self.player.inventory.remove_item(
                        "professora_pendrive"
                    )
                    self.game.register_quest_event(
                        "return_item",
                        "professora_pendrive",
                    )
                    self.dialogue_flow = "pendrive_revelation"
                elif (
                    "investigation_unlocked" in self.game.story_flags
                    and snack_status == QuestStatus.COMPLETED
                    and pendrive_status == QuestStatus.ACTIVE
                ):
                    self.professora.dialogue_id = (
                        "professora_missao_chaveiro"
                    )
                elif quest_status == QuestStatus.ACTIVE:
                    if necklace_status == QuestStatus.COMPLETED:
                        self.npc_controller.start_monologue_lines(
                            (
                                "Ah, você está aí? Estava apenas pensando "
                                "alto... de qualquer maneira, preciso "
                                "daquela chave!",
                            ),
                            npc=self.professora,
                        )
                    else:
                        self.npc_controller.start_monologue(
                            "professora_monologo",
                            npc=self.professora,
                        )
                    return
                else:
                    self.professora.dialogue_id = (
                        "professora_chave_devolvida"
                        if quest_status == QuestStatus.COMPLETED
                        else "professora_introducao"
                    )

        self.npc_controller.handle_event(event)
        if (
            was_dialogue_active
            and not self.game.dialogue_manager.is_active
            and event.type == pygame.KEYDOWN
            and event.key == pygame.K_e
        ):
            self._continue_dialogue_flow()

    def _continue_dialogue_flow(self):
        """Avança a aula e o desfecho após cada diálogo roteirizado."""
        flow = self.dialogue_flow
        self.dialogue_flow = None

        if flow == "key_return":
            self.dialogue_flow = "lesson_staging"
            self.lesson_cutscene = CutsceneController.create_story_cutscene(
                self.game,
                self.npc_controller,
                cutscene_npc(
                    "professora",
                    self.map_point((820, 220)),
                ),
                player_destination(self.map_point((650, 220))),
                face_direction("professora", "left"),
                face_direction("player", "right"),
                cutscene_id="professora_hardware_lesson",
                bounds=self.bounds,
                camera=self.camera,
            )
            self.lesson_cutscene.start()
        elif flow == "lesson":
            self.dialogue_flow = "lesson_followup"
            self.lesson_followup_cutscene = (
                CutsceneController.create_story_cutscene(
                    self.game,
                    self.npc_controller,
                    time_passes_prompt(),
                    dialogue_from_id("professora_encontrar_rubi"),
                    dialogue_from_id("passando_mal_luz"),
                    cutscene_id="professora_rubi_and_symptoms",
                    bounds=self.bounds,
                    camera=self.camera,
                )
            )
            self.lesson_followup_cutscene.start()
        elif flow == "necklace_report":
            self.player.inventory.remove_item("lost_necklace")
            self.game.register_quest_event(
                "report_item",
                "lost_necklace",
            )
            self._update_story_quest_unlocks()
        elif flow == "pendrive_revelation":
            self.dialogue_flow = "offer"
            self.npc_controller.start_monologue(
                "oferta_transformacao",
                npc=self.professora,
            )
        elif flow == "offer":
            self.choice_active = True
        elif flow == "accepted":
            self.game.ending = "accepted"
        elif flow == "refused":
            self.game.ending = "battle_pending"

    def _update_story_quest_unlocks(self):
        """Libera a missão do pen-drive após os marcos obrigatórios."""
        self.game.refresh_story_quest_unlocks()

    def _choose_ending(self, outcome):
        """Inicia o diálogo correspondente à escolha do jogador."""
        if outcome == "accepted":
            dialogue_id = "final_aceitar_transformacao"
        else:
            dialogue_id = "final_recusar_transformacao"

        self.choice_active = False
        self.dialogue_flow = outcome
        self.npc_controller.start_monologue(
            dialogue_id,
            npc=self.professora,
        )

    def update(self, delta_time):
        """Atualiza câmera, professora e jogador com as colisões do laboratório."""
        self.update_camera(
            delta_time,
            self.lesson_followup_cutscene or self.lesson_cutscene,
        )
        player_obstacles = self.npc_controller.get_player_obstacles(
            self.get_door_obstacles()
        )
        self.npc_controller.update(
            delta_time,
            player_bounds=self.bounds,
            player_obstacles=player_obstacles,
        )
        if self.lesson_cutscene is not None:
            self.lesson_cutscene.update(delta_time)
            if (
                not self.lesson_cutscene.is_active
                and self.dialogue_flow == "lesson_staging"
            ):
                self.dialogue_flow = "lesson"
                self.npc_controller.start_monologue(
                    "professora_aula_introducao",
                    npc=self.professora,
                )
        if self.lesson_followup_cutscene is not None:
            self.lesson_followup_cutscene.update(delta_time)
            if (
                not self.lesson_followup_cutscene.is_active
                and self.dialogue_flow == "lesson_followup"
            ):
                self.dialogue_flow = None
                self.game.story_flags.add("ruby_delivered")
                self.game.story_flags.add("investigation_unlocked")
                self.game.refresh_story_quest_unlocks()
                self.game.quest_manager.unlock_quest("eat_snacks")
                self.game.start_quest("eat_snacks")
        if (
            self.npc_controller.active_dialogue_npc is self.professora
            and self.game.quest_manager.get_status("find_lost_necklace")
            == QuestStatus.COMPLETED
        ):
            self._update_story_quest_unlocks()
        self.player.update(
            delta_time,
            accept_input=(
                not self.game.inventory_open
                and not self.game.dialogue_manager.is_active
                and not self.choice_active
                and self.game.ending is None
                and not (
                    self.lesson_cutscene is not None
                    and self.lesson_cutscene.locks_player_control
                )
                and not (
                    self.lesson_followup_cutscene is not None
                    and self.lesson_followup_cutscene.locks_player_control
                )
                and not self.npc_controller.interaction_cutscene.is_active
                and not self.npc_controller.is_approaching_npc
                and self.npc_controller.pending_interaction_npc is None
            ),
            bounds=self.bounds,
            obstacles=player_obstacles,
        )

    def draw(self, screen):
        """Renderiza o cenário, os objetos ordenados e a interface da cena."""
        world = self.begin_world_draw()
        self.draw_scene_entities(world, self.npc_controller.npcs)
        for item in self.items:
            item.draw(world)
        self.render_world(screen)

        self.npc_controller.draw_ui(screen, camera=self.camera)
        title = self.title_font.render(
            "Laboratório da Professora",
            True,
            (255, 255, 255),
        )
        screen.blit(title, (24, 20))
        self.draw_door_hint(
            screen,
            self.hint_font,
            self.player,
            self.doors,
            dialogue_manager=self.game.dialogue_manager,
        )
        nearby_item = next(
            (item for item in self.items if item.can_interact(self.player)),
            None,
        )
        if nearby_item is not None:
            draw_prompt(
                screen,
                f"E - Coletar {nearby_item.name}",
                self.hint_font,
                dialogue_manager=self.game.dialogue_manager,
            )
        if self.choice_active:
            self._draw_ending_choice(screen)
        elif self.game.ending == "accepted":
            self._draw_ending_screen(
                screen,
                "Você aceitou a transformação.",
            )
        elif self.game.ending == "battle_pending":
            self._draw_ending_screen(
                screen,
                "Minigame final: as mecânicas de combate e as condições "
                "de vitória ainda precisam ser definidas.",
            )
        if self.lesson_cutscene is not None:
            self.lesson_cutscene.draw_overlay(screen)
        if self.lesson_followup_cutscene is not None:
            self.lesson_followup_cutscene.draw_overlay(screen)

    def _draw_ending_choice(self, screen):
        """Mostra as duas escolhas de transformação do documento."""
        self._draw_ending_screen(
            screen,
            "1 - Aceitar a transformação     2 - Recusar",
        )

    def _draw_ending_screen(self, screen, message):
        """Desenha um painel central de história sobre a cena."""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(100, 220, screen.get_width() - 200, 180)
        pygame.draw.rect(screen, (24, 24, 36), panel, border_radius=12)
        pygame.draw.rect(
            screen,
            (210, 190, 130),
            panel,
            width=3,
            border_radius=12,
        )
        words = message.split()
        lines = []
        current_line = ""
        for word in words:
            candidate = f"{current_line} {word}".strip()
            if (
                current_line
                and self.ending_font.size(candidate)[0] > panel.width - 48
            ):
                lines.append(current_line)
                current_line = word
            else:
                current_line = candidate
        if current_line:
            lines.append(current_line)

        line_height = self.ending_font.get_linesize()
        y = panel.centery - len(lines) * line_height // 2
        for line in lines:
            label = self.ending_font.render(line, True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=(panel.centerx, y)))
            y += line_height
