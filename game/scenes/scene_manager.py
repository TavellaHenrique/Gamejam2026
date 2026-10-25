
import pygame

from game.scenes.scene import Scene


class SceneManager:
    """Mantém a cena atual e encaminha para ela eventos, atualizações e desenho."""

    def __init__(self, game):
        """Armazena o jogo e começa sem uma cena ativa."""
        self.game = game
        self.current_scene = None
        self.transition_factory = None
        self.transition_duration = 0.0
        self.transition_elapsed = 0.0
        self.transition_phase = None
        self.transition_time_passes = None
        self.transition_font = None

    def change_scene(self, new_scene: Scene):
        """Encerra a cena anterior e ativa a nova cena."""
        # Os callbacks permitem que cada cena prepare ou libere seus próprios recursos.
        if self.current_scene is not None:
            self.current_scene.on_exit()

        self.current_scene = new_scene
        self.current_scene.on_enter()

    @property
    def is_paused(self):
        """Indica se a cena ativa está pausada por uma interface modal."""
        return bool(
            self.current_scene is not None
            and self.current_scene.is_paused
        )

    def transition_to(
        self,
        scene_factory,
        duration=0.5,
        player_spawn=None,
        time_passes=None,
    ):
        """Troca de cena com fade, opcionalmente mantendo legenda na tela preta."""
        if self.transition_phase is not None:
            return False
        if time_passes is None and duration <= 0:
            raise ValueError("A duração da transição precisa ser positiva.")
        if not callable(scene_factory):
            raise TypeError("scene_factory precisa ser uma função chamável.")

        # Um spawn informado na transição prevalece sobre o ponto global atual.
        if player_spawn is not None:
            self.game.set_player_spawn_point(player_spawn)

        self.transition_factory = scene_factory
        self.transition_time_passes = time_passes
        self.transition_duration = (
            sum(time_passes[1:4]) if time_passes is not None else duration
        )
        self.transition_elapsed = 0.0
        self.transition_phase = "fade_out"
        return True

    def handle_event(self, event):
        """Encaminha eventos somente quando há uma cena ativa."""
        # Durante a transição a cena está sendo substituída e não recebe comandos.
        if self.current_scene and self.transition_phase is None:
            self.current_scene.handle_event(event)

    def update(self, delta_time):
        """Atualiza a cena ativa com o tempo decorrido desde o quadro anterior."""
        if self.transition_phase is not None:
            if self.transition_time_passes is not None:
                self._update_time_passes_transition(delta_time)
                return

            self.transition_elapsed += delta_time
            if self.transition_elapsed >= self.transition_duration:
                self.transition_elapsed = 0.0
                if self.transition_phase == "fade_out":
                    self.change_scene(self.transition_factory())
                    self.transition_factory = None
                    self.transition_phase = "fade_in"
                else:
                    self.transition_phase = None
            return

        if self.current_scene:
            self.current_scene.update(delta_time)

    def draw(self, screen):
        """Solicita à cena ativa que desenhe seus elementos na tela."""
        self.game.dialogue_manager.begin_frame()
        if self.current_scene:
            self.current_scene.draw(screen)

        if self.transition_phase is None:
            return

        if self.transition_time_passes is not None:
            _, fade_out_duration, _, fade_in_duration, _ = (
                self.transition_time_passes
            )
            if self.transition_phase == "fade_out":
                alpha = (
                    255
                    if fade_out_duration == 0
                    else round(
                        255 * self.transition_elapsed / fade_out_duration
                    )
                )
            elif self.transition_phase == "hold":
                alpha = 255
            else:
                alpha = (
                    0
                    if fade_in_duration == 0
                    else round(
                        255 * (
                            1 - self.transition_elapsed / fade_in_duration
                        )
                    )
                )
        elif self.transition_phase == "fade_out":
            alpha = round(255 * self.transition_elapsed / self.transition_duration)
        else:
            alpha = round(
                255 * (
                    1 - self.transition_elapsed / self.transition_duration
                )
            )

        overlay = pygame.Surface(screen.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))

        if (
            self.transition_time_passes is not None
            and self.transition_phase == "hold"
            and self.transition_time_passes[0]
        ):
            text, _, _, _, font_size = self.transition_time_passes
            if self.transition_font is None:
                self.transition_font = pygame.font.Font(None, font_size)
            label = self.transition_font.render(text, True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=screen.get_rect().center))

    def _update_time_passes_transition(self, delta_time):
        """Troca a cena durante a tela preta e termina o fade na cena nova."""
        _, fade_out_duration, hold_duration, fade_in_duration, _ = (
            self.transition_time_passes
        )
        remaining = delta_time

        while self.transition_phase is not None:
            if self.transition_phase == "fade_out":
                phase_duration = fade_out_duration
            elif self.transition_phase == "hold":
                phase_duration = hold_duration
            else:
                phase_duration = fade_in_duration

            time_left = phase_duration - self.transition_elapsed
            if time_left > remaining:
                self.transition_elapsed += remaining
                return

            remaining -= max(0.0, time_left)
            self.transition_elapsed = 0.0

            if self.transition_phase == "fade_out":
                self.change_scene(self.transition_factory())
                self.transition_factory = None
                self.transition_phase = "hold"
            elif self.transition_phase == "hold":
                self.transition_phase = "fade_in"
            else:
                self.transition_phase = None
                self.transition_time_passes = None
                self.transition_font = None
                return

            if remaining <= 0:
                return
