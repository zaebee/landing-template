"""
Builds the index.html file from configured blocks for multiple languages.
"""

import json
import os
import sys
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union

from google.protobuf.message import Message

# Ensure the project root (and thus 'generated' directory) is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
generated_dir = os.path.join(project_root, "generated")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if generated_dir not in sys.path:
    sys.path.insert(0, generated_dir)  # Add generated to sys.path


# Protobuf imports - These MUST come AFTER sys.path manipulation
from generated.blog_post_pb2 import BlogPost  # noqa: E402
from generated.contact_form_config_pb2 import ContactFormConfig  # noqa: E402
from generated.feature_item_pb2 import FeatureItem  # noqa: E402
from generated.hero_item_pb2 import HeroItem  # noqa: E402
from generated.nav_item_pb2 import Navigation  # noqa: E402
from generated.portfolio_item_pb2 import PortfolioItem  # noqa: E402
from generated.testimonial_item_pb2 import TestimonialItem  # noqa: E402

# Type aliases
Translations = Dict[str, str]
# Define a TypeVar for generic protobuf messages
T = TypeVar("T", bound=Message)

# Import functions from the new translation module
from build_protocols.translation import (  # noqa: E402
    load_translations,
    translate_html_content,
)
# Import functions from the new data_loading module
from build_protocols.data_loading import (  # noqa: E402
    load_dynamic_data,
    load_single_item_dynamic_data,
    preload_dynamic_data,
)
# Import functions from the new html_generation module
from build_protocols.html_generation import (  # noqa: E402
    generate_blog_html,
    generate_contact_form_html,
    generate_features_html,
    generate_hero_html,
    generate_portfolio_html,
    generate_testimonials_html,
)
# Import functions from the new config_management module
from build_protocols.config_management import (  # noqa: E402
    generate_language_config,
    generate_navigation_data_for_config,
    load_app_config,
)
# Import functions from the new page_assembly module
from build_protocols.page_assembly import (  # noqa: E402
    assemble_translated_page,
    extract_base_html_parts,
)


def main() -> None:
    """
    Reads config, assembles blocks, translates, and writes new index_<lang>.html
    files.
    """
    # Load main application configuration
    app_config = load_app_config()  # Uses default "public/config.json"

    supported_langs: List[str] = app_config.get("supported_langs", ["en", "es"])
    default_lang: str = app_config.get("default_lang", "en")

    # Define the dynamic data loaders configuration
    # This could also be part of the app_config if it needs to be more dynamic
    dynamic_data_loaders_config: Dict[str, Dict[str, Any]] = {
        "portfolio.html": {
            "data_file": "data/portfolio_items.json",
            "message_type": PortfolioItem,
            "generator": generate_portfolio_html,
            "placeholder": "{{portfolio_items}}",
        },
        "blog.html": {
            "data_file": "data/blog_posts.json",
            "message_type": BlogPost,
            "generator": generate_blog_html,
            "placeholder": "{{blog_posts}}",
        },
        "features.html": {
            "data_file": "data/feature_items.json",
            "message_type": FeatureItem,
            "generator": generate_features_html,
            "placeholder": "{{feature_items}}",
        },
        "testimonials.html": {
            "data_file": "data/testimonial_items.json",
            "message_type": TestimonialItem,
            "generator": generate_testimonials_html,
            "placeholder": "{{testimonial_items}}",
            "is_list": True,
        },
        "hero.html": {
            "data_file": "data/hero_item.json",
            "message_type": HeroItem,
            "generator": generate_hero_html,
            "placeholder": "{{hero_content}}",
            "is_list": False,
        },
        "contact-form.html": {
            "data_file": "data/contact_form_config.json",
            "message_type": ContactFormConfig,
            "generator": generate_contact_form_html,
            "placeholder": "{{contact_form_attributes}}",
            "is_list": False,
        },
    }

    # Pre-load all dynamic data
    dynamic_data_cache: Dict[str, Union[List[Message], Message, None]] = {}
    preload_dynamic_data(dynamic_data_loaders_config, dynamic_data_cache)

    # Load navigation proto data
    navigation_data_file_path = app_config.get(
        "navigation_data_file", "data/navigation.json"
    )
    navigation_proto_data: Navigation | None = load_single_item_dynamic_data(
        navigation_data_file_path, Navigation
    )

    # Create a directory for generated language-specific configs
    os.makedirs("public/generated_configs", exist_ok=True)

    # Extract parts from base index.html (or other configured base file)
    # Assuming base_html_file is 'index.html' by default as per original logic
    # html_parts is a tuple: (html_start, header_content, footer_content, html_end)
    html_parts = extract_base_html_parts()

    for lang in supported_langs:
        process_language_build(
            lang=lang,
            app_config=app_config,  # Pass the loaded application config
            dynamic_data_cache=dynamic_data_cache,
            nav_proto_data=navigation_proto_data,
            html_parts=html_parts,
            dynamic_data_loaders_config=dynamic_data_loaders_config,
            default_lang=default_lang,
        )

    print("Build process complete.")


# Functions preload_dynamic_data, generate_language_config, and assemble_translated_page
# have been moved to their respective modules in build_protocols/


def process_language_build(
    lang: str,
    app_config: Dict[str, Any],  # Base application config
    dynamic_data_cache: Dict[str, Union[List[Message], Message, None]],
    nav_proto_data: Navigation | None,
    html_parts: Tuple[str, str, str, str],
    dynamic_data_loaders_config: Dict[str, Dict[str, Any]],
    default_lang: str,
) -> None:
    """
    Handles the generation of index_<lang>.html and config_<lang>.json
    for a single language.
    """
    print(f"Processing language: {lang}")
    translations = load_translations(lang)

    # 1. Generate and save language-specific JSON config
    lang_specific_config = generate_language_config(
        app_config, nav_proto_data, translations, lang
    )
    generated_config_path = f"public/generated_configs/config_{lang}.json"
    try:
        with open(generated_config_path, "w", encoding="utf-8") as f_config:
            json.dump(lang_specific_config, f_config, indent=4, ensure_ascii=False)
        print(f"Generated language-specific config: {generated_config_path}")
    except IOError as e:
        print(f"Error writing language-specific config {generated_config_path}: {e}")
        # Depending on severity, might want to exit or raise exception

    # 2. Assemble main content from blocks
    blocks_html_parts: List[str] = []
    # Use the 'blocks' list from the base app_config
    for block_file_any in app_config.get("blocks", []):
        if not isinstance(block_file_any, str):
            print(
                f"Warning: Invalid block file entry in config: {block_file_any}. "
                "Skipping."
            )
            continue
        block_file: str = block_file_any
        try:
            with open(f"blocks/{block_file}", "r", encoding="utf-8") as f_block:
                block_template_content = f_block.read()
            block_content_with_data: str

            if block_file in dynamic_data_loaders_config:
                loader_config = dynamic_data_loaders_config[block_file]
                data_items = dynamic_data_cache.get(loader_config["data_file"])

                data_items_for_gen: Union[List[Any], Message, None]
                if loader_config.get("is_list", True):
                    data_items_for_gen = data_items if data_items is not None else []
                else:
                    data_items_for_gen = data_items  # Can be None for single items

                generated_html = loader_config["generator"](
                    data_items_for_gen, translations
                )
                block_content_with_data = block_template_content.replace(
                    loader_config["placeholder"], generated_html
                )
            else:
                block_content_with_data = block_template_content

            translated_block_content = translate_html_content(
                block_content_with_data, translations
            )
            blocks_html_parts.append(translated_block_content)
        except FileNotFoundError:
            print(f"Warning: Block file blocks/{block_file} not found. Skipping.")
        except Exception as e:
            print(
                f"Error processing block {block_file} for lang {lang}: {e}. "
                "Skipping."
            )

    assembled_main_content = "\n".join(blocks_html_parts)

    # 3. Assemble the full translated page
    full_html_content = assemble_translated_page(
        lang, translations, html_parts, assembled_main_content
    )

    # 4. Write the output HTML file
    output_filename = f"index_{lang}.html"
    if lang == default_lang:
        output_filename = "index.html"

    print(f"Writing {output_filename}")
    try:
        with open(output_filename, "w", encoding="utf-8") as f_out:
            f_out.write(full_html_content)
    except IOError as e:
        print(f"Error writing file {output_filename}: {e}")


if __name__ == "__main__":
    main()
