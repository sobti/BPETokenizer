# registry.py

import os
import json
from config import REGISTRY_FILE

class WikiRegistry:
    """Manages tracking the frequency of downloads."""
    def __init__(self, registry_path=REGISTRY_FILE):
        self.registry_path = registry_path
        self.registry = self._load()

    def _load(self):
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def increment(self, page_name, lang):
        key = f"{lang}:{page_name}"
        self.registry[key] = self.registry.get(key, 0) + 1
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=4)
        return self.registry[key]