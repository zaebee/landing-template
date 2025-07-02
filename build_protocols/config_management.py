"""
Manages the loading and generation of application configurations.

This module provides the `DefaultAppConfigManager` class, which implements
the `AppConfigManager` protocol for handling main application configurations
and generating language-specific configurations by integrating navigation data
and translations.
"""

import json
from typing import Any, Dict, List, Optional

from generated.nav_item_pb2 import Navigation

from .interfaces import AppConfigManager, Translations


class ConfigLoadError(Exception):
    """Custom exception for errors during configuration loading."""


class DefaultAppConfigManager(AppConfigManager):
    """
    Default implementation for managing application and language-specific
    configurations.
    """

    def load_app_config(
        self, config_path: str = "public/config.json"
    ) -> Dict[str, Any]:
        """Loads the main application configuration file.

        Args:
            config_path: The path to the main application configuration JSON file.

        Returns:
            A dictionary containing the application configuration.

        Raises:
            ConfigLoadError: If the file is not found or if there's an error
                             decoding the JSON.
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config: Dict[str, Any] = json.load(f)
                return config
        except FileNotFoundError as e:
            raise ConfigLoadError(f"Configuration file {config_path} not found.") from e
        except json.JSONDecodeError as e:
            raise ConfigLoadError(f"Could not decode JSON from {config_path}.") from e

    def _generate_navigation_data_for_config(
        self, nav_proto: Optional[Navigation], translations: Translations
    ) -> List[Dict[str, str]]:
        """
        Generates a list of navigation item dictionaries for the configuration.

        This is a helper method to transform Navigation protobuf data into a
        list of dictionaries suitable for inclusion in the JSON configuration,
        applying translations to labels.

        Args:
            nav_proto: An optional Navigation protobuf message containing
                       navigation items.
            translations: A dictionary of translations for the current language.

        Returns:
            A list of dictionaries, where each dictionary represents a
            navigation item with its translated label, key, and href.
        """
        nav_items_for_config: List[Dict[str, str]] = []
        if not nav_proto:
            return nav_items_for_config

        for item in nav_proto.items:
            # item.label is of type TranslatableString from common.proto
            # It has a 'key' field for the translation lookup.
            label_key = item.label.key if item.label and item.label.key else ""
            label: str = translations.get(label_key, label_key)  # Default to key

            href = item.href if item.href else "#"

            nav_items_for_config.append(
                {"label_i18n_key": label_key, "label": label, "href": href}
            )
        return nav_items_for_config

    def generate_language_config(
        self,
        base_config: Dict[str, Any],
        nav_data: Optional[Navigation],
        translations: Translations,
        lang: str,
    ) -> Dict[str, Any]:
        """Generates a language-specific configuration dictionary.

        This method takes the base application configuration and augments it
        with language-specific information, such as translated navigation items
        and the current language code.

        Args:
            base_config: The base application configuration dictionary.
            nav_data: An optional Navigation protobuf message containing
                      navigation items.
            translations: A dictionary of translations for the target language.
            lang: The language code (e.g., "en", "es") for which to generate
                  the configuration.

        Returns:
            A new dictionary representing the language-specific configuration.
        """
        # pylint: disable=unused-argument
        # lang might be used for more complex logic or filtering in the future.
        lang_config = base_config.copy()

        lang_config["navigation"] = self._generate_navigation_data_for_config(
            nav_data, translations
        )

        lang_config["current_lang"] = lang
        lang_config["ui_strings"] = translations

        return lang_config
