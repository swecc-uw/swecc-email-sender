"""
Command-line interface for SWECC Email Sender.
"""

import sys
import argparse
import logging
from typing import Optional, Sequence

from swecc_email_sender.core.sender import EmailSender
from swecc_email_sender.core.loader import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='Send emails using SendGrid API with support for templates and Markdown.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--from', dest='from_email', type=str, required=True,
                      help='Sender email address')
    parser.add_argument('--api-key', type=str,
                      help='SendGrid API key (defaults to SENDGRID_API_KEY env var)')

    content_group = parser.add_mutually_exclusive_group(required=True)
    content_group.add_argument('--content', type=str,
                           help='Direct email content')
    content_group.add_argument('--template', type=str,
                           help='Path to template file for email content')

    recipient_group = parser.add_mutually_exclusive_group(required=True)
    recipient_group.add_argument('--to', type=str,
                              help='Single recipient email address')
    recipient_group.add_argument('--src', type=str,
                              help='Source file path (CSV or JSON) for batch sending')

    parser.add_argument('--subject', type=str, required=True,
                      help='Email subject')
    parser.add_argument('--markdown', action='store_true',
                      help='Treat content as Markdown')
    parser.add_argument('--validate', action='store_true',
                      help='Validate templates without sending')
    parser.add_argument('--preview', action='store_true',
                      help='Preview the first email content without sending')
    parser.add_argument('--verbose', action='store_true',
                      help='Enable verbose logging')

    return parser

def main(argv: Optional[Sequence[str]] = None) -> int:
    """
    Main entry point for the email sender CLI.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        sender = EmailSender(args.api_key)
        content = (DataLoader.load_template(args.template)
                  if args.template
                  else args.content)

        if args.to:
            success = sender.send_email(
                args.to,
                args.subject,
                content,
                args.from_email,
                args.markdown
            )
            return 0 if success else 1

        data = DataLoader.load_data(args.src)

        if args.preview and data:
            print("\nPreview of first email:")
            print("-" * 40)
            preview_content = sender.format_with_fallback(content, data[0])
            if args.markdown:
                print("Markdown content:")
                print(preview_content)
                print("\nConverted HTML:")
                print(sender.convert_markdown_to_html(preview_content))
            else:
                print(preview_content)
            return 0

        if args.validate:
            logger.info("Validating templates...")
            has_errors = False
            for item in data:
                missing_keys = sender.validate_template_keys(content, item)
                if missing_keys:
                    has_errors = True
                    logger.error(
                        f"Missing keys for {item.get('to_email', 'unknown recipient')}: "
                        f"{', '.join(missing_keys)}"
                    )
                if args.subject:
                    missing_subject_keys = sender.validate_template_keys(args.subject, item)
                    if missing_subject_keys:
                        has_errors = True
                        logger.error(
                            f"Missing subject keys for {item.get('to_email', 'unknown recipient')}: "
                            f"{', '.join(missing_subject_keys)}"
                        )
            return 1 if has_errors else 0

        success_count = 0
        for item in data:
            if 'to_email' not in item:
                logger.warning("Skipping record: missing to_email field")
                continue

            if sender.send_email(
                item['to_email'],
                args.subject,
                content,
                args.from_email,
                args.markdown,
                template_data=item
            ):
                success_count += 1

        logger.info(f"Sent {success_count}/{len(data)} emails successfully")
        return 0 if success_count == len(data) else 1

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
