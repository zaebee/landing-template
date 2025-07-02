"""
Defines the protocols (interfaces) for various components of the static site
generation system.

These protocols ensure that different implementations of services like translation,
data loading, HTML generation, configuration management, page building, and
caching can be used interchangeably as long as they adhere to these defined
contracts.
"""

from typing import Any, Dict, List, Optional, Protocol, Tuple, Type, TypeVar, Union

from google.protobuf.message import Message

# Import specific generated types used in protocols for clarity.
from generated.nav_item_pb2 import Navigation as NavigationProto

# --- Type Aliases and TypeVariables ---

Translations = Dict[str, str]
"""
A type alias for translation dictionaries, mapping translation keys (str)
to their translated string values (str).
"""

T = TypeVar("T", bound=Message)
"""
A generic TypeVar constrained to protobuf Message types, used by DataLoader
and DataCache to specify the type of message they handle.
"""


# --- Protocol Definitions ---


class TranslationProvider(Protocol):
    """
    Defines the interface for services that provide translation capabilities.
    """

    def load_translations(self, lang: str) -> Translations:
        """Loads translation strings for a given language.

        Args:
            lang: The language code (e.g., "en", "es") for which to load
                  translations.

        Returns:
            A Translations dictionary containing key-value pairs of
            translation strings.
        """
        ...

    def translate_html_content(
        self, html_content: str, translations: Translations
    ) -> str:
        """Translates placeholder tags within an HTML content string.

        Args:
            html_content: The HTML content string possibly containing
                          translation tags (e.g., {{i18n_key}}).
            translations: The Translations dictionary for the current language.

        Returns:
            The HTML content string with translation tags replaced by their
            corresponding translated values.
        """
        ...


class DataLoader(Protocol[T]):
    """
    Defines the interface for services that load data and parse it into
    protobuf messages of a generic type T.
    """

    def load_dynamic_list_data(
        self, data_file_path: str, message_type: Type[T]
    ) -> List[T]:
        """Loads a list of data items from a specified source.

        Args:
            data_file_path: The path or identifier for the data source
                            containing a list of items.
            message_type: The protobuf message class to parse each item into.

        Returns:
            A list of protobuf messages of type T.
        """
        ...

    def load_dynamic_single_item_data(
        self, data_file_path: str, message_type: Type[T]
    ) -> Optional[T]:
        """Loads a single data item from a specified source.

        Args:
            data_file_path: The path or identifier for the data source
                            containing a single item.
            message_type: The protobuf message class to parse the item into.

        Returns:
            An optional protobuf message of type T, or None if the item
            cannot be loaded.
        """
        ...


class HtmlBlockGenerator(Protocol):
    """
    Defines the interface for services that generate HTML for a specific
    block or component of a page.
    """

    def generate_html(self, data: Any, translations: Translations) -> str:
        """Generates an HTML string for a content block.

        Args:
            data: The data required to generate the HTML block. The specific
                  type of this data will depend on the concrete implementation
                  (e.g., a specific protobuf message or a list of messages).
                  For the protocol, `Any` allows flexibility.
            translations: The Translations dictionary for the current language,
                          to be used for localizing text within the block.

        Returns:
            An HTML string representing the content block.
        """
        ...


class AppConfigManager(Protocol):
    """
    Defines the interface for services that manage application configuration.
    """

    def load_app_config(
        self, config_path: str = "public/config.json"
    ) -> Dict[str, Any]:
        """Loads the main application configuration.

        Args:
            config_path: The path to the main configuration file.
                         Defaults to "public/config.json".

        Returns:
            A dictionary containing the application configuration.
        """
        ...

    def generate_language_config(
        self,
        base_config: Dict[str, Any],
        nav_data: Optional[NavigationProto],
        translations: Translations,
        lang: str,
    ) -> Dict[str, Any]:
        """Generates a language-specific configuration.

        Args:
            base_config: The base application configuration dictionary.
            nav_data: An optional Navigation protobuf message containing
                      navigation items. `NavigationProto` is the concrete
                      generated type.
            translations: The Translations dictionary for the target language.
            lang: The language code (e.g., "en", "es") for which to generate
                  the configuration.

        Returns:
            A new dictionary representing the language-specific configuration.
        """
        ...


class PageBuilder(Protocol):
    """
    Defines the interface for services that assemble a full HTML page
    from its constituent parts.
    """

    def extract_base_html_parts(
        self, base_html_path: str = "index.html"
    ) -> Tuple[str, str, str, str]:
        """Extracts structural parts from a base HTML template file.

        Typically, this involves splitting the base HTML into segments like
        (html_start, header, footer, html_end).

        Args:
            base_html_path: Path to the base HTML template file.
                            Defaults to "index.html".

        Returns:
            A tuple of strings representing the distinct parts of the HTML
            template (e.g., start, header, footer, end).
        """
        ...

    def assemble_translated_page(
        self,
        lang: str,
        translations: Translations,
        html_parts: Tuple[str, str, str, str],
        main_content: str,
        navigation_items: Optional[List[Dict[str, Any]]] = None,
        page_title: Optional[str] = None,
    ) -> str:
        """Assembles a full HTML page using translated and generated content.

        Args:
            lang: The language code for the page.
            translations: The Translations dictionary for the current language.
            html_parts: A tuple of base HTML structural parts (e.g., from
                        `extract_base_html_parts`).
            main_content: The main content area of the page, already processed
                          and translated.
            navigation_items: Optional list of navigation item dictionaries for the header.

        Returns:
            A string containing the complete HTML for the assembled page.
        """
        ...


class DataCache(Protocol[T]):
    """
    Defines the interface for services that provide caching for data items,
    typically protobuf messages of generic type T.
    """

    def get_item(self, key: str) -> Optional[Union[List[T], T]]:
        """Retrieves an item or a list of items from the cache.

        Args:
            key: The unique key identifying the cached item.

        Returns:
            The cached item (List[T] or T) if found, otherwise None.
        """
        ...

    def set_item(self, key: str, value: Union[List[T], T, None]) -> None:
        """Sets or updates an item in the cache.

        If `value` is None, implementations might choose to remove the key
        or store None explicitly.

        Args:
            key: The unique key for the item.
            value: The item (List[T], T, or None) to cache.
        """
        ...

    def preload_data(
        self, loaders_config: Dict[str, Dict[str, Any]], data_loader: DataLoader[T]
    ) -> None:
        """Pre-loads data into the cache based on a configuration.

        Args:
            loaders_config: A dictionary where keys might be block names or
                            other identifiers, and values are dictionaries
                            containing parameters for the `data_loader`
                            (e.g., 'data_file_path', 'message_type').
            data_loader: A DataLoader instance to use for loading the data
                         that will be cached.
        """
        ...


# Notes on design choices:
# - `HtmlBlockGenerator.generate_html` uses `data: Any` for maximum flexibility
#   at the protocol level. Concrete implementations should specify the exact
#   data type they expect (e.g., `data: List[PortfolioItem]`).
# - `AppConfigManager.generate_language_config` uses the concrete
#   `NavigationProto` type for `nav_data` as it's a specific, known type.
# - The `DataCache.set_item` allows `value` to be `None`, enabling explicit
#   caching of "not found" or clearing entries.
