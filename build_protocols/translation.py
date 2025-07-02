import json
from typing import Dict, List, Union

from bs4 import BeautifulSoup
from bs4.element import Tag

# Type aliases
Translations = Dict[str, str]


def get_attribute_value_as_str(element: Tag, attr_name: str) -> str:
    """Safely retrieves an attribute value as a string.
    BeautifulSoup can return a list if an attribute is multi-valued,
    but for 'data-i18n', we expect a single string.
    """
    attr_val: Union[str, List[str], None] = element.get(attr_name)
    if isinstance(attr_val, list):
        return str(attr_val[0]) if attr_val else ""
    elif attr_val is not None:
        return str(attr_val)
    return ""


def load_translations(lang: str) -> Translations:
    """Loads translation strings for a given language."""
    try:
        with open(f"public/locales/{lang}.json", "r", encoding="utf-8") as f:
            translations: Translations = json.load(f)
            return translations
    except FileNotFoundError:
        print(f"Warning: Translation file for '{lang}' not found. Using default text.")
        return {}
    except json.JSONDecodeError:
        print(
            f"Warning: Could not decode JSON from locales/{lang}.json. "
            "Using default text."
        )
        return {}


def translate_html_content(html_content: str, translations: Translations) -> str:
    """Translates data-i18n tagged elements in HTML content."""
    if not translations:
        return html_content

    soup = BeautifulSoup(html_content, "html.parser")
    for element in soup.find_all(attrs={"data-i18n": True}):
        if isinstance(element, Tag):  # Ensure element is a Tag
            key: str = get_attribute_value_as_str(element, "data-i18n")
            if key and key in translations:  # ensure key is not empty
                element.string = translations[key]
            # Avoid replacing placeholders like {{...}} if key is not found
            elif (
                key
                and "{{" not in element.decode_contents(formatter="html")
                and "}}" not in element.decode_contents(formatter="html")
            ):
                print(
                    f"Warning: Translation key '{key}' not found in translations for "
                    f"current language. Element: <{element.name} "
                    f"data-i18n='{key}'>...</{element.name}>"
                )
    return str(soup)
