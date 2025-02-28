"""
Post-install hook for SWECC Email Sender.
"""

import sys
import os
from pathlib import Path
from typing import Any, Dict

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

def is_ci_environment() -> bool:
    """Check if we're running in a CI environment."""
    ci_vars = [
        'CI',
        'GITHUB_ACTIONS',
    ]
    return any(var in os.environ for var in ci_vars)

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        """Initialize build hook."""
        super().initialize(version, build_data)

        # skip interactive setup in CI environments
        if is_ci_environment():
            return

        try:
            # only run setup on fresh install (not an upgrade)
            if not (Path.home() / ".swecc" / "email_sender_config.json").exists():
                print("\nWould you like to configure SWECC Email Sender now? [Y/n] ", end="")
                response = input().lower()
                if response in ["", "y", "yes"]:
                    from scripts.setup_env import setup_environment
                    setup_environment()
                else:
                    print("\nYou can configure later by running: swecc-email-sender-setup")
        except Exception as e:
            print(f"\nError during post-install setup: {e}", file=sys.stderr)
            print("You can configure later by running: swecc-email-sender-setup", file=sys.stderr)
