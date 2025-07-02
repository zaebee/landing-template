"""
Provides the `DefaultPageBuilder` for assembling final HTML pages.

This module includes functionality to extract structural parts from a base
HTML template, and then assemble these parts with translated content,
main content, and language-specific attributes to form a complete HTML page.

Refactored to use BeautifulSoup more consistently for HTML parsing and
manipulation, reducing reliance on regex and string splitting.
"""

import logging
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup, Doctype
from bs4.element import NavigableString, Tag

from .interfaces import PageBuilder, TranslationProvider, Translations

logger = logging.getLogger(__name__)


class PageAssemblyError(Exception):
    """Custom exception for errors during page assembly."""


class DefaultPageBuilder(PageBuilder):
    """
    Default implementation for assembling HTML pages.

    This builder leverages BeautifulSoup to extract parts from a base HTML
    file (like header, footer) and then combine them with generated main
    content and translations to produce the final HTML output for different
    languages.
    """

    def __init__(self, translation_provider: TranslationProvider):
        """Initializes the DefaultPageBuilder.

        Args:
            translation_provider: An instance of a TranslationProvider
                                  to handle content translation.
        """
        self.translation_provider = translation_provider

    def _extract_doctype_str(self, soup: BeautifulSoup) -> str:
        """Extracts the DOCTYPE string from a BeautifulSoup object.

        Args:
            soup: The BeautifulSoup object of the parsed base HTML.

        Returns:
            The DOCTYPE string (e.g., "<!DOCTYPE html>\n") or an empty string.
        """
        doctype_item = None
        for item in soup.contents:
            if isinstance(item, Doctype):
                doctype_item = item
                break
        return ("<!DOCTYPE " + doctype_item + ">\n") if doctype_item else ""

    def _extract_header_footer_from_body(
        self, soup_body: Optional[Tag]
    ) -> Tuple[str, str]:
        """Extracts header and footer content parts relative to the <main> tag
           using BeautifulSoup.

        Args:
            soup_body: The BeautifulSoup Tag object for the <body> element.

        Returns:
            A tuple containing two strings: (header_html, footer_html).
        """
        header_elements: List[str] = []
        footer_elements: List[str] = []

        if not soup_body:
            logger.warning(
                "<body> tag not found by BeautifulSoup. Header/footer content will be empty."
            )
            return "", ""

        main_tag = soup_body.find("main")

        if not main_tag:
            logger.warning(
                "<main> tag not found within <body>. "
                "Considering all direct children of <body> as header content."
            )
            for child in soup_body.children:
                if isinstance(child, NavigableString) and not child.strip():
                    continue  # Skip empty strings
                header_elements.append(str(child))
            return "\n".join(header_elements), ""

        # Content before <main> is header content
        for sibling in main_tag.previous_siblings:
            if isinstance(sibling, NavigableString) and not sibling.strip():
                continue
            header_elements.insert(0, str(sibling))  # Prepend to maintain order

        # Content after <main> is footer content
        for sibling in main_tag.next_siblings:
            if isinstance(sibling, NavigableString) and not sibling.strip():
                continue
            footer_elements.append(str(sibling))

        return "\n".join(header_elements), "\n".join(footer_elements)

    def _build_html_shell_parts(
        self, soup: BeautifulSoup, doctype_str: str, lang: Optional[str] = None
    ) -> Tuple[str, str]:
        """Builds the html_start and html_end strings using BeautifulSoup.

        Args:
            soup: The BeautifulSoup object of the parsed base HTML.
            doctype_str: The DOCTYPE string.
            lang: Optional language code to set on the <html> tag.

        Returns:
            A tuple (html_start_str, html_end_str).
        """
        html_tag = soup.find("html")
        if not html_tag or not isinstance(html_tag, Tag):
            logger.warning("<html> tag not found. Using default HTML structure.")
            default_head = (
                '<head><meta charset="UTF-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
                "<title>Page</title></head>"
            )
            default_doctype_with_newline = "<!DOCTYPE html>\n"
            html_start = f'{doctype_str or default_doctype_with_newline}<html lang="{lang or "en"}">{default_head}<body>\n'
            html_end = "\n</body>\n</html>"
            return html_start, html_end

        if lang:
            html_tag["lang"] = lang

        head_tag = html_tag.find("head")
        head_content = (
            str(head_tag) if head_tag else "<head></head>"
        )  # Ensure head exists

        # Create a temporary soup to get the opening <html> tag with attributes and head
        temp_soup = BeautifulSoup("", "html.parser")

        # Ensure all attribute values in html_tag.attrs are strings for new_tag
        processed_attrs = {
            k: " ".join(v) if isinstance(v, list) else str(v)
            for k, v in html_tag.attrs.items()
        }
        new_html_tag = temp_soup.new_tag(html_tag.name, attrs=processed_attrs)

        # The html_start includes doctype, html tag (with attrs), head content, and opening body tag
        # To get the opening body tag, we can serialize up to it or reconstruct
        body_tag = html_tag.find("body")
        body_attrs_str = ""
        if body_tag and isinstance(body_tag, Tag):
            body_attrs_list = []
            for k, v_list in body_tag.attrs.items():
                # Ensure v_list is treated as a list for classes, etc.
                v = " ".join(v_list) if isinstance(v_list, list) else v_list
                body_attrs_list.append(f'{k}="{v}"')
            if body_attrs_list:
                body_attrs_str = " " + " ".join(body_attrs_list)

        opening_body_tag = f"<body{body_attrs_str}>"

        # Construct html_start string
        # html_tag.prettify() would include everything. We need to split.
        # One way: render html_tag without body children, then append opening body.

        # Detach body children for a moment to print html_tag start and head
        original_body_children = []
        if isinstance(body_tag, Tag): # Ensure body_tag is a Tag before accessing .children
            original_body_children = [child.extract() for child in body_tag.children]

        # Now html_tag string without its body's children but with body tag itself
        # This is tricky. Let's reconstruct more manually for clarity.
        html_start_str = (
            doctype_str
            + str(new_html_tag).replace("</html>", "")
            + head_content
            + opening_body_tag
            + "\n"
        )

        # Put children back if they were taken (though not strictly necessary for this func's output)
        if isinstance(body_tag, Tag) and original_body_children: # Ensure body_tag is a Tag for .append
            for child in original_body_children:
                body_tag.append(child)

        html_end_str = "\n</body>\n</html>"  # Standard closing

        return html_start_str, html_end_str

    def extract_base_html_parts(
        self, base_html_path: str = "index.html"
    ) -> Tuple[str, str, str, str]:
        """Extracts key structural parts from the base HTML file using BeautifulSoup.

        Returns a tuple: (html_start, header_content, footer_content, html_end).
        - `html_start`: From <!DOCTYPE> up to and including the opening <body> tag.
                        The lang attribute is NOT set here, but in assemble_translated_page.
        - `header_content`: Content found between the <body> tag and the <main> tag.
        - `footer_content`: Content found between the </main> tag and the </body> tag.
        - `html_end`: Typically '</body></html>'.

        Args:
            base_html_path: Path to the base HTML template file.

        Returns:
            A tuple of four strings: (html_start, header_content, footer_content, html_end).

        Raises:
            PageAssemblyError: If the base_html_path file is not found or parsing fails.
        """
        try:
            with open(base_html_path, "r", encoding="utf-8") as f:
                base_content = f.read()
        except FileNotFoundError as e:
            raise PageAssemblyError(
                f"Base HTML file '{base_html_path}' not found."
            ) from e

        try:
            soup = BeautifulSoup(base_content, "html.parser")
        except Exception as e:  # Catch potential BeautifulSoup parsing errors
            raise PageAssemblyError(
                f"Error parsing base HTML file '{base_html_path}': {e}"
            ) from e

        doctype_str = self._extract_doctype_str(soup)

        # Build shell without lang initially. Lang will be set during page assembly.
        # This keeps extract_base_html_parts language-agnostic.
        html_start_template, html_end_str = self._build_html_shell_parts(
            soup, doctype_str
        )

        header_content_str, footer_content_str = self._extract_header_footer_from_body(
            soup.body
        )

        return (
            html_start_template,
            header_content_str,
            footer_content_str,
            html_end_str,
        )

    def _set_html_lang_attribute(self, soup_html_tag: Tag, lang: str) -> None:
        """Sets the lang attribute on the given <html> Tag object."""
        if soup_html_tag:
            soup_html_tag["lang"] = lang
        else:
            logger.warning(
                "Cannot set lang attribute: <html> tag not found in parsed soup."
            )

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
        # Corrected method call: _update_html_lang_attribute -> _set_html_lang_attribute (which works on soup)
        # This part needs rethinking as _set_html_lang_attribute works on a soup object,
        # and html_start_original is a string.
        # We need to parse html_start_original, set lang, then stringify.

        temp_soup = BeautifulSoup(html_start_original, "html.parser")
        html_tag_in_start = temp_soup.find("html")
        if isinstance(html_tag_in_start, Tag): # Ensure it's a Tag before passing
            self._set_html_lang_attribute(html_tag_in_start, lang)
            # Reconstruct the html_start string from temp_soup
            # This will include doctype if it was part of html_start_original
            # and the modified html tag

            # Need to handle doctype carefully. self._extract_doctype_str(temp_soup)
            # plus the string of temp_soup.html
            doctype_from_start_original = self._extract_doctype_str(temp_soup)
            final_html_start = doctype_from_start_original + str(temp_soup.html) if temp_soup.html else html_start_original

        else:
            logger.warning(f"Could not find <html> tag in html_start_original to set lang='{lang}'. Using original.")
            final_html_start = html_start_original


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
