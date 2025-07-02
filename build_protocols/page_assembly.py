"""
Provides the `DefaultPageBuilder` for assembling final HTML pages.

This module includes functionality to extract structural parts from a base
HTML template, and then assemble these parts with translated content,
main content, and language-specific attributes to form a complete HTML page.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from jinja2 import Environment

from .interfaces import PageBuilder, TranslationProvider, Translations

logger = logging.getLogger(__name__)


class PageAssemblyError(Exception):
    """Custom exception for errors during page assembly."""


class DefaultPageBuilder(PageBuilder):
    """
    Default implementation for assembling HTML pages using Jinja2.

    This builder uses a Jinja2 environment to render a base template,
    injecting main content, translations, and other necessary data.
    """

    def __init__(
        self, translation_provider: TranslationProvider, jinja_env: Environment
    ):
        """Initializes the DefaultPageBuilder.

        Args:
            translation_provider: An instance of a TranslationProvider
                                  to handle content translation (can be used by templates).
            jinja_env: An initialized Jinja2 Environment.
        """
        self.translation_provider = translation_provider
        self.jinja_env = jinja_env

    def extract_base_html_parts(
        self, base_html_path: str = "index.html"
    ) -> Tuple[str, str, str, str]:
        """
        Extracts key structural parts from the base HTML file.
        NOTE: This method is now largely obsolete with Jinja2 managing the base structure.
        It's kept to satisfy the protocol but should ideally be removed or re-evaluated
        if the PageBuilder protocol changes. For now, it returns dummy values
        as the main assembly logic is in `assemble_translated_page` using Jinja.
        """
        logger.warning(
            "extract_base_html_parts is called but is largely obsolete "
            "with Jinja2 templating. Returning dummy values."
        )
        # These parts are no longer extracted this way.
        # The base.html Jinja template defines these sections.
        # Returning placeholder values to satisfy the interface.
        # The actual header/footer content for the template will be passed
        # directly to assemble_translated_page or handled within base.html itself.
        return ("", "", "", "")

    def assemble_translated_page(
        self,
        lang: str,
        translations: Translations,
        html_parts: Tuple[str, str, str, str],  # This argument is now less relevant
        main_content: str,
        navigation_items: Optional[
            List[Dict[str, Any]]
        ] = None,  # Processed navigation items
        page_title: Optional[str] = None,
    ) -> str:
        """Assembles a full HTML page using a Jinja2 base template.

        Args:
            lang: The language code (e.g., "en").
            translations: A dictionary of translations for the language.
            html_parts: A tuple from `extract_base_html_parts`.
                        NOTE: Largely ignored due to Jinja2 templating.
            main_content: The HTML string for the main content of the page
                          (already rendered blocks).
            navigation_items: Optional list of navigation item dictionaries for the header.
            page_title: Optional title for the page.


        Returns:
            The complete HTML string for the translated page.
        """
        base_template = self.jinja_env.get_template("base.html")

        context = {
            "lang": lang,
            "title": page_title
            or translations.get("default_page_title", "Landing Page"),
            "translations": translations,
            "main_content": main_content,
            "navigation_items": navigation_items or [],
            # Add any other variables your base.html might need
        }
        return str(base_template.render(context))
