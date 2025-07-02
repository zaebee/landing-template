"""
Builds the index.html file from configured blocks for multiple languages.
"""
import sys
import os

# Ensure the project root (and thus 'generated' directory) is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
generated_dir = os.path.join(project_root, "generated")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if generated_dir not in sys.path:
    sys.path.insert(0, generated_dir) # Add generated to sys.path

print(f"DEBUG (top): project_root: {project_root}")
print(f"DEBUG (top): generated_dir: {generated_dir}")
print(f"DEBUG (top): sys.path: {sys.path}")
if os.path.exists(generated_dir):
    print(f"DEBUG (top): Contents of generated_dir: {os.listdir(generated_dir)}")
else:
    print(f"DEBUG (top): generated_dir {generated_dir} does not exist.")
"""
# Removed debug prints from here:
# print(f"DEBUG (top): project_root: {project_root}")
# print(f"DEBUG (top): generated_dir: {generated_dir}")
# print(f"DEBUG (top): sys.path: {sys.path}")
# if os.path.exists(generated_dir):
#     print(f"DEBUG (top): Contents of generated_dir: {os.listdir(generated_dir)}")
# else:
#     print(f"DEBUG (top): generated_dir {generated_dir} does not exist.")
"""
import json
from typing import Any, Dict, List, Type, TypeVar, Union

from bs4 import BeautifulSoup
from bs4.element import Tag  # Removed _RawAttributeValues
from google.protobuf import json_format
from google.protobuf.message import Message

# This is where the error occurs
from generated.blog_post_pb2 import BlogPost
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import HeroItem  # Added
from generated.nav_item_pb2 import Navigation  # Added
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem

# Ensure the project root (and thus 'generated' directory) is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
generated_dir = os.path.join(project_root, "generated")

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if generated_dir not in sys.path:
    sys.path.insert(0, generated_dir) # Add generated to sys.path

print(f"DEBUG: project_root: {project_root}")
print(f"DEBUG: generated_dir: {generated_dir}")
print(f"DEBUG: sys.path: {sys.path}")
import os
print(f"DEBUG: Contents of generated_dir: {os.listdir(generated_dir)}")


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
        description: str = translations.get(item.details.description.key, item.details.description.key)
        alt_text: str = translations.get(item.image.alt_text.key, "Portfolio image") # Default alt

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
        description: str = translations.get(item.content.description.key, item.content.description.key)
        html_output.append(
            f"""
        <div class="feature-item">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """
        )
    return "\n".join(html_output)


def generate_hero_html(item: HeroItem | None, translations: Translations) -> str:
    """Generates HTML for the hero section."""
    if not item:
        return "<!-- Hero data not found -->"

    # HeroItem: title (I18nString), subtitle (I18nString), cta (CTA)
    # CTA: text (I18nString), link (string)
    title = translations.get(item.title.key, item.title.key)
    subtitle = translations.get(item.subtitle.key, item.subtitle.key)
    cta_text = translations.get(item.cta.text.key, item.cta.text.key)

    return f"""
    <h1>{title}</h1>
    <p>{subtitle}</p>
    <a href="{item.cta.link}" class="cta-button">{cta_text}</a>
    """


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
            <a href="{post.cta.link}" class="read-more">{cta_text}</a>
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
        nav_items_for_config.append({"label_i18n_key": item.label.key, "label": label, "href": item.href})
    return nav_items_for_config


def main() -> None:
    """
    Reads config, assembles blocks, translates, and writes new index_<lang>.html
    files.
    """
    supported_langs: List[str] = ["en", "es"]
    default_lang: str = "en"

    # Define the dynamic data loaders configuration
    dynamic_data_loaders: Dict[str, Dict[str, Any]] = {
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
            "is_list": True,  # Indicates data is a list of items
        },
        "hero.html": {
            "data_file": "data/hero_item.json",
            "message_type": HeroItem,
            "generator": generate_hero_html,
            "placeholder": "{{hero_content}}",  # Correct placeholder
            "is_list": False,  # Indicates data is a single item
        },
    }

    # Pre-load all dynamic data once
    loaded_data_cache: Dict[str, Union[List[Message], Message, None]] = (
        {}
    )  # Allow single Message or None

    # Load navigation data first as it might be needed by config processing
    # Assuming nav_data_file path will be added to config.json or hardcoded for now
    # For now, let's assume a fixed path for navigation data
    # and that it's loaded for each language variant if needed, or once if translations applied later
    # The plan is to put navigation data into config.json, so we load it before processing languages.

    raw_config: Dict[str, Any]
    try:
        with open("public/config.json", "r", encoding="utf-8") as f:
            raw_config = json.load(f)
    except FileNotFoundError:
        print("Error: public/config.json not found. Exiting.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from public/config.json. Exiting.")
        sys.exit(1)

    # Load navigation proto data
    # This assumes a single navigation.json for all languages, with labels being i18n keys
    navigation_data_file_path = raw_config.get("navigation_data_file", "data/navigation.json")
    navigation_proto_data: Navigation | None = load_single_item_dynamic_data(
        navigation_data_file_path, Navigation
    )

    # TODO: use `block_name, config_item` to put into dynamic place.
    for _, config_item in dynamic_data_loaders.items():
        data_file = config_item["data_file"]
        message_type = config_item["message_type"]
        is_list = config_item.get("is_list", True)  # Default to True if not specified

        if data_file not in loaded_data_cache:
            if is_list:
                loaded_data_cache[data_file] = load_dynamic_data(
                    data_file, message_type
                )
            else:
                loaded_data_cache[data_file] = load_single_item_dynamic_data(
                    data_file, message_type
                )

    # The main config object will be language-specific if navigation is injected per language
    # For now, let's keep one main 'raw_config' and adapt it per language if necessary
    # The objective is to have `build.py` generate the navigation array for `config.json`
    # This means the `config.json` written to disk or used by JS should have this.
    # Let's refine this: `build.py` will *not* rewrite `public/config.json`.
    # Instead, it will make the navigation data available for the JavaScript running in `index.html`.
    # The simplest way is to embed it as a JS variable or make `generateNavigation()` fetch a new file.
    # Plan step 4. says "Modify `build.py` to populate the `navigation` array within `public/config.json`"
    # This is tricky as `build.py` generates `index_LANG.html`.
    # Let's assume `build.py` will create a *new* config file for each language, e.g. `public/config_en.json`
    # which `index_en.html` will load.

    # Original config loaded into raw_config
    # We will create language-specific configs based on this raw_config
    # and add the translated navigation items to them.

    # The existing config structure in `public/config.json` will be used as a base.
    # `build.py` will generate language-specific versions of this config if needed,
    # or directly embed the navigation data if that's simpler.

    # Let's stick to the plan of `build.py` making nav data available to the *existing* JS.
    # The existing JS (`generateNavigation` in `index.html`) fetches `public/config.json`.
    # So, `build.py` needs to create/update `public/config_en.json`, `public/config_es.json` etc.
    # These files will be copies of the original `public/config.json` but with an added `navigation` array.

    # Create a directory for generated language-specific configs if it doesn't exist
    os.makedirs("public/generated_configs", exist_ok=True)


    config: Dict[str, Any] # This will be used inside the loop for language-specific config
    try:
        # This is the base config, will be augmented with navigation for each lang
        with open("public/config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Exiting.")
        sys.exit(1)  # Exit if config is essential
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from config.json. Exiting.")
        sys.exit(1)  # Exit if config is essential

    portfolio_data_untyped: List[Message] = load_dynamic_data(
        "data/portfolio_items.json", PortfolioItem
    )
    portfolio_data: List[PortfolioItem] = [
        item for item in portfolio_data_untyped if isinstance(item, PortfolioItem)
    ]

    blog_data_untyped: List[Message] = load_dynamic_data(
        "data/blog_posts.json", BlogPost
    )
    blog_data: List[BlogPost] = [
        item for item in blog_data_untyped if isinstance(item, BlogPost)
    ]

    feature_data_untyped: List[Message] = load_dynamic_data(
        "data/feature_items.json", FeatureItem
    )
    feature_data: List[FeatureItem] = [
        item for item in feature_data_untyped if isinstance(item, FeatureItem)
    ]

    testimonial_data_untyped: List[Message] = load_dynamic_data(
        "data/testimonial_items.json", TestimonialItem
    )
    # The individual data lists (portfolio_data, blog_data, etc.) are no longer needed here,
    # as data will be fetched from loaded_data_cache within the loop.

    base_content: str
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            base_content = f.read()
    except FileNotFoundError:
        print("Error: Base index.html not found. Exiting.")
        sys.exit(1)  # Exit if base template is essential

    base_soup: BeautifulSoup = BeautifulSoup(base_content, "html.parser")

    header_content: str = ""
    body_tag = base_soup.body
    if body_tag and isinstance(body_tag, Tag):
        main_tag = body_tag.find("main")
        if main_tag and isinstance(main_tag, Tag):
            for element in main_tag.previous_siblings:
                header_content += str(element)
        else:
            print(
                "Warning: <main> tag not found in base index.html. "
                "Header might be incomplete."
            )
    else:
        print(
            "Warning: <body> tag not found in base index.html. "
            "Header might be empty."
        )

    footer_content: str = ""
    if body_tag and isinstance(body_tag, Tag):
        main_tag = body_tag.find("main")
        if main_tag and isinstance(main_tag, Tag):
            for element in main_tag.find_next_siblings():
                footer_content += str(element)
        else:
            print(
                "Warning: <main> tag not found in base index.html. "
                "Footer might be incomplete."
            )
    else:
        print(
            "Warning: <body> tag not found in base index.html. "
            "Footer might be empty."
        )

    html_tag = base_soup.find("html")
    html_start: str
    if html_tag and isinstance(html_tag, Tag):
        html_parts = str(html_tag).split("<body>", 1)
        if len(html_parts) > 1:
            html_start = html_parts[0] + "<body>\n"
        else:
            html_start = html_parts[0] + "\n<body>\n"
    else:
        print("Warning: <html> tag not found. Using default HTML structure.")
        html_start = (
            '<!DOCTYPE html>\n<html><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, '
            'initial-scale=1.0"><title>Page</title></head><body>\n'
        )
    html_end: str = "\n</body>\n</html>"

    for lang in supported_langs:
        print(f"Processing language: {lang}")
        translations: Translations = load_translations(lang)

        # Generate language-specific config with navigation
        lang_config = raw_config.copy() # Start with a copy of the base config
        lang_config["navigation"] = generate_navigation_data_for_config(navigation_proto_data, translations)

        # Save the language-specific config
        # The JS in index.html will need to be updated to load config_en.json instead of config.json
        # Or, if we are generating index_en.html, index_es.html, we can change the script path in those files.
        # Let's assume for now the script in the generated HTML will point to the correct lang-specific config.
        generated_config_path = f"public/generated_configs/config_{lang}.json"
        try:
            with open(generated_config_path, "w", encoding="utf-8") as f_config:
                json.dump(lang_config, f_config, indent=4, ensure_ascii=False)
            print(f"Generated language-specific config: {generated_config_path}")
        except IOError as e:
            print(f"Error writing language-specific config {generated_config_path}: {e}")


        blocks_html_parts: List[str] = []
        # Use raw_config here for block list, as lang_config is for JS side.
        for block_file_any in raw_config.get("blocks", []):
            if not isinstance(block_file_any, str):
                print(
                    f"Warning: Invalid block file entry in config: {block_file_any}. "
                    "Skipping."
                )
                continue
            block_file: str = block_file_any
            try:
                with open(f"blocks/{block_file}", "r", encoding="utf-8") as f:
                    block_template_content: str = f.read()
                    block_content_with_data: str

                    if block_file in dynamic_data_loaders:
                        loader_config = dynamic_data_loaders[block_file]
                        # Fetch pre-loaded data from cache
                        # Ensure items are correctly typed for the generator function
                        # The list from loaded_data_cache might be List[Message],
                        # so we filter/cast if necessary or ensure generators accept List[Message]
                        # and handle type checking internally if strict typing is desired.
                        # For simplicity, we'll assume generators can handle List[Message]
                        # or that the types are compatible enough.
                        # A more robust solution might involve type checking here or ensuring
                        # generators are flexible.
                        data_items = loaded_data_cache.get(
                            loader_config["data_file"], []
                        )

                        # Ensure the data passed to the generator is correctly typed.
                        # This step is crucial if generators expect specific protobuf types.
                        # Example: typed_data_items = [item for item in data_items if isinstance(item, loader_config["message_type"])]
                        # However, load_dynamic_data already returns List[T] where T is the message_type.
                        # So, data_items from loaded_data_cache should already be correctly typed.

                        generated_html: str = loader_config["generator"](
                            data_items, translations  # Pass the correctly typed list
                        )
                        block_content_with_data = block_template_content.replace(
                            loader_config["placeholder"], generated_html
                        )
                    else:
                        # Static block, no dynamic data injection needed beyond i18n
                        block_content_with_data = block_template_content

                    translated_block_content: str = translate_html_content(
                        block_content_with_data, translations
                    )
                    blocks_html_parts.append(translated_block_content)
            except FileNotFoundError:
                print(f"Warning: Block file blocks/{block_file} not found. Skipping.")
                continue
            except Exception as e:
                print(f"Error processing block {block_file}: {e}. Skipping.")
                continue

        assembled_main_content: str = "\n".join(blocks_html_parts)

        # Translate header and footer sections if they have data-i18n tags
        # For this, we'll re-parse the original header and footer parts of index.html
        # and apply translations to them.

        # Create a full HTML document string for this language
        # The header and footer parts are taken from the original index.html,
        # and then translated. The main content is built from translated blocks.

        # Translate navigation and other header elements
        # that are part of the main index.html template
        translated_header_soup = BeautifulSoup(header_content, "html.parser")
        for element in translated_header_soup.find_all(attrs={"data-i18n": True}):
            if isinstance(element, Tag):
                key = get_attribute_value_as_str(element, "data-i18n")
                if key and key in translations:
                    element.string = translations[key]

        # Translate footer elements
        translated_footer_soup = BeautifulSoup(footer_content, "html.parser")
        for element in translated_footer_soup.find_all(attrs={"data-i18n": True}):
            if isinstance(element, Tag):
                key = get_attribute_value_as_str(element, "data-i18n")
                if key and key in translations:
                    element.string = translations[key]

        current_html_start = html_start
        temp_soup = BeautifulSoup(current_html_start, "html.parser")
        html_tag_from_temp = temp_soup.find("html")

        if html_tag_from_temp and isinstance(html_tag_from_temp, Tag):
            html_tag_from_temp["lang"] = lang

            reconstructed_start_parts = str(temp_soup).split("<body>", 1)
            if len(reconstructed_start_parts) > 1:
                current_html_start = reconstructed_start_parts[0] + "<body>\n"
            else:  # If <body> wasn't in the original html_start or temp_soup string
                current_html_start = str(temp_soup)  # Use the whole soup string
        else:
            # Fallback if no <html> tag in current_html_start (e.g. it's just a doctype)
            # Attempt to inject lang into <html> tag if present, otherwise prepend
            # new html tag
            if "<html" in current_html_start.lower():
                current_html_start = current_html_start.lower().replace(
                    "<html", f'<html lang="{lang}"', 1
                )
            else:
                current_html_start = (
                    f'<!DOCTYPE html>\n<html lang="{lang}">\n' + current_html_start
                )

        output_filename: str = f"index_{lang}.html"
        if lang == default_lang:
            output_filename = "index.html"

        print(f"Writing {output_filename}")
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(current_html_start)
                f.write(str(translated_header_soup))
                f.write("<main>\n")
                f.write(assembled_main_content)
                f.write("\n</main>")
                f.write(str(translated_footer_soup))
                f.write(html_end)
        except IOError as e:
            print(f"Error writing file {output_filename}: {e}")

    print("Build process complete.")


if __name__ == "__main__":
    main()
