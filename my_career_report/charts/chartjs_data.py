import json
import os
from typing import Dict, List, Any


def generate_chartjs_data(data: Dict[str, Any], output_path: str) -> str:
    """Generate a JSON file with Chart.js-friendly data."""
    dataset = {
        "big5": data.get("big5", {}),
        "big5_norm": data.get("big5_norm", {}),
        "riasec": data.get("riasec", {}),
        "riasec_norm": data.get("riasec_norm", {}),
        "values": data.get("values", {}),
        "values_norm": data.get("values_norm", {}),
        "ai": data.get("ai", {}),
        "ai_norm": data.get("ai_norm", {}),
        "soft": {
            "labels": [item["name"] for item in data.get("soft", [])],
            "scores": [item["score"] for item in data.get("soft", [])],
        },
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    return output_path
