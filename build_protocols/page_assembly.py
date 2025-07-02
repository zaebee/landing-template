"""
Provides the `DefaultPageBuilder` for assembling final HTML pages.

This module includes functionality to extract structural parts from a base
HTML template, and then assemble these parts with translated content,
main content, and language-specific attributes to form a complete HTML page.
"""

import logging
import re
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup
from bs4.element import Tag

from .interfaces import PageBuilder, TranslationProvider, Translations

logger = logging.getLogger(__name__)


class PageAssemblyError(Exception):
    """Custom exception for errors during page assembly."""


class DefaultPageBuilder(PageBuilder):
    """
    Default implementation for assembling HTML pages.

    This builder can extract parts from a base HTML file (like header, footer)
    and then combine them with generated main content and translations to
    produce the final HTML output for different languages.
    """

    def __init__(self, translation_provider: TranslationProvider):
        """Initializes the DefaultPageBuilder.

        Args:
            translation_provider: An instance of a TranslationProvider
                                  to handle content translation.
        """
        self.translation_provider = translation_provider

    def _get_attributes_string(self, tag: Tag) -> str:
        """Converts a BeautifulSoup Tag's attributes into an HTML string.

        Args:
            tag: The BeautifulSoup Tag object.

        Returns:
            A string representing the tag's attributes (e.g., ' class="foo" id="bar"').
        """
        attrs_list = []
        if tag.attrs:
            for key, value in tag.attrs.items():
                if isinstance(value, list):  # Handle multi-valued attributes like class
                    value = " ".join(value)
                attrs_list.append(f'{key}="{value}"')
        return " ".join(attrs_list)

    def _extract_doctype(self, base_content: str) -> str:
        """Extracts the DOCTYPE declaration from the base HTML content.

        Args:
            base_content: The full string content of the base HTML file.

        Returns:
            The DOCTYPE string (e.g., "<!DOCTYPE html>\n") or an empty string
            if not found.
        """
        doctype_match = re.match(
            r"^(<!DOCTYPE[^>]+>)\s*", base_content, re.IGNORECASE | re.DOTALL
        )
        return doctype_match.group(1) + "\n" if doctype_match else ""

    def _extract_header_footer_from_body(
        self, body_tag: Optional[Tag]
    ) -> Tuple[List[str], List[str]]:
        """Extracts header and footer content parts relative to the <main> tag.

        Args:
            body_tag: The BeautifulSoup Tag object for the <body> element.

        Returns:
            A tuple containing two lists of strings: (header_parts, footer_parts).
        """
        header_content_parts: List[str] = []
        footer_content_parts: List[str] = []

        if not (body_tag and isinstance(body_tag, Tag)):
            logger.warning("<body> tag not found. Header/footer content will be empty.")
            return header_content_parts, footer_content_parts

        main_tag = body_tag.find("main")
        if not (main_tag and isinstance(main_tag, Tag)):
            logger.warning(
                "<main> tag not found. Header/footer content may be incomplete."
            )
            # If no <main>, consider all direct children of <body> as header for simplicity,
            # or handle as an error, or return empty. For now, returning empty for footer.
            # This part might need refinement based on expected template structures.
            for element in body_tag.children:  # Iterate direct children
                if str(element).strip():
                    header_content_parts.append(str(element))
            return header_content_parts, footer_content_parts

        for element in main_tag.previous_siblings:
            if str(element).strip():
                header_content_parts.insert(
                    0, str(element)
                )  # Prepend to maintain order
        for element in main_tag.find_next_siblings():
            if str(element).strip():
                footer_content_parts.append(str(element))

        return header_content_parts, footer_content_parts

    def _build_html_shell(
        self, soup: BeautifulSoup, doctype_str: str
    ) -> Tuple[str, str]:
        """Builds the html_start and html_end strings.

        Args:
            soup: The BeautifulSoup object of the parsed base HTML.
            doctype_str: The DOCTYPE string.

        Returns:
            A tuple (final_html_start, final_html_end).
        """
        html_tag_obj = soup.find("html")
        html_start_str: str
        html_end_str: str

        if html_tag_obj and isinstance(html_tag_obj, Tag):
            full_html_minus_doctype = str(html_tag_obj)
            html_attrs_str = self._get_attributes_string(html_tag_obj)

            head_tag = soup.head
            head_content = str(head_tag) if head_tag else "<head></head>"

            # Attempt to find existing <body> tag to split accurately
            body_open_match = re.search(
                r"<body[^>]*>", full_html_minus_doctype, re.IGNORECASE
            )
            if body_open_match:
                # html_start includes <html>, <head>, and opening <body> tag
                html_start_str = (
                    f"<html {html_attrs_str}>{head_content}{body_open_match.group(0)}"
                )
            else:
                # Fallback: if no <body> tag, construct a basic start
                logger.warning(
                    "No <body> tag found within <html>; constructing a basic one."
                )
                html_start_str = f"<html {html_attrs_str}>{head_content}<body>"

            body_close_match = re.search(
                r"</body>\s*</html>\s*$",
                full_html_minus_doctype,
                re.IGNORECASE | re.DOTALL,
            )
            html_end_str = (
                body_close_match.group(0) if body_close_match else "</body></html>"
            )
        else:
            logger.warning("<html> tag not found. Using default HTML structure.")
            doctype_str = doctype_str or "<!DOCTYPE html>\n"
            html_start_str = (
                '<html><head><meta charset="UTF-8">'
                '<meta name="viewport" content="width=device-width, '
                'initial-scale=1.0"><title>Page</title></head><body>'
            )
            html_end_str = "\n</body>\n</html>"

        final_html_start = doctype_str + html_start_str.strip() + "\n"
        return final_html_start, html_end_str.strip()

    def extract_base_html_parts(
        self, base_html_path: str = "index.html"
    ) -> Tuple[str, str, str, str]:
        """Extracts key structural parts from the base HTML file.

        Returns a tuple: (html_start, header_content, footer_content, html_end).
        - `html_start`: From <!DOCTYPE> up to and including the opening <body> tag.
        - `header_content`: Content found between the <body> tag and the <main> tag.
        - `footer_content`: Content found between the </main> tag and the </body> tag.
        - `html_end`: Typically '</body></html>'.

        Args:
            base_html_path: Path to the base HTML template file.

        Returns:
            A tuple of four strings: (html_start, header_content, footer_content, html_end).

        Raises:
            PageAssemblyError: If the base_html_path file is not found.
        """
        try:
            with open(base_html_path, "r", encoding="utf-8") as f:
                base_content = f.read()
        except FileNotFoundError as e:
            raise PageAssemblyError(
                f"Base HTML file '{base_html_path}' not found."
            ) from e

        soup = BeautifulSoup(base_content, "html.parser")
        doctype_str = self._extract_doctype(base_content)
        final_html_start, final_html_end = self._build_html_shell(soup, doctype_str)
        header_parts, footer_parts = self._extract_header_footer_from_body(soup.body)

        return (
            final_html_start,
            "\n".join(header_parts),
            "\n".join(footer_parts),
            final_html_end,
        )

    def _update_html_lang_attribute(self, html_start_str: str, lang: str) -> str:
        """Updates or adds the lang attribute to the <html> tag."""
        html_tag_pattern = re.compile(r"(<html[^>]*>)", re.IGNORECASE)
        match = html_tag_pattern.search(html_start_str)

        if not match:
            logger.warning(
                "No <html> tag found in html_start_str. Cannot set lang attribute."
            )
            # Fallback: if html_start_str is just doctype, append html tag
            if html_start_str.lower().strip().startswith("<!doctype"):
                return f'{html_start_str.strip()}\n<html lang="{lang}">'
            return f'<html lang="{lang}">{html_start_str}'

        original_html_tag = match.group(1)
        new_html_tag: str

        if re.search(r"lang\s*=", original_html_tag, re.IGNORECASE):
            new_html_tag = re.sub(
                r'(lang\s*=\s*["\'])([^"\']*)(["\'])',
                rf"\1{lang}\3",
                original_html_tag,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            # Add lang attribute. Insert it after '<html'
            new_html_tag = re.sub(
                r"(<html)",
                rf'\1 lang="{lang}"',
                original_html_tag,
                count=1,
                flags=re.IGNORECASE,
            )
        return html_start_str.replace(original_html_tag, new_html_tag, 1)

    def assemble_translated_page(
        self,
        lang: str,
        translations: Translations,
        html_parts: Tuple[str, str, str, str],
        main_content: str,
        header_content: Optional[str] = None,
        footer_content: Optional[str] = None,
    ) -> str:
        """Assembles a full HTML page with translated content.

        Args:
            lang: The language code (e.g., "en").
            translations: A dictionary of translations for the language.
            html_parts: A tuple (html_start, header_original, footer_original, html_end)
                        from `extract_base_html_parts`.
            main_content: The HTML string for the main content of the page.
            header_content: Optional pre-translated header HTML. If None,
                            the original header from html_parts is used.
            footer_content: Optional pre-translated footer HTML. If None,
                            the original footer from html_parts is used.
        Returns:
            The complete HTML string for the translated page.
        """
        html_start_original, header_original, footer_original, html_end_original = (
            html_parts
        )

        # Use provided header/footer if available, otherwise use originals from template
        current_header_str = (
            header_content if header_content is not None else header_original
        )
        current_footer_str = (
            footer_content if footer_content is not None else footer_original
        )

        # Translate the header and footer content (even if they were pre-translated,
        # this ensures any remaining i18n tags are processed).
        final_header_content = self.translation_provider.translate_html_content(
            current_header_str, translations
        )
        final_footer_content = self.translation_provider.translate_html_content(
            current_footer_str, translations
        )

        # Set the lang attribute on the <html> tag.
        final_html_start = self._update_html_lang_attribute(html_start_original, lang)

        # Assemble the full page.
        # Ensure <main> tags correctly wrap the main_content.
        page_components = [
            final_html_start,
            final_header_content,
            "\n<main>\n",  # Ensure main tag is present
            main_content,
            "\n</main>\n",  # Ensure main tag is closed
            final_footer_content,
            html_end_original,
        ]
        return "".join(
            filter(None, page_components)
        )  # Filter out None or empty strings
