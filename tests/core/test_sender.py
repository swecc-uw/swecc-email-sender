"""Tests for EmailSender"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from swecc_email_sender.core.sender import EmailSender

@pytest.fixture
def sender():
    """Create an EmailSender instance with a test API key."""
    return EmailSender(api_key='test_key')

def test_init_with_explicit_key():
    """Test initialization with explicit API key."""
    sender = EmailSender(api_key='explicit_key')
    assert sender.api_key == 'explicit_key'

def test_validate_template_keys():
    """Test template key validation."""
    template = "Hello {name}! Your order #{order_id} is ready."
    data = {"name": "John", "email": "john@example.com"}
    missing = EmailSender.validate_template_keys(template, data)
    assert missing == ["order_id"]

def test_format_with_fallback():
    """Test template formatting with fallback values."""
    template = "Hello {name}! Your order #{order_id} is ready."
    data = {"name": "John"}
    result = EmailSender.format_with_fallback(template, data, fallback='N/A')
    assert result == "Hello John! Your order #N/A is ready."

@pytest.mark.parametrize("is_markdown,expected_type", [
    (True, "text/html"),
    (False, "text/plain")
])
def test_send_email_content_type(sender, is_markdown, expected_type):
    """Test email sending with different content types."""
    mock_response = MagicMock()
    mock_response.status = 202

    with patch('http.client.HTTPSConnection') as mock_conn:
        mock_conn.return_value.getresponse.return_value = mock_response

        success = sender.send_email(
            to_email="test@example.com",
            subject="Test",
            content="Test content",
            from_email="sender@example.com",
            is_markdown=is_markdown
        )

        assert success

        call_args = mock_conn.return_value.request.call_args
        sent_payload = json.loads(call_args[1]['body'])
        assert sent_payload['content'][0]['type'] == expected_type

def test_send_email_with_template_data(sender):
    """Test email sending with template substitution."""
    mock_response = MagicMock()
    mock_response.status = 202

    with patch('http.client.HTTPSConnection') as mock_conn:
        mock_conn.return_value.getresponse.return_value = mock_response

        success = sender.send_email(
            to_email="test@example.com",
            subject="Order #{order_id}",
            content="Hello {name}!",
            from_email="sender@example.com",
            template_data={"name": "John", "order_id": "12345"}
        )

        assert success

        call_args = mock_conn.return_value.request.call_args
        sent_payload = json.loads(call_args[1]['body'])
        assert sent_payload['subject'] == "Order #12345"
        assert sent_payload['content'][0]['value'] == "Hello John!"

def test_send_email_failure(sender):
    """Test email sending failure handling."""
    mock_response = MagicMock()
    mock_response.status = 400
    mock_response.read.return_value = b'{"errors": ["Invalid recipient"]}'

    with patch('http.client.HTTPSConnection') as mock_conn:
        mock_conn.return_value.getresponse.return_value = mock_response

        success = sender.send_email(
            to_email="invalid@example.com",
            subject="Test",
            content="Test content",
            from_email="sender@example.com"
        )

        assert not success

def test_send_email_exception(sender):
    """Test email sending exception handling."""
    with patch('http.client.HTTPSConnection') as mock_conn:
        mock_conn.return_value.request.side_effect = Exception("Connection error")

        success = sender.send_email(
            to_email="test@example.com",
            subject="Test",
            content="Test content",
            from_email="sender@example.com"
        )

        assert not success
