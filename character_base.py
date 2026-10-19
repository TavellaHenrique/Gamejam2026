
import pygame

# Subclasse da classe de sprites do pygame
class CharacterBase(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        self.animations = {}

        self.current_animation = ""
        self.frame_index = 0
        self.frame_delay = 120 # ms
        self.animation_timer = 0

        self.speed = 10

    def get_sprites_from_sheet(self, path, frame_width, frame_height, frame_count, scale) -> list:
        sheet = pygame.image.load(path).convert_alpha()

        frames = []

        for i in range(frame_count):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)).copy()
            frame = pygame.transform.scale(frame, (frame_width * scale, frame_height * scale))
            frames.append(frame)

        return frames

    def update(self, delta_time):
        self.animation_timer += delta_time
        if self.animation_timer >= self.frame_delay:
            self.animation_timer -= self.frame_delay
            self.frame_index = (self.frame_index + 1) % len(self.animations.get(self.current_animation))

        self.image = self.animations.get(self.current_animation)[self.frame_index]

    # Essa função DEVE ser chamada no método __init__(self) nas SUBCLASSES
    def set_image(self, x, y):
        self.image = self.animations.get(self.current_animation)[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

    def get_animations(self):
        raise Exception("Essa função deve ser sobrescrita nas subclasses...")
