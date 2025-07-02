"""
Builds the index.html file from configured blocks for multiple languages
using a class-based approach with protocols.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

from google.protobuf.message import Message
from jinja2 import Environment, FileSystemLoader

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
            translation_provider: Provides translation services for text and HTML
                content.
            data_loader: Loads data from various sources (e.g., JSON files)
                into protobuf messages.
            data_cache: Caches loaded data to avoid redundant loading
                operations.
            page_builder: Assembles the final HTML page from various parts.
            html_generators: A dictionary mapping block names to their
                respective HTML generator instances.
        """
        self.app_config_manager = app_config_manager
        self.translation_provider = translation_provider
        self.data_loader = data_loader
        self.data_cache = data_cache
        self.page_builder = page_builder
        self.html_generators = html_generators

        self.app_config: Dict[str, Any] = {}
        self.nav_proto_data: Optional[Navigation] = None

    def _bundle_component_css(self) -> None:
        """Finds all component CSS files and bundles them into a single file."""
        print("Bundling component CSS files...")
        component_css_dir = os.path.join(project_root, "templates", "components")
        output_dir = os.path.join(project_root, "public", "dist")
        output_file_path = os.path.join(output_dir, "main.css")

        os.makedirs(output_dir, exist_ok=True)
        css_contents = []

        for component_name in os.listdir(component_css_dir):
            component_dir_path = os.path.join(component_css_dir, component_name)
            if os.path.isdir(component_dir_path):
                css_file_path = os.path.join(component_dir_path, f"{component_name}.css")
                if os.path.exists(css_file_path):
                    try:
                        with open(css_file_path, "r", encoding="utf-8") as f:
                            css_contents.append(f.read())
                        print(f"Read CSS from: {css_file_path}")
                    except IOError as e:
                        print(f"Error reading CSS file {css_file_path}: {e}")

        if not css_contents:
            print("No component CSS files found to bundle.")
            # Create an empty main.css if no components have CSS
            # to avoid missing file errors if base.html links to it.
            try:
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write("/* No component CSS found or bundled. */")
                print(f"Created empty CSS bundle: {output_file_path}")
            except IOError as e:
                print(f"Error creating empty CSS bundle {output_file_path}: {e}")
            return

        try:
            with open(output_file_path, "w", encoding="utf-8") as outfile:
                outfile.write("\n\n/* --- Component CSS Bundle --- */\n\n")
                for content in css_contents:
                    outfile.write(content)
                    outfile.write("\n\n/* --- End of component CSS --- */\n\n")
            print(f"Successfully bundled CSS to: {output_file_path}")
        except IOError as e:
            print(f"Error writing bundled CSS to {output_file_path}: {e}")

    def _bundle_component_js(self) -> None:
        """Finds all component JS files and shared JS, bundles them."""
        print("Bundling JavaScript files...")
        js_files_to_bundle = []

        # 1. Component-specific JS
        component_js_dir = os.path.join(project_root, "templates", "components")
        for component_name in os.listdir(component_js_dir):
            component_dir_path = os.path.join(component_js_dir, component_name)
            if os.path.isdir(component_dir_path):
                js_file_path = os.path.join(component_dir_path, f"{component_name}.js")
                if os.path.exists(js_file_path):
                    js_files_to_bundle.append(js_file_path)
                    print(f"Found component JS: {js_file_path}")

        # 2. Shared/Global JS
        shared_js_dir = os.path.join(project_root, "public", "js")

        # Prioritize SADS engine, then app.js, then component JS
        sads_engine_path = os.path.join(shared_js_dir, "sads-style-engine.js")
        if os.path.exists(sads_engine_path):
            js_files_to_bundle.insert(0, sads_engine_path)
            print(f"Found SADS Engine JS: {sads_engine_path}")

        app_js_path = os.path.join(shared_js_dir, "app.js")
        if os.path.exists(app_js_path):
            # Insert after SADS engine if present, otherwise at the beginning
            insert_idx = 1 if sads_engine_path in js_files_to_bundle else 0
            js_files_to_bundle.insert(insert_idx, app_js_path)
            print(f"Found shared App JS: {app_js_path}")

        output_dir = os.path.join(project_root, "public", "dist")
        output_file_path = os.path.join(output_dir, "main.js")
        os.makedirs(output_dir, exist_ok=True)

        if not js_files_to_bundle:
            print("No JavaScript files found to bundle.")
            try:
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write("// No JavaScript files found or bundled.")
                print(f"Created empty JS bundle: {output_file_path}")
            except IOError as e:
                print(f"Error creating empty JS bundle {output_file_path}: {e}")
            return

        js_contents = []
        for file_path in js_files_to_bundle:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    js_contents.append(f.read())
            except IOError as e:
                print(f"Error reading JS file {file_path}: {e}")

        try:
            with open(output_file_path, "w", encoding="utf-8") as outfile:
                outfile.write("\n// --- JavaScript Bundle --- //\n\n")
                for i, content in enumerate(js_contents):
                    original_path = js_files_to_bundle[i]
                    outfile.write(f"\n// --- Source: {os.path.basename(original_path)} --- //\n")
                    outfile.write(content)
                    outfile.write("\n// --- End Source --- //\n\n")
            print(f"Successfully bundled JavaScript to: {output_file_path}")
        except IOError as e:
            print(f"Error writing bundled JavaScript to {output_file_path}: {e}")


    def load_initial_configurations(self) -> None:
        """Loads base configurations like app config and navigation data.

        This method populates `self.app_config` and `self.nav_proto_data`.
        """
        self.app_config = self.app_config_manager.load_app_config()

        nav_data_file = self.app_config.get(
            "navigation_data_file", "data/navigation.json"
        )
        # The DataLoader is generic (Message), but here we expect Navigation.
        # A type: ignore is used as the generic loader's signature doesn't
        # specifically guarantee Navigation without more complex generics.
        self.nav_proto_data = (
            self.data_loader.load_dynamic_single_item_data(
                nav_data_file,
                Navigation,  # type: ignore
            )
        )

    def _process_language(
        self,
        lang: str,
        default_lang: str,
        dynamic_data_loaders_config: Dict[str, Dict[str, Any]],
        navigation_items: List[Dict[str, Any]],
    ) -> None:
        """Processes and builds the page for a single language."""
        print(f"Processing language: {lang}")
        translations = self.translation_provider.load_translations(lang)

        self._generate_language_specific_config(lang, translations)

        assembled_main_content = (
            self._assemble_main_content_for_lang(
                lang, translations, dynamic_data_loaders_config
            )
        )

        page_title = translations.get("page_title_default", "Simple Landing Page")
        # Add specific page titles per language if defined, e.g. "page_title_landing_es"
        page_title = translations.get(f"page_title_landing_{lang}", page_title)

        full_html_content = self.page_builder.assemble_translated_page(
            lang=lang,
            translations=translations,
            main_content=assembled_main_content,
            navigation_items=navigation_items,
            page_title=page_title,
            app_config=self.app_config, # Pass app_config
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
        self._bundle_component_css() # Bundle CSS
        self._bundle_component_js() # Bundle JS

        supported_langs: List[str] = self.app_config.get(
            "supported_langs", ["en", "es"]
        )
        default_lang: str = self.app_config.get("default_lang", "en")

        # Mapping of message type names (from config) to actual protobuf classes
        proto_message_types = {
            "PortfolioItem": PortfolioItem,
            "BlogPost": BlogPost,
            "FeatureItem": FeatureItem,
            "TestimonialItem": TestimonialItem,
            "HeroItem": HeroItem,
            "ContactFormConfig": ContactFormConfig,
            "Navigation": Navigation, # Added for completeness, though not in block_data_loaders
        }

        # Get block data loader configuration from app_config
        block_loaders_config_raw = self.app_config.get("block_data_loaders", {})

        # Resolve message_type_name to actual message_type class
        dynamic_data_loaders_config_resolved = {}
        for block_name, config_item in block_loaders_config_raw.items():
            message_type_name = config_item.get("message_type_name")
            message_type_class = proto_message_types.get(message_type_name)
            if not message_type_class:
                print(f"Warning: Unknown message_type_name '{message_type_name}' for block '{block_name}'. Skipping.")
                continue

            # Create a new config dict for resolved types to avoid modifying original app_config
            resolved_item_config = config_item.copy()
            resolved_item_config["message_type"] = message_type_class
            dynamic_data_loaders_config_resolved[block_name] = resolved_item_config

        self.data_cache.preload_data(
            dynamic_data_loaders_config_resolved, self.data_loader
        )

        os.makedirs("public/generated_configs", exist_ok=True)

        # Process navigation data into the format expected by the template
        processed_nav_items = []
        if self.nav_proto_data:
            for item in self.nav_proto_data.items:
                processed_nav_items.append({
                    "label": {"key": item.label.key}, # Pass the key for translation in template
                    "href": item.href,
                    "animation_hint": item.animation_hint
                })

        for lang in supported_langs:
            self._process_language(
                lang=lang,
                default_lang=default_lang,
                dynamic_data_loaders_config=dynamic_data_loaders_config_resolved, # Use resolved config
                navigation_items=processed_nav_items,
            )

        print("Build process complete.")

    def _generate_language_specific_config(
        self, lang: str, translations: Translations
    ) -> None:
        """Generates and saves the language-specific JSON configuration file.

        Args:
            lang: The language code (e.g., "en", "es").
            translations: The translation data for the given language.

        Raises:
            IOError: If there is an error writing the configuration file.
        """
        # This method prints errors to stdout rather than raising an IOError
        # directly to allow the build process to continue for other languages
        # if one configuration file fails to write.
        lang_specific_config = (
            self.app_config_manager.generate_language_config(
                base_config=self.app_config,
                nav_data=self.nav_proto_data,
                translations=translations,
                lang=lang,
            )
        )
        generated_config_path = (
            f"public/generated_configs/config_{lang}.json"
        )
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
            # Consider logging this error instead of just printing.
            print(
                f"Error writing language-specific config "
                f"{generated_config_path}: {e}"
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
            data_loaders_config: Configuration for data loading for each
                block.

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

            # The concept of reading block template content directly and replacing placeholders
            # is now handled by Jinja2 within each HtmlBlockGenerator.
            # The generators will use their Jinja environment to load templates from
            # `templates/blocks/`
            generated_html_for_block = ""
            try:
                if (
                    block_file_name in data_loaders_config
                    and block_file_name in self.html_generators
                ):
                    loader_cfg = data_loaders_config[block_file_name]
                    html_generator = self.html_generators[block_file_name]

                    # Data loading remains the same
                    data_items: Any = self.data_cache.get_item(loader_cfg["data_file"])
                    if loader_cfg.get("is_list", True) and data_items is None:
                        data_items = []
                    elif not loader_cfg.get("is_list", True) and data_items is None:
                        # For single items, if data_items is None, pass None to generator
                        pass

                    # HtmlBlockGenerator now handles its own template loading & rendering
                    generated_html_for_block = html_generator.generate_html(
                        data_items, translations
                    )
                else:
                    # If block is not in html_generators, it might be a simple static block
                    # This path needs clarification: for now, assume all configured blocks
                    # have a generator. If not, we might need to read its content from
                    # templates/blocks/ directly if it's purely static.
                    # Or, this is an error in configuration.
                    # For now, we'll just log a warning if a block has no generator.
                    print(
                        f"Warning: No HTML generator found for block: {block_file_name}. Skipping data injection."
                    )
                    # Attempt to read static block content if needed, but this wasn't the old behavior.
                    # The old behavior relied on a placeholder for replacement.
                    # With Jinja, if a block is purely static, its template would just be static HTML.
                    # The current HtmlBlockGenerators expect data.
                    # This logic branch might need to be removed or adapted if static blocks
                    # without data are listed in app_config['blocks'].
                    # For now, we assume blocks in app_config['blocks'] are dynamic and have generators.
                    # If a block is purely static HTML, it should be part of the main base.html
                    # or a Jinja include there, not processed via this loop.

                    # Fallback: try to load the block as a static template if no generator
                    # This is a deviation, as the old code expected a generator to fill a placeholder.
                    # If it's a static block, it would have been included directly.
                    # This part might be an over-correction.
                    # Let's stick to: if it's in 'blocks' config, it should have a generator.
                    # If a block is purely static, it shouldn't be in 'blocks' config for this loop.
                    # It should be part of the base.html or included there.
                    # The original code read the file content and then potentially replaced a placeholder.
                    # If no placeholder replacement, it used the content as is.
                    # With Jinja generators, the generator IS the one loading the template.
                    # So, if a block is in config, it MUST have a generator.

                    # The old code would read the block file, then if no generator,
                    # it would still try to translate the raw content.
                    # Let's replicate that if no generator is found but block is in config.
                    # This means the block is treated as mostly static HTML but with i18n tags.
                    try:
                        block_template_path = os.path.join(
                            "templates", "blocks", block_file_name
                        )  # new path
                        with open(
                            block_template_path, "r", encoding="utf-8"
                        ) as block_file:
                            static_block_content = block_file.read()
                        generated_html_for_block = static_block_content
                        print(
                            f"Info: Treating block {block_file_name} as static HTML for translation only."
                        )
                    except FileNotFoundError:
                        print(
                            f"Warning: Static block file {block_file_name} not found. Skipping."
                        )
                        continue

                # The translation of the entire block's generated HTML
                # should ideally be handled by the Jinja templates themselves if they use
                # the `translations` context properly.
                # If `translate_html_content` is still needed here, it implies that
                # the generated HTML from blocks might *still* contain {{i18n_key}} tags
                # that Jinja didn't process (e.g. if they were part of string literals
                # within the protobuf data that got directly embedded).
                # This should be minimized; translations should occur within Jinja templates.
                # For safety, we can keep it, but it might indicate a smell.
                # The Jinja templates for blocks now receive `translations` object, so they *should*
                # be doing all necessary translations.
                # Let's assume the block HTML from generator is fully translated.
                # If not, `translate_html_content` would be needed here.
                # The original code did this translation *after* placeholder replacement.

                # If HtmlBlockGenerator.generate_html already returns fully translated HTML
                # (because Jinja templates use the `translations` object), then this
                # `translate_html_content` call might be redundant or even harmful
                # if it re-processes already translated content.
                # Let's assume for now that generators output translated content.
                # The `base.html` itself will handle its own i18n via client-side.
                # Server-side translation of `base.html` structure is done by passing `translations` to its context.

                # Decision: The individual block templates are responsible for their own translation
                # using the `translations` object passed to them.
                # So, `generated_html_for_block` should be final.
                blocks_html_parts.append(generated_html_for_block)

            except FileNotFoundError:  # This would now be an issue with Jinja's loader
                print(
                    f"Warning: Template for block {block_file_name} not found by Jinja. Skipping."
                )
            except Exception as e:
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
        """
        # This method prints errors to stdout rather than raising an IOError
        # directly to allow the build process to continue if one file fails.
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
    # Initialize Jinja2 Environment
    jinja_env = Environment(
        loader=FileSystemLoader("templates"), autoescape=True  # Enable autoescaping
    )

    # Instantiate service components with more descriptive names
    app_config_manager_instance = DefaultAppConfigManager()
    translation_provider_instance = DefaultTranslationProvider()
    # Note: JsonProtoDataLoader and InMemoryDataCache are generic.
    # We specify Message here as they will handle various protobuf message types.
    data_loader_instance = JsonProtoDataLoader[Message]()
    data_cache_instance = InMemoryDataCache[Message]()
    page_builder_instance = DefaultPageBuilder(
        translation_provider=translation_provider_instance,
        jinja_env=jinja_env,  # Pass env to PageBuilder
    )

    # Map block filenames to their specific HTML generator instances
    # Pass jinja_env to each generator
    html_generator_instances: Dict[str, HtmlBlockGenerator] = {
        "portfolio.html": PortfolioHtmlGenerator(jinja_env=jinja_env),
        "blog.html": BlogHtmlGenerator(jinja_env=jinja_env),
        "features.html": FeaturesHtmlGenerator(jinja_env=jinja_env),
        "testimonials.html": TestimonialsHtmlGenerator(jinja_env=jinja_env),
        "hero.html": HeroHtmlGenerator(jinja_env=jinja_env),
        "contact-form.html": ContactFormHtmlGenerator(jinja_env=jinja_env),
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
