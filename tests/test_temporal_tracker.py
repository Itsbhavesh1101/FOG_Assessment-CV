import unittest
from bowlvision.core.models import PlayerScorecard, FrameCell
from bowlvision.analytics.temporal_aggregator import TemporalScoreboardTracker


class TestTemporalTracker(unittest.TestCase):
    def test_cutaway_state_freeze(self):
        tracker = TemporalScoreboardTracker(window_size=3)

        # Create visible state at t = 0.0s
        card = PlayerScorecard(row_index=1, name="JAGDISH")
        card.frames[1].rolls = ["X"]
        card.frames[1].cumulative_score = 15
        card.total_score = 15

        obs_map = {"JAGDISH": card}
        tracker.process_frame(timestamp=0.0, is_visible=True, observed_players=obs_map)

        # Simulate camera cutaway at t = 1.0s
        snap = tracker.process_frame(timestamp=1.0, is_visible=False, observed_players=None)
        self.assertFalse(snap["scoreboard_visible"])

        # Check preserved state
        current_jagdish = tracker.current_players["JAGDISH"]
        self.assertEqual(current_jagdish.frames[1].rolls, ["X"])
        self.assertEqual(current_jagdish.frames[1].cumulative_score, 15)
        self.assertEqual(current_jagdish.total_score, 15)

    def test_ttl_calculation_from_highest_frame(self):
        tracker = TemporalScoreboardTracker(window_size=3)

        card = PlayerScorecard(row_index=2, name="VISHAL")
        card.frames[1].rolls = ["8-"]
        card.frames[1].cumulative_score = 8
        card.frames[2].rolls = ["3-"]
        card.frames[2].cumulative_score = 11

        tracker.process_frame(timestamp=0.0, is_visible=True, observed_players={"VISHAL": card})
        self.assertEqual(tracker.current_players["VISHAL"].total_score, 11)


if __name__ == "__main__":
    unittest.main()
