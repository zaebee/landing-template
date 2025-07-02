"""
Builds the index.html file from configured blocks for multiple languages
using a class-based approach with protocols.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

from google.protobuf.message import Message

# Ensure the project root (and thus 'generated' directory) is in the Python path
# This allows for direct execution of this script.
project_root = os.path.dirname(os.path.abspath(__file__))
generated_dir = os.path.join(project_root, "generated")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if generated_dir not in sys.path:
    sys.path.insert(0, generated_dir)

# Application-specific imports (Protobuf and services)
# Generated Protobuf message class imports
# Updated build_protocols imports
from build_protocols.config_management import DefaultAppConfigManager
from build_protocols.data_loading import (
    DataFileNotFoundError,  # Import new exceptions
    DataJsonDecodeError,
    DataLoaderError,
    DataProtobufParseError,
    InMemoryDataCache,
    JsonProtoDataLoader,
)
from build_protocols.html_generation import (
    BlogHtmlGenerator,
    ContactFormHtmlGenerator,
    FeaturesHtmlGenerator,
    HeroHtmlGenerator,
    PortfolioHtmlGenerator,
    TestimonialsHtmlGenerator,
)
from build_protocols.interfaces import (
    AppConfigManager,
    DataCache,
    DataLoader,
    HtmlBlockGenerator,
    PageBuilder,
    TranslationProvider,
    Translations,
)
from build_protocols.page_assembly import DefaultPageBuilder
from build_protocols.translation import DefaultTranslationProvider
from generated.blog_post_pb2 import BlogPost
from generated.contact_form_config_pb2 import ContactFormConfig
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import HeroItem
from generated.nav_item_pb2 import Navigation
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem


class BuildOrchestrator:
    """
    Orchestrates the website build process using various service components.

    This class coordinates the loading of configurations, data, and translations,
    and then assembles HTML pages for each supported language.
    """

    def __init__(
        self,
        app_config_manager: AppConfigManager,
        translation_provider: TranslationProvider,
        data_loader: DataLoader[Message],
        data_cache: DataCache[Message],
        page_builder: PageBuilder,
        html_generators: Dict[str, HtmlBlockGenerator],
    ):
        """Initializes the BuildOrchestrator with necessary service components.

        Args:
            app_config_manager: Manages loading and processing of application
                configuration.
            translation_provider: Provides translation services for text and
                HTML content.
            data_loader: Loads data from various sources (e.g., JSON files) into
                protobuf messages.
            data_cache: Caches loaded data to avoid redundant loading operations.
            page_builder: Assembles the final HTML page from various parts.
            html_generators: A dictionary mapping block names to their respective
                HTML generator instances.
        """
        self.app_config_manager = app_config_manager
        self.translation_provider = translation_provider
        self.data_loader = data_loader
        self.data_cache = data_cache
        self.page_builder = page_builder
        self.html_generators = html_generators

        self.app_config: Dict[str, Any] = {}
        self.nav_proto_data: Optional[Navigation] = None

    def load_initial_configurations(self) -> None:
        """Loads base configurations like app config and navigation data.

        This method populates `self.app_config` and `self.nav_proto_data`.
        """
        self.app_config = self.app_config_manager.load_app_config()
        self.nav_proto_data = None  # Ensure it's None by default

        nav_data_file = self.app_config.get(
            "navigation_data_file", "data/navigation.json"
        )
        if nav_data_file:
            try:
                # The DataLoader is generic (Message), but here we expect Navigation.
                # A type: ignore is used as the generic loader's signature doesn't
                # specifically guarantee Navigation without more complex generics.
                self.nav_proto_data = self.data_loader.load_dynamic_single_item_data(
                    nav_data_file,
                    Navigation,  # type: ignore
                )
                if (
                    self.nav_proto_data is None
                ):  # Should not happen if loader raises exceptions
                    print(
                        f"Warning: Navigation data file {nav_data_file} loaded as None unexpectedly."
                    )

            except (
                DataFileNotFoundError,  # type: ignore
                DataJsonDecodeError,  # type: ignore
                DataProtobufParseError,  # type: ignore
                DataLoaderError,  # type: ignore
            ) as e:  # Catching specific data loading errors
                print(
                    f"Error loading navigation data from '{nav_data_file}': {e}. Proceeding without navigation data."
                )
            except Exception as e:  # Catch any other unexpected errors
                print(
                    f"Unexpected error loading navigation data from '{nav_data_file}': {e}. Proceeding without navigation data."
                )
        else:
            print(
                "Warning: 'navigation_data_file' not specified in app config. Proceeding without navigation data."
            )

    def _process_language(
        self,
        lang: str,
        default_lang: str,
        html_parts: tuple[str, str, str, str],
        dynamic_data_loaders_config: Dict[str, Dict[str, Any]],
    ) -> None:
        """Processes and builds the page for a single language."""
        print(f"Processing language: {lang}")
        translations = self.translation_provider.load_translations(lang)

        _html_start, original_header_html, original_footer_html, _html_end = html_parts

        translated_header = self.translation_provider.translate_html_content(
            original_header_html, translations
        )
        translated_footer = self.translation_provider.translate_html_content(
            original_footer_html, translations
        )

        self._generate_language_specific_config(lang, translations)

        assembled_main_content = self._assemble_main_content_for_lang(
            lang, translations, dynamic_data_loaders_config
        )

        full_html_content = self.page_builder.assemble_translated_page(
            lang=lang,
            translations=translations,
            html_parts=html_parts,
            main_content=assembled_main_content,
            header_content=translated_header,
            footer_content=translated_footer,
        )

        output_filename = f"index_{lang}.html"
        if lang == default_lang:
            output_filename = "index.html"

        self._write_output_file(output_filename, full_html_content)

    def build_all_languages(self) -> None:
        """Builds pages for all supported languages.

        This is the main entry point for the build process after initialization.
        It orchestrates loading, data preloading, and iterates through each
        supported language to generate the respective HTML output.
        """
        self.load_initial_configurations()

        supported_langs: List[str] = self.app_config.get(
            "supported_langs", ["en", "es"]
        )
        default_lang: str = self.app_config.get("default_lang", "en")

        dynamic_data_loaders_config = self._get_dynamic_data_loaders_config()
        self.data_cache.preload_data(dynamic_data_loaders_config, self.data_loader)

        os.makedirs("public/generated_configs", exist_ok=True)

        base_html_path = self.app_config.get("base_html_file", "index.html")
        html_parts = self.page_builder.extract_base_html_parts(base_html_path)

        for lang in supported_langs:
            self._process_language(
                lang, default_lang, html_parts, dynamic_data_loaders_config
            )

        print("Build process complete.")

    def _get_dynamic_data_loaders_config(self) -> Dict[str, Dict[str, Any]]:
        """Constructs the configuration for data loaders and HTML generators.

        This configuration maps block filenames (e.g., "portfolio.html")
        to their data requirements (data file, message type, etc.) and
        placeholder string in the block's HTML template. This config is
        primarily used for data preloading and content injection.

        Returns:
            A dictionary where keys are block filenames and values are
            dictionaries containing data loading and templating information.
        """
        # Line length is managed by breaking down the dictionary.
        return {
            "portfolio.html": {
                "data_file": "data/portfolio_items.json",
                "message_type": PortfolioItem,
                "is_list": True,
                "placeholder": "{{portfolio_items}}",
            },
            "blog.html": {
                "data_file": "data/blog_posts.json",
                "message_type": BlogPost,
                "is_list": True,
                "placeholder": "{{blog_posts}}",
            },
            "features.html": {
                "data_file": "data/feature_items.json",
                "message_type": FeatureItem,
                "is_list": True,
                "placeholder": "{{feature_items}}",
            },
            "testimonials.html": {
                "data_file": "data/testimonial_items.json",
                "message_type": TestimonialItem,
                "is_list": True,
                "placeholder": "{{testimonial_items}}",
            },
            "hero.html": {
                "data_file": "data/hero_item.json",
                "message_type": HeroItem,
                "is_list": False,
                "placeholder": "{{hero_content}}",
            },
            "contact-form.html": {
                "data_file": "data/contact_form_config.json",
                "message_type": ContactFormConfig,
                "is_list": False,
                "placeholder": "{{contact_form_attributes}}",
            },
        }

    def _generate_language_specific_config(
        self, lang: str, translations: Translations
    ) -> None:
        """Generates and saves the language-specific JSON configuration file.

        Args:
            lang: The language code (e.g., "en", "es").
            translations: The translation data for the given language.

        Raises:
            IOError: If there is an error writing the configuration file.
                     (Note: Currently prints error instead of raising)
        """
        lang_specific_config = self.app_config_manager.generate_language_config(
            base_config=self.app_config,
            nav_data=self.nav_proto_data,
            translations=translations,
            lang=lang,
        )
        generated_config_path = f"public/generated_configs/config_{lang}.json"
        try:
            with open(generated_config_path, "w", encoding="utf-8") as config_file:
                json.dump(
                    lang_specific_config,
                    config_file,
                    indent=4,
                    ensure_ascii=False,
                )
            print(f"Generated language-specific config: {generated_config_path}")
        except IOError as e:
            # Consider logging this error instead of just printing for production apps
            print(
                f"Error writing language-specific config {generated_config_path}: {e}"
            )

    def _assemble_main_content_for_lang(
        self,
        lang: str,
        translations: Translations,
        data_loaders_config: Dict[str, Dict[str, Any]],
    ) -> str:
        """Assembles the main content by processing and translating HTML blocks.

        Iterates through configured HTML blocks, loads their templates,
        injects dynamic data using HTML generators, and translates the
        resulting content.

        Args:
            lang: The language code for which to assemble content.
            translations: The translation data for the current language.
            data_loaders_config: Configuration for data loading for each block.

        Returns:
            A string containing the assembled and translated main HTML content.
        """
        blocks_html_parts: List[str] = []
        block_filenames: List[str] = self.app_config.get("blocks", [])

        for block_file_name in block_filenames:
            if not isinstance(block_file_name, str):
                print(
                    "Warning: Invalid block file entry in config: "
                    f"{block_file_name}. Skipping."
                )
                continue

            try:
                block_template_path = os.path.join("blocks", block_file_name)
                with open(block_template_path, "r", encoding="utf-8") as block_file:
                    block_template_content = block_file.read()

                block_content_with_data = block_template_content

                if (
                    block_file_name in data_loaders_config
                    and block_file_name in self.html_generators
                ):
                    loader_cfg = data_loaders_config[block_file_name]
                    html_generator = self.html_generators[block_file_name]

                    data_items: Any = self.data_cache.get_item(loader_cfg["data_file"])

                    if loader_cfg.get("is_list", True) and data_items is None:
                        data_items = []

                    generated_html_for_block = html_generator.generate_html(
                        data_items, translations
                    )

                    block_content_with_data = block_template_content.replace(
                        loader_cfg["placeholder"], generated_html_for_block
                    )

                translated_block_html = (
                    self.translation_provider.translate_html_content(
                        block_content_with_data, translations
                    )
                )
                blocks_html_parts.append(translated_block_html)

            except FileNotFoundError:
                print(f"Warning: Block file {block_template_path} not found. Skipping.")
            except Exception as e:  # pylint: disable=broad-except
                # Catching general Exception to ensure one block's failure
                # doesn't stop the entire build for a language.
                # Consider more specific exceptions if error handling needs refinement.
                print(
                    f"Error processing block {block_file_name} for lang {lang}: "
                    f"{e}. Skipping."
                )

        return "\n".join(blocks_html_parts)

    def _write_output_file(self, filename: str, content: str) -> None:
        """Writes content to the specified output file.

        Args:
            filename: The name of the file to write.
            content: The string content to write to the file.

        Raises:
            IOError: If there is an error writing the file.
                     (Note: Currently prints error instead of raising)
        """
        print(f"Writing {filename}")
        try:
            with open(filename, "w", encoding="utf-8") as output_file:
                output_file.write(content)
        except IOError as e:
            # Consider logging this error.
            print(f"Error writing file {filename}: {e}")


def main() -> None:
    """Initializes services and runs the build orchestrator.

    This function sets up all the necessary components (managers, providers,
    loaders, etc.) and then invokes the BuildOrchestrator to perform the
    website build.
    """
    # Instantiate service components with more descriptive names
    app_config_manager_instance = DefaultAppConfigManager()
    translation_provider_instance = DefaultTranslationProvider()
    # Note: JsonProtoDataLoader and InMemoryDataCache are generic.
    # We specify Message here as they will handle various protobuf message types.
    data_loader_instance = JsonProtoDataLoader[Message]()
    data_cache_instance = InMemoryDataCache[Message]()
    page_builder_instance = DefaultPageBuilder(
        translation_provider=translation_provider_instance
    )

    # Map block filenames to their specific HTML generator instances
    # Formatted for line length.
    html_generator_instances: Dict[str, HtmlBlockGenerator] = {
        "portfolio.html": PortfolioHtmlGenerator(),
        "blog.html": BlogHtmlGenerator(),
        "features.html": FeaturesHtmlGenerator(),
        "testimonials.html": TestimonialsHtmlGenerator(),
        "hero.html": HeroHtmlGenerator(),
        "contact-form.html": ContactFormHtmlGenerator(),
    }

    # Create and run the orchestrator
    orchestrator = BuildOrchestrator(
        app_config_manager=app_config_manager_instance,
        translation_provider=translation_provider_instance,
        data_loader=data_loader_instance,
        data_cache=data_cache_instance,
        page_builder=page_builder_instance,
        html_generators=html_generator_instances,
    )
    orchestrator.build_all_languages()


if __name__ == "__main__":
    main()
