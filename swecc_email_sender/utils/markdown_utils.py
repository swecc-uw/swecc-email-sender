"""
Markdown processing utilities for email content.
"""

from typing import Optional

import markdown


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
    font_family = """-apple-system, BlinkMacSystemFont, 'Segoe UI',
Roboto, 'Helvetica Neue', Arial, sans-serif"""
    return f"""
    <div style="font-family: {font_family};"{class_attr}>
        {html}
    </div>
    """
