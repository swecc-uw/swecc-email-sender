"""
Email sender module using SendGrid API.
"""

import http.client
import json
import logging
import os
from string import Formatter
from typing import Dict, Optional

from swecc_email_sender.utils.markdown_utils import convert_markdown_to_html

logger = logging.getLogger(__name__)

SENDGRID_SUCCESS_STATUS = 202

class EmailSender:
    """Class to handle email sending operations using SendGrid API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize EmailSender with optional API key."""
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            msg = """No SendGrid API key provided. Set SENDGRID_API_KEY
environment variable or pass it as an argument."""
            raise ValueError(msg)

    @staticmethod
    def validate_template_keys(template: str, data: dict) -> list[str]:
        """Validate that all format specifiers in template have matching keys in data."""
        required_keys = {
            fname for _, fname, _, _ in Formatter().parse(template)
            if fname is not None
        }
        return [key for key in required_keys if key not in data]

    @staticmethod
    def format_with_fallback(template: str, data: dict, fallback: str = '') -> str:
        """Format string with dict data, replacing missing values with fallback."""
        class DefaultDict(dict):
            def __missing__(self, _):
                return fallback

        try:
            return template.format_map(DefaultDict(data))
        except ValueError as e:
            logger.warning(f"Format error in template: {e}")
            return template

    def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        from_email: str,
        is_markdown: bool = False,
        template_data: Optional[Dict] = None
    ) -> bool:
        """
        Send a single email using SendGrid's API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            content: Email body content (can include format specifiers)
            from_email: Sender email address
            is_markdown: Whether the content is Markdown
            template_data: Dictionary of values to format the content with

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if template_data:
            content = self.format_with_fallback(content, template_data)
            subject = self.format_with_fallback(subject, template_data)

        content_type = "text/html" if is_markdown else "text/plain"
        if is_markdown:
            content = convert_markdown_to_html(content)

        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [{"type": content_type, "value": content}]
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            conn = http.client.HTTPSConnection("api.sendgrid.com")
            conn.request(
                "POST",
                "/v3/mail/send",
                body=json.dumps(payload),
                headers=headers
            )

            response = conn.getresponse()
            conn.close()

            if response.status == SENDGRID_SUCCESS_STATUS:
                logger.info(f"Email sent successfully to {to_email}")
                return True

            error_msg = response.read().decode()
            logger.error(f"SendGrid API error (status {response.status}): {error_msg}")
            return False

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e!s}")
            return False
