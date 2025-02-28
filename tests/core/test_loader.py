"""Tests for DataLoader"""

import json
import pytest
from pathlib import Path
from typing import Any, Dict, List

from swecc_email_sender.core.loader import DataLoader

@pytest.fixture
def temp_json_file(tmp_path) -> Path:
    """Create a temporary JSON file for testing."""
    data = [
        {"to_email": "test1@example.com", "name": "Test 1"},
        {"to_email": "test2@example.com", "name": "Test 2"}
    ]
    file_path = tmp_path / "test.json"
    file_path.write_text(json.dumps(data))
    return file_path

@pytest.fixture
def temp_csv_file(tmp_path) -> Path:
    """Create a temporary CSV file for testing."""
    content = "to_email,name\ntest1@example.com,Test 1\ntest2@example.com,Test 2"
    file_path = tmp_path / "test.csv"
    file_path.write_text(content)
    return file_path

@pytest.fixture
def temp_template_file(tmp_path) -> Path:
    """Create a temporary template file for testing."""
    content = "Hello {name}!\nYour email is {to_email}."
    file_path = tmp_path / "template.txt"
    file_path.write_text(content)
    return file_path

def test_load_json_data(temp_json_file):
    """Test loading data from JSON file."""
    data = DataLoader.load_data(temp_json_file)
    assert len(data) == 2
    assert all(isinstance(item, dict) for item in data)
    assert all('to_email' in item and 'name' in item for item in data)

def test_load_csv_data(temp_csv_file):
    """Test loading data from CSV file."""
    data = DataLoader.load_data(temp_csv_file)
    assert len(data) == 2
    assert all(isinstance(item, dict) for item in data)
    assert all('to_email' in item and 'name' in item for item in data)

def test_load_invalid_format(tmp_path):
    """Test loading data from unsupported file format."""
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.touch()
    with pytest.raises(ValueError):
        DataLoader.load_data(invalid_file)

def test_load_nonexistent_data_file():
    """Test loading data from non-existent file."""
    with pytest.raises(FileNotFoundError):
        DataLoader.load_data("nonexistent.json")

def test_load_template(temp_template_file):
    """Test loading template content."""
    content = DataLoader.load_template(temp_template_file)
    assert "{name}" in content
    assert "{to_email}" in content

def test_load_nonexistent_template():
    """Test loading non-existent template file."""
    with pytest.raises(FileNotFoundError):
        DataLoader.load_template("nonexistent.txt")
