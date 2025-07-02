"""
Provides data loading and caching capabilities for protobuf messages from JSON files.

This module includes:
- `JsonProtoDataLoader`: A class that implements the `DataLoader` protocol
  to load data from JSON files and parse it into specified protobuf messages.
- `InMemoryDataCache`: A class that implements the `DataCache` protocol
  for simple in-memory storage of loaded data.
- Module-level convenience functions (`load_dynamic_list_data`,
  `load_dynamic_single_item_data`) that use a default instance of
  `JsonProtoDataLoader` for ease of use or backward compatibility.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Type, Union

from google.protobuf import json_format
from google.protobuf.message import Message

from .interfaces import DataCache, DataLoader, T

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JsonProtoDataLoader(DataLoader[T]):
    """
    Loads data from JSON files into Protobuf messages.
    Implements the `DataLoader` protocol using a generic type `T` for messages.
    """

    def load_dynamic_list_data(
        self, data_file_path: str, message_type: Type[T]
    ) -> List[T]:
        """Loads a list of data items from a JSON file into protobuf messages.

        Args:
            data_file_path: Path to the JSON file containing a list of items.
            message_type: The protobuf message class to parse each item into.

        Returns:
            A list of protobuf messages of type T. Returns an empty list if
            the file is not found, cannot be decoded, or if parsing fails.
            Warnings are logged in such cases.
        """
        items: List[T] = []
        try:
            with open(data_file_path, "r", encoding="utf-8") as f:
                data_list_json = json.load(f)
                if not isinstance(data_list_json, list):
                    logger.warning(
                        "Data in %s is not a list. Returning empty list.",
                        data_file_path,
                    )
                    return []
                for item_data in data_list_json:
                    message = message_type()
                    json_format.ParseDict(item_data, message)
                    items.append(message)
        except FileNotFoundError:
            logger.warning(
                "Data file %s not found. Returning empty list.", data_file_path
            )
        except json.JSONDecodeError:
            logger.warning(
                "Could not decode JSON from %s. Returning empty list.",
                data_file_path,
            )
        except json_format.ParseError as e:
            logger.warning(
                "Could not parse JSON into protobuf for %s: %s. Returning empty list.",
                data_file_path,
                e,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(
                "An unexpected error occurred loading list %s: %s",
                data_file_path,
                e,
            )
        return items

    def load_dynamic_single_item_data(
        self, data_file_path: str, message_type: Type[T]
    ) -> Optional[T]:
        """Loads a single data item from a JSON file into a protobuf message.

        Args:
            data_file_path: Path to the JSON file containing a single item.
            message_type: The protobuf message class to parse the item into.

        Returns:
            An optional protobuf message of type T. Returns None if the file
            is not found, cannot be decoded, or if parsing fails.
            Warnings are logged in such cases.
        """
        try:
            with open(data_file_path, "r", encoding="utf-8") as f:
                data_json = json.load(f)
                message: T = message_type()
                json_format.ParseDict(data_json, message)
                return message
        except FileNotFoundError:
            logger.warning("Data file %s not found. Returning None.", data_file_path)
        except json.JSONDecodeError:
            logger.warning(
                "Could not decode JSON from %s. Returning None.", data_file_path
            )
        except json_format.ParseError as e:
            logger.warning(
                "Could not parse JSON into protobuf for %s: %s. Returning None.",
                data_file_path,
                e,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.warning(
                "An unexpected error occurred loading single item %s: %s",
                data_file_path,
                e,
            )
        return None


class InMemoryDataCache(DataCache[T]):
    """
    Simple in-memory cache for dynamic data, generic over message type T.
    Implements the `DataCache` protocol.
    """

    def __init__(self) -> None:
        """Initializes an empty in-memory cache."""
        # The internal cache stores Union[List[Message], Message, None] to handle
        # various protobuf message types loaded by a generic DataLoader.
        # The type variable T in DataCache[T] implies that users of this cache
        # expect items of type T or List[T].
        self._cache: Dict[str, Union[List[Message], Message, None]] = {}

    def get_item(self, key: str) -> Optional[Union[List[T], T]]:
        """Retrieves an item or a list of items from the cache by key.

        Args:
            key: The key (typically the data file path) for the cached item.

        Returns:
            The cached item(s) (List[T] or T) or None if the key is not found.
            A `type: ignore` is used here because the internal cache holds
            `Message` types for flexibility, while the interface promises `T`.
            This assumes `T` will be compatible with `Message` (e.g., `T` is a
            subclass of `Message` or `Message` itself), which is generally
            true for protobuf messages.
        """
        item = self._cache.get(key)
        if item is None:
            return None
        # This type assertion is based on the assumption that items are stored
        # correctly by `set_item` and `preload_data`, and that T is compatible
        # with Message. If T were bound (e.g., T = TypeVar('T', bound=Message)),
        # this ignore might be avoidable or replaced with a cast.
        return item  # type: ignore

    def set_item(self, key: str, value: Union[List[T], T, None]) -> None:
        """Sets or updates an item in the cache.

        Args:
            key: The key (typically the data file path) for the item.
            value: The item (List[T], T, or None) to cache.
        """
        self._cache[key] = value

    def preload_data(
        self,
        loaders_config: Dict[str, Dict[str, Any]],
        data_loader: DataLoader[Message],
    ) -> None:
        """Pre-loads data specified in the configuration into the cache.

        Iterates through the `loaders_config`, using the provided `data_loader`
        to load data and then stores it in the cache. The 'data_file' path
        from the config is used as the cache key.

        Args:
            loaders_config: A dictionary defining what data to load.
                            Keys are typically block filenames, and values are
                            dictionaries with 'data_file', 'message_type',
                            and 'is_list' keys.
            data_loader: An instance of a DataLoader (typically JsonProtoDataLoader)
                         configured to handle any `Message` type.
        """
        logger.info("Pre-loading dynamic data...")
        for _block_file, loader_config in loaders_config.items():
            data_file = loader_config.get("data_file")
            message_type = loader_config.get("message_type")  # Expected: Type[Message]
            is_list = loader_config.get("is_list", True)

            if not data_file or not message_type:
                logger.warning(
                    "Incomplete configuration for loader: %s. Skipping.",
                    loader_config,
                )
                continue

            if self.get_item(data_file) is not None:
                # logger.info("Data for %s already in cache. Skipping reload.", data_file)
                continue

            loaded_data: Union[List[Message], Optional[Message]]
            if is_list:
                loaded_data = data_loader.load_dynamic_list_data(
                    data_file, message_type
                )
            else:
                loaded_data = data_loader.load_dynamic_single_item_data(
                    data_file, message_type
                )

            self.set_item(data_file, loaded_data)
            # logger.info("Loaded data for %s into cache.", data_file)
        logger.info("Dynamic data pre-loading complete.")


# --- Module-Level Convenience Functions ---
# These functions use a default instance of JsonProtoDataLoader for ease of use
# or for backward compatibility with code that expects module-level functions.
# Ideally, new code should instantiate and use JsonProtoDataLoader and
# InMemoryDataCache directly for better testability and explicitness.

_default_loader: JsonProtoDataLoader = JsonProtoDataLoader()

load_dynamic_list_data = _default_loader.load_dynamic_list_data
"""Module-level function to load a list of data items. See JsonProtoDataLoader."""

load_dynamic_single_item_data = _default_loader.load_dynamic_single_item_data
"""Module-level function to load a single data item. See JsonProtoDataLoader."""

# Alias for potential backward compatibility if 'load_dynamic_data' was used
# specifically for list data in the past.
load_dynamic_data = load_dynamic_list_data
"""Alias for load_dynamic_list_data for backward compatibility."""

# Note: The original `preload_dynamic_data` function (if it existed as a
# standalone module function) is now primarily a method of `InMemoryDataCache`.
# If a standalone function is absolutely needed for strict backward compatibility,
# it would need to accept a cache instance:
#
# def preload_dynamic_data_module_level(
#     loaders_config: Dict[str, Dict[str, Any]],
#     cache: InMemoryDataCache,
#     data_loader: DataLoader[Message]
# ) -> None:
#     """Stand-alone version of preload_data for specific use cases."""
#     cache.preload_data(loaders_config, data_loader)
