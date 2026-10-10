import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_approvals


class CheckApprovalsTest(unittest.TestCase):
    def flagged(self, text):
        return [p["claim"].lower() for p in check_approvals.find_uncited(text)]

    def test_flags_uncited_approval(self):
        # The 2026-10-09 aegis-redteam incident shape.
        self.assertEqual(self.flagged("Two findings approved 2026-09-25."), ["approved"])

    def test_flags_uncited_pr_state(self):
        self.assertTrue(self.flagged("Gateway fix: PR is merged and deployed."))
        self.assertTrue(self.flagged("The audit PR is pending review."))

    def test_pr_url_in_same_sentence_is_cited(self):
        text = "Merged https://github.com/hamidmatiny/aegis/pull/42 after review, PR merged."
        self.assertEqual(self.flagged(text), [])

    def test_citation_in_other_sentence_does_not_count(self):
        text = "See https://github.com/hamidmatiny/aegis/pull/42. The rollout was approved."
        self.assertEqual(self.flagged(text), ["approved"])

    def test_responded_queue_item_is_cited(self):
        text = "Hire approved per queue request_id `q-123` (responded 2026-10-08T14:02Z)."
        self.assertEqual(self.flagged(text), [])

    def test_unresponded_queue_item_is_not_a_citation(self):
        self.assertTrue(self.flagged("Tier change approved, request_id q-9 still open."))

    def test_true_state_negations_pass(self):
        text = ("Gateway finding not approved. No PR opened. "
                "Awaiting Hamid (queue `q-7`, no response yet).")
        self.assertEqual(self.flagged(text), [])

    def test_main_exit_codes(self):
        import io
        from contextlib import redirect_stdout
        old = sys.stdin
        try:
            for text, code in (("All five dispatched.", 0), ("Fix authorized.", 1)):
                sys.stdin = io.StringIO(text)
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(check_approvals.main(["-"]), code)
        finally:
            sys.stdin = old


if __name__ == "__main__":
    unittest.main()
