"""Tests for the cli"""

import os
import pytest
from unittest.mock import patch, MagicMock

from swecc_email_sender.cli import main, create_parser

@pytest.fixture
def mock_env():
    """Set up environment variables for testing."""
    with patch.dict(os.environ, {'SENDGRID_API_KEY': 'test_key'}):
        yield

@pytest.fixture
def mock_sender():
    """Create a mock EmailSender."""
    with patch('swecc_email_sender.cli.EmailSender') as mock:
        instance = MagicMock()
        instance.send_email.return_value = True
        instance.format_with_fallback.return_value = "Hello Test 1"
        mock.return_value = instance
        yield instance

@pytest.fixture
def mock_data_loader():
    """Create a mock DataLoader."""
    with patch('swecc_email_sender.cli.DataLoader') as mock:
        mock.load_template.return_value = "Hello {name}!"
        mock.load_data.return_value = [
            {"to_email": "test1@example.com", "name": "Test 1"},
            {"to_email": "test2@example.com", "name": "Test 2"}
        ]
        yield mock

def test_parser_required_args():
    """Test that required arguments are enforced."""
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])

def test_parser_content_group():
    """Test content group mutual exclusivity."""
    parser = create_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([
            '--from', 'sender@example.com',
            '--to', 'recipient@example.com',
            '--subject', 'Test',
            '--content', 'Hello',
            '--template', 'template.txt'
        ])

def test_single_email_success(mock_env, mock_sender):
    """Test sending a single email successfully."""
    exit_code = main([
        '--from', 'sender@example.com',
        '--to', 'recipient@example.com',
        '--subject', 'Test',
        '--content', 'Hello'
    ])

    assert exit_code == 0
    mock_sender.send_email.assert_called_once()

def test_single_email_failure(mock_env, mock_sender):
    """Test sending a single email with failure."""
    mock_sender.send_email.return_value = False

    exit_code = main([
        '--from', 'sender@example.com',
        '--to', 'recipient@example.com',
        '--subject', 'Test',
        '--content', 'Hello'
    ])

    assert exit_code == 1

def test_batch_email_success(mock_env, mock_sender, mock_data_loader, tmp_path):
    """Test sending batch emails successfully."""
    data_file = tmp_path / "data.json"
    data_file.touch()

    exit_code = main([
        '--from', 'sender@example.com',
        '--src', str(data_file),
        '--subject', 'Test',
        '--content', 'Hello {name}'
    ])

    assert exit_code == 0
    assert mock_sender.send_email.call_count == 2

def test_preview_mode(mock_env, mock_sender, mock_data_loader, tmp_path):
    """Test preview mode doesn't send emails."""
    data_file = tmp_path / "data.json"
    data_file.touch()

    exit_code = main([
        '--from', 'sender@example.com',
        '--src', str(data_file),
        '--subject', 'Test',
        '--content', 'Hello {name}',
        '--preview'
    ])

    assert exit_code == 0
    mock_sender.send_email.assert_not_called()

def test_validate_mode(mock_env, mock_sender, mock_data_loader, tmp_path):
    """Test validation mode doesn't send emails."""
    data_file = tmp_path / "data.json"
    data_file.touch()

    mock_sender.validate_template_keys.return_value = []

    exit_code = main([
        '--from', 'sender@example.com',
        '--src', str(data_file),
        '--subject', 'Test',
        '--template', 'template.txt',
        '--validate'
    ])

    assert exit_code == 0
    mock_sender.send_email.assert_not_called()

def test_exception_handling(mock_env):
    """Test handling of exceptions."""
    with patch('swecc_email_sender.cli.EmailSender') as mock:
        mock.side_effect = Exception("Test error")

        exit_code = main([
            '--from', 'sender@example.com',
            '--to', 'recipient@example.com',
            '--subject', 'Test',
            '--content', 'Hello'
        ])

        assert exit_code == 1
