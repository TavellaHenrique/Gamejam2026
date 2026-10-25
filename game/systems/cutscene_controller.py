from dataclasses import dataclass

import pygame

from game.entities.npc import NPC
from game.systems.collision import can_occupy
from game.systems.cutscene import Cutscene
from game.systems.navigation import find_path, find_path_near_target
from game.systems.trigger import Trigger as AreaTrigger


@dataclass(frozen=True)
class CutsceneAction:
    """Descreve uma ação declarativa para compor uma cutscene."""

    kind: str
    options: dict


def npc(npc_id, npc_arrival):
    """Cria uma ação de movimento para o NPC identificado por npc_id."""
    return CutsceneAction(
        "npc",
        {"npc_id": npc_id, "destination": npc_arrival},
    )


def npcs(destinations):
    """Move vários NPCs em paralelo com um mapeamento ID -> destino."""
    if not destinations:
        raise ValueError("Informe ao menos um NPC para movimentar.")
    return CutsceneAction("npcs", {"destinations": dict(destinations)})


def face_direction(actor_id, direction):
    """Orienta o jogador ou um NPC para uma direção explícita."""
    return CutsceneAction(
        "face_direction",
        {"actor_id": actor_id, "direction": direction},
    )


def player_destination(destination, obstacles=()):
    """Cria uma ação de movimento do jogador até um destino."""
    return CutsceneAction(
        "player",
        {"destination": destination, "obstacles": tuple(obstacles)},
    )


def camera_move(position, duration=0.75, zoom=None):
    """Move suavemente a câmera até um ponto durante uma cutscene."""
    if duration < 0:
        raise ValueError("A duração do movimento de câmera não pode ser negativa.")
    if zoom is not None and zoom <= 0:
        raise ValueError("O zoom da câmera deve ser positivo.")
    return CutsceneAction(
        "camera_move",
        {
            "position": tuple(position),
            "duration": duration,
            "zoom": zoom,
        },
    )


def set_player_spawn_point(position):
    """Define onde o jogador surgirá quando uma cena não informar outro ponto."""
    return CutsceneAction(
        "set_player_spawn_point",
        {"position": tuple(position)},
    )


def wait(seconds):
    """Cria uma pausa temporizada na sequência."""
    return CutsceneAction("wait", {"seconds": seconds})


def change_scene(
    scene_factory,
    duration=None,
    player_spawn=None,
    text=None,
    fade_out_duration=None,
    fade_in_duration=None,
    font_size=36,
):
    """Troca de cena, opcionalmente com a pausa e legenda de time_passes."""
    if not callable(scene_factory):
        raise TypeError("scene_factory precisa ser uma função chamável.")
    if player_spawn is not None:
        player_spawn = tuple(player_spawn)

    has_time_passes = any(
        value is not None
        for value in (text, fade_out_duration, fade_in_duration)
    )
    if has_time_passes:
        hold_duration = 1.5 if duration is None else duration
        fade_out_duration = (
            0.5 if fade_out_duration is None else fade_out_duration
        )
        fade_in_duration = (
            0.5 if fade_in_duration is None else fade_in_duration
        )
        if any(
            value < 0
            for value in (
                fade_out_duration,
                hold_duration,
                fade_in_duration,
            )
        ):
            raise ValueError("Durações de transição não podem ser negativas.")
        if font_size <= 0:
            raise ValueError("O tamanho da fonte precisa ser positivo.")
        transition = (
            text or "",
            fade_out_duration,
            hold_duration,
            fade_in_duration,
            font_size,
        )
        transition_duration = None
    else:
        transition_duration = 0.5 if duration is None else duration
        if transition_duration <= 0:
            raise ValueError("A duração da transição precisa ser positiva.")
        transition = None

    return CutsceneAction(
        "change_scene",
        {
            "scene_factory": scene_factory,
            "duration": transition_duration,
            "player_spawn": player_spawn,
            "transition": transition,
        },
    )


def time_passes(
    text="Passa um tempo",
    fade_out_duration=0.5,
    duration=1.5,
    fade_in_duration=0.5,
    font_size=36,
):
    """Escurece a tela, mantém uma legenda e retorna gradualmente à cena."""
    durations = (fade_out_duration, duration, fade_in_duration)
    if any(value < 0 for value in durations):
        raise ValueError("Durações de transição não podem ser negativas.")
    if font_size <= 0:
        raise ValueError("O tamanho da fonte precisa ser positivo.")
    return CutsceneAction(
        "time_passes",
        {
            "text": text,
            "fade_out_duration": fade_out_duration,
            "duration": duration,
            "fade_in_duration": fade_in_duration,
            "font_size": font_size,
        },
    )


def time_passes_prompt():
    """Cria uma tela de passagem do tempo que aguarda confirmação por ENTER."""
    return CutsceneAction(
        "time_passes_prompt",
        {
            "text": "Algum tempo depois...",
            "continue_text": "Pressione ENTER para continuar",
        },
    )


def dialogue(text, speaker="Calouro"):
    """Cria uma fala inline, sem exigir uma entrada no JSON."""
    return CutsceneAction(
        "dialogue",
        {"text": text, "speaker": speaker},
    )


def dialogue_from_id(dialogue_id, speaker=None):
    """Busca texto e falante pelo ID; permite sobrescrever o nome se necessário."""
    return CutsceneAction(
        "dialogue_from_id",
        {
            "dialogue_id": dialogue_id,
            "speaker": speaker,
        },
    )


def npc_dialogue(npc_id, text):
    """Cria uma fala inline atribuída ao NPC indicado."""
    return CutsceneAction(
        "npc_dialogue",
        {"npc_id": npc_id, "text": text},
    )


def spawn_npc(remove_at_end=True, **npc_options):
    """Cria um NPC durante o roteiro e o remove ao fim por padrão."""
    if "npc_id" not in npc_options:
        raise ValueError("NPC temporário precisa de npc_id.")
    return CutsceneAction(
        "spawn_npc",
        {
            "npc_options": dict(npc_options),
            "remove_at_end": remove_at_end,
        },
    )


def fade_out(npc_id, duration=1.0):
    """Faz o NPC desaparecer gradualmente e o remove ao concluir."""
    if duration < 0:
        raise ValueError("A duração do fade-out não pode ser negativa.")
    return CutsceneAction(
        "fade_out",
        {"npc_id": npc_id, "duration": duration},
    )


def trigger(
    trigger_position=None,
    trigger_radius=None,
    action=None,
    visible=False,
    trigger_rect=None,
):
    """Cria um gatilho de entrada e as ações a executar quando ativado."""
    # O gatilho deve definir exatamente uma geometria: círculo ou retângulo.
    if trigger_rect is None and (
        trigger_position is None or trigger_radius is None
    ):
        raise ValueError("Informe trigger_rect ou posição e raio.")
    if trigger_rect is not None and (
        trigger_position is not None or trigger_radius is not None
    ):
        raise ValueError("Use trigger_rect ou posição e raio, não ambos.")
    if action is None:
        raise ValueError("Informe ao menos uma ação para o trigger.")

    if isinstance(action, CutsceneAction):
        actions = (action,)
    else:
        actions = tuple(action)
    # Exige ações presentes; em seguida valida o tipo de cada uma.
    if not actions or not all(
        isinstance(item, CutsceneAction) for item in actions
    ):
        raise TypeError("As ações do trigger devem ser CutsceneAction.")
    return CutsceneAction(
        "trigger",
        {
            "position": trigger_position,
            "radius": trigger_radius,
            "rect": trigger_rect,
            "visible": visible,
            "actions": actions,
        },
    )


class CutsceneController:
    """Executa sequências de gatilhos, movimento, orientação e diálogo."""

    def __init__(
        self,
        player,
        npc_controller,
        dialogue_manager,
        game,
        cutscene_id,
        bounds=None,
        camera=None,
    ):
        self.player = player
        self.npc_controller = npc_controller
        self.dialogue_manager = dialogue_manager
        self.game = game
        self.cutscene_id = cutscene_id
        self.bounds = bounds
        self.camera = camera
        self.steps = []
        self.step_index = 0
        self.is_active = False
        self.waiting_for = None
        self.waiting_for_npc_ids = ()
        self.player_obstacles = ()
        self.player_cutscene = Cutscene()
        self.trigger = None
        self.triggers = []
        self.wait_timer = 0.0
        self.fade_npc_id = None
        self.fade_elapsed = 0.0
        self.fade_duration = 0.0
        self.temporary_npc_ids = set()
        self.screen_transition = None
        self.screen_transition_elapsed = 0.0
        self.screen_transition_font = None
        self.screen_transition_font_size = None
        self.time_passes_message = None
        self.time_passes_hint = None

    @classmethod
    def create_story_cutscene(
        cls,
        game,
        npc_controller,
        *actions,
        cutscene_id,
        bounds=None,
        camera=None,
    ):
        """Monta uma sequência identificada e persistente na execução atual."""
        if not cutscene_id:
            raise ValueError("Toda cutscene precisa de um cutscene_id.")
        cutscene = cls(
            game.player,
            npc_controller,
            game.dialogue_manager,
            game,
            cutscene_id,
            bounds=bounds,
            camera=camera,
        )
        if not actions:
            raise ValueError("Informe ao menos uma ação para a cutscene.")
        for action in actions:
            cutscene.add_action(action)
        return cutscene

    @property
    def is_player_moving(self):
        return self.waiting_for == "player_movement"

    @property
    def locks_player_control(self):
        # O jogador pode andar livremente enquanto aguarda entrar no gatilho.
        return self.is_active and self.waiting_for != "trigger"

    def wait_for_trigger(self, trigger):
        """Adiciona uma etapa que aguarda o jogador entrar em um gatilho."""
        self.steps.append(("trigger", trigger))
        return self

    def add_action(self, action):
        """Converte uma ação declarativa em etapas executáveis."""
        if not isinstance(action, CutsceneAction):
            raise TypeError("Cada etapa deve ser criada por um helper da cutscene.")

        options = action.options
        if action.kind == "npc":
            self.move_npc(options["npc_id"], [options["destination"]])
        elif action.kind == "npcs":
            self.move_npcs(
                {
                    npc_id: [destination]
                    for npc_id, destination
                    in options["destinations"].items()
                }
            )
        elif action.kind == "player":
            self.move_player(
                [options["destination"]],
                obstacles=options["obstacles"],
            )
        elif action.kind == "camera_move":
            self.steps.append(
                (
                    "camera_movement",
                    (
                        options["position"],
                        options["duration"],
                        options["zoom"],
                    ),
                )
            )
        elif action.kind == "set_player_spawn_point":
            self.steps.append(
                ("set_player_spawn_point", options["position"])
            )
        elif action.kind == "wait":
            seconds = options["seconds"]
            if seconds < 0:
                raise ValueError("A duração de wait não pode ser negativa.")
            self.steps.append(("wait", seconds))
        elif action.kind == "change_scene":
            self.steps.append(
                (
                    "change_scene",
                    (
                        options["scene_factory"],
                        options["duration"],
                        options["player_spawn"],
                        options["transition"],
                    ),
                )
            )
        elif action.kind == "time_passes":
            self.steps.append(
                (
                    "time_passes",
                    (
                        options["text"],
                        options["fade_out_duration"],
                        options["duration"],
                        options["fade_in_duration"],
                        options["font_size"],
                    ),
                )
            )
        elif action.kind == "time_passes_prompt":
            self.steps.append(
                (
                    "time_passes_prompt",
                    (options["text"], options["continue_text"]),
                )
            )
        elif action.kind == "dialogue":
            self.steps.append(
                (
                    "inline_dialogue",
                    ((options["text"],), options["speaker"]),
                )
            )
        elif action.kind == "dialogue_from_id":
            self.steps.append(
                (
                    "dialogue",
                    (
                        options["dialogue_id"],
                        options["speaker"],
                    ),
                )
            )
        elif action.kind == "npc_dialogue":
            self.steps.append(
                (
                    "npc_dialogue",
                    (options["npc_id"], options["text"]),
                )
            )
        elif action.kind == "face_direction":
            self.steps.append(
                (
                    "face_direction",
                    (options["actor_id"], options["direction"]),
                )
            )
        elif action.kind == "spawn_npc":
            self.steps.append(
                (
                    "spawn_npc",
                    (
                        options["npc_options"],
                        options["remove_at_end"],
                    ),
                )
            )
        elif action.kind == "fade_out":
            self.steps.append(
                (
                    "fade_out",
                    (options["npc_id"], options["duration"]),
                )
            )
        elif action.kind == "trigger":
            # Cada trigger entra na sequência e executa suas ações logo depois.
            if options["rect"] is not None:
                area_trigger = AreaTrigger(
                    rect=options["rect"],
                    once=True,
                )
            else:
                area_trigger = AreaTrigger(
                    position=options["position"],
                    radius=options["radius"],
                    once=True,
                )
            self.steps.append(("trigger", area_trigger))
            self.triggers.append((area_trigger, options["visible"]))
            for nested_action in options["actions"]:
                self.add_action(nested_action)
        else:
            raise ValueError(f"Ação de cutscene desconhecida: {action.kind}")
        return self

    def move_npc(self, npc_id, points):
        """Adiciona uma etapa que move um NPC registrado por pontos."""
        return self.move_npcs({npc_id: points})

    def move_npcs(self, movements):
        """Move vários NPCs em paralelo, cada um seguindo seus próprios pontos."""
        if not movements:
            raise ValueError("Informe ao menos um NPC para movimentar.")

        self.steps.append(
            (
                "npc_movements",
                tuple(
                    (npc_id, tuple(points))
                    for npc_id, points in movements.items()
                ),
            )
        )
        return self

    def move_player(self, points, obstacles=()):
        """Adiciona uma etapa que move o jogador por pontos do cenário."""
        self.steps.append(("player_movement", (tuple(points), tuple(obstacles))))
        return self

    def face_direction(self, actor_id, direction):
        """Adiciona uma etapa que define a direção explícita de um ator."""
        self.steps.append(("face_direction", (actor_id, direction)))
        return self

    def dialogue(self, dialogue_id, speaker=""):
        """Adiciona uma fala consultada pelo identificador do diálogo."""
        self.steps.append(("dialogue", (dialogue_id, speaker)))
        return self

    def draw_trigger(self, screen):
        """Desenha o gatilho do roteiro, se este possuir um."""
        if self.game.is_cutscene_completed(self.cutscene_id):
            return
        for area_trigger, visible in self.triggers:
            # Só desenha gatilhos marcados como visíveis e ainda não acionados.
            if visible and not area_trigger.has_triggered:
                area_trigger.draw(screen)

    def draw_overlay(self, screen):
        """Desenha a transição de tela e a legenda centralizada, se ativa."""
        if self.waiting_for == "time_passes_prompt":
            screen.fill((0, 0, 0))
            title_font = pygame.font.Font(None, 48)
            hint_font = pygame.font.Font(None, 28)
            title = title_font.render(
                self.time_passes_message,
                True,
                (255, 255, 255),
            )
            hint = hint_font.render(
                self.time_passes_hint,
                True,
                (190, 190, 190),
            )
            screen.blit(
                title,
                title.get_rect(
                    center=(
                        screen.get_width() // 2,
                        screen.get_height() // 2 - 20,
                    )
                ),
            )
            screen.blit(
                hint,
                hint.get_rect(
                    center=(
                        screen.get_width() // 2,
                        screen.get_height() // 2 + 30,
                    )
                ),
            )
            return

        if self.screen_transition is None:
            return

        text, fade_out_duration, hold_duration, fade_in_duration, font_size = (
            self.screen_transition
        )
        elapsed = self.screen_transition_elapsed

        if elapsed < fade_out_duration:
            alpha = round(255 * elapsed / fade_out_duration)
        elif elapsed < fade_out_duration + hold_duration:
            alpha = 255
        else:
            fade_in_elapsed = elapsed - fade_out_duration - hold_duration
            alpha = round(
                255 * (1 - fade_in_elapsed / fade_in_duration)
            )

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, max(0, min(255, alpha))))
        screen.blit(overlay, (0, 0))

        if (
            alpha >= 128
            and elapsed >= fade_out_duration
            and elapsed < fade_out_duration + hold_duration
            and text
        ):
            if self.screen_transition_font_size != font_size:
                self.screen_transition_font = pygame.font.Font(
                    None,
                    font_size,
                )
                self.screen_transition_font_size = font_size
            label = self.screen_transition_font.render(
                text,
                True,
                (255, 255, 255),
            )
            screen.blit(label, label.get_rect(center=screen.get_rect().center))

    def start(self):
        """Inicia a sequência a partir da primeira etapa configurada."""
        if self.is_active:
            return False
        if self.game.is_cutscene_completed(self.cutscene_id):
            return False
        if not self.steps:
            raise ValueError("A cutscene precisa de pelo menos uma etapa.")

        self.step_index = 0
        self.waiting_for = None
        self.waiting_for_npc_ids = ()
        self.is_active = True
        self._run_ready_steps()
        return True

    def handle_event(self, event):
        """Encaminha eventos ao diálogo somente enquanto a cutscene fala."""
        if self.waiting_for == "time_passes_prompt":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.time_passes_message = None
                self.time_passes_hint = None
                self._finish_current_step()
                self._run_ready_steps()
            return True

        # Fora de uma fala, evita teclas como E vazarem para interações da cena.
        if self.waiting_for != "dialogue":
            return self.locks_player_control

        self.dialogue_manager.handle_event(event)
        return True

    def update(self, delta_time):
        """Avança a etapa ativa e executa etapas prontas em sequência."""
        if not self.is_active:
            return

        if self.waiting_for == "player_movement":
            obstacles = self.npc_controller.get_player_obstacles(
                self.player_obstacles
            )
            if not self._update_player_cutscene_route(obstacles):
                return
            self.player_cutscene.update(
                delta_time,
                bounds=self.bounds,
                obstacles=obstacles,
            )
            if self.player_cutscene.is_active:
                return
            self._finish_current_step()

        elif self.waiting_for == "camera_movement":
            if self.camera is None:
                raise RuntimeError(
                    "A cutscene solicitou movimento de câmera, mas nenhuma "
                    "CameraManager foi configurada."
                )
            self.camera.update(delta_time)
            if self.camera.is_animating:
                return
            self._finish_current_step()

        elif self.waiting_for == "npc_movement":
            if any(
                self.npc_controller.is_npc_moving(npc_id)
                for npc_id in self.waiting_for_npc_ids
            ):
                return
            self.waiting_for_npc_ids = ()
            self._finish_current_step()

        elif self.waiting_for == "trigger":
            trigger = self.steps[self.step_index][1]
            if not trigger.update(self.player):
                return
            self._finish_current_step()

        elif self.waiting_for == "dialogue":
            if self.dialogue_manager.is_active:
                return
            self._finish_current_step()

        elif self.waiting_for == "wait":
            self.wait_timer -= delta_time
            if self.wait_timer > 0:
                return
            self._finish_current_step()

        elif self.waiting_for == "npc_fade":
            self.fade_elapsed += delta_time
            opacity = 255 * (
                1 - self.fade_elapsed / self.fade_duration
            )
            npc = self.npc_controller.get_npc(self.fade_npc_id)
            npc.set_opacity(opacity)
            if self.fade_elapsed < self.fade_duration:
                return
            self.npc_controller.remove_npc(self.fade_npc_id)
            self.fade_npc_id = None
            self._finish_current_step()

        elif self.waiting_for == "screen_transition":
            self.screen_transition_elapsed += delta_time
            transition_duration = sum(
                self.screen_transition[1:4]
            )
            if self.screen_transition_elapsed < transition_duration:
                return
            self.screen_transition = None
            self.screen_transition_elapsed = 0.0
            self._finish_current_step()

        self._run_ready_steps()

    def _update_player_cutscene_route(self, obstacles):
        """Recalcula o trecho atual quando um obstáculo bloqueia o jogador."""
        cutscene = self.player_cutscene
        if not cutscene.is_active:
            return True

        bounds = self.bounds
        if bounds is None:
            surface = pygame.display.get_surface()
            bounds = pygame.Rect(
                0,
                0,
                surface.get_width(),
                surface.get_height(),
            )

        target = cutscene.path[cutscene.path_index]
        distance = self.player.position.distance_to(target)
        steps = max(1, int(distance / 4) + 1)
        if all(
            can_occupy(
                self.player,
                self.player.position.lerp(target, step / steps),
                bounds,
                obstacles,
            )
            for step in range(1, steps + 1)
        ):
            return True

        route = find_path(self.player, target, bounds, obstacles)
        if not route:
            if (
                self.player.position.distance_to(target) > 16
                or not can_occupy(self.player, target, bounds, obstacles)
            ):
                route, reachable_target = find_path_near_target(
                    self.player,
                    target,
                    bounds,
                    obstacles,
                )
                if route is None:
                    print(
                        "Cutscene: destino do jogador inacessível; "
                        f"continuando '{self.cutscene_id}'."
                    )
                    cutscene.path = cutscene.path[
                        cutscene.path_index + 1:
                    ]
                    cutscene.path_index = 0
                    cutscene.is_active = bool(cutscene.path)
                    return True
                target = reachable_target
            else:
                route = [pygame.Vector2(target)]
        if route and route[-1].distance_to(target) > 0.001:
            route.append(pygame.Vector2(target))

        remaining_path = cutscene.path[cutscene.path_index + 1:]
        cutscene.path = route + remaining_path
        cutscene.path_index = 0
        cutscene.is_active = bool(cutscene.path)
        return True

    def _run_ready_steps(self):
        # Executa etapas imediatas até encontrar uma ação que precise aguardar.
        # Continua apenas com cutscene ativa e sem etapa aguardando evento/tempo.
        while self.is_active and self.waiting_for is None:
            if self.step_index >= len(self.steps):
                self.is_active = False
                return

            action, arguments = self.steps[self.step_index]
            if action == "trigger":
                self.waiting_for = "trigger"
                return

            elif action == "wait":
                self.wait_timer = arguments
                if self.wait_timer > 0:
                    self.waiting_for = "wait"
                    return
                self._finish_current_step()
                continue

            elif action == "time_passes":
                self.screen_transition = arguments
                self.screen_transition_elapsed = 0.0
                transition_duration = sum(arguments[1:4])
                if transition_duration > 0:
                    self.waiting_for = "screen_transition"
                    return
                self.screen_transition = None

            elif action == "time_passes_prompt":
                self.time_passes_message, self.time_passes_hint = arguments
                self.waiting_for = "time_passes_prompt"
                return

            elif action == "change_scene":
                scene_factory, duration, player_spawn, transition = arguments
                if not self.game.scene_manager.transition_to(
                    scene_factory,
                    duration=duration,
                    player_spawn=player_spawn,
                    time_passes=transition,
                ):
                    raise RuntimeError(
                        "Já existe uma transição de cena em andamento."
                    )
                self._complete()
                return

            elif action == "set_player_spawn_point":
                self.game.set_player_spawn_point(arguments)

            elif action == "npc_movements":
                active_npc_ids = self.npc_controller.start_npc_cutscenes(
                    dict(arguments),
                    bounds=self.bounds,
                )
                if active_npc_ids:
                    self.waiting_for_npc_ids = tuple(active_npc_ids)
                    self.waiting_for = "npc_movement"
                    return

            elif action == "spawn_npc":
                npc_options, remove_at_end = arguments
                spawned_npc = self.npc_controller.add_npc(
                    NPC(**npc_options)
                )
                if remove_at_end:
                    self.temporary_npc_ids.add(spawned_npc.npc_id)

            elif action == "fade_out":
                npc_id, duration = arguments
                npc = self.npc_controller.get_npc(npc_id)
                self.fade_npc_id = npc_id
                self.fade_elapsed = 0.0
                self.fade_duration = duration
                if duration == 0:
                    self.npc_controller.remove_npc(npc_id)
                    self.fade_npc_id = None
                else:
                    self.waiting_for = "npc_fade"
                    return

            elif action == "player_movement":
                points, obstacles = arguments
                if not points:
                    raise ValueError(
                        "O movimento da cutscene precisa de destinos."
                    )
                self.player_obstacles = obstacles
                self.player_cutscene.start(self.player, points)
                if self.player_cutscene.is_active:
                    self.waiting_for = "player_movement"
                    return

            elif action == "camera_movement":
                if self.camera is None:
                    raise RuntimeError(
                        "A ação camera_move exige uma CameraManager."
                    )
                position, duration, zoom = arguments
                self.camera.move_to(position, duration=duration, zoom=zoom)
                if self.camera.is_animating:
                    self.waiting_for = "camera_movement"
                    return

            elif action == "face_direction":
                actor_id, direction = arguments
                if actor_id == "player":
                    self.player.face_direction(direction)
                else:
                    self.npc_controller.face_direction(
                        actor_id,
                        direction,
                    )

            elif action == "dialogue":
                dialogue_id, speaker = arguments
                if self.dialogue_manager.is_active:
                    return
                if self.dialogue_manager.start(
                    dialogue_id,
                    speaker=speaker,
                ):
                    self.waiting_for = "dialogue"
                    return

            elif action == "inline_dialogue":
                lines, speaker = arguments
                if self.dialogue_manager.is_active:
                    return
                if self.dialogue_manager.start_lines(lines, speaker=speaker):
                    self.waiting_for = "dialogue"
                    return

            elif action == "npc_dialogue":
                npc_id, text = arguments
                if self.dialogue_manager.is_active:
                    return
                npc = self.npc_controller.get_npc(npc_id)
                if self.dialogue_manager.start_lines(
                    (text,),
                    speaker=npc.display_name,
                ):
                    self.waiting_for = "dialogue"
                    return

            else:
                raise ValueError(f"Ação de cutscene desconhecida: {action}")

            self._finish_current_step()

    def _finish_current_step(self):
        self.step_index += 1
        self.waiting_for = None
        if self.step_index >= len(self.steps):
            self._complete()

    def _complete(self):
        """Registra a conclusão e remove NPCs temporários restantes."""
        for npc_id in tuple(self.temporary_npc_ids):
            if self.npc_controller.has_npc(npc_id):
                self.npc_controller.remove_npc(npc_id)
        self.temporary_npc_ids.clear()
        self.game.mark_cutscene_completed(self.cutscene_id)
        self.is_active = False
        self.waiting_for = None
