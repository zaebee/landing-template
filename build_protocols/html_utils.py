"""
HTML generation utility functions.

This module provides simple helper functions to create HTML elements
programmatically, aiming to improve readability and maintainability
of HTML construction code compared to direct f-string formatting.
"""

from typing import Dict, Optional


def escape_html(text: str) -> str:
    """Basic HTML escaping for content."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def create_element(
    tag_name: str, content: str = "", attributes: Optional[Dict[str, str]] = None
) -> str:
    """
    Creates an HTML element string.

    Args:
        tag_name: The name of the HTML tag (e.g., "div", "h3", "p").
        content: The inner HTML content of the element. Content is NOT escaped by default.
                 If content needs escaping, it should be done beforehand.
        attributes: A dictionary of HTML attributes (e.g., {"class": "my-class"}).
                    Attribute values are escaped.

    Returns:
        An HTML string representing the element.
    """
    attrs_str = ""
    if attributes:
        attrs_list = []
        for k, v in attributes.items():
            if v is not None:  # Only include attributes with actual values
                attrs_list.append(f'{escape_html(k)}="{escape_html(str(v))}"')
        if attrs_list:
            attrs_str = " " + " ".join(attrs_list)

    if not content and tag_name.lower() in [
        "img",
        "br",
        "hr",
        "input",
        "meta",
        "link",
    ]:  # Self-closing tags
        return f"<{tag_name}{attrs_str}>"
    else:
        return f"<{tag_name}{attrs_str}>{content}</{tag_name}>"


def img(src: str, alt: str = "", attributes: Optional[Dict[str, str]] = None) -> str:
    """
    Creates an <img> HTML element string.

    Args:
        src: The source URL of the image.
        alt: The alternative text for the image.
        attributes: Additional HTML attributes for the img tag.

    Returns:
        An HTML string representing the <img> element.
    """
    final_attrs: Dict[str, str] = {"src": src, "alt": alt}
    if attributes:
        final_attrs.update(attributes)

    # Remove alt if it's empty and not explicitly provided in attributes,
    # but always keep src.
    if not alt and "alt" not in (attributes or {}):
        final_attrs["alt"] = ""  # Ensure alt is present, even if empty, for validity.

    return create_element("img", attributes=final_attrs)
