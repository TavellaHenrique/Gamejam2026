"""Objetos, posições e colisões do laboratório da professora.

Mantém o mesmo layout base do Laboratório 1 para evitar diferenças visuais e de
colisão entre ambientes, mas sem NPCs.
"""

from game.systems.tilemap_scene import LABORATORY_FURNITURE, LABORATORY_OBSTACLES


ENVIRONMENT_OBSTACLES = LABORATORY_OBSTACLES

LABORATORY_OBJECTS = [
    {
        "image": "assets/tileset/scene_objects/mesa_prof.png",
        "position": (44, 110),
        "occlusion_y": 62,
    },
    *(
        {
            "image": "assets/tileset/scene_objects/Vaso.png",
            "position": position,
            "occlusion_y": 60,
        }
        for position in (
            (913, 119),
            (913, 190),
            (913, 262),
            (913, 335),
            (913, 478),
            (913, 551),
        )
    ),
    *(
        {
            "image": "assets/tileset/scene_objects/mesa_computador_cadeira.png",
            "position": position,
            "occlusion_y": 60,
        }
        for position in LABORATORY_FURNITURE
    ),
]


def create_laboratory_objects(scene):
    """Instancia os objetos da planta com colisão e oclusão configuradas."""
    return [
        scene.create_map_object(
            object_layout["image"],
            object_layout["position"],
            collidable=True,
            occlusion_y=object_layout["occlusion_y"],
        )
        for object_layout in LABORATORY_OBJECTS
    ]


def create_environment_obstacles(scene):
    """Converte as colisões fixas da planta para coordenadas do mundo."""
    return tuple(
        scene.map_rect(rect)
        for rect in ENVIRONMENT_OBSTACLES
    )
