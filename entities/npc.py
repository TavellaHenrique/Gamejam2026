
import pygame

from systems.animated_character import AnimatedCharacter
from systems.collision import move_with_collisions
from systems.trigger import Trigger


class NPC(AnimatedCharacter):
    """Personagem não controlável que pode exibir um diálogo ao jogador."""

    def __init__(
        self,
        npc_id,
        display_name,
        position,
        sprite_path,
        dialogue_id,
        frame_width=48,
        frame_height=64,
        frame_count=8,
        scale=4,
        interaction_radius=60,
        ambient_radius=180,
        ambient_lines=(),
        speed=180,
        use_player_animations=False,
        interactable=True,
    ):
        """Configura identidade, alcance de interação e animação do NPC."""
        super().__init__("idle")

        # Identificadores e nome são usados para encontrar o diálogo e exibir o personagem.
        self.npc_id = npc_id
        self.display_name = display_name
        self.dialogue_id = dialogue_id
        self.position = pygame.Vector2(position)
        self.interaction_radius = interaction_radius
        self.interaction_trigger = Trigger(
            position=self.position,
            radius=interaction_radius,
        )
        self.ambient_radius = ambient_radius
        self.ambient_lines = tuple(ambient_lines)
        self.speed = speed
        self.interactable = interactable
        self.facing = pygame.Vector2(0, 1)
        self.is_moving = False
        self.use_player_animations = use_player_animations
        self.opacity = 255

        # A animação usa o sprite informado ou, no NPC de demonstração, os sprites do jogador.
        if use_player_animations:
            self._load_player_animations()
        else:
            self.animations = {
                "idle": self.get_sprites_from_spritesheet(
                    path=sprite_path,
                    frame_width=frame_width,
                    frame_height=frame_height,
                    frame_count=frame_count,
                    scale=scale
                )
            }

        self.set_image()

        # O retângulo de colisão acompanha o centro da posição lógica do NPC.
        self._base_image = self.image
        self.rect = self.image.get_rect(
            center=(
                round(self.position.x),
                round(self.position.y)
            )
        )
        self.interaction_trigger.position.update(self.position)

    def update(self, delta_time):
        """Avança a animação e sincroniza o sprite com a posição atual."""
        super().update(delta_time)

        self._base_image = self.image
        self._apply_facing_image()
        if self.opacity < 255:
            self.image = self.image.copy()
            self.image.set_alpha(self.opacity)

        self.rect = self.image.get_rect(
            center=(
                round(self.position.x),
                round(self.position.y)
            )
        )
        self.interaction_trigger.position.update(self.position)

    def can_interact(self, player):
        """Indica se o jogador está dentro do raio de interação deste NPC."""
        if not self.interactable:
            return False

        return self.interaction_trigger.contains(player)

    def is_in_ambient_range(self, player):
        """Indica se o jogador entrou no raio maior usado para falas aleatórias."""
        distance = self.position.distance_to(player.position)

        return distance <= self.ambient_radius

    def look_at(self, target):
        """Guarda a direção do NPC para um ponto e espelha o sprite se olhar à esquerda."""
        direction = pygame.Vector2(target) - self.position
        if direction.length_squared() == 0:
            return

        self.set_facing(direction)

    def set_facing(self, direction):
        """Define a direção do NPC e atualiza sua animação de parado."""
        direction = pygame.Vector2(direction)
        if direction.length_squared() == 0:
            return

        self.facing = direction.normalize()
        self.is_moving = False
        self._select_animation(moving=False)
        self._apply_facing_image()

    def set_opacity(self, opacity):
        """Atualiza a opacidade do sprite sem alterar os quadros compartilhados."""
        self.opacity = max(0, min(255, round(opacity)))

    def _apply_facing_image(self):
        """Aplica a orientação horizontal disponível no spritesheet do NPC."""
        if self.use_player_animations:
            self.image = self._base_image
        else:
            self.image = pygame.transform.flip(
                self._base_image,
                self.facing.x < 0,
                False,
            )

    def move_towards(
        self,
        target,
        delta_time,
        bounds=None,
        obstacles=(),
        keep_walking=False,
    ):
        """Move o NPC em direção ao ponto e anima a caminhada se configurada."""
        target = pygame.Vector2(target)
        offset = target - self.position
        distance = offset.length()

        if distance == 0:
            self.is_moving = False
            self._select_animation(moving=False)
            return True

        max_distance = self.speed * delta_time
        if bounds is None:
            surface = pygame.display.get_surface()
            bounds = pygame.Rect(0, 0, surface.get_width(), surface.get_height())

        if distance <= max_distance:
            moved = move_with_collisions(self, offset, bounds, obstacles)
            if self.position.distance_to(target) > 0.001:
                self.is_moving = moved
                self._select_animation(moving=moved)
                return False
            self.facing = offset.normalize()
            self.is_moving = keep_walking
            self._select_animation(moving=keep_walking)
            return True

        self.facing = offset / distance
        self.is_moving = move_with_collisions(
            self,
            self.facing * max_distance,
            bounds,
            obstacles,
        )
        self._select_animation(moving=self.is_moving)
        return False

    def _load_player_animations(self):
        """Carrega animações direcionais usando os mesmos sprites do jogador."""
        base_path = "assets/sprites/player/TheFemaleAdventurer"
        frame_settings = {
            "frame_width": 48,
            "frame_height": 64,
            "frame_count": 8,
            "scale": 4,
        }

        def load(path):
            return self.get_sprites_from_spritesheet(
                path=f"{base_path}/{path}",
                **frame_settings,
            )

        idle_paths = {
            "down": "Idle/Idle_Down.png",
            "up": "Idle/Idle_Up.png",
            "left": "Idle/Idle_Left_Down.png",
            "right": "Idle/Idle_Right_Down.png",
            "up_left": "Idle/Idle_Up.png",
            "up_right": "Idle/Idle_Up.png",
            "down_left": "Idle/Idle_Left_Down.png",
            "down_right": "Idle/Idle_Right_Down.png",
        }
        walk_paths = {
            "down": "Walk/walk_Down.png",
            "up": "Walk/walk_Up.png",
            "left": "Walk/walk_Left_Down.png",
            "right": "Walk/walk_Right_Down.png",
            "up_left": "Walk/walk_Left_Up.png",
            "up_right": "Walk/walk_Right_Up.png",
            "down_left": "Walk/walk_Left_Down.png",
            "down_right": "Walk/walk_Right_Down.png",
        }

        self.animations = {
            "idle": load(idle_paths["down"]),
            **{
                f"idle_{direction}": load(path)
                for direction, path in idle_paths.items()
            },
            **{
                f"walk_{direction}": load(path)
                for direction, path in walk_paths.items()
            },
        }

    def _select_animation(self, moving):
        """Seleciona o quadro parado ou de caminhada na direção atual."""
        if not self.use_player_animations:
            return

        x = round(self.facing.x)
        y = round(self.facing.y)
        direction = {
            (0, -1): "up",
            (0, 1): "down",
            (-1, 0): "left",
            (1, 0): "right",
            (-1, -1): "up_left",
            (1, -1): "up_right",
            (-1, 1): "down_left",
            (1, 1): "down_right",
        }.get((x, y), "down")
        animation_name = f"{'walk' if moving else 'idle'}_{direction}"
        self.play(animation_name)
