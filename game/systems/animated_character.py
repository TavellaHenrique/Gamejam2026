import pygame


class AnimatedCharacter(pygame.sprite.Sprite):
    """Sprite base class that loads, selects, and advances animations."""

    def __init__(self, current_animation="idle", frame_delay=0.120):
        super().__init__()
        self.animations = {}
        self.current_animation = current_animation
        self.frame_index = 0
        self.frame_delay = frame_delay
        self.animation_timer = 0.0
        self.image = None
        self.rect = None

    def get_sprites_from_spritesheet(
        self,
        path,
        frame_width,
        frame_height,
        frame_count,
        scale=1,
        row=0,
        output_size=None,
        fit_content_size=None,
    ):
        """Loads frames from one horizontal row of a spritesheet."""
        if frame_width <= 0 or frame_height <= 0 or frame_count <= 0:
            raise ValueError("As dimensões e a quantidade de quadros devem ser positivas.")
        if row < 0 or scale <= 0:
            raise ValueError("A linha e a escala devem ser valores válidos.")
        if output_size is not None and min(output_size) <= 0:
            raise ValueError("O tamanho de saída deve ser positivo.")
        if fit_content_size is not None and min(fit_content_size) <= 0:
            raise ValueError("O tamanho do conteúdo deve ser positivo.")

        spritesheet = pygame.image.load(path).convert_alpha()
        if (
            (frame_count * frame_width) > spritesheet.get_width()
            or (row + 1) * frame_height > spritesheet.get_height()
        ):
            raise ValueError(
                f"A linha {row} do spritesheet '{path}' não contém "
                f"{frame_count} quadros de {frame_width}x{frame_height}."
            )

        frames = []

        for index in range(frame_count):
            rect = pygame.Rect(
                index * frame_width,
                row * frame_height,
                frame_width,
                frame_height,
            )
            frame = spritesheet.subsurface(rect).copy()
            if fit_content_size is not None:
                content_rect = frame.get_bounding_rect()
                if content_rect.width == 0 or content_rect.height == 0:
                    raise ValueError(
                        f"O quadro {index} da linha {row} em '{path}' está vazio."
                    )
                content = frame.subsurface(content_rect).copy()
                fit_scale = min(
                    fit_content_size[0] / content_rect.width,
                    fit_content_size[1] / content_rect.height,
                )
                content_size = (
                    max(1, round(content_rect.width * fit_scale)),
                    max(1, round(content_rect.height * fit_scale)),
                )
                content = pygame.transform.scale(content, content_size)
                frame = pygame.Surface(output_size, pygame.SRCALPHA)
                frame.blit(
                    content,
                    (
                        (output_size[0] - content_size[0]) // 2,
                        output_size[1] - content_size[1],
                    ),
                )
            elif output_size is not None:
                frame = pygame.transform.scale(frame, output_size)
            elif scale != 1:
                frame = pygame.transform.scale(
                    frame,
                    (
                        max(1, round(frame_width * scale)),
                        max(1, round(frame_height * scale)),
                    ),
                )
            frames.append(frame)

        return frames

    def play(self, animation_name):
        """Selects a loaded animation and restarts it when it changes."""
        if animation_name not in self.animations:
            raise ValueError(f"Animation not found: {animation_name}")
        if animation_name == self.current_animation:
            return

        self.current_animation = animation_name
        self.frame_index = 0
        self.animation_timer = 0.0
        self.image = self.animations[animation_name][0]

    def set_image(self):
        """Sets the sprite image to the current animation frame."""
        self.image = self.animations[self.current_animation][self.frame_index]

    def update(self, delta_time):
        """Advances animation frames according to elapsed time."""
        frames = self.animations[self.current_animation]
        self.animation_timer += delta_time

        while self.animation_timer >= self.frame_delay:
            self.animation_timer -= self.frame_delay
            self.frame_index = (self.frame_index + 1) % len(frames)

        self.image = frames[self.frame_index]
