"""
SWECC Email Sender - An email automation library using SendGrid.
"""

from swecc_email_sender.core.sender import EmailSender
from swecc_email_sender.core.loader import DataLoader

__version__ = "1.0.0"
__all__ = ["EmailSender", "DataLoader"]
