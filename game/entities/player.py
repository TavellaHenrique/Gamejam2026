
import pygame

from game.systems.animated_character import AnimatedCharacter
from game.systems.collision import move_with_collisions
from game.systems.inventory import Inventory


class Player(AnimatedCharacter):
    """Personagem controlado pelo jogador, com movimento e animações direcionais."""

    # Modos de animação disponíveis para escolher a quantidade de direções animadas.
    ANIMATION_8_DIRECTIONS = "8_directions"
    ANIMATION_5_DIRECTIONS = "5_directions"

    def __init__(
        self,
        position,
        speed=180,
        animation_mode=ANIMATION_8_DIRECTIONS,
        animation_scale=3,
    ):
        """Inicializa posição, velocidade, direção e conjunto de animações."""
        super().__init__("idle")
        self.position = pygame.Vector2(position)
        self.speed = speed

        self.animation_mode = animation_mode
        self.animation_scale = animation_scale

        # A direção inicial aponta para baixo e é mantida quando o jogador para.
        self.facing = pygame.Vector2(0, 1)
        self.is_moving = False
        self._last_update_position = self.position.copy()

        # Carrega as animações antes de selecionar o primeiro quadro do sprite.
        self.get_animations()

        self.set_image()

        self.rect = self.image.get_rect(
            center=(
                round(self.position.x),
                round(self.position.y)
            )
        )
        self.inventory = Inventory()
        
    def update(
        self,
        delta_time,
        accept_input=True,
        bounds=None,
        obstacles=(),
    ):
        """Atualiza movimento, animação selecionada, imagem e área do sprite."""
        # Durante uma cutscene, outra rotina movimenta o jogador sem ler o teclado.
        if accept_input:
            self.move(delta_time, bounds, obstacles)
        else:
            # A cutscene can move the player outside this update method.
            self.is_moving = self.position != self._last_update_position

        # Seleciona animação correspondente
        self.update_player_animation(self.is_moving)

        # Atualiza quadro da animação
        super().update(delta_time)

        # Sincroniza imagem e retângulo com a posição atual
        self.rect = self.image.get_rect(
            center=(
                round(self.position.x),
                round(self.position.y)
            )
        )
        self._last_update_position.update(self.position)

    def move(self, delta_time, bounds=None, obstacles=()):
        """Lê as teclas direcionais e move o jogador proporcionalmente ao tempo."""
        keys = pygame.key.get_pressed()

        # A diferença entre teclas opostas cria o vetor de direção do movimento.
        direction = pygame.Vector2(
            keys[pygame.K_d] - keys[pygame.K_a],
            keys[pygame.K_s] - keys[pygame.K_w]
        )

        if bounds is None:
            bounds = pygame.Rect(
                0,
                0,
                pygame.display.get_surface().get_width(),
                pygame.display.get_surface().get_height(),
            )

        self.move_in_direction(direction, delta_time, bounds, obstacles)

    def move_in_direction(
        self,
        direction,
        delta_time,
        bounds=None,
        obstacles=(),
    ):
        """Move o jogador em uma direção fornecida por teclado ou cutscene."""
        direction = pygame.Vector2(direction)

        if direction.length_squared() > 0:
            # Normalizar evita que o movimento diagonal seja mais rápido.
            direction = direction.normalize()

            displacement = direction * self.speed * delta_time
            if bounds is None:
                bounds = pygame.Rect(
                    0,
                    0,
                    pygame.display.get_surface().get_width(),
                    pygame.display.get_surface().get_height(),
                )
            self.is_moving = move_with_collisions(
                self,
                displacement,
                bounds,
                obstacles,
            )
            if self.is_moving:
                self.facing = direction
        else:
            self.is_moving = False

        # Mantém o retângulo alinhado para desenho e futuras verificações espaciais.
        self.rect.center = (
            round(self.position.x),
            round(self.position.y)
        )

    def move_towards(
        self,
        target,
        delta_time,
        bounds=None,
        obstacles=(),
        keep_walking=False,
    ):
        """Avança em direção ao ponto sem ultrapassá-lo e informa quando chegou."""
        target = pygame.Vector2(target)
        offset = target - self.position
        distance = offset.length()

        if distance == 0:
            self.is_moving = False
            return True

        direction = offset / distance
        max_distance = self.speed * delta_time
        if bounds is None:
            bounds = pygame.Rect(
                0,
                0,
                pygame.display.get_surface().get_width(),
                pygame.display.get_surface().get_height(),
            )

        if distance <= max_distance:
            move_with_collisions(
                self,
                offset,
                bounds,
                obstacles,
            )
            if self.position.distance_to(target) > 0.001:
                return False
            self.facing = direction
            self.is_moving = keep_walking
            self.rect.center = (
                round(self.position.x),
                round(self.position.y)
            )
            return True

        self.move_in_direction(
            direction,
            delta_time,
            bounds,
            obstacles,
        )
        return False

    def look_at(self, target):
        """Orienta o jogador para um ponto e atualiza sua animação de parado."""
        direction = pygame.Vector2(target) - self.position
        if direction.length_squared() == 0:
            return

        self.facing = direction.normalize()
        self.is_moving = False
        self.update_player_animation(False)

    def face_direction(self, direction):
        """Orienta o jogador usando um vetor ou direção cardinal/diagonal."""
        directions = {
            "up": (0, -1),
            "down": (0, 1),
            "left": (-1, 0),
            "right": (1, 0),
            "up_left": (-1, -1),
            "up_right": (1, -1),
            "down_left": (-1, 1),
            "down_right": (1, 1),
        }
        vector = pygame.Vector2(
            directions[direction]
            if isinstance(direction, str)
            else direction
        )
        if vector.length_squared() == 0:
            raise ValueError("A direção não pode ser zero.")
        self.facing = vector.normalize()
        self.is_moving = False
        self.update_player_animation(False)

    def update_player_animation(self, moving):
        """Escolhe a animação conforme a direção e o estado atual do movimento."""
        if self.animation_mode == self.ANIMATION_8_DIRECTIONS:
            self.animate_8_directions(moving)
        elif self.animation_mode == self.ANIMATION_5_DIRECTIONS:
            self.animate_5_directions(moving)

    def animate_8_directions(self, moving):
        """Escolhe uma animação de parado ou caminhada entre oito direções."""
        x = round(self.facing.x)
        y = round(self.facing.y)
        direction = self.get_direction_name(x, y)
        prefix = "walk" if moving else "idle"
        self.set_animation(f"{prefix}_{direction}")

    def animate_5_directions(self, moving):
        """Escolhe animações simplificadas para parado e quatro direções."""
        if not moving:
            self.set_animation("idle")
            return

        # A maior componente determina a direção dominante do movimento.
        x = self.facing.x
        y = self.facing.y
        if abs(x) > abs(y):
            direction = "right" if x > 0 else "left"
        else:
            direction = "down" if y > 0 else "up"
        self.set_animation(f"walk_{direction}")

    @staticmethod
    def get_direction_name(x, y):
        """Converte componentes direcionais arredondadas em um nome de animação."""
        directions = {
            (0, -1): "up",
            (0, 1): "down",
            (-1, 0): "left",
            (1, 0): "right",
            (-1, -1): "up_left",
            (1, -1): "up_right",
            (-1, 1): "down_left",
            (1, 1): "down_right"
        }

        return directions.get((x, y), "down")

    def set_animation(self, animation_name):
        """Troca a animação atual somente quando o nome solicitado é diferente."""
        if animation_name == self.current_animation:
            return

        self.play(animation_name)
    
    def get_animations(self):
        """Carrega os spritesheets usados pelo jogador e monta o mapa de animações."""
        base_path = "assets/sprites/player/TheFemaleAdventurer"

        # Os spritesheets compartilham o mesmo tamanho de quadro e fator de escala.
        frame_settings = {
            "frame_width": 48,
            "frame_height": 64,
            "frame_count": 8,
            "scale": self.animation_scale
        }

        def load_animation(path):
            """Carrega um spritesheet relativo à pasta base do personagem."""
            return self.get_sprites_from_spritesheet(
                path=f"{base_path}/{path}",
                **frame_settings
            )

        self.animations = {
            # -- Idle --
            "idle": load_animation("Idle/Idle_Down.png"),
            "idle_up": load_animation("Idle/Idle_Up.png"),
            "idle_down": load_animation("Idle/Idle_Down.png"),
            "idle_left": load_animation("Idle/Idle_Left_Down.png"),
            "idle_right": load_animation("Idle/Idle_Right_Down.png"),
            "idle_up_left": load_animation("Idle/Idle_Up.png"),
            "idle_up_right": load_animation("Idle/Idle_Up.png"),
            "idle_down_left": load_animation("Idle/Idle_Left_Down.png"),
            "idle_down_right": load_animation("Idle/Idle_Right_Down.png"),

            # -- Walk --
            "walk_up": load_animation("Walk/walk_Up.png"),
            "walk_down": load_animation("Walk/walk_Down.png"),
            "walk_left": load_animation("Walk/walk_Left_Down.png"),
            "walk_right": load_animation("Walk/walk_Right_Down.png"),
            "walk_up_left": load_animation("Walk/walk_Left_Up.png"),
            "walk_up_right": load_animation("Walk/walk_Right_Up.png"),
            "walk_down_left": load_animation("Walk/walk_Left_Down.png"),
            "walk_down_right": load_animation("Walk/walk_Right_Down.png"),
        }