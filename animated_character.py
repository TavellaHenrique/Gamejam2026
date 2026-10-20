
import pygame

# Subclasse da classe de sprites do pygame
# Serve como base para as classes de personagem que possuem animação (ou sprites estáticos)
class AnimatedCharacter(pygame.sprite.Sprite):

    def __init__(self):
        # Construtor da superclasse
        super().__init__()

        # -- Definições da animação --
        # Conjunto de animações (ou sprites estáticos) do personagem
        self.animations = {}

        # Animação atual e inicial do personagem (deve corresponder a uma animação do conjunto acima)
        self.current_animation = "" # deve ser definida em subclasses

        # Quadro (frame) atual e inicial da animação
        self.frame_index = 0

        # Tempo até trocar de quadro, em milissegundos (ms)
        self.frame_delay = 0.120

        # Variável de controle do tempo de exibição de cada quadro
        self.animation_timer = 0

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
            self.animation_timer = 0

            self.frame_index = (self.frame_index + 1) % len(self.animations.get(self.current_animation))

        self.image = self.animations.get(self.current_animation)[self.frame_index]

    # Essa função DEVE ser chamada no método __init__(self) nas SUBCLASSES
    def set_image(self, x, y):
        self.image = self.animations.get(self.current_animation)[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

    def get_animations(self):
        raise Exception("Essa função deve ser sobrescrita nas subclasses...")
        # Essa função deve adicionar uma imagem ou lista de imagens ao dicionário self.animations nas subclasses
        # Não pode ser feito aqui porque essa class é abstrata e não tem nenhuma imagem para acessar de fato
