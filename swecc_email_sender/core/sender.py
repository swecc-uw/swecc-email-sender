"""
Email sender module using SendGrid API.
"""

import getpass
import http.client
import json
import logging
import os
from pathlib import Path
from string import Formatter
from typing import Dict, List, Optional

from swecc_email_sender.utils.markdown_utils import convert_markdown_to_html

logger = logging.getLogger(__name__)

SENDGRID_SUCCESS_STATUS = 202
CONFIG_DIR = Path.home() / ".config" / "swecc-email-sender"
CONFIG_FILE = CONFIG_DIR / "email_sender_config.json"


def save_api_key(api_key: str) -> None:
    """Save API key to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps({"SENDGRID_API_KEY": api_key}))
    CONFIG_FILE.chmod(0o600)  # Read/write for owner only


def load_api_key() -> Optional[str]:
    """Load API key from config file or environment."""
    # First check environment
    if api_key := os.getenv("SENDGRID_API_KEY"):
        return api_key

    # Then check config file
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text())
            return str(config.get("SENDGRID_API_KEY"))
        except (json.JSONDecodeError, OSError):
            return None

    return None


def prompt_for_api_key() -> str:
    """Prompt user for SendGrid API key."""
    print(
        "\nSendGrid API key not found. You can get one from https://app.sendgrid.com/settings/api_keys"
    )
    api_key = getpass.getpass("Enter your SendGrid API key (starts with 'SG.'): ")

    # Ask if they want to save it
    save = input("Would you like to save this API key for future use? [Y/n] ").lower()
    if save in ["", "y", "yes"]:
        save_api_key(api_key)
        print(f"API key saved to {CONFIG_FILE}")
    else:
        print(
            """API key will not be saved. Set SENDGRID_API_KEY environment
            variable to skip this prompt."""
        )

    return api_key


class EmailSender:
    """Class to handle email sending operations using SendGrid API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize EmailSender with optional API key."""
        self.api_key = api_key
        self._api_key_loaded = bool(api_key)

    def _ensure_api_key(self) -> None:
        """Ensure API key is available, prompting user if necessary."""
        if self._api_key_loaded:
            return

        # try to load from config or env
        if api_key := load_api_key():
            self.api_key = api_key
            self._api_key_loaded = True
            return

        # prompt user for API key
        self.api_key = prompt_for_api_key()
        self._api_key_loaded = True

    @staticmethod
    def validate_template_keys(template: str, data: Dict[str, str]) -> List[str]:
        """Validate that all format specifiers in template have matching keys in data."""
        required_keys = {
            fname for _, fname, _, _ in Formatter().parse(template) if fname is not None
        }
        return [key for key in required_keys if key not in data]

    @staticmethod
    def format_with_fallback(template: str, data: Dict[str, str], fallback: str = "") -> str:
        """Format string with dict data, replacing missing values with fallback."""

        class DefaultDict(Dict[str, str]):
            def __missing__(self, _: str) -> str:
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
        template_data: Optional[Dict[str, str]] = None,
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
        self._ensure_api_key()

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
            "content": [{"type": content_type, "value": content}],
        }

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        try:
            conn = http.client.HTTPSConnection("api.sendgrid.com")
            conn.request("POST", "/v3/mail/send", body=json.dumps(payload), headers=headers)

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
