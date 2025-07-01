"""
Builds the index.html file from configured blocks for multiple languages.
"""

import json
import os
import sys

from bs4 import BeautifulSoup
from google.protobuf import json_format

from generated.blog_post_pb2 import BlogPost
from generated.portfolio_item_pb2 import PortfolioItem

# Ensure the project root (and thus 'generated' directory) is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def load_translations(lang):
    """Loads translation strings for a given language."""
    try:
        with open(f"public/locales/{lang}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Translation file for '{lang}' not found. Using default text.")
        return {}


def translate_html_content(html_content, translations):
    """Translates data-i18n tagged elements in HTML content."""
    if not translations:
        return html_content

    soup = BeautifulSoup(html_content, "html.parser")
    for element in soup.find_all(attrs={"data-i18n": True}):
        key = element["data-i18n"]
        if key in translations:
            element.string = translations[key]
        elif (
            "{{" not in element.decode_contents()
            and "}}" not in element.decode_contents()
        ):  # Avoid replacing placeholders
            print(
                f"Warning: Translation key '{key}' not found in translations for "
                f"current language. Element: <{element.name} "
                f"data-i18n='{key}'>...</{element.name}>"
            )
    return str(soup)


def load_dynamic_data(data_file_path, message_type):
    """
    Loads dynamic data from a JSON file and parses it into a list of protobuf
    messages.
    """
    items = []
    try:
        with open(data_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
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


def generate_portfolio_html(items: list[PortfolioItem], translations):
    """Generates HTML for portfolio items."""
    html_output = []
    for item in items:
        title = translations.get(item.title_i18n_key, item.title_i18n_key)
        description = translations.get(item.desc_i18n_key, item.desc_i18n_key)
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


def generate_blog_html(posts: list[BlogPost], translations):
    """Generates HTML for blog posts."""
    html_output = []
    for post in posts:
        title = translations.get(post.title_i18n_key, post.title_i18n_key)
        excerpt = translations.get(post.excerpt_i18n_key, post.excerpt_i18n_key)
        cta = translations.get(post.cta_i18n_key, post.cta_i18n_key)
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


def main():
    """
    Reads config, assembles blocks, translates, and writes new index_<lang>.html
    files.
    """
    # Define supported languages (could also be read from a config file)
    supported_langs = ["en", "es"]
    default_lang = "en"

    # Read the main configuration file
    with open("public/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    # Load dynamic data using protobuf
    dynamic_data_loaders = {
        "portfolio.html": {
            "loader": load_dynamic_data,
            "args": ["data/portfolio_items.json", PortfolioItem],
            "generator": generate_portfolio_html,
            "placeholder": "{{portfolio_items}}",
        },
        "blog.html": {
            "loader": load_dynamic_data,
            "args": ["data/blog_posts.json", BlogPost],
            "generator": generate_blog_html,
            "placeholder": "{{blog_posts}}",
        },
    }

    loaded_dynamic_data = {}
    # Use a different variable name here to avoid shadowing the main 'config' object
    for block_name, data_loader_config in dynamic_data_loaders.items():
        loaded_dynamic_data[block_name] = data_loader_config["loader"](*data_loader_config["args"])

    # Read the base index.html structure (header and footer)
    # We use the existing index.html as a template for the overall page structure
    # but will replace its content with translated blocks.
    with open("index.html", "r", encoding="utf-8") as f:
        base_content = f.read()
        base_soup = BeautifulSoup(base_content, "html.parser")

        # Extract header (everything before <main>)
        header_content = ""
        for element in base_soup.body.find("main").previous_siblings:
            header_content += str(element)

        # Extract footer (everything after </main>)
        footer_content = ""
        for element in base_soup.body.find("main").find_next_siblings():
            footer_content += str(element)

        # Get the outer HTML structure including <html>, <head>, and opening <body> tag
        # and closing </body>, </html> tags
        html_start = str(base_soup.find("html")).split("<body>")[0] + "<body>\n"
        html_end = "\n</body>\n</html>"

    for lang in supported_langs:
        print(f"Processing language: {lang}")
        translations = load_translations(lang)

        # Assemble the blocks
        blocks_html_parts = []
        for block_file in config["blocks"]:
            try:
                with open(f"blocks/{block_file}", "r", encoding="utf-8") as f:
                    block_template_content = f.read()

                    # Inject dynamic content before translation
                    block_content_with_data = block_template_content
                    if block_file in dynamic_data_loaders:
                        data_config = dynamic_data_loaders[block_file]
                        placeholder = data_config["placeholder"]
                        if placeholder in block_template_content:
                            items = loaded_dynamic_data[block_file]
                            generated_html = data_config["generator"](items, translations)
                            block_content_with_data = block_template_content.replace(
                                placeholder, generated_html
                            )
                        else:
                            print(f"Warning: Placeholder '{placeholder}' not found in {block_file}")
                    # No 'else' needed here as block_content_with_data is already block_template_content

                    # Blocks are translated individually after dynamic data injection
                    translated_block_content = translate_html_content(
                        block_content_with_data, translations
                    )
                    blocks_html_parts.append(translated_block_content)
            except FileNotFoundError:
                print(f"Warning: Block file {block_file} not found. Skipping.")
                continue

        assembled_main_content = "\n".join(blocks_html_parts)

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
            key = element["data-i18n"]
            if key in translations:
                element.string = translations[key]

        # Translate footer elements
        translated_footer_soup = BeautifulSoup(footer_content, "html.parser")
        for element in translated_footer_soup.find_all(attrs={"data-i18n": True}):
            key = element["data-i18n"]
            if key in translations:
                element.string = translations[key]

        # Construct the final HTML for the current language
        # Ensure the html tag has the correct lang attribute
        # Remove "<body>\n" from html_start for parsing just the head part
        final_html_soup = BeautifulSoup(html_start[:-7], "html.parser")
        final_html_soup.html["lang"] = lang

        # Reconstruct the start of the HTML document correctly
        html_head_part = str(final_html_soup).split("</head>")[0]
        final_html_start = f"{html_head_part}</head>\n<body>\n"

        output_filename = f"index_{lang}.html"
        if lang == default_lang:
            output_filename = "index.html"  # The default language saves as index.html

        print(f"Writing {output_filename}")
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(final_html_start)  # html, head, opening body
            f.write(str(translated_header_soup))  # header content (nav, etc.)
            f.write("<main>\n")
            f.write(assembled_main_content)  # assembled and translated blocks
            f.write("\n</main>")
            f.write(str(translated_footer_soup))  # footer content
            f.write(html_end)  # closing body, html

    print("Build process complete.")


if __name__ == "__main__":
    main()
