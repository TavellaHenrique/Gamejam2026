"""Funções compartilhadas para limitar e bloquear o movimento de entidades."""

import pygame


def get_entity_hitbox(entity, position=None):
    """Retorna a metade inferior da área visível, mantendo a largura do sprite."""
    image = entity.image
    center = entity.position if position is None else pygame.Vector2(position)
    if not hasattr(entity, "_collision_cached_visible_bounds"):
        # Mantém a hitbox estável enquanto os quadros da animação mudam.
        entity._collision_cached_visible_bounds = image.get_bounding_rect()

    visible_bounds = entity._collision_cached_visible_bounds
    lower_height = max(1, visible_bounds.height // 2)
    lower_bounds = pygame.Rect(
        visible_bounds.left,
        visible_bounds.bottom - lower_height,
        visible_bounds.width,
        lower_height,
    )
    image_origin = (
        round(center.x - image.get_width() / 2),
        round(center.y - image.get_height() / 2),
    )
    return lower_bounds.move(image_origin)


def can_occupy(entity, position, bounds, obstacles=()):
    """Verifica limites da tela e colisões sem alterar a posição da entidade."""
    hitbox = get_entity_hitbox(entity, position)
    if not bounds.contains(hitbox):
        return False
    return not any(hitbox.colliderect(obstacle) for obstacle in obstacles)


def _collision_score(hitbox, bounds, obstacles):
    """Mede quanto a hitbox está fora da tela ou sobreposta a obstáculos."""
    score = (
        max(0, bounds.left - hitbox.left)
        + max(0, hitbox.right - bounds.right)
        + max(0, bounds.top - hitbox.top)
        + max(0, hitbox.bottom - bounds.bottom)
    )
    for obstacle in obstacles:
        overlap = hitbox.clip(obstacle)
        score += overlap.width * overlap.height
    return score


def can_step(entity, start, destination, bounds, obstacles=()):
    """Permite sair de uma sobreposição somente quando ela diminui."""
    current_score = _collision_score(
        get_entity_hitbox(entity, start),
        bounds,
        obstacles,
    )
    destination_score = _collision_score(
        get_entity_hitbox(entity, destination),
        bounds,
        obstacles,
    )
    # Aceita uma posição sem colisão ou que reduza uma colisão já existente.
    return destination_score == 0 or destination_score < current_score


def _clamp_position_to_bounds(entity, position, bounds):
    """Ajusta a posição após uma troca de quadro alterar a hitbox visível."""
    hitbox = get_entity_hitbox(entity, position)
    offset_x = 0
    offset_y = 0
    if hitbox.left < bounds.left:
        offset_x = bounds.left - hitbox.left
    elif hitbox.right > bounds.right:
        offset_x = bounds.right - hitbox.right
    if hitbox.top < bounds.top:
        offset_y = bounds.top - hitbox.top
    elif hitbox.bottom > bounds.bottom:
        offset_y = bounds.bottom - hitbox.bottom
    return pygame.Vector2(position) + (offset_x, offset_y)


def move_with_collisions(entity, displacement, bounds, obstacles=()):
    """Move por eixo, bloqueando paredes e obstáculos e permitindo deslizar."""
    original_position = pygame.Vector2(entity.position)
    start = _clamp_position_to_bounds(entity, original_position, bounds)
    destination = start.copy()
    displacement = pygame.Vector2(displacement)
    step_count = max(
        1,
        int(max(abs(displacement.x), abs(displacement.y)) / 4) + 1,
    )
    step = displacement / step_count

    # Subpassos evitam atravessar obstáculos mesmo quando o quadro demora muito.
    for _ in range(step_count):
        for axis in (0, 1):
            candidate = destination.copy()
            candidate[axis] += step[axis]
            current_hitbox = get_entity_hitbox(entity, destination)
            candidate_hitbox = get_entity_hitbox(entity, candidate)
            current_score = _collision_score(
                current_hitbox,
                bounds,
                obstacles,
            )
            candidate_score = _collision_score(
                candidate_hitbox,
                bounds,
                obstacles,
            )
            # Move para espaço livre ou permite escapar de uma sobreposição anterior.
            if candidate_score == 0 or candidate_score < current_score:
                destination = candidate

    entity.position.update(destination)
    entity.rect.center = (
        round(destination.x),
        round(destination.y),
    )
    return destination != original_position
