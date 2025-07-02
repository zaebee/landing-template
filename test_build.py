"""
Unit tests for the static site build script and its components.

This module contains test cases for various parts of the build process,
including translation loading, data loading, HTML generation for different
content blocks, and the main build orchestration logic. It uses a temporary
file system structure to simulate real project files (configs, data, locales,
blocks) and extensive mocking to isolate units under test.
"""

import json
import os
import re
import shutil
import tempfile
import unittest
from typing import Any, Dict  # For type hinting self.dummy_config
from unittest import mock

from google.protobuf import json_format
from google.protobuf.message import Message  # Explicit import for T = TypeVar bound
from jinja2 import Environment, FileSystemLoader

from build import main as build_main
from build_protocols.data_loading import JsonProtoDataLoader
from build_protocols.html_generation import (
    BlogHtmlGenerator,
    ContactFormHtmlGenerator,
    FeaturesHtmlGenerator,
    HeroHtmlGenerator,
    PortfolioHtmlGenerator,
    TestimonialsHtmlGenerator,
)
from build_protocols.interfaces import Translations
from build_protocols.translation import DefaultTranslationProvider

# Generated protobuf messages
from generated.blog_post_pb2 import BlogPost
from generated.contact_form_config_pb2 import ContactFormConfig
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import HeroItem, HeroItemContent
from generated.nav_item_pb2 import Navigation
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem


class TestBuildScript(unittest.TestCase):
    """Test cases for build.py script components and main execution."""

    def setUp(self) -> None:
        """Set up a temporary test environment before each test.

        This involves:
        - Creating a temporary root directory.
        - Changing the current working directory to this temporary root.
        - Creating necessary subdirectories (public/locales, data, blocks, etc.).
        - Instantiating service components (translation provider, data loader,
          HTML generators) for direct testing.
        - Creating dummy translation files, data files, config files, and
          HTML block files within the temporary directory structure.
        """
        self.original_cwd: str = os.getcwd()
        self.test_root_dir: str = tempfile.mkdtemp()
        os.chdir(self.test_root_dir)

        self._create_test_directories()
        self._instantiate_services()
        self._create_dummy_translation_files()
        self._create_dummy_data_files()
        self._create_dummy_config_and_index()
        self._create_dummy_block_files()

    def _create_test_directories(self) -> None:
        """Creates the necessary directory structure within the temp root."""
        self.test_locales_dir: str = os.path.join(
            self.test_root_dir, "public", "locales"
        )
        self.test_data_dir: str = os.path.join(self.test_root_dir, "data")
        # self.test_blocks_dir is no longer needed as dummy blocks go into templates/blocks
        self.test_public_dir: str = os.path.join(self.test_root_dir, "public")
        self.test_public_generated_configs_dir: str = os.path.join(
            self.test_public_dir, "generated_configs"
        )

        os.makedirs(self.test_locales_dir, exist_ok=True)
        os.makedirs(self.test_data_dir, exist_ok=True)
        # os.makedirs(self.test_blocks_dir, exist_ok=True) # Not needed
        os.makedirs(self.test_public_generated_configs_dir, exist_ok=True)
        # Ensure the target directory for dummy block templates exists
        os.makedirs(os.path.join(self.test_root_dir, "templates", "components", "hero"), exist_ok=True)
        os.makedirs(os.path.join(self.test_root_dir, "templates", "components", "features"), exist_ok=True)
        os.makedirs(os.path.join(self.test_root_dir, "templates", "components", "testimonials"), exist_ok=True)
        os.makedirs(os.path.join(self.test_root_dir, "templates", "components", "portfolio"), exist_ok=True)
        os.makedirs(os.path.join(self.test_root_dir, "templates", "components", "blog"), exist_ok=True)
        os.makedirs(os.path.join(self.test_root_dir, "templates", "components", "contact-form"), exist_ok=True)
        # Keep templates/blocks for any old tests or general structure if needed, though components are primary now
        os.makedirs(os.path.join(self.test_root_dir, "templates", "blocks"), exist_ok=True)


    def _instantiate_services(self) -> None:
        """Instantiates common service components used in tests."""
        # Create a dummy Jinja2 environment for testing generators
        # It needs a loader, even if templates aren't actually loaded in all unit tests.
        # The "templates" directory is assumed to exist or be created by test setup if needed.
        # For many generator unit tests, the actual rendering might be mocked,
        # but the constructor needs the env.
        # Ensure a dummy 'templates' dir exists for FileSystemLoader, or use a mock loader.
        # For simplicity, assuming 'templates' might be a general dir or we mock rendering.
        # Let's create a dummy templates dir for the loader to be valid.
        # This directory is now created in _create_test_directories
        # os.makedirs(
        #     os.path.join(self.test_root_dir, "templates", "blocks"), exist_ok=True
        # ) # Moved to _create_test_directories
        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(self.test_root_dir, "templates"))
        )

        self.translation_provider = DefaultTranslationProvider()
        self.data_loader = JsonProtoDataLoader[Message]()
        self.portfolio_generator = PortfolioHtmlGenerator(jinja_env=self.jinja_env)
        self.blog_generator = BlogHtmlGenerator(jinja_env=self.jinja_env)
        self.features_generator = FeaturesHtmlGenerator(jinja_env=self.jinja_env)
        self.testimonials_generator = TestimonialsHtmlGenerator(
            jinja_env=self.jinja_env
        )
        self.hero_generator = HeroHtmlGenerator(jinja_env=self.jinja_env)
        self.contact_form_generator = ContactFormHtmlGenerator(jinja_env=self.jinja_env)

    def _create_dummy_translation_files(self) -> None:
        """Creates dummy translation JSON files (en.json, es.json)."""
        self.en_translations: Translations = {
            "greeting": "Hello",
            "farewell": "Goodbye",
            "header_text": "Test Header",
            "footer_text": "Test Footer",
            "portfolio_alt_1": "Alt 1 EN",
            "portfolio_title_1": "Title 1 EN",
            "portfolio_desc_1": "Desc 1 EN",
            "portfolio_alt_2": "Alt 2 EN",
            "portfolio_title_2": "Title 2 EN",
            "portfolio_desc_2": "Desc 2 EN",
            "blog_title_1": "Blog Title 1 EN",
            "blog_excerpt_1": "Excerpt 1 EN",
            "blog_cta_1": "Read EN",
            "blog_title_2": "Blog Title 2 EN",
            "blog_excerpt_2": "Excerpt 2 EN",
            "blog_cta_2": "More EN",
            "feature_title_1": "Feat Title 1 EN",
            "feature_desc_1": "Feat Desc 1 EN",
            "feature_title_2": "Feat Title 2 EN",
            "feature_desc_2": "Feat Desc 2 EN",
            "testimonial_text_1": "Testimonial Text EN",
            "testimonial_author_1": "Author EN",
            "testimonial_alt_1": "Alt EN",
            "hero_title_main_v1": "Hero V1 EN",
            "hero_subtitle_main_v1": "Sub V1 EN",
            "hero_cta_main_v1": "CTA V1 EN",
            "hero_title_main_v2": "Hero V2 EN",
            "hero_subtitle_main_v2": "Sub V2 EN",
            "hero_cta_main_v2": "CTA V2 EN",
            "contact_success": "Success EN",
            "contact_error": "Error EN",
        }
        with open(
            os.path.join(self.test_locales_dir, "en.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.en_translations, f)

        self.es_translations: Translations = {
            "greeting": "Hola",
            "farewell": "Adiós",
            "header_text": "Cabecera de Prueba",
            "footer_text": "Pie de Página de Prueba",
            "portfolio_alt_1": "Alt 1 ES",
            "portfolio_title_1": "Título 1 ES",
            "portfolio_desc_1": "Desc 1 ES",
            "portfolio_alt_2": "Alt 2 ES",
            "portfolio_title_2": "Título 2 ES",
            "portfolio_desc_2": "Desc 2 ES",
            "blog_title_1": "Blog Título 1 ES",
            "blog_excerpt_1": "Extracto 1 ES",
            "blog_cta_1": "Leer ES",
            "blog_title_2": "Blog Título 2 ES",
            "blog_excerpt_2": "Extracto 2 ES",
            "blog_cta_2": "Más ES",
            "feature_title_1": "Caract Título 1 ES",
            "feature_desc_1": "Caract Desc 1 ES",
            "feature_title_2": "Caract Título 2 ES",
            "feature_desc_2": "Caract Desc 2 ES",
            "testimonial_text_1": "Testimonio Texto ES",
            "testimonial_author_1": "Autor ES",
            "testimonial_alt_1": "Alt ES",
            "hero_title_main_v1": "Héroe V1 ES",
            "hero_subtitle_main_v1": "Sub V1 ES",
            "hero_cta_main_v1": "CTA V1 ES",
            "hero_title_main_v2": "Héroe V2 ES",
            "hero_subtitle_main_v2": "Sub V2 ES",
            "hero_cta_main_v2": "CTA V2 ES",
            "contact_success": "Éxito ES",
            "contact_error": "Error ES",
        }
        with open(
            os.path.join(self.test_locales_dir, "es.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.es_translations, f)

    def _create_dummy_data_files(self) -> None:
        """Creates dummy JSON data files for portfolio, blog, etc."""
        self.portfolio_items_data = [
            {
                "id": "p1",
                "image": {"src": "img1.jpg", "alt_text": {"key": "portfolio_alt_1"}},
                "details": {
                    "title": {"key": "portfolio_title_1"},
                    "description": {"key": "portfolio_desc_1"},
                },
            },
            {
                "id": "p2",
                "image": {"src": "img2.jpg", "alt_text": {"key": "portfolio_alt_2"}},
                "details": {
                    "title": {"key": "portfolio_title_2"},
                    "description": {"key": "portfolio_desc_2"},
                },
            },
        ]
        with open(
            os.path.join(self.test_data_dir, "portfolio.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.portfolio_items_data, f)

        self.blog_posts_data = [
            {
                "id": "b1",
                "title": {"key": "blog_title_1"},
                "excerpt": {"key": "blog_excerpt_1"},
                "cta": {"text": {"key": "blog_cta_1"}, "uri": "link1.html"},
            },
            {
                "id": "b2",
                "title": {"key": "blog_title_2"},
                "excerpt": {"key": "blog_excerpt_2"},
                "cta": {"text": {"key": "blog_cta_2"}, "uri": "link2.html"},
            },
        ]
        with open(
            os.path.join(self.test_data_dir, "blog.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.blog_posts_data, f)

        self.feature_items_data = [
            {
                "content": {
                    "title": {"key": "feature_title_1"},
                    "description": {"key": "feature_desc_1"},
                }
            },
            {
                "content": {
                    "title": {"key": "feature_title_2"},
                    "description": {"key": "feature_desc_2"},
                }
            },
        ]
        with open(
            os.path.join(self.test_data_dir, "features.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.feature_items_data, f)

        self.testimonial_items_data = [
            {
                "text": {"key": "testimonial_text_1"},
                "author": {"key": "testimonial_author_1"},
                "author_image": {
                    "src": "img_testimonial1.jpg",
                    "alt_text": {"key": "testimonial_alt_1"},
                },
            }
        ]
        with open(
            os.path.join(self.test_data_dir, "testimonials.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.testimonial_items_data, f)

        self.hero_item_data = {
            "variations": [
                {
                    "variation_id": "var1",
                    "title": {"key": "hero_title_main_v1"},
                    "subtitle": {"key": "hero_subtitle_main_v1"},
                    "cta": {"text": {"key": "hero_cta_main_v1"}, "uri": "#gohere_v1"},
                },
                {
                    "variation_id": "var2",
                    "title": {"key": "hero_title_main_v2"},
                    "subtitle": {"key": "hero_subtitle_main_v2"},
                    "cta": {"text": {"key": "hero_cta_main_v2"}, "uri": "#gohere_v2"},
                },
            ],
            "default_variation_id": "var1",
        }
        with open(
            os.path.join(self.test_data_dir, "hero.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.hero_item_data, f)

    def _create_dummy_config_and_index(self) -> None:
        """Creates dummy index.html and config.json files."""
        self.dummy_index_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body>
            <header data-i18n="header_text">Header</header>
            <main>
                <p>Placeholder</p>
            </main>
            <footer data-i18n="footer_text">Footer</footer>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(self.dummy_index_content)

        self.dummy_config: Dict[str, Any] = {
            "blocks": [
                "hero.html",
                "features.html",
                "testimonials.html",
                "portfolio.html",
                "blog.html",
            ],
            "supported_langs": ["en", "es"],
            "default_lang": "en",
            "navigation_data_file": os.path.join(
                "data", "navigation.json"
            ),  # Ensure this path is used by tests
            "base_html_file": "index.html",
        }
        os.makedirs("public", exist_ok=True)
        with open(os.path.join("public", "config.json"), "w", encoding="utf-8") as f:
            json.dump(self.dummy_config, f)
        # Create dummy navigation.json
        dummy_nav_data = {
            "items": [{"label": {"key": "nav_home"}, "href": "index.html"}]
        }
        with open(
            os.path.join(self.test_data_dir, "navigation.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(dummy_nav_data, f)

    def _create_dummy_block_files(self) -> None:
        """Creates dummy HTML block files in their respective templates/components/<name>/<name>.html paths."""

        # For hero.html
        dummy_hero_dir = os.path.join("templates", "components", "hero")
        hero_template_content = """
<section class="hero">
    {% if hero_item %}
    <h1>{{ translations[hero_item.title.key] }}</h1>
    <p>{{ translations[hero_item.subtitle.key] }}</p>
    <a href="{{ hero_item.cta.uri }}" class="cta-button">{{ translations[hero_item.cta.text.key] }}</a>
    <!-- Selected variation: {{ hero_item.variation_id }} -->
    {% else %}
    <!-- Hero item data was None or empty in dummy template -->
    {% endif %}
</section>
"""
        with open(os.path.join(dummy_hero_dir, "hero.html"), "w", encoding="utf-8") as f:
            f.write(hero_template_content)

        # For features.html
        dummy_features_dir = os.path.join("templates", "components", "features")
        features_template_content = """
<div>
    {% for item in items %}
    <div class="feature-item">
        <h2>{{ translations[item.content.title.key] }}</h2>
        <p>{{ translations[item.content.description.key] }}</p>
    </div>
    {% endfor %}
</div>
"""
        with open(os.path.join(dummy_features_dir, "features.html"), "w", encoding="utf-8") as f:
            f.write(features_template_content)

        # For testimonials.html
        dummy_testimonials_dir = os.path.join("templates", "components", "testimonials")
        testimonials_template_content = """
<div>
    {% for item in items %}
    <div class="testimonial-item">
        <p>"{{ translations[item.text.key] }}"</p>
        <cite>- {{ translations[item.author.key] }}</cite>
        <img src="{{ item.author_image.src }}" alt="{{ translations[item.author_image.alt_text.key] }}" />
    </div>
    {% endfor %}
</div>
"""
        with open(os.path.join(dummy_testimonials_dir, "testimonials.html"), "w", encoding="utf-8") as f:
            f.write(testimonials_template_content)

        # For portfolio.html
        dummy_portfolio_dir = os.path.join("templates", "components", "portfolio")
        portfolio_template_content = """
<div>
    {% for item in items %}
    <div id="{{ item.id }}">
        <img src="{{ item.image.src }}" alt="{{ translations[item.image.alt_text.key] }}" />
        <h3>{{ translations[item.details.title.key] }}</h3>
        <p>{{ translations[item.details.description.key] }}</p>
    </div>
    {% endfor %}
</div>
"""
        with open(os.path.join(dummy_portfolio_dir, "portfolio.html"), "w", encoding="utf-8") as f:
            f.write(portfolio_template_content)

        # For blog.html
        dummy_blog_dir = os.path.join("templates", "components", "blog")
        blog_template_content = """
<div>
    {% for item in items %}
    <article id="{{ item.id }}">
        <h2>{{ translations[item.title.key] }}</h2>
        <p>{{ translations[item.excerpt.key] }}</p>
        <a href="{{ item.cta.uri }}">{{ translations[item.cta.text.key] }}</a>
    </article>
    {% endfor %}
</div>
"""
        with open(os.path.join(dummy_blog_dir, "blog.html"), "w", encoding="utf-8") as f:
            f.write(blog_template_content)

        # For contact-form.html
        dummy_contact_form_dir = os.path.join("templates", "components", "contact-form")
        contact_form_template_content = """
<form id="contact-form" action="{{ config.form_action_uri if config else '' }}">
    {% if config %}
    <p class="success-message">{{ translations[config.success_message_key] }}</p>
    <p class="error-message">{{ translations[config.error_message_key] }}</p>
    {% endif %}
</form>
"""
        with open(os.path.join(dummy_contact_form_dir, "contact-form.html"), "w", encoding="utf-8") as f:
            f.write(contact_form_template_content)

        # Create dummy base.html, header.html, footer.html in templates/ and templates/components/
        # These are needed for the main build test (test_main_function_creates_files)
        # and for the PageBuilder to find them.

        # templates/base.html
        base_html_content = """<!DOCTYPE html>
<html lang="{{ lang }}">
<head><title>{{ title }}</title><link rel="stylesheet" href="public/dist/main.css"></head>
<body>
    {% include "components/header/header.html" %}
    <main>{{ main_content | safe }}</main>
    {% include "components/footer/footer.html" %}
    <script src="public/dist/main.js" defer></script>
</body>
</html>"""
        with open(os.path.join("templates", "base.html"), "w", encoding="utf-8") as f:
            f.write(base_html_content)

        # templates/components/header/header.html
        os.makedirs(os.path.join("templates", "components", "header"), exist_ok=True)
        header_html_content = "<header>Test Header Content with {{ app_config.supported_langs|length }} langs</header>"
        with open(os.path.join("templates", "components", "header", "header.html"), "w", encoding="utf-8") as f:
            f.write(header_html_content)

        # templates/components/footer/footer.html
        os.makedirs(os.path.join("templates", "components", "footer"), exist_ok=True)
        footer_html_content = "<footer>Test Footer Content</footer>"
        with open(os.path.join("templates", "components", "footer", "footer.html"), "w", encoding="utf-8") as f:
            f.write(footer_html_content)


    def tearDown(self) -> None:
        """Clean up the temporary test environment after each test."""
        os.chdir(self.original_cwd)
        if hasattr(self, "test_root_dir") and os.path.exists(self.test_root_dir):
            shutil.rmtree(self.test_root_dir)

    def test_load_translations_existing(self):
        """Test loading existing translation files using DefaultTranslationProvider."""
        translations_en = self.translation_provider.load_translations("en")
        self.assertEqual(translations_en["greeting"], self.en_translations["greeting"])

        translations_es = self.translation_provider.load_translations("es")
        self.assertEqual(translations_es["greeting"], self.es_translations["greeting"])

    def test_load_translations_non_existing(self):
        """Test loading non-existing translation file with DefaultTranslationProvider."""
        translations = self.translation_provider.load_translations("non_existent_lang")
        self.assertEqual(translations, {})

    def test_load_translations_invalid_json(self):
        """Test loading translation file with invalid JSON with DefaultTranslationProvider."""
        invalid_json_file_path = os.path.join(self.test_locales_dir, "invalid.json")
        with open(invalid_json_file_path, "w", encoding="utf-8") as f:
            f.write('{"greeting": "Hello", "farewell":')  # Malformed JSON

        translations = self.translation_provider.load_translations("invalid")
        self.assertEqual(translations, {})

    def test_translate_html_content(self):
        """Test HTML content translation with DefaultTranslationProvider."""
        html_content = (
            '<p data-i18n="greeting">Original Greeting</p>'
            '<p data-i18n="farewell">Original Farewell</p>'
        )
        # Use a subset of translations for this specific test for clarity
        test_translations = {"greeting": "Hello Test", "farewell": "Goodbye Test"}
        translated_html = self.translation_provider.translate_html_content(
            html_content, test_translations
        )
        self.assertIn(test_translations["greeting"], translated_html)
        self.assertIn(test_translations["farewell"], translated_html)

    def test_translate_html_content_no_translations(self):
        """Test HTML content translation with no translations with DefaultTranslationProvider."""
        html_content = '<p data-i18n="greeting">Greeting</p>'
        translated_html = self.translation_provider.translate_html_content(
            html_content, {}
        )
        self.assertIn("Greeting", translated_html)

    def test_translate_html_content_missing_key(self):
        """Test HTML content translation with a missing key with DefaultTranslationProvider."""
        html_content = (
            '<p data-i18n="greeting">Greeting</p><p data-i18n="missing_key">Missing</p>'
        )
        test_translations = {"greeting": "Hello Test"}
        translated_html = self.translation_provider.translate_html_content(
            html_content, test_translations
        )
        self.assertIn(test_translations["greeting"], translated_html)
        self.assertIn("Missing", translated_html)  # Should remain if key is missing

    def test_load_dynamic_data_portfolio(self):
        """Test loading dynamic portfolio data with JsonProtoDataLoader."""
        portfolio_file_path = os.path.join("data", "portfolio.json")
        items = self.data_loader.load_dynamic_list_data(
            portfolio_file_path, PortfolioItem
        )
        self.assertEqual(len(items), len(self.portfolio_items_data))
        if items:
            self.assertIsInstance(items[0], PortfolioItem)
            self.assertEqual(
                items[0].details.title.key,
                self.portfolio_items_data[0]["details"]["title"]["key"],
            )

    def test_load_dynamic_data_feature(self):
        """Test loading dynamic feature data with JsonProtoDataLoader."""
        feature_file_path = os.path.join("data", "features.json")
        items = self.data_loader.load_dynamic_list_data(feature_file_path, FeatureItem)
        self.assertEqual(len(items), len(self.feature_items_data))
        if items:
            self.assertIsInstance(items[0], FeatureItem)
            self.assertEqual(
                items[0].content.title.key,
                self.feature_items_data[0]["content"]["title"]["key"],
            )

    def test_load_dynamic_data_testimonial(self):
        """Test loading dynamic testimonial data with JsonProtoDataLoader."""
        testimonial_file_path = os.path.join("data", "testimonials.json")
        items = self.data_loader.load_dynamic_list_data(
            testimonial_file_path, TestimonialItem
        )
        self.assertEqual(len(items), len(self.testimonial_items_data))
        if items:
            self.assertIsInstance(items[0], TestimonialItem)
            self.assertEqual(
                items[0].text.key, self.testimonial_items_data[0]["text"]["key"]
            )

    def test_load_single_item_dynamic_data_hero(self):
        """Test loading dynamic hero item data with JsonProtoDataLoader."""
        hero_file_path = os.path.join("data", "hero.json")
        item = self.data_loader.load_dynamic_single_item_data(hero_file_path, HeroItem)
        self.assertIsNotNone(item)
        if item and item.variations:  # type: ignore
            self.assertIsInstance(item, HeroItem)
            self.assertEqual(  # type: ignore
                item.variations[0].title.key,  # type: ignore
                self.hero_item_data["variations"][0]["title"]["key"],
            )

    def test_load_single_item_dynamic_data_not_found(self):
        """Test loading single item from non-existent file with JsonProtoDataLoader."""
        item = self.data_loader.load_dynamic_single_item_data(
            os.path.join("data", "non_existent_hero.json"), HeroItem
        )
        self.assertIsNone(item)

    def test_load_dynamic_data_blog(self):
        """Test loading dynamic blog data with JsonProtoDataLoader."""
        blog_file_path = os.path.join("data", "blog.json")
        posts = self.data_loader.load_dynamic_list_data(blog_file_path, BlogPost)
        self.assertEqual(len(posts), len(self.blog_posts_data))
        if posts:
            self.assertIsInstance(posts[0], BlogPost)
            self.assertEqual(
                posts[0].title.key, self.blog_posts_data[0]["title"]["key"]
            )

    def test_load_dynamic_data_file_not_found(self):
        """Test loading dynamic data from a non-existent file with JsonProtoDataLoader."""
        items = self.data_loader.load_dynamic_list_data(
            os.path.join("data", "non_existent_data.json"), PortfolioItem
        )
        self.assertEqual(items, [])

    def test_load_dynamic_data_invalid_json(self):
        """Test loading dynamic data from a file with invalid JSON with JsonProtoDataLoader."""
        invalid_json_filename = "invalid_data.json"
        invalid_json_path_abs = os.path.join(self.test_data_dir, invalid_json_filename)
        with open(invalid_json_path_abs, "w", encoding="utf-8") as f:
            f.write("[{'title': 'Test' }, {]")  # Invalid JSON

        items = self.data_loader.load_dynamic_list_data(
            os.path.join("data", invalid_json_filename), PortfolioItem
        )
        self.assertEqual(items, [])

    def test_generate_portfolio_html(self):
        """Test generation of portfolio HTML with PortfolioHtmlGenerator."""
        items = [
            PortfolioItem(
                id="p1",
                image={"src": "img.png", "alt_text": {"key": "p_alt"}},
                details={"title": {"key": "p_title"}, "description": {"key": "p_desc"}},
            )
        ]
        translations = {
            "p_title": "Translated Title",
            "p_desc": "Translated Description",
            "p_alt": "Translated Alt Text",
        }
        html = self.portfolio_generator.generate_html(items, translations)
        self.assertIn("Translated Title", html)
        self.assertIn("Translated Description", html)
        self.assertIn('src="img.png"', html)
        self.assertIn('alt="Translated Alt Text"', html)
        self.assertIn('id="p1"', html)

    def test_generate_portfolio_html_empty(self):
        """Test portfolio HTML generation with no items."""
        html = self.portfolio_generator.generate_html([], self.en_translations)
        self.assertEqual(html.strip(), "")

    def test_generate_blog_html(self):
        """Test generation of blog HTML with BlogHtmlGenerator."""
        posts = [
            BlogPost(
                id="b1",
                title={"key": "b_title"},
                excerpt={"key": "b_excerpt"},
                cta={"text": {"key": "b_cta"}, "uri": "link.html"},
            )
        ]
        translations = {
            "b_title": "Blog Title",
            "b_excerpt": "Blog Excerpt",
            "b_cta": "Read More",
        }
        html = self.blog_generator.generate_html(posts, translations)
        self.assertIn("Blog Title", html)
        self.assertIn("Blog Excerpt", html)
        self.assertIn('href="link.html"', html)
        self.assertIn(">Read More</a>", html)
        self.assertIn('id="b1"', html)

    def test_generate_blog_html_empty(self):
        """Test blog HTML generation with no posts."""
        html = self.blog_generator.generate_html([], self.en_translations)
        self.assertEqual(html.strip(), "")

    def test_generate_features_html(self):
        """Test generation of features HTML with FeaturesHtmlGenerator."""
        items = [
            FeatureItem(
                content={"title": {"key": "f_title"}, "description": {"key": "f_desc"}}
            )
        ]
        translations = {
            "f_title": "Translated Feature Title",
            "f_desc": "Translated Feature Description",
        }
        html = self.features_generator.generate_html(items, translations)
        self.assertIn("Translated Feature Title", html)
        self.assertIn("Translated Feature Description", html)
        self.assertIn('<div class="feature-item">', html)

    def test_generate_features_html_empty(self):
        """Test features HTML generation with no items."""
        html = self.features_generator.generate_html([], self.en_translations)
        self.assertEqual(html.strip(), "")

    def test_generate_testimonials_html(self):
        """Test generation of testimonials HTML with TestimonialsHtmlGenerator."""
        items = [
            TestimonialItem(
                text={"key": "t_text"},
                author={"key": "t_author"},
                author_image={"src": "testimonial.png", "alt_text": {"key": "t_alt"}},
            )
        ]
        translations = {
            "t_text": "Translated Testimonial Text",
            "t_author": "Translated Testimonial Author",
            "t_alt": "Translated Testimonial Alt Text",
        }
        html = self.testimonials_generator.generate_html(items, translations)
        self.assertIn("Translated Testimonial Text", html)
        self.assertIn("Translated Testimonial Author", html)
        self.assertIn('src="testimonial.png"', html)
        self.assertIn('alt="Translated Testimonial Alt Text"', html)
        self.assertIn('<div class="testimonial-item">', html)
        self.assertIn(f'<p>"{translations["t_text"]}"</p>', html)

    def test_generate_testimonials_html_empty(self):
        """Test testimonials HTML generation with no items."""
        html = self.testimonials_generator.generate_html([], self.en_translations)
        self.assertEqual(html.strip(), "")

    def test_generate_hero_html(self):
        """Test generation of hero HTML with HeroHtmlGenerator."""
        hero_item_instance = HeroItem()
        json_format.ParseDict(self.hero_item_data, hero_item_instance)
        translations = self.en_translations  # Use full translations from setUp

        with mock.patch(
            "build_protocols.html_generation.random.choice", side_effect=lambda x: x[0]
        ):
            html = self.hero_generator.generate_html(hero_item_instance, translations)

        # Check against keys from self.en_translations
        self.assertIn(f"<h1>{translations['hero_title_main_v1']}</h1>", html)
        self.assertIn(f"<p>{translations['hero_subtitle_main_v1']}</p>", html)
        self.assertIn(
            f'<a href="#gohere_v1" class="cta-button">{translations["hero_cta_main_v1"]}</a>',
            html,
        )
        self.assertIn(
            f"<!-- Selected variation: {hero_item_instance.variations[0].variation_id} -->",  # type: ignore
            html,
        )

    def test_generate_hero_html_none_item(self):
        """Test hero HTML generation when item is None."""
        html = self.hero_generator.generate_html(None, self.en_translations)
        self.assertEqual(html.strip(), "<!-- Hero data not found or no variations -->")

    @mock.patch("build.DefaultAppConfigManager.load_app_config")
    @mock.patch("build.DefaultTranslationProvider.load_translations")
    @mock.patch("build.DefaultTranslationProvider.translate_html_content")
    @mock.patch("build.JsonProtoDataLoader.load_dynamic_list_data")
    @mock.patch("build.JsonProtoDataLoader.load_dynamic_single_item_data")
    @mock.patch("build.InMemoryDataCache.preload_data")
    @mock.patch("build.InMemoryDataCache.get_item")
    @mock.patch("build.DefaultAppConfigManager.generate_language_config")
    # @mock.patch("build.DefaultPageBuilder.extract_base_html_parts") # This method is no longer used directly by the orchestrator
    @mock.patch("build.DefaultPageBuilder.assemble_translated_page")
    @mock.patch("build_protocols.html_generation.PortfolioHtmlGenerator.generate_html")
    @mock.patch("build_protocols.html_generation.BlogHtmlGenerator.generate_html")
    @mock.patch("build_protocols.html_generation.FeaturesHtmlGenerator.generate_html")
    @mock.patch(
        "build_protocols.html_generation.TestimonialsHtmlGenerator.generate_html"
    )
    @mock.patch("build_protocols.html_generation.HeroHtmlGenerator.generate_html")
    @mock.patch(
        "build_protocols.html_generation.ContactFormHtmlGenerator.generate_html"
    )
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_main_function_creates_files(
        self,
        mock_builtin_open,
        mock_gen_contact_html,
        mock_gen_hero_html,
        mock_gen_testimonials_html,
        mock_gen_features_html,
        mock_gen_blog_html,
        mock_gen_portfolio_html,
        mock_assemble_page,
        # mock_extract_parts, # Removed as the method is no longer patched
        mock_generate_lang_config,
        mock_data_cache_get_item,
        mock_data_cache_preload,
        mock_load_single_item_data,
        mock_load_list_data,
        mock_translate_content,
        mock_load_translations,
        mock_load_app_config,
    ):
        """Test that build_main (via BuildOrchestrator) creates output files."""
        mock_load_app_config.return_value = self.dummy_config
        mock_load_translations.side_effect = lambda lang: (
            self.en_translations if lang == "en" else self.es_translations
        )
        mock_translate_content.side_effect = lambda content, translations: content

        mock_portfolio_item = PortfolioItem(id="p1", details={"title": {"key": "ptk"}})
        mock_blog_post = BlogPost(id="b1", title={"key": "btk"})
        mock_feature_item = FeatureItem(content={"title": {"key": "ftk"}})
        mock_testimonial_item = TestimonialItem(text={"key": "ttk"})
        mock_hero_item = HeroItem(
            default_variation_id="v1",
            variations=[HeroItemContent(variation_id="v1", title={"key": "htk"})],
        )  # type: ignore
        mock_contact_config = ContactFormConfig(
            form_action_uri="/test_action",
            success_message_key="contact_success",
            error_message_key="contact_error",
        )
        mock_navigation_data = Navigation()

        def load_list_data_side_effect(data_file_path, message_type):
            if "portfolio" in data_file_path:
                return [mock_portfolio_item]
            if "blog" in data_file_path:
                return [mock_blog_post]
            if "features" in data_file_path:
                return [mock_feature_item]
            if "testimonials" in data_file_path:
                return [mock_testimonial_item]
            return []

        mock_load_list_data.side_effect = load_list_data_side_effect

        def load_single_item_data_side_effect(data_file_path, message_type):
            if "hero" in data_file_path:
                return mock_hero_item
            if "contact_form" in data_file_path:
                return mock_contact_config
            # Check basename as data_file_path might be absolute in tests
            if os.path.basename(data_file_path) == "navigation.json":
                return mock_navigation_data
            return None

        mock_load_single_item_data.side_effect = load_single_item_data_side_effect

        mock_data_cache_preload.return_value = None

        def data_cache_get_item_side_effect(key):
            if "portfolio" in key:
                return [mock_portfolio_item]
            if "blog" in key:
                return [mock_blog_post]
            if "features" in key:
                return [mock_feature_item]
            if "testimonials" in key:
                return [mock_testimonial_item]
            if "hero" in key:
                return mock_hero_item
            if "contact_form" in key:
                return mock_contact_config
            return None

        mock_data_cache_get_item.side_effect = data_cache_get_item_side_effect

        mock_gen_portfolio_html.return_value = "<p>Portfolio Content</p>"
        mock_gen_blog_html.return_value = "<p>Blog Content</p>"
        mock_gen_features_html.return_value = "<p>Features Content</p>"
        mock_gen_testimonials_html.return_value = "<p>Testimonials Content</p>"
        mock_gen_hero_html.return_value = "<p>Hero Content</p>"
        mock_gen_contact_html.return_value = 'data-form-id="contact-form-attrs"'
        mock_generate_lang_config.return_value = {
            "lang": "test",
            "ui_strings": {},
        }

        header_match = re.search(
            r"<header.*?>(.*?)<\/header>",
            self.dummy_index_content,
            re.DOTALL,
        )
        footer_match = re.search(
            r"<footer.*?>(.*?)<\/footer>",
            self.dummy_index_content,
            re.DOTALL,
        )
        _ = header_match.group(0) if header_match else "<header></header>"
        _ = footer_match.group(0) if footer_match else "<footer></footer>"

        # mock_extract_parts.return_value = ( # No longer needed as the function is not called
        #     "<html><head_content/></head><body>",
        #     dummy_header_content,
        #     dummy_footer_content,
        #     "</body></html>",
        # )
        mock_assemble_page.return_value = (
            "<html><body>Assembled Page Content</body></html>"
        )

        def mock_builtin_open_side_effect(filename, mode="r", *args, **kwargs):
            normalized_filename = os.path.normpath(filename)
            if mode == "r":
                if normalized_filename.startswith(os.path.join("blocks")):
                    block_name = os.path.basename(filename)
                    placeholder_map = {
                        "hero.html": "{{hero_content}}",
                        "features.html": "{{feature_items}}",
                        "testimonials.html": "{{testimonial_items}}",
                        "portfolio.html": "{{portfolio_items}}",
                        "blog.html": "{{blog_posts}}",
                        "contact-form.html": "{{contact_form_attributes}}",
                    }
                    return mock.mock_open(
                        read_data=(f"<div>{placeholder_map.get(block_name, '')}</div>")
                    ).return_value
                if normalized_filename == "index.html":
                    return mock.mock_open(
                        read_data=self.dummy_index_content
                    ).return_value
                if normalized_filename == os.path.join("public", "config.json"):
                    return mock.mock_open(
                        read_data=json.dumps(self.dummy_config)
                    ).return_value
                if normalized_filename == os.path.normpath(
                    os.path.join("public", "locales", "en.json")
                ):
                    return mock.mock_open(
                        read_data=json.dumps(self.en_translations)
                    ).return_value
                if normalized_filename == os.path.normpath(
                    os.path.join("public", "locales", "es.json")
                ):
                    return mock.mock_open(
                        read_data=json.dumps(self.es_translations)
                    ).return_value
                if normalized_filename == os.path.normpath(
                    os.path.join("data", "navigation.json")
                ):
                    return mock.mock_open(
                        read_data=json.dumps({"items": []})
                    ).return_value
            elif mode == "w":
                return mock.MagicMock()
            return mock.mock_open(read_data="").return_value

        mock_builtin_open.side_effect = mock_builtin_open_side_effect

        build_main()

        expected_paths = [
            os.path.join("public", "generated_configs", "config_en.json"),
            "index.html",
            os.path.join("public", "generated_configs", "config_es.json"),
            "index_es.html",
            os.path.join("public", "dist", "main.css"), # Added CSS bundle
            os.path.join("public", "dist", "main.js"),   # Added JS bundle
        ]
        expected_write_calls = [
            mock.call(os.path.normpath(p), "w", encoding="utf-8")
            for p in expected_paths
        ]

        actual_write_calls = [
            c for c in mock_builtin_open.call_args_list if c.args[1] == "w"
        ]

        self.assertEqual(
            len(actual_write_calls),
            len(expected_write_calls),
            "Number of write calls does not match.",
        )

        for expected_call in expected_write_calls:
            normalized_actual_calls = [
                mock.call(os.path.normpath(c.args[0]), *c.args[1:], **c.kwargs)
                for c in actual_write_calls
            ]
            self.assertIn(
                expected_call,
                normalized_actual_calls,
                (
                    f"Expected write call not found: {expected_call}\n"
                    f"Actual write calls: {actual_write_calls}"
                ),
            )

        mock_load_app_config.assert_called_once()
        self.assertEqual(mock_load_translations.call_count, 2)
        mock_data_cache_preload.assert_called_once()
        # mock_extract_parts.assert_called_once() # Method is no longer called
        self.assertEqual(mock_assemble_page.call_count, 2)
        self.assertEqual(mock_generate_lang_config.call_count, 2)

        _ = len(self.dummy_config["supported_langs"])

        # Header and Footer are now Jinja includes and handle their own translations.
        # translate_html_content is no longer called for them in _process_language.
        # If other parts of the main flow were to use it, this would need adjustment.
        # For now, assuming it's 0 for the parts previously covered by header/footer.
        expected_translate_calls_for_header_footer = 0
        # If translate_html_content is used elsewhere in the tested flow,
        # this assertion needs to be more specific or the overall count adjusted.
        # Based on the current refactoring, the direct calls from _process_language for
        # header/footer strings are removed.
        self.assertEqual(
            mock_translate_content.call_count,
            expected_translate_calls_for_header_footer,
            f"Expected {expected_translate_calls_for_header_footer} direct calls to "
            f"translate_html_content from the main orchestrator loop "
            f"(excluding calls within Jinja templates), got {mock_translate_content.call_count}",
        )


if __name__ == "__main__":
    unittest.main()
