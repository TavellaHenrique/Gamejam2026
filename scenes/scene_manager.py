
import pygame

from scenes.scene import Scene


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

    def change_scene(self, new_scene: Scene):
        """Encerra a cena anterior e ativa a nova cena."""
        # Os callbacks permitem que cada cena prepare ou libere seus próprios recursos.
        if self.current_scene is not None:
            self.current_scene.on_exit()

        self.current_scene = new_scene
        self.current_scene.on_enter()

    def transition_to(self, scene_factory, duration=0.5):
        """Troca de cena com fade preto; a fábrica cria a cena no meio da transição."""
        if self.transition_phase is not None:
            return False
        if duration <= 0:
            raise ValueError("A duração da transição precisa ser positiva.")

        self.transition_factory = scene_factory
        self.transition_duration = duration
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
        if self.current_scene:
            self.current_scene.draw(screen)

        if self.transition_phase is None:
            return

        if self.transition_phase == "fade_out":
            alpha = round(
                255 * self.transition_elapsed / self.transition_duration
            )
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