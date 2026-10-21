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
    ):
        """Loads frames from a horizontal spritesheet."""
        spritesheet = pygame.image.load(path).convert_alpha()
        frames = []

        for index in range(frame_count):
            rect = pygame.Rect(
                index * frame_width,
                0,
                frame_width,
                frame_height,
            )
            frame = spritesheet.subsurface(rect).copy()
            if scale != 1:
                frame = pygame.transform.scale(
                    frame,
                    (frame_width * scale, frame_height * scale),
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
