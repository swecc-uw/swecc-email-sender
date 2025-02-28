"""
SWECC Email Sender - An email automation library using SendGrid.
"""

from swecc_email_sender.core.loader import DataLoader
from swecc_email_sender.core.sender import EmailSender

__version__ = "1.0.7"
__all__ = ["DataLoader", "EmailSender"]
