"""
Provides the default implementation for translation services.

This module includes the `DefaultTranslationProvider` class which handles
loading translation files (JSON format) for different languages and applying
these translations to HTML content by targeting elements with 'data-i18n'
attributes.

Module-level convenience functions are also provided for direct use, aliasing
methods from a default provider instance.
"""

import json
import logging
from typing import List, Union

from bs4 import BeautifulSoup
from bs4.element import Tag

from .interfaces import TranslationProvider, Translations

logger = logging.getLogger(__name__)


class DefaultTranslationProvider(TranslationProvider):
    """
    Default implementation for loading and applying translations.

    This provider loads translations from JSON files located in a locale-specific
    directory (e.g., `public/locales/en.json`). It then uses BeautifulSoup
    to parse HTML content and replace text in elements marked with
    `data-i18n="translation_key"` attributes.
    """

    def _get_attribute_value_as_str(self, element: Tag, attr_name: str) -> str:
        """Safely retrieves an attribute value as a string.

        BeautifulSoup's `element.get(attr_name)` can return a list if an
        attribute is multi-valued (e.g. `class="foo bar"` can be `['foo', 'bar']`).
        This helper ensures a single string is returned, prioritizing the first
        value if it's a list, which is suitable for 'data-i18n'.

        Args:
            element: The BeautifulSoup Tag element.
            attr_name: The name of the attribute to retrieve.

        Returns:
            The attribute value as a string, or an empty string if the
            attribute is not found or is empty.
        """
        attr_val: Union[str, List[str], None] = element.get(attr_name)
        if isinstance(attr_val, list):
            return str(attr_val[0]) if attr_val else ""
        if attr_val is not None:  # Handles str and other potential simple types
            return str(attr_val)
        return ""

    def load_translations(self, lang: str) -> Translations:
        """Loads translation strings for a given language from a JSON file.

        The expected file path is `public/locales/{lang}.json`.

        Args:
            lang: The language code (e.g., "en", "es").

        Returns:
            A Translations dictionary. If the file is not found or there's
            a JSON decoding error, a warning is logged and an empty dictionary
            is returned, effectively falling back to default text or keys.
        """
        # Path construction assumes execution from the project root.
        # For more robustness, consider paths relative to this file or
        # configurable base paths.
        file_path = f"public/locales/{lang}.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                translations: Translations = json.load(f)
                return translations
        except FileNotFoundError:
            logger.warning(
                "Translation file for '%s' not found at %s. Using default text.",
                lang,
                file_path,
            )
            return {}
        except json.JSONDecodeError:
            logger.warning(
                "Could not decode JSON from %s. Using default text.", file_path
            )
            return {}

    def translate_html_content(
        self, html_content: str, translations: Translations
    ) -> str:
        """Translates elements in HTML content marked with `data-i18n` attributes.

        It parses the HTML, finds all elements with a `data-i18n` attribute,
        and replaces their content with the corresponding translated string.
        If a translation key is not found, a warning is logged, and the original
        content is preserved, unless it looks like a template placeholder.

        Args:
            html_content: The HTML content string to translate.
            translations: The Translations dictionary for the current language.

        Returns:
            The translated HTML content string.
        """
        if not translations or not html_content.strip():
            return html_content

        soup = BeautifulSoup(html_content, "html.parser")
        for element in soup.find_all(attrs={"data-i18n": True}):
            if not isinstance(element, Tag):  # Should always be Tag due to find_all
                continue

            key: str = self._get_attribute_value_as_str(element, "data-i18n")
            if key and key in translations:
                element.string = translations[key]
            elif key:
                # Avoid warning for untranslated template placeholders like {{...}}
                # by checking if the element's content looks like one.
                current_content = element.decode_contents(formatter="html")
                if "{{" not in current_content and "}}" not in current_content:
                    logger.warning(
                        "Translation key '%s' not found for language. "
                        "Element: <%s data-i18n='%s'>...</%s>",
                        key,
                        element.name,
                        key,
                        element.name,
                    )
        return str(soup)


# --- Module-Level Convenience Functions ---
# These functions use a default instance of DefaultTranslationProvider for ease
# of use or for backward compatibility with code that expects module-level functions.
# Ideally, new code should instantiate and use DefaultTranslationProvider directly.

# _default_provider is a module-level instance used by the convenience functions
# below. It is intended to be stateless for these operations.
_default_provider = DefaultTranslationProvider()

load_translations = _default_provider.load_translations
"""
Module-level function to load translations. See `DefaultTranslationProvider.load_translations`.
"""

translate_html_content = _default_provider.translate_html_content
"""
Module-level function to translate HTML content. See `DefaultTranslationProvider.translate_html_content`.
"""
