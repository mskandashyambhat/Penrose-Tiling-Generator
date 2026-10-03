"""Pure geometry for the Penrose triangle generator."""

from __future__ import annotations

import math
from dataclasses import dataclass

PHI = (1 + math.sqrt(5)) / 2
TAU = math.tau


@dataclass(frozen=True)
class Triangle:
    a: complex
    b: complex
    c: complex
    kind: int  # 0: thin, 1: thick


def subdivide(triangle: Triangle) -> list[Triangle]:
    """Apply Robinson's two subdivision rules using 1/phi cut points."""
    a, b, c = triangle.a, triangle.b, triangle.c
    if triangle.kind == 0:
        p = a + (b - a) / PHI
        return [Triangle(c, p, a, 0), Triangle(p, c, b, 1)]

    p = a + (b - a) / PHI
    q = a + (c - a) / PHI
    return [
        Triangle(p, q, a, 0),
        Triangle(p, b, q, 1),
        Triangle(q, b, c, 1),
    ]


def seed_triangles(scale: float, rotation: float) -> list[Triangle]:
    """Create a symmetric 10-fold seed around the origin."""
    triangles: list[Triangle] = []
    for index in range(10):
        start = rotation + index * TAU / 10
        outer_a = scale * complex(math.cos(start), math.sin(start))
        outer_b = scale * complex(
            math.cos(start + TAU / 10), math.sin(start + TAU / 10)
        )
        triangles.append(Triangle(0j, outer_a, outer_b, index % 2))
    return triangles


def generate(depth: int, scale: float, rotation_degrees: float) -> list[Triangle]:
    triangles = seed_triangles(scale, math.radians(rotation_degrees))
    for _ in range(depth):
        triangles = [child for triangle in triangles for child in subdivide(triangle)]
    return triangles
