"""Busca caminhos ortogonais que respeitam os limites e colisões do cenário."""

from collections import deque

import pygame

from game.systems.collision import can_occupy, can_step


def find_path(entity, target, bounds, obstacles=(), cell_size=16):
    """Usa busca em largura para encontrar uma rota de quatro direções."""
    start = pygame.Vector2(entity.position)
    target = pygame.Vector2(target)
    start_cell = (
        round(start.x),
        round(start.y),
    )
    target_cell = (
        round((target.x - start_cell[0]) / cell_size) * cell_size
        + start_cell[0],
        round((target.y - start_cell[1]) / cell_size) * cell_size
        + start_cell[1],
    )

    if not can_occupy(entity, target_cell, bounds, obstacles):
        return []

    queue = deque([start_cell])
    previous = {start_cell: None}
    directions = (
        (cell_size, 0),
        (-cell_size, 0),
        (0, cell_size),
        (0, -cell_size),
    )

    while queue:
        current = queue.popleft()
        if current == target_cell:
            break

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in previous:
                continue
            if not can_step(
                entity,
                current,
                neighbor,
                bounds,
                obstacles,
            ):
                continue

            previous[neighbor] = current
            queue.append(neighbor)

    if target_cell not in previous:
        return []

    path = []
    current = target_cell
    while current is not None:
        path.append(pygame.Vector2(current))
        current = previous[current]

    path.reverse()
    if path:
        path.pop(0)

    # Liga a posição contínua atual à grade por segmentos estritamente ortogonais.
    start_corner = pygame.Vector2(start_cell[0], start.y)
    initial_waypoints = []
    if start_corner.distance_to(start) > 0.001:
        initial_waypoints.append(start_corner)
    if pygame.Vector2(start_cell).distance_to(start_corner) > 0.001:
        initial_waypoints.append(pygame.Vector2(start_cell))

    return initial_waypoints + path


def find_path_near_target(
    entity,
    target,
    bounds,
    obstacles=(),
    cell_size=16,
    max_distance=48,
):
    """Busca uma rota ao destino ou ao ponto acessível mais próximo."""
    target = pygame.Vector2(target)
    start = pygame.Vector2(entity.position)
    candidates = [target]
    directions = (
        (1, 0),
        (-1, 0),
        (0, 1),
        (0, -1),
        (1, 1),
        (-1, 1),
        (1, -1),
        (-1, -1),
    )
    max_radius = max(1, int(max_distance / cell_size))
    for radius in range(1, max_radius + 1):
        candidates.extend(
            target + pygame.Vector2(dx, dy) * (radius * cell_size)
            for dx, dy in directions
        )
    candidates.sort(key=lambda position: position.distance_to(target))

    for candidate in candidates:
        if not can_occupy(entity, candidate, bounds, obstacles):
            continue
        if start.distance_to(candidate) <= 0.001:
            return [], candidate

        segment_distance = start.distance_to(candidate)
        segment_steps = max(1, int(segment_distance / 4) + 1)
        if all(
            can_occupy(
                entity,
                start.lerp(candidate, step / segment_steps),
                bounds,
                obstacles,
            )
            for step in range(1, segment_steps + 1)
        ):
            return [candidate], candidate

        route = find_path(entity, candidate, bounds, obstacles, cell_size)
        if not route:
            continue

        route_end = route[-1]
        segment_distance = route_end.distance_to(candidate)
        segment_steps = max(1, int(segment_distance / 4) + 1)
        segment_is_clear = all(
            can_occupy(
                entity,
                route_end.lerp(candidate, step / segment_steps),
                bounds,
                obstacles,
            )
            for step in range(1, segment_steps + 1)
        )
        if segment_is_clear:
            route.append(candidate)
            return route, candidate
        if route_end.distance_to(target) <= max_distance:
            return route, route_end

    return None, None
