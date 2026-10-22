
import pygame


class DialogueBox:
    """Formata falas em páginas e desenha a caixa de diálogo na tela."""

    def __init__(
        self,
        font_path="assets/fonts/typewcond_regular.otf",
        font_size=28,
        speaker_font_size=32,
        max_lines_per_page=2,
        padding=30,
        box_height=230,
        margin=20,
    ):
        """Configura fontes, dimensões, espaçamentos e cores da caixa."""
        self.font = pygame.font.Font(font_path, font_size)
        self.bubble_font = pygame.font.Font(font_path, 20)
        self.speaker_font = pygame.font.Font(
            font_path, speaker_font_size
        )

        self.max_lines_per_page = max_lines_per_page
        self.padding = padding
        self.box_height = box_height
        self.margin = margin

        self.background_color = (20, 24, 32, 230)
        self.border_color = (220, 200, 150)
        self.text_color = (245, 245, 245)
        self.speaker_color = (255, 220, 140)
        self.occupied_bubble_rects = []

    def begin_frame(self):
        """Clears bubble layout state before drawing a new frame."""
        self.occupied_bubble_rects.clear()

    def stack_bubble_rect(self, rect):
        """Moves overlapping UI bubbles upward and reserves the resulting area."""
        rect = pygame.Rect(rect)
        while True:
            overlapping = [
                occupied
                for occupied in self.occupied_bubble_rects
                if rect.colliderect(occupied)
            ]
            if not overlapping:
                break
            next_top = min(occupied.top for occupied in overlapping) - 4
            if next_top < 8:
                break
            rect.bottom = next_top

        self.occupied_bubble_rects.append(rect.copy())
        return rect

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
                    current_line = ""
                    if self.font.size(word)[0] <= max_width:
                        current_line = word
                    else:
                        fragment = ""
                        for character in word:
                            candidate_fragment = fragment + character
                            if (
                                fragment
                                and self.font.size(candidate_fragment)[0]
                                > max_width
                            ):
                                lines.append(fragment)
                                fragment = character
                            else:
                                fragment = candidate_fragment
                        current_line = fragment

            if current_line:
                lines.append(current_line)

        return lines

    def paginate(self, text, screen_width=None):
        """Calcula páginas de texto sem guardar estado do diálogo."""
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
            - self.padding
            - speaker_height
            - hint_height
        )

        lines_per_page = min(
            self.max_lines_per_page,
            max(1, available_height // self.font.get_linesize()),
        )

        # Agrupa as linhas em páginas e garante uma página mesmo para texto vazio.
        pages = [
            "\n".join(lines[i:i + lines_per_page])
            for i in range(0, len(lines), lines_per_page)
        ]

        # Mesmo texto vazio precisa renderizar uma página para manter o fluxo.
        return pages or [""]

    def draw(
        self,
        screen,
        text,
        speaker_name="",
        has_next_page=False,
        show_hint=True,
    ):
        """Desenha uma página e recebe do controlador se há mais páginas."""
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

        # Renderiza cada linha da página atual, preservando as quebras calculadas.
        for line in text.split("\n"):
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
            if has_next_page:
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

    def draw_bubble(self, screen, anchor, text):
        """Desenha um balão compacto ancorado a uma entidade."""
        max_width = screen.get_width() - 40
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            candidate = f"{current_line} {word}".strip()
            if (
                # Só quebra a linha quando já há texto e o próximo termo excede o balão.
                current_line
                and self.bubble_font.size(candidate)[0] > max_width
            ):
                lines.append(current_line)
                current_line = word
            else:
                current_line = candidate

        if current_line:
            lines.append(current_line)

        if not lines:
            return

        rendered_lines = [
            self.bubble_font.render(line, True, (255, 255, 255))
            for line in lines
        ]
        text_width = max(line.get_width() for line in rendered_lines)
        line_height = self.bubble_font.get_linesize()
        padding_x = 8
        padding_y = 5
        bubble_width = text_width + padding_x * 2
        bubble_height = len(rendered_lines) * line_height + padding_y * 2
        image_left = round(anchor.position.x - anchor.image.get_width() / 2)
        image_top = round(anchor.position.y - anchor.image.get_height() / 2)
        visible_bounds = anchor.image.get_bounding_rect()
        anchor_x = image_left + visible_bounds.centerx
        anchor_top = image_top + visible_bounds.top
        bubble_x = max(
            8,
            min(
                anchor_x - bubble_width // 2,
                screen.get_width() - bubble_width - 8,
            ),
        )
        bubble_y = max(8, anchor_top - bubble_height - 4)
        background_rect = pygame.Rect(
            bubble_x,
            bubble_y,
            bubble_width,
            bubble_height,
        )
        background_rect = self.stack_bubble_rect(background_rect)
        bubble_x, bubble_y = background_rect.topleft
        background = pygame.Surface(
            background_rect.size,
            pygame.SRCALPHA,
        )
        background.fill((20, 24, 32, 210))
        screen.blit(background, background_rect.topleft)

        for index, line in enumerate(rendered_lines):
            screen.blit(
                line,
                (
                    bubble_x + padding_x,
                    bubble_y + padding_y + index * line_height,
                ),
            )
