import unittest

from ballsquirrel.game import GROUND_Y, Game
from ballsquirrel.physics import Arena, Body

DT = 1 / 120


class PhysicsTest(unittest.TestCase):
    def setUp(self):
        self.arena = Arena(1200, 500, GROUND_Y)

    def test_bounces_on_ground_and_comes_to_rest(self):
        b = Body(x=600, y=100, radius=10, restitution=0.6)
        went_up = False
        for _ in range(120 * 10):
            b.step(DT, self.arena)
            self.assertLessEqual(b.y, GROUND_Y - 10 + 1e-6)
            went_up |= b.vy < 0
        self.assertTrue(went_up)
        self.assertTrue(b.on_ground)

    def test_bounces_on_side_walls(self):
        b = Body(x=1180, y=200, radius=10, vx=800)
        for _ in range(60):
            b.step(DT, self.arena)
            self.assertLessEqual(b.x, 1190)
        self.assertLess(b.vx, 0)

        b = Body(x=20, y=200, radius=10, vx=-800)
        for _ in range(60):
            b.step(DT, self.arena)
            self.assertGreaterEqual(b.x, 10)
        self.assertGreater(b.vx, 0)


class GameTest(unittest.TestCase):
    def test_farther_click_jumps_stronger(self):
        g = Game(seed=1)
        near = g.jump_velocity(g.squirrel.x + 50, g.squirrel.y - 100)
        far = g.jump_velocity(g.squirrel.x + 150, g.squirrel.y - 300)
        self.assertGreater(abs(far[1]), abs(near[1]))

    def test_jump_passes_through_click(self):
        for target in [(400, 150), (900, 300), (30, 200), (200, 50)]:
            g = Game(seed=1)
            g.acorns = []
            t_hit = g.jump_time(*target)
            g.jump(*target)
            best = min(
                ((g.step(DT), (g.squirrel.x - target[0]) ** 2 + (g.squirrel.y - target[1]) ** 2)[1]
                 for _ in range(int(t_hit / DT) + 10)))
            self.assertLess(best ** 0.5, 15, target)

    def test_jump_only_from_ground(self):
        g = Game(seed=1)
        self.assertTrue(g.jump(400, 100))
        g.step(DT)
        self.assertFalse(g.jump(400, 100))

    def test_acorns_spawn_from_sides(self):
        g = Game(seed=3)
        for _ in range(120 * 20):
            g.step(DT)
            for a in g.acorns:
                if a.age == DT:
                    self.assertTrue(a.body.x < 20 or a.body.x > 1180)
        self.assertGreater(g.missed, 0)

    def test_catching_acorn_scores(self):
        g = Game(seed=1)
        g.spawn_acorn()
        a = g.acorns[0].body
        a.x, a.y, a.vx, a.vy = g.squirrel.x, g.squirrel.y, 0, 0
        events = g.step(DT)
        self.assertEqual(g.score, 3)
        self.assertEqual(events[0][0], "caught")
        self.assertEqual(g.acorns, [])

    def test_catching_grounded_acorn_costs_a_point(self):
        g = Game(seed=1)
        g.spawn_acorn()
        acorn = g.acorns[0]
        a = acorn.body
        a.x, a.y, a.vx, a.vy = 600, GROUND_Y - a.radius - 1, 300, 200
        events = g.step(DT)
        self.assertTrue(acorn.dead)
        self.assertEqual(g.missed, 1)
        self.assertEqual(events[0][0], "missed")
        a.x, a.y = g.squirrel.x, g.squirrel.y
        events = g.step(DT)
        self.assertEqual(events[0][0], "penalty")
        self.assertEqual(g.score, -1)
        self.assertEqual(g.missed, 1)
        self.assertEqual(g.acorns, [])

    def test_same_seed_same_game(self):
        a, b = Game(seed=42), Game(seed=42)
        for _ in range(600):
            a.step(DT)
            b.step(DT)
        self.assertEqual([(x.body.x, x.body.y) for x in a.acorns],
                         [(x.body.x, x.body.y) for x in b.acorns])


if __name__ == "__main__":
    unittest.main()
