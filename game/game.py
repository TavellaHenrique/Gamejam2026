
import pygame

# O gerenciador coordena as cenas e o gerenciador de diálogo mantém as falas.
from game.scenes.scene_manager import SceneManager
from game.systems.dialogue_manager import DialogueManager
from game.scenes.main_menu import MainMenu

from game.data.quests import create_quests
from game.systems.quests.quest_manager import QuestManager
from game.systems.quests.quest_status import QuestStatus

# Entidades compartilhadas podem ser acessadas por diferentes cenas do jogo.
from game.entities.player import Player


class Game:
    """Mantém o estado compartilhado durante toda a execução do jogo."""

    def __init__(self):
        """Cria as entidades e os gerenciadores centrais antes da primeira cena."""
        # O jogador e o inventário pertencem ao jogo, não a uma cena específica.
        self.player_spawn_point = pygame.Vector2(900, 610)
        self.player = Player(self.player_spawn_point)
        self.inventory = None  # Inventory()
        self.inventory_open = False
        self.inventory_selected_index = 0
        # Conclusões ficam no Game para sobreviver à recriação das cenas.
        self.completed_cutscenes = set()
        self.removed_npcs = set()
        self.story_flags = set()
        self.ending = None
        self.show_mouse_coordinates = False
        self.coordinates_font = pygame.font.Font(None, 24)

        # Gerenciador de Missões deve ser compartilhado entre  as cenas
        self.quest_manager = QuestManager(create_quests())

        # Os diálogos são carregados de um arquivo e podem ser consultados pelas cenas.
        self.dialogue_manager = DialogueManager(
            "data/dialogues.json"
        )

        # Começa no menu e permite trocar de cena sem encerrar o estado compartilhado.
        self.scene_manager = SceneManager(self)
        self.scene_manager.change_scene(MainMenu(self))

    def start_quest(self, quest_id):
        """Inicia uma missão e registra a mudança de estado no terminal."""
        quest = self.quest_manager.quests.get(quest_id)
        if quest is None:
            return False

        if not self.quest_manager.start_quest(quest_id):
            return False

        print(
            f"Missão atualizada: {quest.name} ({quest.quest_id}). "
            "Status: AVAIABLE -> ACTIVE"
        )
        return True

    def register_quest_event(self, event_type, target, amount=1):
        """Registra eventos e anuncia mudanças de progresso das missões."""
        previous_states = {
            quest_id: (
                quest.status,
                tuple(objective.progress for objective in quest.objectives),
            )
            for quest_id, quest in self.quest_manager.quests.items()
        }
        self.quest_manager.register_event(event_type, target, amount)
        for quest_id, quest in self.quest_manager.quests.items():
            previous_status, previous_progress = previous_states[quest_id]
            changed_objectives = [
                (objective, old_progress)
                for objective, old_progress in zip(
                    quest.objectives,
                    previous_progress,
                )
                if objective.progress != old_progress
            ]
            if not changed_objectives and quest.status == previous_status:
                continue

            print(f"Missão atualizada: {quest.name} ({quest.quest_id}).")
            for objective, _ in changed_objectives:
                print(
                    f"  {objective.objective_type} '{objective.target}': "
                    f"{objective.progress}/{objective.required}"
                    f"{' (concluído)' if objective.completed else ''}"
                )
            if quest.status != previous_status:
                print(
                    f"  Status: {previous_status.name} -> "
                    f"{quest.status.name}"
                )

        self.refresh_story_quest_unlocks()

    def refresh_story_quest_unlocks(self):
        """Libera o pen-drive quando todos os marcos anteriores foram concluídos."""
        if (
            self.quest_manager.get_status("find_lost_necklace")
            == QuestStatus.COMPLETED
            and "ruby_delivered" in self.story_flags
            and self.quest_manager.get_status("eat_snacks")
            == QuestStatus.COMPLETED
        ):
            self.quest_manager.unlock_quest("find_the_pendrive")

    def set_player_spawn_point(self, position):
        """Atualiza o ponto persistente onde o jogador deve surgir."""
        self.player_spawn_point.update(position)

    def handle_global_event(self, event):
        """Trata atalhos globais como coordenadas e inventário."""
        if self.scene_manager.is_paused:
            return False

        if (
            not self.inventory_open
            and self.show_mouse_coordinates
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            scene = self.scene_manager.current_scene
            print_debug_target = getattr(scene, "print_debug_target", None)
            if callable(print_debug_target):
                print_debug_target(event.pos)
                return True

        if event.type != pygame.KEYDOWN:
            return False

        if self.inventory_open:
            if event.key == pygame.K_i:
                self.inventory_open = False
                return True

            if event.key in (pygame.K_a, pygame.K_w, pygame.K_s, pygame.K_d):
                items = self.player.inventory.get_all_items() if self.player.inventory else []
                if not items:
                    return True

                cols = 4
                row, col = divmod(self.inventory_selected_index, cols)
                if event.key == pygame.K_a:
                    col = max(0, col - 1)
                elif event.key == pygame.K_d:
                    col = min(cols - 1, col + 1)
                elif event.key == pygame.K_w:
                    row = max(0, row - 1)
                elif event.key == pygame.K_s:
                    row = min((len(items) - 1) // cols, row + 1)

                new_index = min(len(items) - 1, row * cols + col)
                self.inventory_selected_index = new_index
                return True

            return True

        if event.key == pygame.K_i:
            self.inventory_open = not self.inventory_open
            if self.inventory_open:
                self.inventory_selected_index = 0
            return True

        if event.key != pygame.K_k:
            return False
        self.show_mouse_coordinates = not self.show_mouse_coordinates
        return True

    def draw_inventory(self, screen):
        """Desenha inventário e missões ativas em uma interface modal."""
        if not self.inventory_open or self.player is None:
            return

        items = self.player.inventory.get_all_items() if self.player.inventory else []
        panel_rect = pygame.Rect(20, 120, 540, 420)
        quest_panel_rect = pygame.Rect(580, 120, 360, 420)

        for rect in (panel_rect, quest_panel_rect):
            panel_surface = pygame.Surface(
                (rect.width, rect.height),
                pygame.SRCALPHA,
            )
            panel_surface.fill((15, 18, 28, 220))
            screen.blit(panel_surface, rect)
            pygame.draw.rect(
                screen,
                (76, 88, 102),
                rect,
                width=3,
                border_radius=8,
            )

        title_font = pygame.font.Font(None, 32)
        title = title_font.render("Mochila", True, (255, 255, 255))
        screen.blit(title, (panel_rect.x + 24, panel_rect.y + 18))

        hint_font = pygame.font.Font(None, 18)
        hint = hint_font.render("Pressione I para fechar", True, (180, 200, 220))
        screen.blit(
            hint,
            (panel_rect.right - hint.get_width() - 20, panel_rect.y + 24),
        )

        if not items:
            empty_font = pygame.font.Font(None, 26)
            empty_text = empty_font.render("Uma caneta e um sonho (o resto eu empresto de alguém)", True, (200, 200, 200))
            empty_rect = empty_text.get_rect(center=panel_rect.center)
            screen.blit(empty_text, empty_rect)
        else:
            slot_size = 92
            gap = 16
            cols = 4
            start_x = panel_rect.x + 32
            start_y = panel_rect.y + 70

            for index, item in enumerate(items):
                col = index % cols
                row = index // cols
                slot_rect = pygame.Rect(
                    start_x + col * (slot_size + gap),
                    start_y + row * (slot_size + gap + 28),
                    slot_size,
                    slot_size,
                )
                is_selected = index == self.inventory_selected_index
                fill_color = (
                    (155, 110, 255)
                    if is_selected
                    else (60, 70, 82)
                )
                outline_color = (
                    (255, 255, 255)
                    if is_selected
                    else (110, 128, 145)
                )
                pygame.draw.rect(
                    screen,
                    fill_color,
                    slot_rect,
                    border_radius=8,
                )
                pygame.draw.rect(
                    screen,
                    outline_color,
                    slot_rect,
                    width=2,
                    border_radius=8,
                )

                if item.image is not None:
                    icon_area = slot_rect.inflate(-16, -32)
                    icon_rect = item.image.get_rect().fit(icon_area)
                    icon = pygame.transform.scale(item.image, icon_rect.size)
                    screen.blit(icon, icon_rect)
                else:
                    icon = pygame.Surface((42, 42), pygame.SRCALPHA)
                    icon.fill((190, 170, 255, 200))
                    icon_rect = icon.get_rect(center=slot_rect.center)
                    icon_rect.y -= 8
                    screen.blit(icon, icon_rect)

            if self.inventory_selected_index < len(items):
                selected_item = items[self.inventory_selected_index]
                info_rect = pygame.Rect(
                    panel_rect.x + 32,
                    panel_rect.bottom - 70,
                    panel_rect.width - 64,
                    42,
                )
                pygame.draw.rect(
                    screen,
                    (200, 200, 200),
                    info_rect,
                    border_radius=8,
                )
                description_font = pygame.font.Font(None, 22)
                description = description_font.render(
                    f"{selected_item.name}: {selected_item.description}",
                    True,
                    (30, 30, 30),
                )
                screen.blit(
                    description,
                    (info_rect.x + 12, info_rect.y + 12),
                )

        self._draw_active_quests(screen, quest_panel_rect)

    def _draw_active_quests(self, screen, panel_rect):
        """Lista missões em andamento e o progresso dos objetivos."""
        title_font = pygame.font.Font(None, 32)
        quest_font = pygame.font.Font(None, 25)
        objective_font = pygame.font.Font(None, 21)
        screen.blit(
            title_font.render("Missões ativas", True, (255, 255, 255)),
            (panel_rect.x + 20, panel_rect.y + 18),
        )

        active_quests = [
            quest
            for quest in self.quest_manager.quests.values()
            if quest.status == QuestStatus.ACTIVE
        ]
        if not active_quests:
            empty_text = objective_font.render(
                "Nenhuma missão ativa.",
                True,
                (190, 200, 210),
            )
            screen.blit(empty_text, (panel_rect.x + 20, panel_rect.y + 72))
            return

        objective_labels = {
            "collect_item": "Coletar",
            "return_item": "Entregar",
        }
        item_labels = {
            "lab_key": "chave do laboratório",
            "professora_pendrive": "pen-drive",
            "cantina_vending_machine": "máquina de salgadinhos",
            "lost_necklace": "colar perdido",
        }
        objective_labels["interact_with"] = "Interagir"
        y = panel_rect.y + 68
        max_width = panel_rect.width - 40
        for quest in active_quests:
            y = self._draw_wrapped_text(
                screen,
                quest.name,
                quest_font,
                (230, 215, 160),
                panel_rect.x + 20,
                y,
                max_width,
            )
            y += 4
            for objective in quest.objectives:
                if objective.completed:
                    continue
                action = objective_labels.get(
                    objective.objective_type,
                    objective.objective_type.replace("_", " ").capitalize(),
                )
                target = item_labels.get(objective.target, objective.target)
                text = (
                    f"- {action}: {target} "
                    f"({objective.progress}/{objective.required})"
                )
                y = self._draw_wrapped_text(
                    screen,
                    text,
                    objective_font,
                    (210, 220, 230),
                    panel_rect.x + 24,
                    y,
                    max_width - 4,
                )
            y += 16

    @staticmethod
    def _draw_wrapped_text(
        screen,
        text,
        font,
        color,
        x,
        y,
        max_width,
    ):
        """Desenha um texto quebrado por palavras e retorna o Y seguinte."""
        lines = []
        current_line = ""
        for word in text.split():
            candidate = f"{current_line} {word}".strip()
            if current_line and font.size(candidate)[0] > max_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = candidate
        if current_line:
            lines.append(current_line)

        for line in lines:
            screen.blit(font.render(line, True, color), (x, y))
            y += font.get_linesize()
        return y

    def draw_debug_overlay(self, screen):
        """Shows mouse and world details while the collision debugger is active."""
        if not self.show_mouse_coordinates:
            return

        mouse_position = pygame.mouse.get_pos()
        lines = [
            f"Mouse X: {mouse_position[0]}  Y: {mouse_position[1]}",
            "Clique em um alvo para imprimir os dados no terminal.",
        ]
        scene = self.scene_manager.current_scene
        draw_debug_geometry = getattr(scene, "draw_debug_geometry", None)
        if callable(draw_debug_geometry):
            draw_debug_geometry(screen)
        get_debug_info = getattr(scene, "get_debug_info", None)
        if callable(get_debug_info):
            lines.extend(get_debug_info(mouse_position))

        labels = [
            self.coordinates_font.render(line, True, (255, 255, 255))
            for line in lines
        ]
        content_width = max(label.get_width() for label in labels)
        content_height = sum(label.get_height() for label in labels)
        background_rect = pygame.Rect(
            10,
            10,
            min(screen.get_width() - 20, content_width + 20),
            content_height + 16,
        )
        background = pygame.Surface(background_rect.size, pygame.SRCALPHA)
        background.fill((0, 0, 0, 180))
        screen.blit(background, background_rect)
        y = background_rect.y + 8
        for label in labels:
            screen.blit(label, (background_rect.x + 10, y))
            y += label.get_height()

    def _is_cutscene_active(self):
        """Considera tanto a cutscene da cena quanto a interação roteirizada de NPC."""
        scene = self.scene_manager.current_scene
        if scene is None:
            return False

        cutscene_controller = getattr(scene, "cutscene_controller", None)
        if cutscene_controller is not None and cutscene_controller.is_active:
            return True

        npc_controller = getattr(scene, "npc_controller", None)
        interaction_cutscene = getattr(
            npc_controller,
            "interaction_cutscene",
            None,
        )
        return (
            interaction_cutscene is not None
            and interaction_cutscene.is_active
        )

    def is_cutscene_completed(self, cutscene_id):
        """Verifica se uma cutscene já terminou nesta execução do jogo."""
        return cutscene_id in self.completed_cutscenes

    def mark_cutscene_completed(self, cutscene_id):
        """Registra a conclusão para impedir que a cutscene seja repetida."""
        self.completed_cutscenes.add(cutscene_id)

    def is_npc_removed(self, npc_id, npc_scope=None):
        """Verifica se um NPC foi removido neste escopo durante a execução."""
        return (npc_scope, npc_id) in self.removed_npcs

    def mark_npc_removed(self, npc_id, npc_scope=None):
        """Mantém removido um NPC quando o mesmo escopo for recriado."""
        self.removed_npcs.add((npc_scope, npc_id))
