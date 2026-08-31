import csv
import json
import tempfile
import unittest
from pathlib import Path
from bowlvision.core.models import PlayerScorecard
from bowlvision.export.json_exporter import serialize_match_json
from bowlvision.export.csv_exporter import serialize_match_csv
from bowlvision.export.visualizer import ScoreboardVisualizer


class TestExporters(unittest.TestCase):
    def setUp(self):
        self.p1 = PlayerScorecard(row_index=1, name="JAGDISH")
        self.p1.frames[1].rolls = ["X"]
        self.p1.frames[1].cumulative_score = 15
        self.p1.total_score = 15

        self.p2 = PlayerScorecard(row_index=2, name="VISHAL")

    def test_json_and_csv_serialization(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "output.json"
            csv_file = Path(tmpdir) / "output.csv"

            data = serialize_match_json(
                video_name="game.mp4",
                duration_seconds=57.8,
                players=[self.p1, self.p2],
                output_path=json_file,
            )
            serialize_match_csv(players=[self.p1, self.p2], output_path=csv_file)

            self.assertEqual(data["video"], "game.mp4")
            self.assertEqual(data["total_duration_seconds"], 57.8)
            self.assertEqual(data["players"][0]["name"], "JAGDISH")
            self.assertEqual(data["players"][0]["frames"]["1"]["cumulative"], 15)
            self.assertIsNone(data["players"][1]["frames"]["1"])

            # Read back JSON
            with open(json_file, "r", encoding="utf-8") as f:
                loaded_json = json.load(f)
            self.assertEqual(loaded_json["video"], "game.mp4")

            # Read back CSV
            with open(csv_file, "r", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows[0]["player"], "JAGDISH")
            self.assertEqual(rows[0]["rolls"], "X")
            self.assertEqual(rows[0]["cumulative"], "15")

    def test_terminal_visualizer_formatting(self):
        summary = ScoreboardVisualizer.format_terminal_summary([self.p1])
        self.assertIn("JAGDISH", summary)
        self.assertIn("TTL: 15", summary)


if __name__ == "__main__":
    unittest.main()
