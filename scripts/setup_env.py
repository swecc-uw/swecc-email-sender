#!/usr/bin/env python3
"""
Setup script to configure environment variables for SWECC Email Sender.
This script:
1. prompts for necessary API keys and configuration
2. stores them securely in the user's home directory
3. generates shell scripts to load the environment variables
"""

import json
import os
import platform
import stat
from pathlib import Path
from typing import Dict

CONFIG_DIR = Path.home() / ".swecc"
CONFIG_FILE = CONFIG_DIR / "email_sender_config.json"
SHELL_SCRIPTS_DIR = CONFIG_DIR / "shell"

# templates
BASH_SCRIPT = """#!/bin/bash
# SWECC Email Sender environment variables
export SENDGRID_API_KEY="{sendgrid_key}"
"""

WINDOWS_SCRIPT = """@echo off
:: SWECC Email Sender environment variables
set SENDGRID_API_KEY={sendgrid_key}
"""

def create_directory(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)

def get_user_input(prompt: str, secret: bool = False) -> str:
    """Get user input, optionally hiding it for secrets."""
    if secret and platform.system() != "Windows":
        import getpass
        return getpass.getpass(prompt)
    return input(prompt)

def save_config(config: Dict[str, str]) -> None:
    """Save configuration to file."""
    create_directory(CONFIG_DIR)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    # readable only by the owner
    CONFIG_FILE.chmod(stat.S_IRUSR | stat.S_IWUSR)

def create_shell_scripts(config: Dict[str, str]) -> None:
    """Create shell scripts for different platforms."""
    create_directory(SHELL_SCRIPTS_DIR)

    # create bash script (Linux/macOS)
    bash_script = BASH_SCRIPT.format(sendgrid_key=config["SENDGRID_API_KEY"])
    bash_script_path = SHELL_SCRIPTS_DIR / "load_env.sh"
    bash_script_path.write_text(bash_script)
    bash_script_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    # create batch script (Windows)
    bat_script = WINDOWS_SCRIPT.format(sendgrid_key=config["SENDGRID_API_KEY"])
    bat_script_path = SHELL_SCRIPTS_DIR / "load_env.bat"
    bat_script_path.write_text(bat_script)
    bat_script_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

def setup_environment() -> None:
    """Main setup function."""
    print("SWECC Email Sender Setup")
    print("=======================")
    print("\nThis script will help you configure your environment variables.")
    print("The configuration will be saved in:", CONFIG_DIR)

    config = {}
    config["SENDGRID_API_KEY"] = get_user_input(
        "\nEnter your SendGrid API Key (starts with 'SG.'): ",
        secret=True
    )

    save_config(config)
    create_shell_scripts(config)

    print("\nConfiguration saved successfully!")
    print("\nTo load the environment variables:")
    if platform.system() == "Windows":
        print(f"Run: {SHELL_SCRIPTS_DIR / 'load_env.bat'}")
        print("\nTo load permanently, add this to your environment variables through System Properties.")
    else:
        print(f"Run: source {SHELL_SCRIPTS_DIR / 'load_env.sh'}")
        print("\nTo load permanently, add this line to your shell's rc file (~/.bashrc, ~/.zshrc, etc.):")
        print(f"source {SHELL_SCRIPTS_DIR / 'load_env.sh'}")

if __name__ == "__main__":
    try:
        setup_environment()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        exit(1)
    except Exception as e:
        print(f"\nError during setup: {e}")
        exit(1)
