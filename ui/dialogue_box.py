
import pygame


class DialogueBox:
    """Formata falas em páginas e desenha a caixa de diálogo na tela."""

    def __init__(
        self,
        font_path="assets/fonts/typewcond_regular.otf",
        font_size=28,
        speaker_font_size=32,
        padding=30,
        box_height=200,
        margin=20,
    ):
        """Configura fontes, dimensões, espaçamentos e cores da caixa."""
        self.font = pygame.font.Font(font_path, font_size)
        self.speaker_font = pygame.font.Font(
            font_path, speaker_font_size
        )

        self.padding = padding
        self.box_height = box_height
        self.margin = margin

        self.background_color = (20, 24, 32, 230)
        self.border_color = (220, 200, 150)
        self.text_color = (245, 245, 245)
        self.speaker_color = (255, 220, 140)

        self.pages = []
        self.current_page = 0

    def wrap_text(self, text, max_width):
        """Divide o texto em linhas que cabem na largura disponível."""
        lines = []

        # Mantém parágrafos separados e trata linhas vazias como quebras explícitas.
        for paragraph in text.split("\n"):
            words = paragraph.split()
            current_line = ""

            if not words:
                lines.append("")
                continue

            for word in words:
                candidate = f"{current_line} {word}".strip()

                # Mede o texto renderizado para não exceder a largura máxima.
                if self.font.size(candidate)[0] <= max_width:
                    current_line = candidate
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

        return lines

    def show_text(self, text, screen_width=None):
        """Calcula as páginas do texto usando a largura atual ou a informada."""
        if screen_width is None:
            screen_width = pygame.display.get_surface().get_width()

        # Reserva margens laterais e padding antes de calcular a largura do texto.
        box_width = screen_width - 2 * self.margin
        max_text_width = box_width - 2 * self.padding

        lines = self.wrap_text(text, max_text_width)

        # Reserva espaço vertical para o nome e a indicação de tecla em cada página.
        speaker_height = self.speaker_font.get_linesize() + 10
        hint_height = self.font.get_linesize() + 10

        available_height = (
            self.box_height
            - 2 * self.padding
            - speaker_height
            - hint_height
        )

        lines_per_page = max(
            1,
            available_height // self.font.get_linesize(),
        )

        # Agrupa as linhas em páginas e garante uma página mesmo para texto vazio.
        self.pages = [
            "\n".join(lines[i:i + lines_per_page])
            for i in range(0, len(lines), lines_per_page)
        ]

        if not self.pages:
            self.pages = [""]

        self.current_page = 0

    def advance_page(self):
        """Avança uma página. Retorna False se já estiver na última."""
        if self.current_page + 1 < len(self.pages):
            self.current_page += 1
            return True

        return False

    def draw(self, screen, speaker_name="", show_hint=True):
        """Desenha painel, nome, texto atual e indicação da próxima ação."""
        # Não desenha a caixa até que algum texto tenha sido preparado.
        if not self.pages:
            return

        screen_width, screen_height = screen.get_size()

        # Limita dimensões e posição do painel ao espaço disponível na tela.
        box_width = screen_width - 2 * self.margin
        box_height = min(
            self.box_height,
            screen_height - 2 * self.margin,
        )

        box_x = self.margin
        box_y = screen_height - box_height - self.margin

        box_rect = pygame.Rect(
            box_x, box_y, box_width, box_height
        )

        # A superfície alfa permite desenhar o fundo semitransparente do diálogo.
        panel = pygame.Surface(
            (box_width, box_height), pygame.SRCALPHA
        )
        panel.fill(self.background_color)
        screen.blit(panel, box_rect.topleft)

        pygame.draw.rect(
            screen,
            self.border_color,
            box_rect,
            width=2,
            border_radius=8,
        )

        content_x = box_x + self.padding
        content_y = box_y + self.padding

        # O nome é opcional e, quando presente, desloca para baixo o início da fala.
        if speaker_name:
            speaker_surface = self.speaker_font.render(
                speaker_name, True, self.speaker_color
            )
            screen.blit(
                speaker_surface,
                (content_x, content_y),
            )
            content_y += speaker_surface.get_height() + 10

        line_height = self.font.get_linesize()
        current_text = self.pages[self.current_page]

        # Renderiza cada linha da página atual, preservando as quebras calculadas.
        for line in current_text.split("\n"):
            text_surface = self.font.render(
                line, True, self.text_color
            )
            screen.blit(
                text_surface,
                (content_x, content_y),
            )
            content_y += line_height

        if show_hint:
            # A instrução muda conforme ainda existam páginas ou falas a avançar.
            if self.current_page + 1 < len(self.pages):
                hint_text = "E - Continuar fala"
            else:
                hint_text = "E - Próxima fala"

            hint = self.font.render(
                hint_text, True, self.speaker_color
            )
            hint_rect = hint.get_rect(
                bottomright=(
                    box_rect.right - self.padding,
                    box_rect.bottom - 10,
                )
            )
            screen.blit(hint, hint_rect)
