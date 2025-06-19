# File: utils/loader.py
import json
import yaml


def load_data(path: str) -> dict:
    """Load a JSON or YAML file and return a dictionary."""
    with open(path, 'r', encoding='utf-8') as f:
        if path.endswith('.json'):
            return json.load(f)
        elif path.endswith(('.yml', '.yaml')):
            return yaml.safe_load(f)
        else:
            raise ValueError('Unsupported file format')
