# test_tr_engine.py - The Combined Unit Test Suite (v1.0 Final)
import unittest
from tr_engine import System, Entity, Cycle, Phase, TaskCreditLedger, split, refract, recombine, TR_execute

class TestTRImplementation(unittest.TestCase):
    def setUp(self):
        """Set up the core test case for primary tests."""
        self.entities = [
            Entity(id="D1", state=5.0, stable_states={4.0, 8.0}),
            Entity(id="D2", state=10.0, stable_states={4.0, 8.0}),
            Entity(id="D3", state=2.0, stable_states={4.0, 8.0}),
        ]
        self.cycle = Cycle(length=12, phases=3)
        self.system = System(entities=self.entities, cycle=self.cycle, target_state=4.0)

    # Primary Tests (authored by Gemini)
    def test_core_trace_case_execution(self):
        """Tests the primary trace case: S=17 -> {4,4,4}, excess=5.0."""
        updated_system, success = TR_execute(self.system)
        self.assertTrue(success)
        final_states = {entity.state for entity in updated_system.entities}
        self.assertEqual(final_states, {4.0})
        self.assertAlmostEqual(updated_system.ledger.excess, 5.0)

    def test_split_precision(self):
        """Tests split function for precision."""
        total_state = sum(e.state for e in self.system.entities)
        phases = split(total_state, self.system.cycle.phases)
        self.assertEqual(len(phases), 3)
        self.assertAlmostEqual(sum(p.state for p in phases), 17.0)

    # Edge Case Tests (authored by Grok)
    def test_split_non_divisible(self):
        """Tests split with a non-divisible total state."""
        phases = split(17.0, 4)
        self.assertEqual(len(phases), 4)
        self.assertAlmostEqual(sum(p.state for p in phases), 17.0)

    def test_refract_invalid_target(self):
        """Tests that refract raises an error with an invalid target state."""
        system_invalid = self.system
        system_invalid.target_state = 5.0 # This state is not in the allowed stable_states set
        system_invalid.phases = split(17.0, 3)
        with self.assertRaises(ValueError):
            refract(system_invalid)

    def test_recombine_tolerance_violation(self):
        """Tests that recombine raises an error if no stable state is within tolerance."""
        system_invalid = self.system
        system_invalid.config["MAX_TOLERANCE"] = 0.1
        # ideal state will be 4.0, but we force an adjusted state that is too far
        system_invalid.phases = [Phase(0, 4.0, 6.0)]
        with self.assertRaises(ValueError):
            recombine(system_invalid)

    def test_tr_execute_zero_state(self):
        """Tests that TR_execute raises an error for a zero or negative total state."""
        system_zero = self.system
        system_zero.entities = [Entity("D1", 0.0, {4.0, 8.0})]
        with self.assertRaises(ValueError):
            TR_execute(system_zero)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
