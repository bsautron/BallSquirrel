"""Règles du jeu : l'écureuil, les glands, le score.

Simulation pure (pas de pygame). Le pas de temps est fixe pour que deux
parties avec la même graine soient identiques.
"""
import math
import random
from dataclasses import dataclass, field

from .physics import GRAVITY, Arena, Body

WIDTH, HEIGHT = 1200, 500
GROUND_Y = 395

SQUIRREL_RADIUS = 26
ACORN_RADIUS = 12

# Le saut passe par le point cliqué au bout de JUMP_BASE_TIME + distance / JUMP_PX_PER_S
# secondes : plus on clique loin, plus le saut est long et puissant.
JUMP_BASE_TIME = 0.25
JUMP_PX_PER_S = 1500.0

SPAWN_INTERVAL = (0.7, 1.8)   # secondes entre deux glands
MAX_ACORNS = 6
ACORN_MAX_AGE = 12.0          # un gland qui traîne trop est perdu

CATCH_POINTS = 3              # gland attrapé en plein vol
PENALTY_POINTS = 1            # gland attrapé après avoir touché le sol


@dataclass
class Acorn:
    body: Body
    age: float = 0.0
    dead: bool = False   # a touché le sol : ne rapporte plus de point


@dataclass
class Game:
    seed: int = None
    arena: Arena = field(default_factory=lambda: Arena(WIDTH, HEIGHT, GROUND_Y))

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        self.reset()

    def reset(self):
        self.time = 0.0
        self.score = 0
        self.missed = 0
        self.acorns = []
        self.squirrel = Body(
            x=80, y=GROUND_Y - SQUIRREL_RADIUS, radius=SQUIRREL_RADIUS,
            restitution=0.1, wall_restitution=0.4, ground_drag=25.0, on_ground=True,
        )
        self.facing = 1
        self.next_spawn = 1.0

    # --- actions -------------------------------------------------------

    def can_jump(self):
        return self.squirrel.on_ground

    def jump_time(self, tx, ty):
        """Durée pour atteindre (tx, ty) en sautant."""
        dist = math.hypot(tx - self.squirrel.x, ty - self.squirrel.y)
        return JUMP_BASE_TIME + dist / JUMP_PX_PER_S

    def jump_velocity(self, tx, ty):
        """Vitesse de départ pour que la trajectoire passe par le clic (tx, ty)."""
        t = self.jump_time(tx, ty)
        vx = (tx - self.squirrel.x) / t
        vy = (ty - self.squirrel.y) / t - 0.5 * GRAVITY * t
        return vx, vy

    def jump(self, tx, ty):
        if not self.can_jump():
            return False
        vx, vy = self.jump_velocity(tx, ty)
        self.jump_with_velocity(vx, vy)
        return True

    def jump_with_velocity(self, vx, vy):
        self.squirrel.vx, self.squirrel.vy = vx, vy
        self.squirrel.on_ground = False
        if vx:
            self.facing = 1 if vx > 0 else -1

    # --- simulation ----------------------------------------------------

    def spawn_acorn(self):
        from_left = self.rng.random() < 0.5
        x = ACORN_RADIUS + 1 if from_left else WIDTH - ACORN_RADIUS - 1
        y = self.rng.uniform(60, GROUND_Y - 150)
        vx = self.rng.uniform(250, 650) * (1 if from_left else -1)
        vy = self.rng.uniform(-700, -150)
        body = Body(x=x, y=y, radius=ACORN_RADIUS, vx=vx, vy=vy,
                    restitution=0.2, wall_restitution=0.5, ground_drag=7.0)
        self.acorns.append(Acorn(body))

    def step(self, dt):
        """Avance la partie de dt secondes. Renvoie la liste des événements."""
        events = []
        self.time += dt

        self.next_spawn -= dt
        if self.next_spawn <= 0:
            if len(self.acorns) < MAX_ACORNS:
                self.spawn_acorn()
            self.next_spawn = self.rng.uniform(*SPAWN_INTERVAL)

        self.squirrel.step(dt, self.arena)

        remaining = []
        for acorn in self.acorns:
            acorn.body.step(dt, self.arena)
            acorn.age += dt
            if acorn.body.overlaps(self.squirrel):
                if acorn.dead:   # gland déjà tombé : pénalité
                    self.score -= PENALTY_POINTS
                    events.append(("penalty", acorn))
                else:
                    self.score += CATCH_POINTS
                    events.append(("caught", acorn))
                continue
            if not acorn.dead and (acorn.body.hit_ground or acorn.age > ACORN_MAX_AGE):
                acorn.dead = True
                self.missed += 1
                events.append(("missed", acorn))
            # un gland mort continue de rebondir, puis disparaît une fois arrêté
            if not (acorn.body.on_ground and acorn.body.vx == 0) and acorn.age <= ACORN_MAX_AGE:
                remaining.append(acorn)
        self.acorns = remaining
        return events
