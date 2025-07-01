import json
import os
import shutil  # Added for rmtree
import sys
import unittest
from unittest import mock

from build import (
    generate_blog_html,
    generate_portfolio_html,
    load_dynamic_data,
    load_translations,
    translate_html_content,
)
from build import main as build_main
from generated.blog_post_pb2 import BlogPost
from generated.portfolio_item_pb2 import PortfolioItem

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class TestBuildScript(unittest.TestCase):
    """Test cases for build.py script."""

    def setUp(self):
        """Set up test environment."""
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

        # Create dummy data files
        self.portfolio_items_data = [
            {
                "title_i18n_key": "portfolio_title_1",
                "desc_i18n_key": "portfolio_desc_1",
                "img_src": "img1.jpg",
                "img_alt": "Alt 1",
            },
            {
                "title_i18n_key": "portfolio_title_2",
                "desc_i18n_key": "portfolio_desc_2",
                "img_src": "img2.jpg",
                "img_alt": "Alt 2",
            },
        ]
        with open(
            os.path.join(self.test_data_dir, "portfolio.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.portfolio_items_data, f)

        self.blog_posts_data = [
            {
                "title_i18n_key": "blog_title_1",
                "excerpt_i18n_key": "blog_excerpt_1",
                "link": "link1.html",
                "cta_i18n_key": "blog_cta_1",
            },
            {
                "title_i18n_key": "blog_title_2",
                "excerpt_i18n_key": "blog_excerpt_2",
                "link": "link2.html",
                "cta_i18n_key": "blog_cta_2",
            },
        ]
        with open(
            os.path.join(self.test_data_dir, "blog.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.blog_posts_data, f)

        # Create a dummy index.html for main() to read
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

        # Dummy config.json
        self.dummy_config = {
            "blocks": ["hero.html", "portfolio.html", "blog.html"],
            "supported_langs": ["en", "es"],
            "default_lang": "en",
        }
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.dummy_config, f)

        # Dummy block files
        os.makedirs("blocks", exist_ok=True)
        with open("blocks/hero.html", "w", encoding="utf-8") as f:
            f.write("<div data-i18n='hero_title'>Hero Title</div>")
        with open("blocks/portfolio.html", "w", encoding="utf-8") as f:
            f.write("<div>{{portfolio_items}}</div>")
        with open("blocks/blog.html", "w", encoding="utf-8") as f:
            f.write("<div>{{blog_posts}}</div>")

    def tearDown(self):
        """Clean up test environment."""
        # Use shutil.rmtree to remove directories and their contents
        if os.path.exists(self.test_locales_dir):
            shutil.rmtree(self.test_locales_dir)
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
        if os.path.exists("blocks"):
            shutil.rmtree("blocks")

        # Remove individual files created at root
        if os.path.exists("index.html"):
            os.remove("index.html")
        if os.path.exists("index_es.html"):
            os.remove("index_es.html")
        if os.path.exists("config.json"):
            os.remove("config.json")
        # Individual block files inside "blocks" will be removed by rmtree("blocks")

    @mock.patch("build.project_root", ".")  # Ensure build.py uses test_locales
    def test_load_translations_existing(self):
        """Test loading existing translation files."""
        # Temporarily modify where load_translations looks for files
        with mock.patch(
            "build.open",
            mock.mock_open(read_data=json.dumps(self.en_translations)),
            create=True,
        ) as mocked_open:
            translations = load_translations(f"{self.test_locales_dir}/en")
            self.assertEqual(translations, self.en_translations)
            mocked_open.assert_called_once_with(
                f"locales/{self.test_locales_dir}/en.json", "r", encoding="utf-8"
            )

        with mock.patch(
            "build.open",
            mock.mock_open(read_data=json.dumps(self.es_translations)),
            create=True,
        ) as mocked_open:
            translations = load_translations(f"{self.test_locales_dir}/es")
            self.assertEqual(translations, self.es_translations)
            mocked_open.assert_called_once_with(
                f"locales/{self.test_locales_dir}/es.json", "r", encoding="utf-8"
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
            translations = load_translations(f"{self.test_locales_dir}/invalid")
            self.assertEqual(translations, {})
            mocked_open.assert_called_once_with(
                f"locales/{self.test_locales_dir}/invalid.json", "r", encoding="utf-8"
            )
        os.remove(os.path.join(self.test_locales_dir, "invalid.json"))

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
            self.assertEqual(
                items[0].title_i18n_key, self.portfolio_items_data[0]["title_i18n_key"]
            )

    def test_load_dynamic_data_blog(self):
        """Test loading dynamic blog data."""
        posts = load_dynamic_data(
            os.path.join(self.test_data_dir, "blog.json"), BlogPost
        )
        self.assertEqual(len(posts), len(self.blog_posts_data))
        if posts:  # mypy check
            self.assertIsInstance(posts[0], BlogPost)
            self.assertEqual(
                posts[0].title_i18n_key, self.blog_posts_data[0]["title_i18n_key"]
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
        os.remove(invalid_json_path)

    def test_generate_portfolio_html(self):
        """Test generation of portfolio HTML."""
        items = [
            PortfolioItem(
                title_i18n_key="p_title",
                desc_i18n_key="p_desc",
                img_src="img.png",
                img_alt="alt",
            )
        ]
        translations = {
            "p_title": "Translated Title",
            "p_desc": "Translated Description",
        }
        html = generate_portfolio_html(items, translations)
        self.assertIn("Translated Title", html)
        self.assertIn("Translated Description", html)
        self.assertIn('img src="img.png"', html)

    def test_generate_portfolio_html_empty(self):
        """Test generation of portfolio HTML with no items."""
        html = generate_portfolio_html([], self.en_translations)
        self.assertEqual(html.strip(), "")

    def test_generate_blog_html(self):
        """Test generation of blog HTML."""
        posts = [
            BlogPost(
                title_i18n_key="b_title",
                excerpt_i18n_key="b_excerpt",
                link="link.html",
                cta_i18n_key="b_cta",
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

    @mock.patch("build.load_translations")
    @mock.patch("build.load_dynamic_data")
    @mock.patch("build.translate_html_content")
    @mock.patch("builtins.open", new_callable=mock.mock_open)  # Mock all file opens
    def test_main_function_creates_files(
        self, mock_file_open, mock_translate, mock_load_data, mock_load_trans
    ):
        """Test that main function attempts to create output files."""
        # Setup mock return values
        mock_load_trans.side_effect = [
            {
                "header_text": "EN Header",
                "footer_text": "EN Footer",
                "hero_title": "EN Hero",
            },  # en translations
            {
                "header_text": "ES Header",
                "footer_text": "ES Footer",
                "hero_title": "ES Hero",
            },  # es translations
        ]
        # Mock load_dynamic_data to return specific types
        mock_portfolio_item = PortfolioItem(
            title_i18n_key="p1",
            desc_i18n_key="d1",
            img_src="portfolio.jpg",
            img_alt="alt",
        )
        mock_blog_post = BlogPost(
            title_i18n_key="b1",
            excerpt_i18n_key="e1",
            link="blog.html",
            cta_i18n_key="c1",
        )

        def load_data_side_effect(path, message_type):
            if message_type == PortfolioItem:
                return [mock_portfolio_item]
            if message_type == BlogPost:
                return [mock_blog_post]
            return []

        mock_load_data.side_effect = load_data_side_effect

        mock_translate.side_effect = (
            lambda content, trans: content
        )  # Simple pass-through

        # Mock the reading of index.html, config.json, and block files
        # This is a simplified approach; a more robust mock would differentiate
        # by filename
        def mock_file_open_side_effect(filename, *args, **kwargs):
            if filename == "index.html" and args[0] == "r":
                return mock.mock_open(read_data=self.dummy_index_content).return_value
            if filename == "config.json" and args[0] == "r":
                return mock.mock_open(
                    read_data=json.dumps(self.dummy_config)
                ).return_value
            if filename.startswith("blocks/") and args[0] == "r":
                if "hero" in filename:
                    return mock.mock_open(
                        read_data="<div data-i18n='hero_title'>Hero</div>"
                    ).return_value
                if "portfolio" in filename:
                    return mock.mock_open(
                        read_data="<div>{{portfolio_items}}</div>"
                    ).return_value
                if "blog" in filename:
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
