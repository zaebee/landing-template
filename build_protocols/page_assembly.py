import re
import sys
from typing import List, Optional, Tuple  # Added Optional

from bs4 import BeautifulSoup
from bs4.element import Tag

# get_attribute_value_as_str is used internally by this module's original functions.
# If DefaultTranslationProvider.translate_html_content is used, this direct import might not be needed
# by the class methods, but we keep it for now to ensure existing logic ported to methods works.
# from build_protocols.translation import get_attribute_value_as_str # REMOVED
from .interfaces import (  # ADDED TranslationProvider
    PageBuilder,
    TranslationProvider,
    Translations,
)


class DefaultPageBuilder(PageBuilder):
    """
    Default implementation for assembling HTML pages.
    """
    def __init__(self, translation_provider: TranslationProvider):
        self.translation_provider = translation_provider

    def _get_attributes_string(self, tag: Tag) -> str:
        """Helper to convert tag attributes to a string."""
        attrs = ""
        if tag.attrs:
            for key, value in tag.attrs.items():
                if isinstance(value, list):
                    value = " ".join(value)
                attrs += f' {key}="{value}"'
        return attrs

    def extract_base_html_parts(
        self, base_html_file: str = "index.html"
    ) -> Tuple[str, str, str, str]:
        """
        Extracts key structural parts from the base HTML file.
        Returns a tuple: (html_start, header_content, footer_content, html_end).
        html_start includes from <!DOCTYPE> up to and including opening <body> tag.
        header_content is content between <body> and <main>.
        footer_content is content between </main> and </body> (e.g. <footer>, scripts).
        html_end is typically '</body></html>'.
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
                    if str(element).strip():
                        header_content_parts.append(str(element))
                for element in main_tag.find_next_siblings():
                    if str(element).strip():
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

        html_tag_obj = soup.find("html") # Use a different name to avoid confusion with html module
        html_start_str: str
        html_end_str: str

        doctype_str = ""
        # Preserve existing doctype by finding it in the raw content
        # Use regex for more reliable DOCTYPE extraction
        doctype_match = re.match(r"^(<!DOCTYPE[^>]+>)\s*", base_content, re.IGNORECASE | re.DOTALL)
        if doctype_match:
            doctype_str = doctype_match.group(1) + "\n"


        if html_tag_obj and isinstance(html_tag_obj, Tag):
            # Full HTML content as a string, without doctype (str(html_tag_obj) includes <html>...</html>)
            full_html_minus_doctype = str(html_tag_obj)

            # Try to extract up to the end of the opening <body> tag
            body_open_match = re.search(r"<body[^>]*>", full_html_minus_doctype, re.IGNORECASE)
            if body_open_match:
                # html_start_str is from start of <html> to end of opening <body>
                html_start_str = full_html_minus_doctype[:body_open_match.end()]
            else:
                # Fallback: if no <body> tag inside <html>, construct a basic start
                head_tag = soup.head
                # Include attributes of <html> tag
                html_attrs = self._get_attributes_string(html_tag_obj)
                head_content = str(head_tag) if head_tag else "<head></head>"
                html_start_str = f"<html{html_attrs}>{head_content}<body>"

            # Ensure html_start_str starts with <html...> if it wasn't already
            # This check is mostly for the fallback case above.
            if not html_start_str.strip().lower().startswith("<html"):
                 # This should not happen if full_html_minus_doctype was used primarily
                 html_attrs = self._get_attributes_string(html_tag_obj)
                 html_start_str = f"<html{html_attrs}>{html_start_str}"


            # For html_end, capture from </body> to </html>
            # Search from the end of the string for </body>
            body_close_match = re.search(r"</body>\s*</html>\s*$", full_html_minus_doctype, re.IGNORECASE | re.DOTALL)
            if body_close_match:
                html_end_str = body_close_match.group(0) # Capture "</body></html>"
            else:
                # Fallback if no </body></html> found (e.g. malformed or body-less html element)
                html_end_str = "</body></html>" # Default assumption

        else: # No <html> tag found, use default structure
            print(
                f"Warning: <html> tag not found in {base_html_file}. "
                "Using default HTML structure."
            )
            if not doctype_str: # Add default doctype if none was found
                doctype_str = '<!DOCTYPE html>\n'
            # Default html_start includes up to opening <body>
            html_start_str = (
                '<html><head><meta charset="UTF-8">'
                '<meta name="viewport" content="width=device-width, '
                'initial-scale=1.0"><title>Page</title></head><body>'
            )
            html_end_str = "\n</body>\n</html>"


        # Add doctype at the very beginning
        final_html_start = doctype_str + html_start_str.strip() + "\n"


        return (
            final_html_start,
            "\n".join(header_content_parts),
            "\n".join(footer_content_parts),
            html_end_str.strip(),
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
        html_start_original, header_original, footer_original, html_end_original = html_parts

        current_header_str = header_content if header_content is not None else header_original
        current_footer_str = footer_content if footer_content is not None else footer_original

        final_header_content = self.translation_provider.translate_html_content(
            current_header_str, translations
        )
        final_footer_content = self.translation_provider.translate_html_content(
            current_footer_str, translations
        )

        processed_html_start = html_start_original

        # Regex to find and update/add lang attribute in <html> tag
        # Handles existing lang attribute or adds it if missing
        # Assumes html_start_original contains the full doctype and html tag.

        # Pattern to find <html ... >
        html_tag_pattern = re.compile(r"(<html[^>]*>)", re.IGNORECASE)
        match = html_tag_pattern.search(processed_html_start)

        if match:
            html_tag_str = match.group(1)
            # Check if lang attribute exists
            if re.search(r'lang\s*=', html_tag_str, re.IGNORECASE):
                # Replace existing lang value
                new_html_tag_str = re.sub(r'(lang\s*=\s*["\'])([^"\']*)(["\'])', rf'\1{lang}\3', html_tag_str, count=1, flags=re.IGNORECASE)
            else:
                # Add lang attribute
                new_html_tag_str = re.sub(r'(<html)', rf'\1 lang="{lang}"', html_tag_str, count=1, flags=re.IGNORECASE)

            processed_html_start = processed_html_start.replace(html_tag_str, new_html_tag_str, 1)
        else:
            # This case implies html_start_original did not contain a proper <html> tag.
            # This should be rare given the changes in extract_base_html_parts.
            # Prepend a default html tag with lang if necessary.
            # However, extract_base_html_parts aims to always provide a complete html_start.
            # If doctype is present, it should be before the <html> tag.
            if processed_html_start.lower().strip().startswith("<!doctype html>"):
                 processed_html_start = re.sub(r"(<!doctype html>)", rf'\1\n<html lang="{lang}">', processed_html_start, count=1, flags=re.IGNORECASE)
                 # If body was part of this minimal start, ensure it's still there or add it
                 if "<body" not in processed_html_start.lower():
                     processed_html_start += "\n<body>" # Minimal
            elif not processed_html_start.lower().strip().startswith("<html"):
                 processed_html_start = f'<html lang="{lang}">\n' + processed_html_start


        final_html_start = processed_html_start

        page_parts = [
            final_html_start,
            final_header_content,
            "<main>\n",
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
