
import pygame


class Animation:
    """Armazena quadros de animação e controla sua reprodução ao longo do tempo."""

    def __init__(self, current_animation, frame_delay=0.120):
        """Inicializa o estado da animação e o intervalo entre quadros."""
        self.animations = {}
        self.current_animation = current_animation

        self.frame_index = 0
        self.frame_delay = frame_delay
        self.animation_timer = 0

        self.image = None

    def get_sprites_from_spritesheet(
        self,
        path,
        frame_width,
        frame_height,
        frame_count,
        scale=1
    ):
        """Recorta quadros horizontais de um spritesheet e aplica a escala pedida."""
        spritesheet = pygame.image.load(path).convert_alpha()

        frames = []

        # Cada quadro ocupa uma coluna do spritesheet, começando na coordenada x zero.
        for i in range(frame_count):
            rect = pygame.Rect(
                i * frame_width,
                0,
                frame_width,
                frame_height
            )

            frame = spritesheet.subsurface(rect).copy()

            # Evita redimensionar quando o fator de escala padrão é um.
            if scale != 1:
                frame = pygame.transform.scale(
                    frame,
                    (frame_width * scale, frame_height * scale)
                )

            frames.append(frame)

        return frames

    def play(self, animation_name):
        """Inicia a animação indicada ou informa se ela não estiver carregada."""
        if animation_name not in self.animations:
            raise ValueError(
                f"Animação não encontrada: {animation_name}"
            )

        if animation_name == self.current_animation:
            return

        self.current_animation = animation_name
        self.frame_index = 0
        self.animation_timer = 0
        self.image = self.animations[animation_name][0]

    def update(self, delta_time):
        """Avança os quadros conforme o tempo decorrido e atualiza a imagem atual."""
        frames = self.animations[self.current_animation]

        self.animation_timer += delta_time

        # O while também processa corretamente quadros atrasados após um frame lento.
        while self.animation_timer >= self.frame_delay:
            self.animation_timer -= self.frame_delay
            self.frame_index = (self.frame_index + 1) % len(frames)

        self.image = frames[self.frame_index]

    def set_image(self):
        """Define a imagem inicial usando a animação e o índice de quadro atuais."""
        self.image = self.animations[
            self.current_animation
        ][self.frame_index]
