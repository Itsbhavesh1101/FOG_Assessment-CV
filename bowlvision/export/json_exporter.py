import json
from pathlib import Path
from typing import Dict, List, Optional
from ..core.models import PlayerScorecard


def serialize_match_json(
    video_name: str,
    duration_seconds: float,
    players: List[PlayerScorecard],
    output_path: Optional[Path] = None,
) -> dict:
    """
    Serializes match results into standardized JSON matching the assessment format.
    """
    data = {
        "video": video_name,
        "total_duration_seconds": round(duration_seconds, 2),
        "players": [p.to_export_dict() for p in players],
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    return data
