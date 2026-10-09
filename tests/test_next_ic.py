import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import next_ic


class NextIcTest(unittest.TestCase):
    def test_one_ic_per_hour_in_order(self):
        picked = [next_ic.pick(h)["dispatch"] for h in range(8, 13)]
        self.assertEqual(picked, ["aegis-gateway", "aegis-policy-engine", "aegis-model-router",
                                  "aegis-agent-gate", "aegis-audit"])

    def test_outside_slots_dispatches_nobody(self):
        self.assertIsNone(next_ic.pick(7)["dispatch"])
        self.assertIsNone(next_ic.pick(13)["dispatch"])

    def test_cron_covers_every_slot(self):
        self.assertEqual(next_ic.CRON, "0 8-12 * * *")

    def test_message_names_the_component(self):
        self.assertIn("`audit`", next_ic.pick(12)["message"])


if __name__ == "__main__":
    unittest.main()
