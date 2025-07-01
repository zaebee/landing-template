"""
Builds the index.html file from configured blocks for multiple languages.
"""

import json
import os
import sys
from typing import Any, Dict, List, Type, TypeVar, Union

from bs4 import BeautifulSoup
from bs4.element import Tag  # Removed _RawAttributeValues
from google.protobuf import json_format
from google.protobuf.message import Message

from generated.blog_post_pb2 import BlogPost
from generated.portfolio_item_pb2 import PortfolioItem
from generated.feature_item_pb2 import FeatureItem
from generated.testimonial_item_pb2 import TestimonialItem

# Ensure the project root (and thus 'generated' directory) is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


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


def generate_portfolio_html(
    items: List[PortfolioItem], translations: Translations
) -> str:
    """Generates HTML for portfolio items."""
    html_output: List[str] = []
    for item in items:
        title: str = translations.get(item.title_i18n_key, item.title_i18n_key)
        description: str = translations.get(item.desc_i18n_key, item.desc_i18n_key)
        html_output.append(
            f"""
        <div class="portfolio-item">
            <img src="{item.img_src}" alt="{item.img_alt}">
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
        text: str = translations.get(item.text_i18n_key, item.text_i18n_key)
        author: str = translations.get(item.author_i18n_key, item.author_i18n_key)
        img_alt: str = translations.get(
            item.img_alt_i18n_key, "User photo"
        )  # Default alt text
        html_output.append(
            f"""
        <div class="testimonial-item">
            <img src="{item.img_src}" alt="{img_alt}">
            <p>{text}</p>
            <h4>{author}</h4>
        </div>
        """
        )
    return "\n".join(html_output)


def generate_features_html(
    items: List[FeatureItem], translations: Translations
) -> str:
    """Generates HTML for feature items."""
    html_output: List[str] = []
    for item in items:
        title: str = translations.get(item.title_i18n_key, item.title_i18n_key)
        description: str = translations.get(item.desc_i18n_key, item.desc_i18n_key)
        # Note: If FeatureItem had icon_class or img_src, they would be used here.
        html_output.append(
            f"""
        <div class="feature-item">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """
        )
    return "\n".join(html_output)


def generate_blog_html(posts: List[BlogPost], translations: Translations) -> str:
    """Generates HTML for blog posts."""
    html_output: List[str] = []
    for post in posts:
        title: str = translations.get(post.title_i18n_key, post.title_i18n_key)
        excerpt: str = translations.get(post.excerpt_i18n_key, post.excerpt_i18n_key)
        cta: str = translations.get(post.cta_i18n_key, post.cta_i18n_key)
        html_output.append(
            f"""
        <div class="blog-item">
            <h3>{title}</h3>
            <p>{excerpt}</p>
            <a href="{post.link}" class="read-more">{cta}</a>
        </div>
        """
        )
    return "\n".join(html_output)


def main() -> None:
    """
    Reads config, assembles blocks, translates, and writes new index_<lang>.html
    files.
    """
    supported_langs: List[str] = ["en", "es"]
    default_lang: str = "en"

    config: Dict[str, Any]
    try:
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
    testimonial_data: List[TestimonialItem] = [
        item
        for item in testimonial_data_untyped
        if isinstance(item, TestimonialItem)
    ]

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

        blocks_html_parts: List[str] = []
        for block_file_any in config.get("blocks", []):
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

                    if block_file == "portfolio.html":
                        portfolio_html: str = generate_portfolio_html(
                            portfolio_data, translations
                        )
                        block_content_with_data = block_template_content.replace(
                            "{{portfolio_items}}", portfolio_html
                        )
                    elif block_file == "blog.html":
                        blog_html: str = generate_blog_html(blog_data, translations)
                        block_content_with_data = block_template_content.replace(
                            "{{blog_posts}}", blog_html
                        )
                    elif block_file == "features.html":
                        features_html: str = generate_features_html(
                            feature_data, translations
                        )
                        block_content_with_data = block_template_content.replace(
                            "{{feature_items}}", features_html
                        )
                    elif block_file == "testimonials.html":
                        testimonials_html: str = generate_testimonials_html(
                            testimonial_data, translations
                        )
                        block_content_with_data = block_template_content.replace(
                            "{{testimonial_items}}", testimonials_html
                        )
                    else:
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
