"""
Installation state management for resume capability
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class StateManager:
    """Manages installation state for resume capability"""

    def __init__(self, state_file: Optional[Path] = None):
        """Initialize state manager

        Args:
            state_file: Path to state file. Defaults to ~/.misp-install/state.json
        """
        if state_file is None:
            state_file = Path.home() / ".misp-install" / "state.json"

        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def save(self, phase: int, phase_name: str, config: Optional[Dict] = None):
        """Save installation state

        Args:
            phase: Current phase number
            phase_name: Descriptive phase name
            config: Configuration dictionary (optional)
        """
        state = {
            "phase": phase,
            "phase_name": phase_name,
            "timestamp": datetime.now().isoformat(),
        }

        if config:
            state["config"] = config

        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def load(self) -> Optional[Dict]:
        """Load previous installation state

        Returns:
            State dictionary or None if no state exists
        """
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return None

    def clear(self):
        """Clear installation state"""
        if self.state_file.exists():
            self.state_file.unlink()

    def get_last_phase(self) -> Optional[int]:
        """Get last completed phase number

        Returns:
            Phase number or None if no state exists
        """
        state = self.load()
        if state:
            return state.get('phase')
        return None

    def get_next_phase(self) -> int:
        """Get next phase to execute

        Returns:
            Next phase number (last + 1, or 1 if no state)
        """
        last_phase = self.get_last_phase()
        if last_phase is not None:
            return last_phase + 1
        return 1

    def exists(self) -> bool:
        """Check if state file exists

        Returns:
            True if state file exists
        """
        return self.state_file.exists()
