"""
Provides the `DefaultPageBuilder` for assembling final HTML pages.

This module includes functionality to extract structural parts from a base
HTML template, and then assemble these parts with translated content,
main content, and language-specific attributes to form a complete HTML page.
"""

import logging
from typing import Optional, Tuple

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
        html_parts: Tuple[str, str, str, str], # This argument is now less relevant
        main_content: str,
        header_content: Optional[str] = None, # Can be passed to Jinja context
        footer_content: Optional[str] = None, # Can be passed to Jinja context
        page_title: Optional[str] = None, # Example of an additional context variable
    ) -> str:
        """Assembles a full HTML page using a Jinja2 base template.

        Args:
            lang: The language code (e.g., "en").
            translations: A dictionary of translations for the language.
            html_parts: A tuple from `extract_base_html_parts`.
                        NOTE: Largely ignored due to Jinja2 templating.
            main_content: The HTML string for the main content of the page
                          (already rendered blocks).
            header_content: Optional HTML content for the header block in base.html.
            footer_content: Optional HTML content for the footer block in base.html.
            page_title: Optional title for the page.

        Returns:
            The complete HTML string for the translated page.
        """
        base_template = self.jinja_env.get_template("base.html")

        # Prepare context for the Jinja template
        # The `base.html` template expects `lang`, `main_content`, etc.
        # `translations` can also be passed if needed directly by the base template,
        # though individual blocks should already be translated.
        # `header_content` and `footer_content` can be passed to fill respective blocks
        # in `base.html` if they are not hardcoded or built differently.
        context = {
            "lang": lang,
            "title": page_title or translations.get("default_page_title", "Landing Page"),
            "translations": translations, # Make translations available to base template
            "main_content": main_content, # This is the aggregated HTML of all blocks
            "header_content": header_content, # For {% block header_content %}
            "footer_content": footer_content, # For {% block footer_content %}
            # Add any other variables your base.html might need
        }

        # The translation_provider might still be useful if base.html itself has i18n tags
        # that were not part of the pre-rendered header/footer content.
        # However, if header/footer content are passed as pre-rendered strings,
        # they should already be translated. The main_content is also pre-rendered.
        # For now, we assume base.html primarily structures these parts.
        # If base.html has its own `data-i18n` tags, they'd be handled by client-side JS.
        # Server-side translation of base.html structure can be done by passing translations
        # to its render context (as done above).

        return base_template.render(context)
