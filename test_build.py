import json
import os
import re  # Import re module
import shutil
import sys
import tempfile
import unittest
from unittest import mock

from google.protobuf import json_format  # For Message type hint
from google.protobuf.message import Message  # Explicit import for T = TypeVar bound

from build import main as build_main  # To test the main orchestrator
from build_protocols.data_loading import JsonProtoDataLoader
from build_protocols.html_generation import (
    BlogHtmlGenerator,
    ContactFormHtmlGenerator,
    FeaturesHtmlGenerator,
    HeroHtmlGenerator,
    PortfolioHtmlGenerator,
    TestimonialsHtmlGenerator,
)

# Interfaces might be needed for type hinting if we mock them
from build_protocols.interfaces import Translations
from build_protocols.translation import DefaultTranslationProvider
from generated.blog_post_pb2 import BlogPost
from generated.contact_form_config_pb2 import ContactFormConfig
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import (  # Changed HeroVariation to HeroItemContent
    HeroItem,
    HeroItemContent,
)
from generated.nav_item_pb2 import Navigation
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem

# Ensure the project root (and thus 'generated' directory) is in the Python path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root_for_test = _current_dir

_generated_dir_path = os.path.join(_project_root_for_test, "generated")
if _project_root_for_test not in sys.path:
    sys.path.insert(0, _project_root_for_test)
if _generated_dir_path not in sys.path and os.path.isdir(_generated_dir_path):
    sys.path.insert(0, _generated_dir_path)


class TestBuildScript(unittest.TestCase):
    """Test cases for build.py script components and main execution."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.test_root_dir = (
            tempfile.mkdtemp()
        )  # Create a temporary root directory for tests
        os.chdir(self.test_root_dir)  # Change CWD to the temporary directory

        # Create subdirectories within the temporary root
        self.test_locales_dir = os.path.join(self.test_root_dir, "public", "locales")
        self.test_data_dir = os.path.join(self.test_root_dir, "data")
        self.test_blocks_dir = os.path.join(self.test_root_dir, "blocks")
        self.test_public_dir = os.path.join(self.test_root_dir, "public")
        self.test_public_generated_configs_dir = os.path.join(
            self.test_public_dir, "generated_configs"
        )

        os.makedirs(self.test_locales_dir, exist_ok=True)
        os.makedirs(self.test_data_dir, exist_ok=True)
        os.makedirs(self.test_blocks_dir, exist_ok=True)
        # public dir itself is created by test_locales_dir if "public" is in its path
        os.makedirs(self.test_public_generated_configs_dir, exist_ok=True)

        # Instantiate service components for direct testing
        self.translation_provider = DefaultTranslationProvider()
        self.data_loader = JsonProtoDataLoader[
            Message
        ]()  # Use Message for generic loader instance
        self.portfolio_generator = PortfolioHtmlGenerator()
        self.blog_generator = BlogHtmlGenerator()
        self.features_generator = FeaturesHtmlGenerator()
        self.testimonials_generator = TestimonialsHtmlGenerator()
        self.hero_generator = HeroHtmlGenerator()
        self.contact_form_generator = ContactFormHtmlGenerator()
        # Other services like AppConfigManager, PageBuilder can be instantiated if needed for specific tests

        # Dummy translation files (now created in temp_root/public/locales/)
        self.en_translations: Translations = {
            "greeting": "Hello",
            "farewell": "Goodbye",
            "header_text": "Test Header",
            "footer_text": "Test Footer",
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
        }
        with open(
            os.path.join(self.test_locales_dir, "es.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.es_translations, f)

        # Dummy data files (now created in temp_root/data/)
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
        ) as f:  # Corresponds to data/hero_item.json used in build.py
            json.dump(self.hero_item_data, f)

        # Create a dummy index.html for main() to read (in self.test_root_dir)
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
        with open(
            "index.html", "w", encoding="utf-8"
        ) as f:  # Will be in self.test_root_dir
            f.write(self.dummy_index_content)

        # Dummy config.json (for build.py, which expects public/config.json)
        self.dummy_config = {
            "blocks": [
                "hero.html",
                "features.html",
                "testimonials.html",
                "portfolio.html",
                "blog.html",
            ],
            "supported_langs": ["en", "es"],
            "default_lang": "en",
        }

        # Create public directory and public/config.json within self.test_root_dir
        os.makedirs("public", exist_ok=True)
        with open(os.path.join("public", "config.json"), "w", encoding="utf-8") as f:
            json.dump(self.dummy_config, f)

        # Create a root config.json as well if some tests directly expect it
        # (though build.py itself uses public/config.json)
        with open(
            "config.json", "w", encoding="utf-8"
        ) as f:  # will be in self.test_root_dir
            json.dump(self.dummy_config, f)

        # Dummy block files (in self.test_root_dir/blocks/)
        os.makedirs("blocks", exist_ok=True)  # will be self.test_root_dir/blocks
        with open(os.path.join("blocks", "hero.html"), "w", encoding="utf-8") as f:
            f.write('<section class="hero">{{hero_content}}</section>')
        with open(os.path.join("blocks", "features.html"), "w", encoding="utf-8") as f:
            f.write("<div>{{feature_items}}</div>")
        with open(
            os.path.join("blocks", "testimonials.html"), "w", encoding="utf-8"
        ) as f:
            f.write("<div>{{testimonial_items}}</div>")
        with open(os.path.join("blocks", "portfolio.html"), "w", encoding="utf-8") as f:
            f.write("<div>{{portfolio_items}}</div>")
        with open(os.path.join("blocks", "blog.html"), "w", encoding="utf-8") as f:
            f.write("<div>{{blog_posts}}</div>")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)  # Restore original CWD
        if hasattr(self, "test_root_dir") and os.path.exists(self.test_root_dir):
            shutil.rmtree(self.test_root_dir)

    def test_load_translations_existing(self):
        """Test loading existing translation files using DefaultTranslationProvider."""
        # The setUp method now creates dummy files in the temp CWD's public/locales
        # So, we can test the actual file loading if mocks are not used,
        # or mock 'open' to control the content precisely.
        # For this test, let's use the actual files created in setUp.
        # No, the provider uses `open(f"public/locales/{lang}.json")` which is relative to CWD.
        # And CWD is self.test_root_dir. So it will look for `self.test_root_dir/public/locales/en.json`.
        # This matches where setUp creates them.

        translations_en = self.translation_provider.load_translations("en")
        self.assertEqual(translations_en, self.en_translations)

        translations_es = self.translation_provider.load_translations("es")
        self.assertEqual(translations_es, self.es_translations)

    def test_load_translations_non_existing(self):
        """Test loading non-existing translation file with DefaultTranslationProvider."""
        # This will try to open 'public/locales/non_existent_lang.json' in the CWD (temp_root)
        # It should not find it and return {}.
        translations = self.translation_provider.load_translations("non_existent_lang")
        self.assertEqual(translations, {})

    def test_load_translations_invalid_json(self):
        """Test loading translation file with invalid JSON with DefaultTranslationProvider."""
        # Create an invalid JSON file in the expected path within the temp directory
        invalid_json_file_path = os.path.join(self.test_locales_dir, "invalid.json")
        with open(invalid_json_file_path, "w", encoding="utf-8") as f:
            f.write('{"greeting": "Hello", "farewell":')  # Malformed JSON

        translations = self.translation_provider.load_translations("invalid")
        self.assertEqual(translations, {})
        # The provider prints a warning, which is fine.

    def test_translate_html_content(self):
        """Test HTML content translation with DefaultTranslationProvider."""
        html_content = (
            '<p data-i18n="greeting">Original Greeting</p>'
            '<p data-i18n="farewell">Original Farewell</p>'
        )
        translated_html = self.translation_provider.translate_html_content(
            html_content, self.en_translations
        )
        self.assertIn(self.en_translations["greeting"], translated_html)
        self.assertIn(self.en_translations["farewell"], translated_html)

    def test_translate_html_content_no_translations(self):
        """Test HTML content translation with no translations with DefaultTranslationProvider."""
        html_content = '<p data-i18n="greeting">Greeting</p>'
        translated_html = self.translation_provider.translate_html_content(
            html_content, {}
        )
        self.assertIn("Greeting", translated_html)  # Should remain unchanged

    def test_translate_html_content_missing_key(self):
        """Test HTML content translation with a missing key with DefaultTranslationProvider."""
        html_content = (
            '<p data-i18n="greeting">Greeting</p><p data-i18n="missing_key">Missing</p>'
        )
        translated_html = self.translation_provider.translate_html_content(
            html_content, self.en_translations
        )
        self.assertIn(self.en_translations["greeting"], translated_html)
        self.assertIn("Missing", translated_html)

    def test_load_dynamic_data_portfolio(self):
        """Test loading dynamic portfolio data with JsonProtoDataLoader."""
        # Data files are created in self.test_data_dir by setUp.
        # JsonProtoDataLoader expects paths relative to CWD (which is self.test_root_dir).
        # So, the path should be "data/portfolio.json".
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
        if item and item.variations:
            self.assertIsInstance(item, HeroItem)
            self.assertEqual(
                item.variations[0].title.key,
                self.hero_item_data["variations"][0]["title"]["key"],
            )

    def test_load_single_item_dynamic_data_not_found(self):
        """Test loading single item from non-existent file with JsonProtoDataLoader."""
        # Path relative to CWD (self.test_root_dir)
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
        # Create the invalid file directly in self.test_data_dir (which is temp_root/data)
        invalid_json_path_abs = os.path.join(self.test_data_dir, invalid_json_filename)
        with open(invalid_json_path_abs, "w", encoding="utf-8") as f:
            f.write("[{'title': 'Test' }, {]")  # Invalid JSON

        # Path for loader should be relative to CWD (self.test_root_dir)
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
                details={
                    "title": {"key": "p_title"},
                    "description": {"key": "p_desc"},
                },
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
                content={
                    "title": {"key": "f_title"},
                    "description": {"key": "f_desc"},
                }
                # icon field removed as it's not in the proto definition
            )
        ]
        translations = {
            "f_title": "Translated Feature Title",
            "f_desc": "Translated Feature Description",
        }
        html = self.features_generator.generate_html(items, translations)
        self.assertIn("Translated Feature Title", html)
        self.assertIn("Translated Feature Description", html)
        # self.assertIn("<svg></svg>", html) # Icon check removed as FeatureItem proto has no icon field
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
                author_image={
                    "src": "testimonial.png",
                    "alt_text": {"key": "t_alt"},
                },
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
        self.assertIn(
            f'<p>"{translations["t_text"]}"</p>', html
        )  # Check exact structure

    def test_generate_testimonials_html_empty(self):
        """Test testimonials HTML generation with no items."""
        html = self.testimonials_generator.generate_html([], self.en_translations)
        self.assertEqual(html.strip(), "")

    def test_generate_hero_html(self):
        """Test generation of hero HTML with HeroHtmlGenerator."""
        hero_item_instance = HeroItem()
        json_format.ParseDict(self.hero_item_data, hero_item_instance)

        translations = {
            "hero_title_main_v1": "Translated Hero Title V1",
            "hero_subtitle_main_v1": "Translated Hero Subtitle V1",
            "hero_cta_main_v1": "Translated CTA Text V1",
            "hero_title_main_v2": "Translated Hero Title V2",  # For other variations
            "hero_subtitle_main_v2": "Translated Hero Subtitle V2",
            "hero_cta_main_v2": "Translated CTA Text V2",
        }
        # Mock random.choice within the html_generation module
        with mock.patch(
            "build_protocols.html_generation.random.choice", side_effect=lambda x: x[0]
        ):
            html = self.hero_generator.generate_html(hero_item_instance, translations)

        self.assertIn(f"<h1>{translations['hero_title_main_v1']}</h1>", html)
        self.assertIn(f"<p>{translations['hero_subtitle_main_v1']}</p>", html)
        self.assertIn(
            f'<a href="#gohere_v1" class="cta-button">{translations["hero_cta_main_v1"]}</a>',
            html,
        )
        # Check that the selected variation is the first one due to mock
        self.assertIn(
            f"<!-- Selected variation: {hero_item_instance.variations[0].variation_id} -->",
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
    @mock.patch("build.DefaultPageBuilder.extract_base_html_parts")
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
        mock_builtin_open,  # Corresponds to @mock.patch("builtins.open")
        mock_gen_contact_html,
        mock_gen_hero_html,
        mock_gen_testimonials_html,
        mock_gen_features_html,
        mock_gen_blog_html,
        mock_gen_portfolio_html,
        mock_assemble_page,
        mock_extract_parts,
        mock_generate_lang_config,
        mock_data_cache_get_item,
        mock_data_cache_preload,
        mock_load_single_item_data,
        mock_load_list_data,
        mock_translate_content,  # Corresponds to DefaultTranslationProvider.translate_html_content
        mock_load_translations,  # Corresponds to DefaultTranslationProvider.load_translations
        mock_load_app_config,  # Corresponds to DefaultAppConfigManager.load_app_config
    ):
        """Test that build_main (via BuildOrchestrator) creates output files."""

        # --- Configure Mocks ---
        mock_load_app_config.return_value = self.dummy_config

        mock_load_translations.side_effect = lambda lang: (
            self.en_translations if lang == "en" else self.es_translations
        )
        mock_translate_content.side_effect = (
            lambda content, translations: content
        )  # Passthrough

        mock_portfolio_item = PortfolioItem(id="p1", details={"title": {"key": "ptk"}})
        mock_blog_post = BlogPost(id="b1", title={"key": "btk"})
        mock_feature_item = FeatureItem(content={"title": {"key": "ftk"}})
        mock_testimonial_item = TestimonialItem(text={"key": "ttk"})
        # Corrected HeroVariation to HeroItemContent
        mock_hero_item = HeroItem(
            default_variation_id="v1",
            variations=[HeroItemContent(variation_id="v1", title={"key": "htk"})],
        )
        mock_contact_config = ContactFormConfig(
            form_action_url="/test_action",
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
            if "navigation" in data_file_path:
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

        mock_generate_lang_config.return_value = {"lang": "test", "ui_strings": {}}

        header_match = re.search(
            r"<header.*?>(.*?)<\/header>", self.dummy_index_content, re.DOTALL
        )
        footer_match = re.search(
            r"<footer.*?>(.*?)<\/footer>", self.dummy_index_content, re.DOTALL
        )
        dummy_header_content = (
            header_match.group(0) if header_match else "<header></header>"
        )
        dummy_footer_content = (
            footer_match.group(0) if footer_match else "<footer></footer>"
        )

        mock_extract_parts.return_value = (
            "<html><head_content/></head><body>",
            dummy_header_content,
            dummy_footer_content,
            "</body></html>",
        )
        mock_assemble_page.return_value = (
            "<html><body>Assembled Page Content</body></html>"
        )

        def mock_builtin_open_side_effect(filename, mode="r", *args, **kwargs):
            if mode == "r":
                if filename.startswith("blocks" + os.sep):
                    block_name = os.path.basename(filename)
                    placeholder_map = {
                        "hero.html": "{{hero_content}}",
                        "features.html": "{{feature_items}}",
                        "testimonials.html": "{{testimonial_items}}",
                        "portfolio.html": "{{portfolio_items}}",
                        "blog.html": "{{blog_posts}}",
                        "contact-form.html": "{{contact_form_attributes}}",
                    }
                    placeholder = placeholder_map.get(
                        block_name, "{{unknown_placeholder}}"
                    )
                    return mock.mock_open(
                        read_data=f"<div>{placeholder}</div>"
                    ).return_value
                elif filename == "index.html":
                    return mock.mock_open(
                        read_data=self.dummy_index_content
                    ).return_value
                elif filename == os.path.join("public", "config.json"):
                    return mock.mock_open(
                        read_data=json.dumps(self.dummy_config)
                    ).return_value
            elif mode == "w":
                return mock.MagicMock()
            return mock.mock_open(read_data="").return_value

        mock_builtin_open.side_effect = mock_builtin_open_side_effect

        build_main()

        expected_write_calls = [
            mock.call(
                os.path.join("public", "generated_configs", "config_en.json"),
                "w",
                encoding="utf-8",
            ),
            mock.call("index.html", "w", encoding="utf-8"),
            mock.call(
                os.path.join("public", "generated_configs", "config_es.json"),
                "w",
                encoding="utf-8",
            ),
            mock.call("index_es.html", "w", encoding="utf-8"),
        ]

        # Corrected filtering of actual write calls
        actual_write_calls = [
            c
            for c in mock_builtin_open.call_args_list
            if len(c.args) > 1 and c.args[1] == "w"
        ]

        for expected_call in expected_write_calls:
            self.assertIn(  # Use assertIn for comparing call objects with list of calls
                expected_call,
                actual_write_calls,
                f"Expected write call not found: {expected_call}\nActual write calls: {actual_write_calls}",
            )

        mock_load_app_config.assert_called_once()
        self.assertEqual(mock_load_translations.call_count, 2)
        mock_data_cache_preload.assert_called_once()
        mock_extract_parts.assert_called_once()
        self.assertEqual(mock_assemble_page.call_count, 2)
        self.assertEqual(mock_generate_lang_config.call_count, 2)

        num_langs = len(self.dummy_config["supported_langs"])
        num_blocks_in_config = len(self.dummy_config["blocks"])

        # Check translate_html_content calls:
        # For each language: 1 for header, 1 for footer, 1 for each block's combined template+data
        expected_translate_calls = num_langs * (2 + num_blocks_in_config)
        self.assertEqual(mock_translate_content.call_count, expected_translate_calls)


if __name__ == "__main__":
    unittest.main()
