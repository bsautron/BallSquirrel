"""Fenêtre pygame : affichage et contrôle à la souris.

Clic gauche : l'écureuil saute vers la souris (seulement s'il est au sol).
R : recommencer   P / Espace : pause   Échap : quitter
"""
import os

import pygame

from .game import ACORN_RADIUS, CATCH_POINTS, PENALTY_POINTS, GROUND_Y, HEIGHT, SQUIRREL_RADIUS, WIDTH, Game
from .physics import GRAVITY

FPS = 60
SIM_DT = 1 / 120   # pas de simulation fixe
IMAGES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")


class App:
    def __init__(self, seed=None):
        pygame.init()
        pygame.display.set_caption("BallSquirrel")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small = pygame.font.Font(None, 22)

        self.background = pygame.image.load(os.path.join(IMAGES, "decors.png")).convert()
        self.ground = pygame.image.load(os.path.join(IMAGES, "bg2.png")).convert_alpha()
        acorn = pygame.image.load(os.path.join(IMAGES, "gland.png")).convert_alpha()
        self.acorn_img = pygame.transform.smoothscale(acorn, (ACORN_RADIUS * 2 + 2,) * 2)
        self.acorn_dead_img = self.acorn_img.copy()
        self.acorn_dead_img.set_alpha(90)
        bird = pygame.image.load(os.path.join(IMAGES, "ab.png")).convert_alpha()
        sprite = pygame.transform.smoothscale(bird, (SQUIRREL_RADIUS * 2 + 8,) * 2)
        self.squirrel_right = sprite
        self.squirrel_left = pygame.transform.flip(sprite, True, False)

        self.game = Game(seed=seed)
        self.paused = False
        self.pops = []   # petites animations "+3" / "-1"

    def run(self):
        accumulator = 0.0
        running = True
        while running:
            frame = self.clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self.game.reset()
                        self.pops.clear()
                    elif event.key in (pygame.K_p, pygame.K_SPACE):
                        self.paused = not self.paused
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.paused:
                    self.game.jump(*event.pos)

            if not self.paused:
                accumulator += min(frame, 0.1)
                while accumulator >= SIM_DT:
                    for kind, acorn in self.game.step(SIM_DT):
                        if kind == "caught":
                            self.pops.append([acorn.body.x, acorn.body.y, 0.6, f"+{CATCH_POINTS}", (255, 230, 80)])
                        elif kind == "penalty":
                            self.pops.append([acorn.body.x, acorn.body.y, 0.6, f"-{PENALTY_POINTS}", (230, 50, 50)])
                    accumulator -= SIM_DT
                for pop in self.pops:
                    pop[1] -= 60 * frame
                    pop[2] -= frame
                self.pops = [p for p in self.pops if p[2] > 0]

            self.draw()
        pygame.quit()

    # --- rendu ---------------------------------------------------------

    def draw(self):
        g = self.game
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.ground, (0, GROUND_Y - 44))

        if g.can_jump() and not self.paused:
            self.draw_aim(pygame.mouse.get_pos())

        for acorn in g.acorns:
            b = acorn.body
            img = self.acorn_dead_img if acorn.dead else self.acorn_img
            self.screen.blit(img, img.get_rect(center=(int(b.x), int(b.y))))

        sq = g.squirrel
        img = self.squirrel_right if g.facing > 0 else self.squirrel_left
        self.screen.blit(img, img.get_rect(center=(int(sq.x), int(sq.y))))

        for x, y, life, text, color in self.pops:
            txt = self.font.render(text, True, color)
            txt.set_alpha(int(255 * min(1, life / 0.3)))
            self.screen.blit(txt, txt.get_rect(center=(int(x), int(y))))

        self.draw_hud()
        pygame.display.flip()

    def draw_aim(self, mouse):
        """Pointillés montrant la trajectoire du saut si on clique maintenant."""
        g = self.game
        vx, vy = g.jump_velocity(*mouse)
        x, y = g.squirrel.x, g.squirrel.y
        end = g.jump_time(*mouse)
        steps = max(4, int(end / 0.04))
        for i in range(1, steps + 1):
            t = end * i / steps
            px = x + vx * t
            py = y + vy * t + 0.5 * GRAVITY * t * t
            if py > GROUND_Y or px < 0 or px > WIDTH:
                break
            pygame.draw.circle(self.screen, (255, 255, 255), (int(px), int(py)), 3)
        pygame.draw.circle(self.screen, (255, 255, 255), mouse, 8, 2)

    def draw_hud(self):
        g = self.game
        score = self.font.render(f"Score : {g.score}", True, (255, 255, 255))
        missed = self.font.render(f"Ratés : {g.missed}", True, (255, 255, 255))
        self.screen.blit(score, (16, 12))
        self.screen.blit(missed, (16, 44))
        help_txt = self.small.render("Clic : sauter   R : rejouer   P : pause   Échap : quitter",
                                     True, (235, 240, 255))
        self.screen.blit(help_txt, (WIDTH - help_txt.get_width() - 16, 14))
        if self.paused:
            txt = self.font.render("PAUSE", True, (255, 255, 255))
            self.screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2)))


def main():
    App().run()
