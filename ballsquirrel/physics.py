"""Physique 2D minimale : gravité, rebonds sur le sol et sur les bords.

Aucune dépendance graphique, pour pouvoir faire tourner la simulation
sans fenêtre (tests, futur apprentissage).
"""
from dataclasses import dataclass

GRAVITY = 1500.0        # px/s²
REST_SPEED = 60.0       # sous cette vitesse verticale, un rebond s'arrête


@dataclass
class Arena:
    width: float
    height: float
    ground_y: float     # ordonnée du sol (y vers le bas)


@dataclass
class Body:
    x: float
    y: float
    radius: float
    vx: float = 0.0
    vy: float = 0.0
    # Coefficient de restitution : part de la vitesse gardée au rebond sur le sol
    # (balle rebondissante ~0.8, bois ~0.5, gland ~0.2, 0 = ne rebondit pas).
    restitution: float = 0.5
    wall_restitution: float = 0.8
    ground_drag: float = 4.0   # freinage quand on roule ou glisse au sol (1/s)
    on_ground: bool = False
    hit_ground: bool = False   # a touché le sol pendant le dernier pas

    def step(self, dt, arena):
        self.vy += GRAVITY * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        self.on_ground = False
        self.hit_ground = False
        floor = arena.ground_y - self.radius
        if self.y >= floor:
            self.y = floor
            self.hit_ground = True
            if self.vy > 0:
                self.vy = -self.vy * self.restitution
            if abs(self.vy) < REST_SPEED:
                self.vy = 0.0
                self.on_ground = True

        if self.on_ground:
            self.vx *= max(0.0, 1.0 - self.ground_drag * dt)
            if abs(self.vx) < 5.0:
                self.vx = 0.0

        if self.x < self.radius:
            self.x = self.radius
            self.vx = abs(self.vx) * self.wall_restitution
        elif self.x > arena.width - self.radius:
            self.x = arena.width - self.radius
            self.vx = -abs(self.vx) * self.wall_restitution

    def overlaps(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        r = self.radius + other.radius
        return dx * dx + dy * dy <= r * r
