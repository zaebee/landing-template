import re
import sys
from typing import List, Tuple, Dict

from bs4 import BeautifulSoup
from bs4.element import Tag

# Assuming Translations type is defined (e.g. in a shared types module or passed directly)
# Assuming get_attribute_value_as_str is available, possibly from translation.py
# For now, let's duplicate it or import if circular dependency is not an issue.
# To avoid issues, let's assume it's passed or defined if needed, or we import it.
# For this refactor, let's try importing from translation
from build_protocols.translation import get_attribute_value_as_str, Translations


def extract_base_html_parts(
    base_html_file: str = "index.html",
) -> Tuple[str, str, str, str]:
    """
    Extracts key structural parts from the base HTML file.

    Returns:
        A tuple containing:
        - html_start: The HTML content up to and including the opening <body> tag.
        - header_content: The content of the <header> or elements before <main>.
        - footer_content: The content of the <footer> or elements after <main>.
        - html_end: The closing </body> and </html> tags.
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
        else:
            html_start = str(soup.find("head")) if soup.head else ""
            if not html_start:
                html_start = (
                    '<!DOCTYPE html>\n<html><head><meta charset="UTF-8">'
                    '<meta name="viewport" content="width=device-width, '
                    'initial-scale=1.0"><title>Page</title></head><body>\n'
                )
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

    html_end: str = "\n</body>\n</html>"

    return (
        html_start,
        "".join(header_content_parts),
        "".join(footer_content_parts),
        html_end,
    )


def assemble_translated_page(  # pylint: disable=too-many-locals
    lang: str,
    translations: Translations, # Explicitly type Translations
    html_parts: Tuple[str, str, str, str],
    assembled_main_content: str,
) -> str:
    """
    Assembles the full HTML page for a given language.
    """
    html_start, header_content, footer_content, html_end = html_parts

    translated_header_soup = BeautifulSoup(header_content, "html.parser")
    for element in translated_header_soup.find_all(attrs={"data-i18n": True}):
        if isinstance(element, Tag):
            key = get_attribute_value_as_str(element, "data-i18n")
            if key and key in translations:
                element.string = translations[key]

    translated_footer_soup = BeautifulSoup(footer_content, "html.parser")
    for element in translated_footer_soup.find_all(attrs={"data-i18n": True}):
        if isinstance(element, Tag):
            key = get_attribute_value_as_str(element, "data-i18n")
            if key and key in translations:
                element.string = translations[key]

    current_html_start = html_start
    temp_soup = BeautifulSoup(current_html_start, "html.parser")
    html_tag_from_temp = temp_soup.find("html")

    if html_tag_from_temp and isinstance(html_tag_from_temp, Tag):
        html_tag_from_temp["lang"] = lang
        reconstructed_start_parts = str(temp_soup).split("<body>", 1)
        if len(reconstructed_start_parts) > 1:
            current_html_start = reconstructed_start_parts[0] + "<body>\n"
        else:
            current_html_start = str(temp_soup)
    else:
        if "<html" in current_html_start.lower():
            current_html_start = re.sub(
                r"<html(\s*[^>]*)>",
                f'<html lang="{lang}"\\1>',
                current_html_start,
                count=1,
                flags=re.IGNORECASE,
            )
        else:
            current_html_start = (
                f'<!DOCTYPE html>\n<html lang="{lang}">\n' + current_html_start
            )

    page_parts = [
        current_html_start,
        str(translated_header_soup),
        "<main>\n",
        assembled_main_content,
        "\n</main>",
        str(translated_footer_soup),
        html_end,
    ]
    return "".join(page_parts)
