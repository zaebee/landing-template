import json
from typing import Any, Dict, List, Optional, Type, Union

from google.protobuf import json_format
from google.protobuf.message import Message

from .interfaces import DataCache, DataLoader, T


class JsonProtoDataLoader(DataLoader[T]):
    """
    Loads data from JSON files into Protobuf messages.
    """

    def load_dynamic_list_data(
        self, data_file_path: str, message_type: Type[T]
    ) -> List[T]:
        """Loads a list of dynamic data from a JSON file into protobuf messages."""
        items: List[T] = []
        try:
            with open(data_file_path, "r", encoding="utf-8") as f:
                data_list_json = json.load(f) # Corrected variable name
                if not isinstance(data_list_json, list):
                    print(
                        f"Warning: Data in {data_file_path} is not a list. "
                        "Returning empty list."
                    )
                    return []
                for item_data in data_list_json:
                    message = message_type()
                    json_format.ParseDict(item_data, message)
                    items.append(message)
        except FileNotFoundError:
            print(
                f"Warning: Data file {data_file_path} not found. Returning empty list."
            )
        except json.JSONDecodeError:
            print(
                f"Warning: Could not decode JSON from {data_file_path}. "
                "Returning empty list."
            )
        except json_format.ParseError as e: # Added specific ParseError handling
            print(
                f"Warning: Could not parse JSON into protobuf for {data_file_path}: {e}. "
                "Returning empty list."
            )
        except Exception as e: # General exception handler
            print(f"An unexpected error occurred loading list {data_file_path}: {e}")
        return items # Ensure items is returned

    def load_dynamic_single_item_data(
        self, data_file_path: str, message_type: Type[T]
    ) -> Optional[T]:
        """Loads a single dynamic data item from a JSON file into a protobuf message."""
        try:
            with open(data_file_path, "r", encoding="utf-8") as f:
                data_json = json.load(f) # Corrected variable name
                message = message_type()
                json_format.ParseDict(data_json, message)
                return message
        except FileNotFoundError:
            print(f"Warning: Data file {data_file_path} not found. Returning None.")
        except json.JSONDecodeError:
            print(
                f"Warning: Could not decode JSON from {data_file_path}. Returning None."
            )
        except json_format.ParseError as e: # Added specific ParseError handling
            print(
                f"Warning: Could not parse JSON into protobuf for {data_file_path}: {e}. "
                "Returning None."
            )
        except Exception as e: # General exception handler
            print(f"An unexpected error occurred loading single item {data_file_path}: {e}")
        return None # Ensure None is returned on error


class InMemoryDataCache(DataCache[T]):
    """
    Simple in-memory cache for dynamic data. Generic over message type T.
    """
    def __init__(self) -> None:
        # The cache can store lists of messages, single messages, or None.
        self._cache: Dict[str, Union[List[Message], Message, None]] = {}


    def get_item(self, key: str) -> Optional[Union[List[T], T]]:
        # External interface uses T, internal _cache uses Message for broader compatibility
        # but get_item should conceptually return items of type T or List[T]
        item = self._cache.get(key)
        if item is None:
            return None
        # This type assertion is based on how items are added in preload_data
        return item # type: ignore

    def set_item(self, key: str, value: Union[List[T], T, None]) -> None:
        self._cache[key] = value


    def preload_data(
        self,
        loaders_config: Dict[str, Dict[str, Any]],
        data_loader: DataLoader[Message] # Expects a DataLoader that can handle any Message
    ) -> None:
        """
        Pre-loads all dynamic data specified in the configuration into this cache.
        Uses the 'data_file' path from the config as the key in the cache.
        """
        print("Pre-loading dynamic data...")
        for _block_file, loader_config in loaders_config.items():
            data_file = loader_config.get("data_file")
            message_type = loader_config.get("message_type") # This is Type[Message]
            is_list = loader_config.get("is_list", True)

            if not data_file or not message_type:
                print(
                    f"Warning: Incomplete configuration for loader: {loader_config}. "
                    "Skipping."
                )
                continue

            # Avoid reloading if already cached
            # Check using self.get_item() which is the public API for the cache
            if self.get_item(data_file) is not None:
                # print(f"Data for {data_file} already in cache. Skipping reload.")
                continue

            loaded_data: Union[List[Message], Optional[Message]]
            if is_list:
                loaded_data = data_loader.load_dynamic_list_data(data_file, message_type)
            else:
                loaded_data = data_loader.load_dynamic_single_item_data(
                    data_file, message_type
                )

            # Set item using the public API
            self.set_item(data_file, loaded_data) # loaded_data matches Union[List[T], T, None]
            # print(f"Loaded data for {data_file} into cache.")
        print("Dynamic data pre-loading complete.")


# Retain original function names for now if they are used elsewhere (e.g. tests)
# but ideally, users of this module would instantiate and use the classes.
_default_loader = JsonProtoDataLoader()
# Renamed to match interface for consistency, but old names aliased for compatibility.
load_dynamic_list_data = _default_loader.load_dynamic_list_data
load_dynamic_single_item_data = _default_loader.load_dynamic_single_item_data

# Alias old names if they were significantly used by tests or other parts not yet refactored.
load_dynamic_data = load_dynamic_list_data

# The preload_dynamic_data function is now a method of InMemoryDataCache.
# If a standalone function is absolutely needed for backward compatibility:
# def preload_dynamic_data(
#     loaders_config: Dict[str, Dict[str, Any]],
#     cache: InMemoryDataCache, # Expects an instance of the cache
#     data_loader: DataLoader[Message] # Expects an instance of a loader
# ) -> None:
# cache.preload_data(loaders_config, data_loader)
