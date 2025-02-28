"""
Data loading, i.e. handling email templates and recipient data.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Union


class DataLoader:
    """Class to handle loading and validating email data from files."""

    @staticmethod
    def load_data(filepath: Union[str, Path]) -> List[Dict]:
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

        if filepath.suffix == '.json':
            with filepath.open('r') as f:
                return json.load(f)
        elif filepath.suffix == '.csv':
            with filepath.open('r') as f:
                return list(csv.DictReader(f))
        else:
            raise ValueError("Unsupported file format. Use .json or .csv")

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
