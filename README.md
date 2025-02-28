# SWECC Email Sender

An email automation library using SendGrid API. Supports both single and batch email sending with Markdown formatting and template substitution.

## Features

- Single and batch email sending
- Markdown to HTML conversion with styling
- Template substitution support
- CSV and JSON data source support
- Preview and validation modes

## Installation

```bash
pip install swecc-email-sender
```

## Quick Start

### Single Email

```python
from swecc_email_sender import EmailSender

sender = EmailSender()  # uses SENDGRID_API_KEY environment variable
success = sender.send_email(
    to_email="recipient@example.com",
    subject="Hello!",
    content="This is a test email",
    from_email="sender@example.com"
)
```

### Markdown Email

```python
success = sender.send_email(
    to_email="recipient@example.com",
    subject="Hello!",
    content="# Hello World\n\nThis is a **markdown** email",
    from_email="sender@example.com",
    is_markdown=True
)
```

### Template Email

```python
template = """
Hello {name}!

Your order #{order_id} has been shipped to:
{address}

Thank you for your business!
"""

success = sender.send_email(
    to_email="customer@example.com",
    subject="Order #{order_id} Shipped",
    content=template,
    from_email="shop@example.com",
    template_data={
        "name": "John Doe",
        "order_id": "12345",
        "address": "123 Main St, City, Country"
    }
)
```

## Command Line Interface

The package includes a command-line interface for easy use:

```bash
# Single email
swecc-email-sender --from sender@example.com --to recipient@example.com --subject "Hello" --content "Test email"

# Markdown email
swecc-email-sender --from sender@example.com --to recipient@example.com --subject "Hello" --content "# Hello" --markdown

# Template with CSV data
swecc-email-sender --from sender@example.com --src recipients.csv --subject "Hello {name}" --template email.md

# Preview first email
swecc-email-sender --from sender@example.com --src data.json --subject "Hello" --template email.md --preview

# Validate templates
swecc-email-sender --from sender@example.com --src data.json --subject "Hello {name}" --template email.md --validate
```

### Data File Formats

#### CSV Example (recipients.csv)
```csv
to_email,name,order_id,address
customer1@example.com,John Doe,12345,123 Main St
customer2@example.com,Jane Smith,12346,456 Oak Ave
```

#### JSON Example (data.json)
```json
[
  {
    "to_email": "customer1@example.com",
    "name": "John Doe",
    "order_id": "12345",
    "address": "123 Main St"
  },
  {
    "to_email": "customer2@example.com",
    "name": "Jane Smith",
    "order_id": "12346",
    "address": "456 Oak Ave"
  }
]
```

## Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/swecc/swecc-email-sender.git
cd swecc-email-sender
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Style

The project uses:
- Black for code formatting
- isort for import sorting
- mypy for type checking
- flake8 for linting

To run all checks:

```bash
ruff --fix
isort .
mypy swecc_email_sender
flake8 swecc_email_sender
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
