import json
import sys
from typing import Any, Dict, List, Optional

from generated.nav_item_pb2 import Navigation

from .interfaces import (  # NavigationProto is aliased as Navigation here essentially
    AppConfigManager,
    Translations,
)


class DefaultAppConfigManager(AppConfigManager): # No type var needed if NavigationProto is used in interface
    """
    Default implementation for managing application and language-specific configurations.
    """

    def load_app_config(self, config_path: str = "public/config.json") -> Dict[str, Any]:
        """Loads the main application configuration file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config: Dict[str, Any] = json.load(f)
                return config
        except FileNotFoundError:
            print(f"Error: Configuration file {config_path} not found. Exiting.")
            sys.exit(1) # Consider custom exception
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {config_path}. Exiting.")
            sys.exit(1) # Consider custom exception

    def _generate_navigation_data_for_config(
        self, nav_proto: Optional[Navigation], translations: Translations
    ) -> List[Dict[str, str]]:
        """
        Generates a list of navigation item dictionaries for config.json
        based on the Navigation proto and translations. (Helper method)
        """
        nav_items_for_config: List[Dict[str, str]] = []
        if not nav_proto:
            return nav_items_for_config

        for item in nav_proto.items:
            # Assuming item.label is TranslatableString with a 'key'
            label_key = item.label.key if item.label and item.label.key else ""
            label: str = translations.get(label_key, label_key) # Default to key

            href = item.href if item.href else "#"

            nav_items_for_config.append(
                {"label_i18n_key": label_key, "label": label, "href": href}
            )
        return nav_items_for_config

    def generate_language_config(
        self,
        base_config: Dict[str, Any], # Renamed from base_app_config for consistency
        nav_data: Optional[Navigation], # Renamed from nav_proto_data
        translations: Translations,
        lang: str,
    ) -> Dict[str, Any]:
        """Generates a language-specific configuration dictionary."""
        # pylint: disable=unused-argument # lang might be used for more complex logic later
        lang_config = base_config.copy() # Start with a copy of the base application config

        # Add/replace navigation with the translated version
        lang_config["navigation"] = self._generate_navigation_data_for_config(
            nav_data, translations
        )

        # Add language identifier
        lang_config["current_lang"] = lang

        # Optionally, include all translations or a subset for client-side use
        lang_config["ui_strings"] = translations # Or filter based on some criteria

        # Potentially add other language-specific config overrides here
        # For example, if base_config has a "lang_specific_overrides" section:
        # if "lang_specific_overrides" in base_config and lang in base_config["lang_specific_overrides"]:
        #     lang_config.update(base_config["lang_specific_overrides"][lang])

        return lang_config

# Aliases for backward compatibility if needed by tests or other parts not yet refactored.
# This assumes DefaultAppConfigManager can be instantiated without specific generic types if Nav is concrete.
# _manager_instance = DefaultAppConfigManager()
# load_app_config = _manager_instance.load_app_config
# generate_language_config = _manager_instance.generate_language_config
# generate_navigation_data_for_config is now a private helper.
