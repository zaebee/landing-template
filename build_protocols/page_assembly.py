import re
import sys
from typing import List, Optional, Tuple  # Added Optional

from bs4 import BeautifulSoup
from bs4.element import Tag

# get_attribute_value_as_str is used internally by this module's original functions.
# If DefaultTranslationProvider.translate_html_content is used, this direct import might not be needed
# by the class methods, but we keep it for now to ensure existing logic ported to methods works.
# from build_protocols.translation import get_attribute_value_as_str # REMOVED

from .interfaces import PageBuilder, Translations, TranslationProvider # ADDED TranslationProvider


class DefaultPageBuilder(PageBuilder):
    """
    Default implementation for assembling HTML pages.
    """
    def __init__(self, translation_provider: TranslationProvider):
        self.translation_provider = translation_provider

    def extract_base_html_parts(
        self, base_html_file: str = "index.html"
    ) -> Tuple[str, str, str, str]:
        """
        Extracts key structural parts from the base HTML file.
        Returns a tuple: (html_start, header_content, footer_content, html_end).
        """
        try:
            with open(base_html_file, "r", encoding="utf-8") as f:
                base_content = f.read()
        except FileNotFoundError:
            print(f"Error: Base HTML file '{base_html_file}' not found. Exiting.")
            sys.exit(1)

        soup = BeautifulSoup(base_content, "html.parser")
        header_content_parts: List[str] = []
        footer_content_parts: List[str] = []

        body_tag = soup.body
        if body_tag and isinstance(body_tag, Tag):
            main_tag = body_tag.find("main")
            if main_tag and isinstance(main_tag, Tag):
                for element in main_tag.previous_siblings:
                    header_content_parts.append(str(element))
                for element in main_tag.find_next_siblings():
                    footer_content_parts.append(str(element))
            else:
                print(
                    f"Warning: <main> tag not found in {base_html_file}. "
                    "Header/footer content might be incomplete."
                )
        else:
            print(
                f"Warning: <body> tag not found in {base_html_file}. "
                "Header/footer content might be empty."
            )

        html_tag = soup.find("html")
        html_start: str
        if html_tag and isinstance(html_tag, Tag):
            html_str = str(html_tag)
            body_open_tag_index = html_str.lower().find("<body")
            if body_open_tag_index != -1:
                body_tag_end_index = html_str.find(">", body_open_tag_index) + 1
                html_start = html_str[:body_tag_end_index] + "\n"
            else: # No <body> tag found within <html>, try to get <head> or default
                html_start = str(soup.find("head")) if soup.head else ""
                if not html_start.strip().endswith("</head>"): # Ensure head is complete
                    html_start += "</head>" if html_start else "<head></head>"
                html_start = f"<html>{html_start}<body>\n" # Add html and body start
        else:
            print(
                f"Warning: <html> tag not found in {base_html_file}. "
                "Using default HTML structure."
            )
            html_start = (
                '<!DOCTYPE html>\n<html><head><meta charset="UTF-8">'
                '<meta name="viewport" content="width=device-width, '
                'initial-scale=1.0"><title>Page</title></head><body>\n'
            )

        # Ensure html_start always begins with <!DOCTYPE html> if not present
        if not html_start.lower().strip().startswith("<!doctype html>"):
            # Check if <!DOCTYPE html> is already there from soup string
            # A bit naive, but better than nothing if soup didn't include it.
            if "<!doctype html>" not in base_content.lower() :
                 html_start = "<!DOCTYPE html>\n" + html_start


        html_end: str = "\n</body>\n</html>"

        return (
            html_start,
            "".join(header_content_parts),
            "".join(footer_content_parts),
            html_end,
        )

    def assemble_translated_page(
        self,
        lang: str,
        translations: Translations,
        html_parts: Tuple[str, str, str, str],
        main_content: str, # This is the fully assembled and translated main block content
        header_content: Optional[str] = None, # Optional override for header
        footer_content: Optional[str] = None, # Optional override for footer
    ) -> str:
        """
        Assembles the full HTML page for a given language.
        Header and footer content (from html_parts or overrides) are translated here.
        """
        # pylint: disable=too-many-locals
        html_start_original, header_original, footer_original, html_end_original = html_parts

        # Use overrides if provided, otherwise use extracted parts
        current_header_str = header_content if header_content is not None else header_original
        current_footer_str = footer_content if footer_content is not None else footer_original

        # Translate header and footer using the translation_provider
        # The main_content is assumed to be already translated before being passed to this function.
        # The translations object is passed to translate_html_content for context.
        final_header_content = self.translation_provider.translate_html_content(
            current_header_str, translations
        )
        final_footer_content = self.translation_provider.translate_html_content(
            current_footer_str, translations
        )

        # Set lang attribute on <html> tag in html_start_original
        final_html_start = html_start_original
        # More robust lang attribute setting
        temp_soup_start = BeautifulSoup(final_html_start, "html.parser")
        html_tag_node = temp_soup_start.find("html", recursive=False) # Find top-level html
        if html_tag_node and isinstance(html_tag_node, Tag):
            html_tag_node["lang"] = lang
            final_html_start = str(temp_soup_start)
        elif "<html" in final_html_start.lower(): # Fallback for regex if parsing is tricky
             final_html_start = re.sub(
                r"<html(\s*[^>]*)>",
                f'<html lang="{lang}"\\1>',
                final_html_start,
                count=1,
                flags=re.IGNORECASE,
            )
        else: # If no html tag, prepend a basic one
            final_html_start = f'<!DOCTYPE html>\n<html lang="{lang}">\n' + final_html_start


        page_parts = [
            final_html_start,
            final_header_content,
            "<main>\n", # Add main tags around the already processed main_content
            main_content,
            "\n</main>",
            final_footer_content,
            html_end_original,
        ]
        return "".join(page_parts)

# Aliases for backward compatibility if tests rely on old function names
# _page_builder_instance = DefaultPageBuilder()
# extract_base_html_parts = _page_builder_instance.extract_base_html_parts
# assemble_translated_page = _page_builder_instance.assemble_translated_page
