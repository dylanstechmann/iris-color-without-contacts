import math
import unittest

from simulate_feasibility import loss_rate, mobile_at, recovery_time, target_time, total_at


class PigmentBalanceChecks(unittest.TestCase):
    def test_unchanged_source_and_loss_preserve_balance(self):
        for h in [1, 20, None]:
            self.assertAlmostEqual(total_at(7, 1, loss_rate(h), 0, .3), 1)

    def test_complete_suppression_has_declared_half_life(self):
        self.assertAlmostEqual(total_at(3, 0, loss_rate(3), 0, 0), .5)

    def test_added_loss_does_not_silently_increase_source(self):
        k = loss_rate(20)
        a = loss_rate(3)
        equilibrium = .05 * k / (k + a)
        self.assertAlmostEqual(mobile_at(1000, .05, k, a), equilibrium)
        self.assertLess(equilibrium, .05)

    def test_new_loss_pathway_can_act_on_preexisting_store(self):
        self.assertAlmostEqual(mobile_at(3, .05, 0, loss_rate(3)), .5)
        self.assertEqual(mobile_at(100, 0, 0, 0), 1)

    def test_persistent_floor_and_unreachable_target(self):
        self.assertAlmostEqual(total_at(1000, 0, loss_rate(1), 0, .3), .3)
        self.assertIsNone(target_time(.25, .05, loss_rate(20), loss_rate(3), .3))

    def test_target_time_round_trip(self):
        for p in [0, .1, .3]:
            t = target_time(.5, .05, loss_rate(20), loss_rate(3), p)
            self.assertIsNotNone(t)
            self.assertAlmostEqual(total_at(t, .05, loss_rate(20), loss_rate(3), p), .5)

    def test_recovery_time_and_no_native_flux(self):
        t = recovery_time(.9, .2, loss_rate(20), 0)
        self.assertAlmostEqual(1 + (.2 - 1) * math.exp(-loss_rate(20) * t), .9)
        self.assertIsNone(recovery_time(.9, .2, 0, 0))
        self.assertLess(recovery_time(.9, .2, loss_rate(20), 0, 5), t)

    def test_independent_numerical_integration(self):
        for f, h, added_h in [(0, 3, None), (.05, 20, 3), (1, 20, 1)]:
            k, a = loss_rate(h), loss_rate(added_h)
            value, dt = 1.0, 7 / 7000
            derivative = lambda m: f*k - (k+a)*m
            for _ in range(7000):
                q1 = derivative(value)
                q2 = derivative(value + dt*q1/2)
                q3 = derivative(value + dt*q2/2)
                q4 = derivative(value + dt*q3)
                value += dt * (q1 + 2*q2 + 2*q3 + q4) / 6
            self.assertAlmostEqual(value, mobile_at(7, f, k, a), places=10)


if __name__ == "__main__":
    unittest.main()
