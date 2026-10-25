"""Áreas de colisão dos objetos, medidas em pixels do mundo."""

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class ObjectCollisionArea:
    """Retângulo da colisão em pixels relativos ao sprite já escalado."""

    x_px: int
    y_px: int
    width_px: int
    height_px: int


_OBJECT_COLLISION_AREAS = {
    "assets/tileset/scene_objects/banco.png": ObjectCollisionArea(
        x_px=0,
        y_px=15,
        width_px=95,
        height_px=18,
    ),
    "assets/tileset/scene_objects/lixeira.png": ObjectCollisionArea(
        x_px=0,
        y_px=12,
        width_px=24,
        height_px=22,
    ),
    "assets/tileset/scene_objects/maquina_roxa.png": ObjectCollisionArea(
        x_px=0,
        y_px=73,
        width_px=66,
        height_px=25,
    ),
    "assets/tileset/scene_objects/Maquina_verde.png": ObjectCollisionArea(
        x_px=0,
        y_px=73,
        width_px=66,
        height_px=25,
    ),
    "assets/tileset/scene_objects/mesa_cadeira.png": ObjectCollisionArea(
        x_px=0,
        y_px=8,
        width_px=116,
        height_px=110,
    ),
    "assets/tileset/scene_objects/mesa_computador_cadeira.png": (
        ObjectCollisionArea(
            x_px=10,
            y_px=42,
            width_px=88,
            height_px=62,
        )
    ),
    "assets/tileset/scene_objects/mesa_prof.png": ObjectCollisionArea(
        x_px=0,
        y_px=25,
        width_px=119,
        height_px=45,
    ),
    "assets/tileset/scene_objects/mesa_refeitorio.png": ObjectCollisionArea(
        x_px=0,
        y_px=50,
        width_px=282,
        height_px=35,
    ),
    "assets/tileset/scene_objects/pia.png": ObjectCollisionArea(
        x_px=0,
        y_px=0,
        width_px=61,
        height_px=60,
    ),
    "assets/tileset/scene_objects/vaso_2.png": ObjectCollisionArea(
        x_px=0,
        y_px=38,
        width_px=39,
        height_px=28,
    ),
    "assets/tileset/scene_objects/Vaso.png": ObjectCollisionArea(
        x_px=0,
        y_px=59,
        width_px=35,
        height_px=30,
    ),
    "assets/tileset/saguao/saguao_exemplo.jpeg": ObjectCollisionArea(
        x_px=0,
        y_px=0,
        width_px=29,
        height_px=87,
    ), # Cadeira rotacionada do saguão
}

OBJECT_COLLISION_AREAS = {
    image_path.casefold(): area
    for image_path, area in _OBJECT_COLLISION_AREAS.items()
}


def create_object_collision(object_rect, image_path):
    """Cria a área configurada sem redimensionar os valores em pixels."""
    normalized_path = image_path.replace("\\", "/").casefold()
    area = OBJECT_COLLISION_AREAS.get(normalized_path)
    if area is None:
        raise ValueError(
            "Não há área de colisão configurada para "
            f"'{normalized_path}'."
        )

    return pygame.Rect(
        object_rect.left + area.x_px,
        object_rect.top + area.y_px,
        area.width_px,
        area.height_px,
    )
