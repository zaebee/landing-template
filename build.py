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
project_root = os.path.dirname(os.path.abspath(__file__))
generated_dir = os.path.join(project_root, "generated")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if generated_dir not in sys.path:
    sys.path.insert(0, generated_dir)


# Protobuf imports
from build_protocols.config_management import DefaultAppConfigManager
from build_protocols.data_loading import InMemoryDataCache, JsonProtoDataLoader
from build_protocols.html_generation import (
    BlogHtmlGenerator,
    ContactFormHtmlGenerator,
    FeaturesHtmlGenerator,
    HeroHtmlGenerator,
    PortfolioHtmlGenerator,
    TestimonialsHtmlGenerator,
)

# Import service classes and protocols
from build_protocols.interfaces import (
    AppConfigManager,
    DataCache,
    DataLoader,
    HtmlBlockGenerator,
    PageBuilder,
    TranslationProvider,
    Translations,  # Ensure Translations type alias is available
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
    """

    def __init__(
        self,
        app_config_manager: AppConfigManager,
        translation_provider: TranslationProvider,
        data_loader: DataLoader[Message],  # Generic Message for DataLoader
        data_cache: DataCache[Message],  # Generic Message for DataCache
        page_builder: PageBuilder,
        html_generators: Dict[
            str, HtmlBlockGenerator
        ],  # Map block name to its generator
    ):
        self.app_config_manager = app_config_manager
        self.translation_provider = translation_provider
        self.data_loader = data_loader
        self.data_cache = data_cache
        self.page_builder = page_builder
        self.html_generators = html_generators

        self.app_config: Dict[str, Any] = {}
        self.nav_proto_data: Optional[Navigation] = None

    def load_initial_configurations(self) -> None:
        """Loads base configurations like app config and navigation data."""
        self.app_config = self.app_config_manager.load_app_config()

        nav_data_file = self.app_config.get(
            "navigation_data_file", "data/navigation.json"
        )
        # Cast is safe if Navigation is the expected type for nav_data_file
        self.nav_proto_data = self.data_loader.load_dynamic_single_item_data(
            nav_data_file, Navigation  # type: ignore
        )

    def build_all_languages(self) -> None:
        """Builds pages for all supported languages."""
        self.load_initial_configurations()

        supported_langs: List[str] = self.app_config.get(
            "supported_langs", ["en", "es"]
        )
        default_lang: str = self.app_config.get("default_lang", "en")

        dynamic_data_loaders_config = self._get_dynamic_data_loaders_config()
        self.data_cache.preload_data(dynamic_data_loaders_config, self.data_loader)

        os.makedirs("public/generated_configs", exist_ok=True)

        # Extract base HTML parts once
        # The page_builder's extract_base_html_parts might take a path from app_config
        base_html_path = self.app_config.get("base_html_file", "index.html")
        html_parts = self.page_builder.extract_base_html_parts(base_html_path)

        # Original header and footer from base HTML. These might contain i18n tags.
        _html_start, original_header_html, original_footer_html, _html_end = html_parts

        for lang in supported_langs:
            print(f"Processing language: {lang}")
            translations = self.translation_provider.load_translations(lang)

            # Translate original header and footer content
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
                translations=translations,  # assemble_translated_page might use this for <html> tag lang
                html_parts=html_parts,  # Contains original untranslated structure
                main_content=assembled_main_content,
                header_content=translated_header,  # Pass pre-translated header
                footer_content=translated_footer,  # Pass pre-translated footer
            )

            output_filename = f"index_{lang}.html"
            if lang == default_lang:
                output_filename = "index.html"

            self._write_output_file(output_filename, full_html_content)

        print("Build process complete.")

    def _get_dynamic_data_loaders_config(self) -> Dict[str, Dict[str, Any]]:
        """Constructs the configuration for data loaders and HTML generators."""
        # This config maps block filenames (e.g., "portfolio.html")
        # to their data requirements and HTML generation logic.
        # The 'generator' key here is not used directly if self.html_generators is used.
        # This config is primarily for data preloading.
        return {
            "portfolio.html": {
                "data_file": "data/portfolio_items.json",
                "message_type": PortfolioItem,
                "is_list": True,
                "placeholder": "{{portfolio_items}}",  # Placeholder in the block template file
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
        """Generates and saves the language-specific JSON config."""
        lang_specific_config = self.app_config_manager.generate_language_config(
            base_config=self.app_config,
            nav_data=self.nav_proto_data,
            translations=translations,
            lang=lang,
        )
        generated_config_path = f"public/generated_configs/config_{lang}.json"
        try:
            with open(generated_config_path, "w", encoding="utf-8") as f_config:
                json.dump(lang_specific_config, f_config, indent=4, ensure_ascii=False)
            print(f"Generated language-specific config: {generated_config_path}")
        except IOError as e:
            print(
                f"Error writing language-specific config {generated_config_path}: {e}"
            )

    def _assemble_main_content_for_lang(
        self,
        lang: str,
        translations: Translations,
        data_loaders_config: Dict[str, Dict[str, Any]],
    ) -> str:
        """Assembles the main content by processing and translating blocks."""
        blocks_html_parts: List[str] = []
        for block_file_name in self.app_config.get("blocks", []):
            if not isinstance(block_file_name, str):
                print(
                    f"Warning: Invalid block file entry in config: {block_file_name}. Skipping."
                )
                continue

            try:
                with open(
                    f"blocks/{block_file_name}", "r", encoding="utf-8"
                ) as f_block:
                    block_template_content = f_block.read()

                block_content_with_data = block_template_content

                if (
                    block_file_name in data_loaders_config
                    and block_file_name in self.html_generators
                ):
                    loader_cfg = data_loaders_config[block_file_name]
                    html_generator = self.html_generators[block_file_name]

                    # Data can be List[Message], Message, or None
                    data_items: Any = self.data_cache.get_item(loader_cfg["data_file"])

                    # Ensure data_items matches what the generator expects (list or single item)
                    # The generators are typed with List[ProtoItem] or Optional[ProtoItem]
                    # The InMemoryDataCache stores Union[List[Message], Message, None]
                    # So, this should align.

                    # Ensure data_items is an empty list if it's None and a list is expected
                    if loader_cfg.get("is_list", True) and data_items is None:
                        data_items = []

                    generated_html_for_block = html_generator.generate_html(
                        data_items, translations
                    )

                    block_content_with_data = block_template_content.replace(
                        loader_cfg["placeholder"], generated_html_for_block
                    )

                # Translate the entire block content (template + injected data)
                translated_block_html = (
                    self.translation_provider.translate_html_content(
                        block_content_with_data, translations
                    )
                )
                blocks_html_parts.append(translated_block_html)

            except FileNotFoundError:
                print(
                    f"Warning: Block file blocks/{block_file_name} not found. Skipping."
                )
            except Exception as e:
                print(
                    f"Error processing block {block_file_name} for lang {lang}: {e}. Skipping."
                )

        return "\n".join(blocks_html_parts)

    def _write_output_file(self, filename: str, content: str) -> None:
        """Writes content to the specified output file."""
        print(f"Writing {filename}")
        try:
            with open(filename, "w", encoding="utf-8") as f_out:
                f_out.write(content)
        except IOError as e:
            print(f"Error writing file {filename}: {e}")


def main() -> None:
    """
    Initializes services and runs the build orchestrator.
    """
    # Instantiate service components
    app_config_mgr = DefaultAppConfigManager()
    translation_prov = DefaultTranslationProvider()
    # Note: JsonProtoDataLoader and InMemoryDataCache are generic.
    # We specify Message here as they will handle various protobuf message types.
    data_loadr = JsonProtoDataLoader[Message]()
    data_cch = InMemoryDataCache[Message]()
    page_bldr = DefaultPageBuilder(
        translation_provider=translation_prov
    )  # Pass translator

    # Map block filenames to their specific HTML generator instances
    html_gens: Dict[str, HtmlBlockGenerator] = {
        "portfolio.html": PortfolioHtmlGenerator(),
        "blog.html": BlogHtmlGenerator(),
        "features.html": FeaturesHtmlGenerator(),
        "testimonials.html": TestimonialsHtmlGenerator(),
        "hero.html": HeroHtmlGenerator(),
        "contact-form.html": ContactFormHtmlGenerator(),
    }

    # Create and run the orchestrator
    orchestrator = BuildOrchestrator(
        app_config_manager=app_config_mgr,
        translation_provider=translation_prov,
        data_loader=data_loadr,
        data_cache=data_cch,
        page_builder=page_bldr,
        html_generators=html_gens,
    )
    orchestrator.build_all_languages()


if __name__ == "__main__":
    main()
