from typing import Any, Dict, List, Optional, Protocol, Tuple, Type, TypeVar, Union

from google.protobuf.message import Message

# Type aliases
Translations = Dict[str, str]
T = TypeVar("T", bound=Message)
Nav = TypeVar("Nav", bound=Message)  # For Navigation type specifically


class TranslationProvider(Protocol):
    def load_translations(self, lang: str) -> Translations:
        ...

    def translate_html_content(
        self, html_content: str, translations: Translations
    ) -> str:
        ...


class DataLoader(Protocol[T]):
    def load_dynamic_list_data(
        self, data_file_path: str, message_type: Type[T]
    ) -> List[T]:
        ...

    def load_dynamic_single_item_data(
        self, data_file_path: str, message_type: Type[T]
    ) -> Optional[T]:
        ...


class HtmlBlockGenerator(Protocol):
    def generate_html(self, data: Any, translations: Translations) -> str:
        ...

# Forward declaration for Navigation if not importing directly
# to avoid circular dependencies if other interfaces need it.
# However, generated types should generally not depend on these interfaces.
from generated.nav_item_pb2 import Navigation as NavigationProto


class AppConfigManager(Protocol):
    def load_app_config(self, config_path: str = "public/config.json") -> Dict[str, Any]:
        ...

    def generate_language_config(
        self,
        base_config: Dict[str, Any],
        nav_data: Optional[NavigationProto], # Using concrete type
        translations: Translations,
        lang: str,
    ) -> Dict[str, Any]:
        ...


class PageBuilder(Protocol):
    def extract_base_html_parts(
        self, base_html_path: str = "index.html"
    ) -> Tuple[str, str, str, str]:
        ...

    def assemble_translated_page(
        self,
        lang: str,
        translations: Translations,
        html_parts: Tuple[str, str, str, str],
        main_content: str,
        header_content: Optional[str] = None, # Added for flexibility
        footer_content: Optional[str] = None, # Added for flexibility
    ) -> str:
        ...


class DataCache(Protocol[T]):
    def get_item(self, key: str) -> Optional[Union[List[T], T]]:
        ...

    def set_item(self, key: str, value: Union[List[T], T]) -> None:
        ...

    def preload_data(
        self,
        loaders_config: Dict[str, Dict[str, Any]],
        data_loader: DataLoader[T]
    ) -> None:
        ...

# Specific Navigation type for AppConfigManager more explicit
# from generated.nav_item_pb2 import Navigation # This would cause circular dependency if interfaces used by generated
# For now, using TypeVar Nav and assuming the concrete class will handle it.

# Placeholder for specific data types if needed for block generators
# For example, if HeroHtmlGenerator expects a HeroItem, its 'data' type could be HeroItem
# However, for the protocol, 'Any' is more flexible.
# Concrete generator classes will use specific types.
