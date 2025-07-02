import json
import os
import shutil
import sys
import tempfile  # Added for temporary directory
import unittest
from unittest import mock

from google.protobuf import json_format

from build import (  # Grouped with other 'from build' imports
    generate_blog_html,
    generate_features_html,
    generate_hero_html,  # Added
    generate_portfolio_html,
    generate_testimonials_html,
    load_dynamic_data,
    load_single_item_dynamic_data,  # Added
    load_translations,
    translate_html_content,
)
from build import main as build_main
from generated.blog_post_pb2 import BlogPost
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import HeroItem
from generated.nav_item_pb2 import Navigation  # Moved to top
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem

# Ensure the project root (and thus 'generated' directory) is in the Python path
# This needs to be done BEFORE other imports from 'build' or 'build_protocols'
_current_dir = os.path.dirname(os.path.abspath(__file__)) # This is /app for test_build.py
_project_root_for_test = _current_dir # Assuming test_build.py is in the project root

# Path to the 'generated' directory, assuming it's a sibling to test_build.py, build.py etc.
_generated_dir_path = os.path.join(_project_root_for_test, "generated")

if _project_root_for_test not in sys.path:
    sys.path.insert(0, _project_root_for_test)
if _generated_dir_path not in sys.path and os.path.isdir(_generated_dir_path):
    sys.path.insert(0, _generated_dir_path)
# This ensures that `from generated.xxx_pb2 import Xxx` works.

# The following is also important from build.py to ensure build_protocols can be found
# if build.py is in project_root and build_protocols is a subdir.
# In this test setup, _project_root_for_test is already the top-level /app,
# so imports like `from build_protocols.xyz` should work if /app is in sys.path.

class TestBuildScript(unittest.TestCase):
    """Test cases for build.py script."""

    def setUp(self):
        """Set up test environment."""
        self.original_cwd = os.getcwd()
        self.test_root_dir = tempfile.mkdtemp()
        os.chdir(self.test_root_dir)

        # These paths are now relative to self.test_root_dir
        self.test_locales_dir = "test_locales"
        self.test_data_dir = "test_data"
        os.makedirs(self.test_locales_dir, exist_ok=True)
        os.makedirs(self.test_data_dir, exist_ok=True)

        # Create dummy translation files
        self.en_translations = {"greeting": "Hello", "farewell": "Goodbye"}
        with open(
            os.path.join(self.test_locales_dir, "en.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.en_translations, f)

        self.es_translations = {"greeting": "Hola", "farewell": "Adiós"}
        with open(
            os.path.join(self.test_locales_dir, "es.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.es_translations, f)

        # Create dummy data files matching the new proto structure
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
                "cta": {"text": {"key": "blog_cta_1"}, "link": "link1.html"},
            },
            {
                "id": "b2",
                "title": {"key": "blog_title_2"},
                "excerpt": {"key": "blog_excerpt_2"},
                "cta": {"text": {"key": "blog_cta_2"}, "link": "link2.html"},
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
                    "cta": {"text": {"key": "hero_cta_main_v1"}, "link": "#gohere_v1"},
                },
                {
                    "variation_id": "var2",
                    "title": {"key": "hero_title_main_v2"},
                    "subtitle": {"key": "hero_subtitle_main_v2"},
                    "cta": {"text": {"key": "hero_cta_main_v2"}, "link": "#gohere_v2"},
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
            shutil.rmtree(self.test_root_dir)  # Remove the entire temporary directory

    @mock.patch("build.project_root", ".")  # Ensure build.py uses test_locales
    def test_load_translations_existing(self):
        """Test loading existing translation files."""
        # Temporarily modify where load_translations looks for files
        with mock.patch(
            "build.open",
            mock.mock_open(read_data=json.dumps(self.en_translations)),
            create=True,
        ) as mocked_open:
            # load_translations prepends 'public/locales/'
            translations = load_translations("en")  # Test with actual lang key
            self.assertEqual(translations, self.en_translations)
            # The call inside load_translations is to "public/locales/en.json"
            # The mock needs to intercept this.
            # For this test, we'll assume the mock is general enough.
            # The assertion should check the path used by the function.
            mocked_open.assert_called_with(
                "public/locales/en.json", "r", encoding="utf-8"
            )

        # Reset mock for the next call if necessary or use different mocks
        mocked_open.reset_mock()

        with mock.patch(
            "build.open",
            mock.mock_open(read_data=json.dumps(self.es_translations)),
            create=True,
        ) as mocked_open_es:  # Use a different mock name or reset
            translations = load_translations("es")  # Test with actual lang key
            self.assertEqual(translations, self.es_translations)
            mocked_open_es.assert_called_with(
                "public/locales/es.json", "r", encoding="utf-8"
            )

    def test_load_translations_non_existing(self):
        """Test loading non-existing translation file."""
        translations = load_translations("non_existent_lang")
        self.assertEqual(translations, {})

    def test_load_translations_invalid_json(self):
        """Test loading translation file with invalid JSON."""
        with open(
            os.path.join(self.test_locales_dir, "invalid.json"), "w", encoding="utf-8"
        ) as f:
            f.write("{'greeting': 'Hello', 'farewell': ")  # Invalid JSON

        with mock.patch(
            "build.open", mock.mock_open(read_data="{invalid_json_content"), create=True
        ) as mocked_open:
            translations = load_translations("invalid")  # Test with actual lang key
            self.assertEqual(translations, {})
            mocked_open.assert_called_with(  # Changed to assert_called_with
                "public/locales/invalid.json", "r", encoding="utf-8"
            )
        # The actual file 'test_locales/invalid.json' is created in the temp dir
        # and will be cleaned up by tearDown. No explicit os.remove needed.

    def test_translate_html_content(self):
        """Test HTML content translation."""
        html_content = (
            '<p data-i18n="greeting">Original Greeting</p>'
            '<p data-i18n="farewell">Original Farewell</p>'
        )
        translated_html = translate_html_content(html_content, self.en_translations)
        self.assertIn(self.en_translations["greeting"], translated_html)
        self.assertIn(self.en_translations["farewell"], translated_html)

    def test_translate_html_content_no_translations(self):
        """Test HTML content translation when no translations are provided."""
        html_content = '<p data-i18n="greeting">Greeting</p>'
        translated_html = translate_html_content(html_content, {})
        self.assertIn("Greeting", translated_html)  # Should remain unchanged

    def test_translate_html_content_missing_key(self):
        """Test HTML content translation with a missing key."""
        html_content = (
            '<p data-i18n="greeting">Greeting</p><p data-i18n="missing_key">Missing</p>'
        )
        translated_html = translate_html_content(html_content, self.en_translations)
        self.assertIn(self.en_translations["greeting"], translated_html)
        self.assertIn(
            "Missing", translated_html
        )  # Key "missing_key" not in en_translations

    def test_load_dynamic_data_portfolio(self):
        """Test loading dynamic portfolio data."""
        items = load_dynamic_data(
            os.path.join(self.test_data_dir, "portfolio.json"), PortfolioItem
        )
        self.assertEqual(len(items), len(self.portfolio_items_data))
        if items:  # mypy check
            self.assertIsInstance(items[0], PortfolioItem)
            # Compare a nested field to ensure parsing worked
            self.assertEqual(
                items[0].details.title.key,
                self.portfolio_items_data[0]["details"]["title"]["key"],
            )

    def test_load_dynamic_data_feature(self):
        """Test loading dynamic feature data."""
        items = load_dynamic_data(
            os.path.join(self.test_data_dir, "features.json"), FeatureItem
        )
        self.assertEqual(len(items), len(self.feature_items_data))
        if items:  # mypy check
            self.assertIsInstance(items[0], FeatureItem)
            self.assertEqual(
                items[0].content.title.key,
                self.feature_items_data[0]["content"]["title"]["key"],
            )

    def test_load_dynamic_data_testimonial(self):
        """Test loading dynamic testimonial data."""
        items = load_dynamic_data(
            os.path.join(self.test_data_dir, "testimonials.json"), TestimonialItem
        )
        self.assertEqual(len(items), len(self.testimonial_items_data))
        if items:  # mypy check
            self.assertIsInstance(items[0], TestimonialItem)
            self.assertEqual(
                items[0].text.key, self.testimonial_items_data[0]["text"]["key"]
            )

    def test_load_single_item_dynamic_data_hero(self):
        """Test loading dynamic hero item data (single item)."""
        item = load_single_item_dynamic_data(
            os.path.join(self.test_data_dir, "hero.json"), HeroItem
        )
        self.assertIsNotNone(item)
        if item and item.variations:  # for type checking
            self.assertIsInstance(item, HeroItem)
            self.assertEqual(
                item.variations[0].title.key,
                self.hero_item_data["variations"][0]["title"]["key"],
            )

    def test_load_single_item_dynamic_data_not_found(self):
        """Test loading single item from non-existent file."""
        item = load_single_item_dynamic_data("non_existent_hero.json", HeroItem)
        self.assertIsNone(item)

    def test_load_dynamic_data_blog(self):
        """Test loading dynamic blog data."""
        posts = load_dynamic_data(
            os.path.join(self.test_data_dir, "blog.json"), BlogPost
        )
        self.assertEqual(len(posts), len(self.blog_posts_data))
        if posts:  # mypy check
            self.assertIsInstance(posts[0], BlogPost)
            self.assertEqual(
                posts[0].title.key, self.blog_posts_data[0]["title"]["key"]
            )

    def test_load_dynamic_data_file_not_found(self):
        """Test loading dynamic data from a non-existent file."""
        items = load_dynamic_data("non_existent_data.json", PortfolioItem)
        self.assertEqual(items, [])

    def test_load_dynamic_data_invalid_json(self):
        """Test loading dynamic data from a file with invalid JSON."""
        invalid_json_path = os.path.join(self.test_data_dir, "invalid.json")
        with open(invalid_json_path, "w", encoding="utf-8") as f:
            f.write("[{'title': 'Test' }, {]")  # Invalid JSON
        items = load_dynamic_data(invalid_json_path, PortfolioItem)
        self.assertEqual(items, [])
        # invalid_json_path is inside self.test_data_dir.
        # It will be cleaned up by tearDown. No explicit os.remove needed.

    def test_generate_portfolio_html(self):
        """Test generation of portfolio HTML."""
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
        html = generate_portfolio_html(items, translations)
        self.assertIn("Translated Title", html)
        self.assertIn("Translated Description", html)
        self.assertIn('src="img.png"', html)
        self.assertIn('alt="Translated Alt Text"', html)

    def test_generate_portfolio_html_empty(self):
        """Test generation of portfolio HTML with no items."""
        html = generate_portfolio_html([], self.en_translations)
        self.assertEqual(html.strip(), "")

    def test_generate_blog_html(self):
        """Test generation of blog HTML."""
        posts = [
            BlogPost(
                id="b1",
                title={"key": "b_title"},
                excerpt={"key": "b_excerpt"},
                cta={"text": {"key": "b_cta"}, "link": "link.html"},
            )
        ]
        translations = {
            "b_title": "Blog Title",
            "b_excerpt": "Blog Excerpt",
            "b_cta": "Read More",
        }
        html = generate_blog_html(posts, translations)
        self.assertIn("Blog Title", html)
        self.assertIn("Blog Excerpt", html)
        self.assertIn('href="link.html"', html)
        self.assertIn(">Read More</a>", html)

    def test_generate_blog_html_empty(self):
        """Test generation of blog HTML with no posts."""
        html = generate_blog_html([], self.en_translations)
        self.assertEqual(html.strip(), "")

    def test_generate_features_html(self):
        """Test generation of features HTML."""
        items = [
            FeatureItem(
                content={
                    "title": {"key": "f_title"},
                    "description": {"key": "f_desc"},
                }
            )
        ]
        translations = {
            "f_title": "Translated Feature Title",
            "f_desc": "Translated Feature Description",
        }
        html = generate_features_html(items, translations)
        self.assertIn("Translated Feature Title", html)
        self.assertIn("Translated Feature Description", html)
        self.assertIn('<div class="feature-item">', html)

    def test_generate_features_html_empty(self):
        """Test generation of features HTML with no items."""
        html = generate_features_html([], self.en_translations)
        self.assertEqual(html.strip(), "")

    def test_generate_testimonials_html(self):
        """Test generation of testimonials HTML."""
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
        html = generate_testimonials_html(items, translations)
        self.assertIn("Translated Testimonial Text", html)
        self.assertIn("Translated Testimonial Author", html)
        self.assertIn('src="testimonial.png"', html)
        self.assertIn('alt="Translated Testimonial Alt Text"', html)
        self.assertIn('<div class="testimonial-item">', html)

    def test_generate_testimonials_html_empty(self):
        """Test generation of testimonials HTML with no items."""
        html = generate_testimonials_html([], self.en_translations)
        self.assertEqual(html.strip(), "")

    def test_generate_hero_html(self):
        """Test generation of hero HTML."""
        # Using the structure from self.hero_item_data for consistency
        # Create a HeroItem instance and parse the dictionary into it
        hero_item_instance = HeroItem()
        json_format.ParseDict(self.hero_item_data, hero_item_instance)

        translations = {
            "hero_title_main_v1": "Translated Hero Title V1",
            "hero_subtitle_main_v1": "Translated Hero Subtitle V1",
            "hero_cta_main_v1": "Translated CTA Text V1",
            "hero_title_main_v2": "Translated Hero Title V2",
            "hero_subtitle_main_v2": "Translated Hero Subtitle V2",
            "hero_cta_main_v2": "Translated CTA Text V2",
        }
        # Mock random.choice to always pick the first variation for predictable testing
        with mock.patch("random.choice", side_effect=lambda x: x[0]):
            html = generate_hero_html(hero_item_instance, translations)

        self.assertIn("<h1>Translated Hero Title V1</h1>", html)
        self.assertIn("<p>Translated Hero Subtitle V1</p>", html)
        self.assertIn(
            '<a href="#gohere_v1" class="cta-button">Translated CTA Text V1</a>', html
        )
        self.assertIn("<!-- Selected variation: var1 -->", html)

    def test_generate_hero_html_none_item(self):
        """Test hero HTML generation when item is None."""
        html = generate_hero_html(None, self.en_translations)
        self.assertEqual(html.strip(), "<!-- Hero data not found or no variations -->")

    @mock.patch("build.load_translations")
    # Patch both data loading functions used in the main pre-loading loop
    @mock.patch("build.load_dynamic_data")  # For list-based items
    @mock.patch("build.load_single_item_dynamic_data")  # For single items like hero
    @mock.patch("build.translate_html_content")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_main_function_creates_files(
        self,
        mock_file_open,
        mock_translate,
        mock_load_single_item_data,  # Order matters for mock args
        mock_load_list_data,
        mock_load_trans,
    ):
        """Test that main function attempts to create output files."""
        mock_load_trans.side_effect = [
            self.en_translations,  # For EN
            self.es_translations,  # For ES
        ]

        # Mock data items using the new structure
        mock_hero_item = HeroItem()
        json_format.ParseDict(
            {
                "variations": [
                    {
                        "variation_id": "v1",
                        "title": {"key": "h_title"},
                        "subtitle": {"key": "h_sub"},
                        "cta": {"text": {"key": "h_cta"}, "link": "#hero"},
                    }
                ],
                "default_variation_id": "v1",
            },
            mock_hero_item,
        )

        mock_portfolio_item = PortfolioItem()
        json_format.ParseDict(
            {
                "id": "p1",
                "image": {"src": "p.jpg", "alt_text": {"key": "p_alt"}},
                "details": {
                    "title": {"key": "p_title"},
                    "description": {"key": "p_desc"},
                },
            },
            mock_portfolio_item,
        )

        mock_blog_post = BlogPost()
        json_format.ParseDict(
            {
                "id": "b1",
                "title": {"key": "b_title"},
                "excerpt": {"key": "b_excerpt"},
                "cta": {"text": {"key": "b_cta"}, "link": "b.html"},
            },
            mock_blog_post,
        )

        mock_feature_item = FeatureItem()
        json_format.ParseDict(
            {
                "content": {
                    "title": {"key": "f_title"},
                    "description": {"key": "f_desc"},
                }
            },
            mock_feature_item,
        )

        mock_testimonial_item = TestimonialItem()
        json_format.ParseDict(
            {
                "text": {"key": "t_text"},
                "author": {"key": "t_author"},
                "author_image": {"src": "t.jpg", "alt_text": {"key": "t_alt"}},
            },
            mock_testimonial_item,
        )

        def load_list_data_side_effect(
            data_file_path, message_type
        ):  # pylint: disable=unused-argument
            if "portfolio_items.json" in data_file_path:
                return [mock_portfolio_item]
            if "blog_posts.json" in data_file_path:
                return [mock_blog_post]
            if "feature_items.json" in data_file_path:
                return [mock_feature_item]
            if "testimonial_items.json" in data_file_path:
                return [mock_testimonial_item]
            return []

        mock_load_list_data.side_effect = load_list_data_side_effect

        def load_single_item_data_side_effect(
            data_file_path, message_type
        ):  # pylint: disable=unused-argument
            if "hero_item.json" in data_file_path:  # Match actual path used in build.py
                return mock_hero_item
            # Add mock for navigation.json if it's loaded as a single item
            if (
                "navigation.json" in data_file_path
            ):  # Assuming Navigation is loaded this way # noqa: E501
                # Return a dummy Navigation object or None as appropriate for the test
                return (
                    Navigation()
                )  # Return an empty Navigation object - import is at top # noqa: E501
            return None

        mock_load_single_item_data.side_effect = load_single_item_data_side_effect

        mock_translate.side_effect = (
            lambda content, trans: content
        )  # Simple pass-through

        # Mock the reading of index.html, config.json, and block files
        # This is a simplified approach; a more robust mock would differentiate
        # by filename
        def mock_file_open_side_effect(filename, *args, **kwargs):
            if filename == "index.html" and args[0] == "r":
                return mock.mock_open(read_data=self.dummy_index_content).return_value
            # Ensure build.py's call to open 'public/config.json' is mocked
            if filename == "public/config.json" and args[0] == "r":
                return mock.mock_open(
                    read_data=json.dumps(self.dummy_config)
                ).return_value
            # Mock for the test's own setup of 'config.json' if it's different
            # For this test, we primarily care about what build_main reads.
            if (
                filename == "config.json"
                and args[0] == "r"
                and "public/" not in filename
            ):
                return mock.mock_open(
                    read_data=json.dumps(self.dummy_config)
                ).return_value

            if filename.startswith("blocks/") and args[0] == "r":
                if "hero.html" == os.path.basename(filename):
                    return mock.mock_open(
                        read_data="<div data-i18n='hero_title'>Hero</div>"
                    ).return_value
                if "features.html" == os.path.basename(filename):
                    return mock.mock_open(
                        read_data="<div>{{feature_items}}</div>"
                    ).return_value
                if "testimonials.html" == os.path.basename(filename):
                    return mock.mock_open(
                        read_data="<div>{{testimonial_items}}</div>"
                    ).return_value
                if "portfolio.html" == os.path.basename(filename):
                    return mock.mock_open(
                        read_data="<div>{{portfolio_items}}</div>"
                    ).return_value
                if "blog.html" == os.path.basename(filename):
                    return mock.mock_open(
                        read_data="<div>{{blog_posts}}</div>"
                    ).return_value
            # For write operations, return a mock object that can be written to
            if args[0] == "w":
                return mock.MagicMock()
            # Fallback for any other unhandled open calls
            return mock.mock_open(read_data="").return_value

        mock_file_open.side_effect = mock_file_open_side_effect

        build_main()

        # Check that files for each language were attempted to be written
        # We check for 'index.html' (default lang 'en') and 'index_es.html'
        _ = [
            mock.call("index.html", "w", encoding="utf-8"),
            mock.call("index_es.html", "w", encoding="utf-8"),
        ]

        # Check if the specific write calls were made.
        # This is tricky because many other read calls are also made by 'open'.
        # We can iterate through the actual calls to mock_file_open.
        _ = [
            call
            for call in mock_file_open.call_args_list
            if call[1].get("mode") == "w" or (len(call[0]) > 1 and call[0][1] == "w")
        ]

        # Assert that the expected write calls are present in the actual write calls
        # This is a more flexible check than assert_has_calls with any_order=True
        # because other write calls might exist
        # (e.g. if tests run in parallel or temp files)

        # For index.html (default lang)
        self.assertTrue(
            any(
                cargs[0] == "index.html" and cargs[1] == "w"
                for cargs, _ in mock_file_open.call_args_list
                if cargs
            )
        )
        # For index_es.html
        self.assertTrue(
            any(
                cargs[0] == "index_es.html" and cargs[1] == "w"
                for cargs, ckwargs in mock_file_open.call_args_list
                if cargs
            )
        )


if __name__ == "__main__":
    unittest.main()
