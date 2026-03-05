import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from core.schema import Manifest
from core.exceptions import StateRollbackError


class StateManager:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.vibe_dir = self.project_path / ".vibe_architect"
        self.manifest_path = self.vibe_dir / "manifest.json"

        # Ensure directories exist
        self.vibe_dir.mkdir(parents=True, exist_ok=True)

        # In-memory stack for snapshots instead of writing to disk constantly
        self._state_stack: List[Manifest] = []

    def save_snapshot(self, manifest: Manifest, tag: str = "auto"):
        """Saves an in-memory snapshot of the current manifest."""
        # Deep copy to ensure independence
        snapshot = manifest.model_copy(deep=True)
        self._state_stack.append(snapshot)

    def persist(self, manifest: Manifest):
        """Persists the current manifest to disk (manifest.json)."""
        json_data = manifest.model_dump_json(indent=2)
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            f.write(json_data)

    def load_latest(self) -> Optional[Manifest]:
        """Loads the current manifest from manifest.json."""
        if not self.manifest_path.exists():
            return None

        try:
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Manifest(**data)
        except Exception:
            return None

    def rollback(self) -> Manifest:
        """Rolls back to the last clean in-memory snapshot."""
        if not self._state_stack:
            raise StateRollbackError("No previous snapshots found to rollback to.")

        # Returns the last snapshot saved before the failed operation
        return self._state_stack.pop()

    def clear_stack(self):
        """Clears the in-memory state stack."""
        self._state_stack.clear()
