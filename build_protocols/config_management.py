import json
import sys
from typing import Any, Dict, List

# Assuming protos are compiled and available in generated.*
# and Translations type is defined (e.g. in a shared types module or passed directly)
from generated.nav_item_pb2 import Navigation

# Type alias from build.py, consider moving to a shared types.py if more are added
Translations = Dict[str, str]


def load_app_config(config_path: str = "public/config.json") -> Dict[str, Any]:
    """Loads the main application configuration file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            result: Dict[str, Any] = json.load(f)
            return result
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found. Exiting.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {config_path}. Exiting.")
        sys.exit(1)


def generate_navigation_data_for_config(
    nav_proto: Navigation | None, translations: Translations
) -> List[Dict[str, str]]:
    """
    Generates a list of navigation item dictionaries for config.json
    based on the Navigation proto and translations.
    """
    nav_items_for_config: List[Dict[str, str]] = []
    if not nav_proto:
        return nav_items_for_config

    for item in nav_proto.items:
        label: str = translations.get(item.label.key, item.label.key)
        nav_items_for_config.append(
            {"label_i18n_key": item.label.key, "label": label, "href": item.href}
        )
    return nav_items_for_config


def generate_language_config(
    base_app_config: Dict[str, Any],
    nav_proto_data: Navigation | None,
    translations: Translations,
    # lang parameter can be used if more lang-specific logic is added later
    lang: str,  # pylint: disable=unused-argument # Keep for potential future use
) -> Dict[str, Any]:
    """Generates a language-specific configuration dictionary."""
    lang_config = base_app_config.copy()
    lang_config["navigation"] = generate_navigation_data_for_config(
        nav_proto_data, translations
    )
    # Potentially add other language-specific config overrides here
    return lang_config
