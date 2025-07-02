"""
Builds the index.html file from configured blocks for multiple languages.
"""

import json
import os
import random  # Moved to top
import re  # Moved to top
import sys
from typing import Any, Dict, List, Tuple, Type, TypeVar, Union

from bs4 import BeautifulSoup
from bs4.element import Tag
from google.protobuf import json_format
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


def get_attribute_value_as_str(element: Tag, attr_name: str) -> str:
    """Safely retrieves an attribute value as a string.
    BeautifulSoup can return a list if an attribute is multi-valued,
    but for 'data-i18n', we expect a single string.
    """
    attr_val: Union[str, List[str], None] = element.get(attr_name)  # Changed type hint
    if isinstance(attr_val, list):
        return str(attr_val[0]) if attr_val else ""
    elif attr_val is not None:
        return str(attr_val)
    return ""


def load_translations(lang: str) -> Translations:
    """Loads translation strings for a given language."""
    try:
        with open(f"public/locales/{lang}.json", "r", encoding="utf-8") as f:
            translations: Translations = json.load(f)
            return translations
    except FileNotFoundError:
        print(f"Warning: Translation file for '{lang}' not found. Using default text.")
        return {}
    except json.JSONDecodeError:
        print(
            f"Warning: Could not decode JSON from locales/{lang}.json. "
            "Using default text."
        )
        return {}


def translate_html_content(html_content: str, translations: Translations) -> str:
    """Translates data-i18n tagged elements in HTML content."""
    if not translations:
        return html_content

    soup = BeautifulSoup(html_content, "html.parser")
    for element in soup.find_all(attrs={"data-i18n": True}):
        if isinstance(element, Tag):  # Ensure element is a Tag
            key: str = get_attribute_value_as_str(element, "data-i18n")
            if key and key in translations:  # ensure key is not empty
                element.string = translations[key]
            # Avoid replacing placeholders like {{...}} if key is not found
            elif (
                key
                and "{{" not in element.decode_contents(formatter="html")
                and "}}" not in element.decode_contents(formatter="html")
            ):
                print(
                    f"Warning: Translation key '{key}' not found in translations for "
                    f"current language. Element: <{element.name} "
                    f"data-i18n='{key}'>...</{element.name}>"
                )
    return str(soup)


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


def generate_portfolio_html(
    items: List[PortfolioItem], translations: Translations
) -> str:
    """Generates HTML for portfolio items."""
    html_output: List[str] = []
    for item in items:
        # PortfolioItem: id, image (Image), details (TitledBlock)
        # Image: src, alt_text (I18nString)
        # TitledBlock: title (I18nString), description (I18nString)
        # I18nString: key
        title: str = translations.get(item.details.title.key, item.details.title.key)
        description: str = translations.get(
            item.details.description.key, item.details.description.key
        )
        alt_text: str = translations.get(
            item.image.alt_text.key, "Portfolio image"
        )  # Default alt

        html_output.append(
            f"""
        <div class="portfolio-item">
            <img src="{item.image.src}" alt="{alt_text}">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """
        )
    return "\n".join(html_output)


def generate_testimonials_html(
    items: List[TestimonialItem], translations: Translations
) -> str:
    """Generates HTML for testimonial items."""
    html_output: List[str] = []
    for item in items:
        # TestimonialItem: text (I18nString), author (I18nString), author_image (Image)
        text: str = translations.get(item.text.key, item.text.key)
        author: str = translations.get(item.author.key, item.author.key)
        img_alt: str = translations.get(
            item.author_image.alt_text.key, "User photo"
        )  # Default alt text
        html_output.append(
            f"""
        <div class="testimonial-item">
            <img src="{item.author_image.src}" alt="{img_alt}">
            <p>{text}</p>
            <h4>{author}</h4>
        </div>
        """
        )
    return "\n".join(html_output)


def generate_features_html(items: List[FeatureItem], translations: Translations) -> str:
    """Generates HTML for feature items."""
    html_output: List[str] = []
    for item in items:
        # FeatureItem: content (TitledBlock)
        # TitledBlock: title (I18nString), description (I18nString)
        title: str = translations.get(item.content.title.key, item.content.title.key)
        description: str = translations.get(
            item.content.description.key, item.content.description.key
        )
        html_output.append(
            f"""
        <div class="feature-item">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """
        )
    return "\n".join(html_output)


# import random  # Moved to top


def generate_hero_html(hero_data: HeroItem | None, translations: Translations) -> str:
    """Generates HTML for the hero section, selecting a variation."""
    if not hero_data or not hero_data.variations:
        return "<!-- Hero data not found or no variations -->"

    selected_variation = None
    if hero_data.variations:
        # Simple random selection for A/B testing.
        # More sophisticated logic could be added here (e.g., based on build count,
        # environment variable)
        selected_variation = random.choice(hero_data.variations)

    # Fallback to default if random selection somehow fails or
    # if specific default is needed
    if not selected_variation:
        default_id = hero_data.default_variation_id
        for var in hero_data.variations:
            if var.variation_id == default_id:
                selected_variation = var
                break
        if not selected_variation:  # If default_id not found, pick first
            selected_variation = hero_data.variations[0]

    if not selected_variation:  # Should not happen if variations exist
        return "<!-- Could not select a hero variation -->"

    # HeroItemContent: title (I18nString), subtitle (I18nString), cta (CTA)
    title = translations.get(selected_variation.title.key, selected_variation.title.key)
    subtitle = translations.get(
        selected_variation.subtitle.key, selected_variation.subtitle.key
    )
    cta_text = translations.get(
        selected_variation.cta.text.key, selected_variation.cta.text.key
    )

    return f"""
    <h1>{title}</h1>
    <p>{subtitle}</p>
    <a href="{selected_variation.cta.uri}" class="cta-button">{cta_text}</a>
    <!-- Selected variation: {selected_variation.variation_id} -->
    """


def generate_contact_form_html(
    config: ContactFormConfig | None, translations: Translations
) -> str:
    """
    Generates HTML for the contact form, including data attributes for AJAX submission.
    The actual form fields are expected to be in the block template.
    This function primarily injects configuration.
    """
    if not config:
        return "<!-- Contact form configuration not found -->"

    # These will be used by the client-side JavaScript
    return (
        f'data-form-action-url="{config.form_action_uri}"\n'
        f'    data-success-message="{translations.get(config.success_message_key, "Message sent!")}"\n'  # noqa: E501
        f'    data-error-message="{translations.get(config.error_message_key, "Error sending message.")}"'  # noqa: E501
    )


def generate_blog_html(posts: List[BlogPost], translations: Translations) -> str:
    """Generates HTML for blog posts."""
    html_output: List[str] = []
    for post in posts:
        # BlogPost: id, title (I18nString), excerpt (I18nString), cta (CTA)
        title: str = translations.get(post.title.key, post.title.key)
        excerpt: str = translations.get(post.excerpt.key, post.excerpt.key)
        cta_text: str = translations.get(post.cta.text.key, post.cta.text.key)
        html_output.append(
            f"""
        <div class="blog-item">
            <h3>{title}</h3>
            <p>{excerpt}</p>
            <a href="{post.cta.uri}" class="read-more">{cta_text}</a>
        </div>
        """
        )
    return "\n".join(html_output)


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


def extract_base_html_parts(
    base_html_file: str = "index.html",
) -> Tuple[str, str, str, str]:
    """
    Extracts key structural parts from the base HTML file.

    Returns:
        A tuple containing:
        - html_start: The HTML content up to and including the opening <body> tag.
        - header_content: The content of the <header> or elements before <main>.
        - footer_content: The content of the <footer> or elements after <main>.
        - html_end: The closing </body> and </html> tags.
    """
    try:
        with open(base_html_file, "r", encoding="utf-8") as f:
            base_content = f.read()
    except FileNotFoundError:
        print(f"Error: Base HTML file '{base_html_file}' not found. Exiting.")
        sys.exit(1)

    soup = BeautifulSoup(base_content, "html.parser")

    header_content_parts: List[str] = []
    footer_content_parts: List[str] = []

    body_tag = soup.body
    if body_tag and isinstance(body_tag, Tag):
        main_tag = body_tag.find("main")
        if main_tag and isinstance(main_tag, Tag):
            # Capture elements before <main> as header content
            for element in main_tag.previous_siblings:
                header_content_parts.append(str(element))
            # Capture elements after <main> as footer content
            for element in main_tag.find_next_siblings():
                footer_content_parts.append(str(element))
        else:
            print(
                f"Warning: <main> tag not found in {base_html_file}. "
                "Header/footer content might be incomplete."
            )
            # Fallback: consider all direct children of <body> as potential
            # header/footer if no <main>
            # This part can be refined based on expected structure if <main> is missing
    else:
        print(
            f"Warning: <body> tag not found in {base_html_file}. "
            "Header/footer content might be empty."
        )

    html_tag = soup.find("html")
    html_start: str
    if html_tag and isinstance(html_tag, Tag):
        # Attempt to reconstruct the part of HTML before <body>, keeping attributes
        html_str = str(html_tag)
        body_open_tag_index = html_str.lower().find("<body")
        if body_open_tag_index != -1:
            # Find where the opening body tag actually ends
            body_tag_end_index = html_str.find(">", body_open_tag_index) + 1
            html_start = html_str[:body_tag_end_index] + "\n"
        else:
            # Fallback if body tag is not found as expected
            html_start = str(soup.find("head")) if soup.head else ""  # Or more robust
            if not html_start:  # Minimal valid start
                html_start = (
                    '<!DOCTYPE html>\n<html><head><meta charset="UTF-8">'
                    '<meta name="viewport" content="width=device-width, '
                    'initial-scale=1.0"><title>Page</title></head><body>\n'
                )
    else:
        print(
            f"Warning: <html> tag not found in {base_html_file}. "
            "Using default HTML structure."
        )
        html_start = (
            '<!DOCTYPE html>\n<html><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, '
            'initial-scale=1.0"><title>Page</title></head><body>\n'
        )

    html_end: str = "\n</body>\n</html>"  # Standard closing tags

    return (
        html_start,
        "".join(header_content_parts),
        "".join(footer_content_parts),
        html_end,
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


def preload_dynamic_data(
    loaders_config: Dict[str, Dict[str, Any]],
    cache: Dict[str, Union[List[Message], Message, None]],
) -> None:
    """Pre-loads dynamic data from JSON files into a cache."""
    for _, config_item in loaders_config.items():
        data_file = config_item["data_file"]
        message_type = config_item["message_type"]
        is_list = config_item.get("is_list", True)

        if data_file not in cache:
            if is_list:
                cache[data_file] = load_dynamic_data(data_file, message_type)
            else:
                cache[data_file] = load_single_item_dynamic_data(
                    data_file, message_type
                )


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


def assemble_translated_page(  # pylint: disable=too-many-locals
    lang: str,
    translations: Translations,
    html_parts: Tuple[str, str, str, str],
    assembled_main_content: str,
) -> str:
    """
    Assembles the full HTML page for a given language.

    This includes:
    - Translating i18n elements in the header and footer.
    - Setting the 'lang' attribute on the <html> tag.
    - Combining the HTML start, translated header, assembled main content,
      translated footer, and HTML end.
    """
    html_start, header_content, footer_content, html_end = html_parts

    # Translate header content
    translated_header_soup = BeautifulSoup(header_content, "html.parser")
    for element in translated_header_soup.find_all(attrs={"data-i18n": True}):
        if isinstance(element, Tag):
            key = get_attribute_value_as_str(element, "data-i18n")
            if key and key in translations:
                element.string = translations[key]

    translated_footer_soup = BeautifulSoup(footer_content, "html.parser")
    for element in translated_footer_soup.find_all(attrs={"data-i18n": True}):
        if isinstance(element, Tag):
            key = get_attribute_value_as_str(element, "data-i18n")
            if key and key in translations:
                element.string = translations[key]

    # Set language attribute in HTML tag
    current_html_start = html_start
    temp_soup = BeautifulSoup(current_html_start, "html.parser")
    html_tag_from_temp = temp_soup.find("html")

    if html_tag_from_temp and isinstance(html_tag_from_temp, Tag):
        html_tag_from_temp["lang"] = lang
        reconstructed_start_parts = str(temp_soup).split("<body>", 1)
        if len(reconstructed_start_parts) > 1:
            current_html_start = reconstructed_start_parts[0] + "<body>\n"
        else:  # Fallback if structure is unexpected (e.g. no body in html_start)
            current_html_start = str(temp_soup)
    else:  # Fallback if no <html> tag found in html_start
        if "<html" in current_html_start.lower():
            # Attempt to replace <html ...> with <html lang="lang" ...>
            # This is a simplified approach;
            # a more robust parser might be needed for complex cases
            # import re # Moved to top
            current_html_start = re.sub(
                r"<html(\s*[^>]*)>",
                f'<html lang="{lang}"\\1>',
                current_html_start,
                count=1,
                flags=re.IGNORECASE,
            )
        else:  # Prepend if no html tag at all
            current_html_start = (
                f'<!DOCTYPE html>\n<html lang="{lang}">\n' + current_html_start
            )

    # Assemble the full page
    page_parts = [
        current_html_start,
        str(translated_header_soup),
        "<main>\n",
        assembled_main_content,
        "\n</main>",
        str(translated_footer_soup),
        html_end,
    ]
    return "".join(page_parts)


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
