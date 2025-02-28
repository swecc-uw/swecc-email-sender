"""
Markdown processing utilities for email content.
"""

from typing import Optional
import markdown
from markdown.extensions import fenced_code, tables, attr_list

def convert_markdown_to_html(content: str, css_class: Optional[str] = None) -> str:
    """
    Convert markdown content to styled HTML.

    Args:
        content: Markdown content to convert
        css_class: Optional CSS class to add to the wrapper div

    Returns:
        HTML string with default styling
    """
    html = markdown.markdown(content, extensions=[
        'fenced_code',
        'tables',
        'attr_list'
    ])

    class_attr = f' class="{css_class}"' if css_class else ''
    return f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;"{class_attr}>
        {html}
    </div>
    """
