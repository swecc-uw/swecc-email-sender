"""
Data loading module for handling email templates and recipient data.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Union


class DataLoader:
    """Class to handle loading and validating email data from files."""

    @staticmethod
    def load_data(filepath: Union[str, Path]) -> List[Dict[str, str]]:
        """
        Load data from either CSV or JSON file.

        Args:
            filepath: Path to the data file (CSV or JSON)

        Returns:
            List of dictionaries containing email data

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is not supported
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        result: List[Dict[str, str]] = []

        if filepath.suffix == ".json":
            with filepath.open("r") as f:
                result = json.load(f)
        elif filepath.suffix == ".csv":
            with filepath.open("r") as f:
                reader = csv.DictReader(f)
                result = [{k: str(v) for k, v in row.items()} for row in reader]
        else:
            raise ValueError("Unsupported file format. Use .json or .csv")

        return result

    @staticmethod
    def load_template(filepath: Union[str, Path]) -> str:
        """
        Load template content from file.

        Args:
            filepath: Path to the template file

        Returns:
            String containing the template content

        Raises:
            FileNotFoundError: If the template file doesn't exist
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Template file not found: {filepath}")

        return filepath.read_text()
