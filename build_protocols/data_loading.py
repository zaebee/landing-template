import json
from typing import Any, Dict, List, Type, TypeVar, Union

from google.protobuf import json_format
from google.protobuf.message import Message

# Define a TypeVar for generic protobuf messages
T = TypeVar("T", bound=Message)


def load_dynamic_data(data_file_path: str, message_type: Type[T]) -> List[T]:
    """
    Loads dynamic data from a JSON file and parses it into a list of protobuf
    messages.
    """
    items: List[T] = []
    try:
        with open(data_file_path, "r", encoding="utf-8") as f:
            # Assuming the JSON data is a list of dictionaries
            data: List[Dict[str, Any]] = json.load(f)
            for item_json in data:
                message = message_type()
                json_format.ParseDict(item_json, message)
                items.append(message)
            return items
    except FileNotFoundError:
        print(f"Warning: Data file {data_file_path} not found. Returning empty list.")
        return []
    except json.JSONDecodeError:
        print(
            f"Warning: Could not decode JSON from {data_file_path}. "
            "Returning empty list."
        )
        return []
    except json_format.ParseError as e:
        print(
            f"Warning: Could not parse JSON into protobuf for {data_file_path}: {e}. "
            "Returning empty list."
        )
        return []
    return []  # Ensure a list is always returned, even if empty due to other errors


def load_single_item_dynamic_data(
    data_file_path: str, message_type: Type[T]
) -> T | None:
    """
    Loads dynamic data for a single item from a JSON file and parses it
    into a protobuf message.
    """
    try:
        with open(data_file_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)  # Expects a single JSON object
            message: T = message_type()
            json_format.ParseDict(data, message)
            return message
    except FileNotFoundError:
        print(f"Warning: Data file {data_file_path} not found. Returning None.")
        return None
    except json.JSONDecodeError:
        print(
            f"Warning: Could not decode JSON from {data_file_path}. " "Returning None."
        )
        return None
    except json_format.ParseError as e:
        print(
            f"Warning: Could not parse JSON into protobuf for {data_file_path}: {e}. "
            "Returning None."
        )
        return None
    return None


def preload_dynamic_data(
    loaders_config: Dict[str, Dict[str, Any]],
    cache: Dict[str, Union[List[Message], Message, None]],
    # Pass message_types to avoid circular dependency if they are defined elsewhere
    # For now, assuming message_type is directly available or passed in loaders_config
) -> None:
    """Pre-loads dynamic data from JSON files into a cache."""
    for _, config_item in loaders_config.items():
        data_file = config_item["data_file"]
        message_type = config_item["message_type"] # This comes from build.py's main config
        is_list = config_item.get("is_list", True)

        if data_file not in cache:
            if is_list:
                cache[data_file] = load_dynamic_data(data_file, message_type)
            else:
                cache[data_file] = load_single_item_dynamic_data(
                    data_file, message_type
                )
