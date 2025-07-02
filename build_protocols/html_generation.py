"""
HTML block generator classes for various content types.

This module provides concrete implementations of the `HtmlBlockGenerator`
protocol for different kinds of data (e.g., portfolio items, testimonials,
features, hero sections, contact forms, and blog posts). Each generator
takes structured data (typically as protobuf messages) and translation data,
and produces an HTML string representation for that block.

Refactored to use `html_utils` for safer and more readable HTML construction.
`ContactFormHtmlGenerator` now returns a dictionary of attributes.
"""

import logging  # Added for ContactFormHtmlGenerator warning
import random
from typing import Dict, List, Optional  # Added Dict, Union

# Generated protobuf message types
from generated.blog_post_pb2 import BlogPost
from generated.contact_form_config_pb2 import ContactFormConfig
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import HeroItem, HeroItemContent
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem

from .html_utils import create_element, escape_html, img
from .interfaces import HtmlBlockGenerator, Translations

logger = logging.getLogger(__name__)


class PortfolioHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a list of portfolio items."""

    def generate_html(
        self, data: List[PortfolioItem], translations: Translations
    ) -> str:
        """Generates HTML markup for portfolio items.

        Args:
            data: A list of PortfolioItem protobuf messages.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the portfolio items, or an empty
            string if no data is provided.
        """
        if not data:
            return ""
        html_output: List[str] = []
        for item in data:
            title_text: str = translations.get(
                item.details.title.key, item.details.title.key
            )
            description_text: str = translations.get(
                item.details.description.key, item.details.description.key
            )
            alt_text: str = translations.get(item.image.alt_text.key, "Portfolio image")

            image_html = img(src=item.image.src, alt=alt_text)
            title_html = create_element("h3", content=escape_html(title_text))
            description_html = create_element(
                "p", content=escape_html(description_text)
            )

            div_attrs = {"class": "portfolio-item"}
            if item.id:
                div_attrs["id"] = item.id

            html_output.append(
                create_element(
                    "div",
                    content=f"\n{image_html}\n{title_html}\n{description_html}\n",
                    attributes=div_attrs,
                )
            )
        return "\n".join(html_output)


class TestimonialsHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a list of testimonial items."""

    def generate_html(
        self, data: List[TestimonialItem], translations: Translations
    ) -> str:
        """Generates HTML markup for testimonial items.

        Args:
            data: A list of TestimonialItem protobuf messages.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the testimonial items, or an empty
            string if no data is provided.
        """
        if not data:
            return ""
        html_output: List[str] = []
        for item in data:
            text_content: str = translations.get(item.text.key, item.text.key)
            author_name: str = translations.get(item.author.key, item.author.key)
            img_alt_text: str = translations.get(
                item.author_image.alt_text.key, "User photo"
            )

            image_html = img(src=item.author_image.src, alt=img_alt_text)
            # Ensure quotes are handled correctly if they are part of the content
            paragraph_html = create_element(
                "p", content=f'"{escape_html(text_content)}"'
            )
            author_html = create_element("h4", content=escape_html(author_name))

            html_output.append(
                create_element(
                    "div",
                    content=f"\n{image_html}\n{paragraph_html}\n{author_html}\n",
                    attributes={"class": "testimonial-item"},
                )
            )
        return "\n".join(html_output)


class FeaturesHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a list of feature items."""

    def generate_html(self, data: List[FeatureItem], translations: Translations) -> str:
        """Generates HTML markup for feature items.

        Args:
            data: A list of FeatureItem protobuf messages.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the feature items, or an empty
            string if no data is provided.
        """
        if not data:
            return ""
        html_output: List[str] = []
        for item in data:
            title_text: str = translations.get(
                item.content.title.key, item.content.title.key
            )
            description_text: str = translations.get(
                item.content.description.key, item.content.description.key
            )

            icon_html_content = ""
            if (
                hasattr(item, "icon")
                and item.icon
                and hasattr(item.icon, "svg_content")
                and item.icon.svg_content
            ):
                # Assuming SVG content is safe and doesn't need escaping here.
                # If it could contain user-input that's not SVG, it would need sanitization.
                icon_html_content = item.icon.svg_content

            title_html = create_element("h3", content=escape_html(title_text))
            description_html = create_element(
                "p", content=escape_html(description_text)
            )

            # Ensure icon_html_content is on its own line if present
            inner_content = f"\n{icon_html_content}\n" if icon_html_content else "\n"
            inner_content += f"{title_html}\n{description_html}\n"

            html_output.append(
                create_element(
                    "div",
                    content=inner_content,
                    attributes={"class": "feature-item"},
                )
            )
        return "\n".join(html_output)


class HeroHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a hero section, possibly with variations."""

    def generate_html(
        self, data: Optional[HeroItem], translations: Translations
    ) -> str:
        """Generates HTML for the hero section, selecting a variation.

        Args:
            data: An optional HeroItem protobuf message.
            translations: A dictionary containing translations.

        Returns:
            An HTML string for the hero section, or an HTML comment indicating
            missing data or inability to select a variation.
        """
        if not data or not data.variations:
            return "<!-- Hero data not found or no variations -->"

        selected_variation: Optional[HeroItemContent] = None

        if data.default_variation_id:
            for var in data.variations:
                if var.variation_id == data.default_variation_id:
                    selected_variation = var
                    break

        if not selected_variation and data.variations:
            selected_variation = random.choice(data.variations)

        if not selected_variation:
            return "<!-- Could not select a hero variation -->"

        title_text = translations.get(
            selected_variation.title.key, selected_variation.title.key
        )
        subtitle_text = translations.get(
            selected_variation.subtitle.key, selected_variation.subtitle.key
        )
        cta_link_text = translations.get(
            selected_variation.cta.text.key, selected_variation.cta.text.key
        )

        h1_html = create_element("h1", content=escape_html(title_text))
        p_html = create_element("p", content=escape_html(subtitle_text))
        a_html = create_element(
            "a",
            content=escape_html(cta_link_text),
            attributes={
                "href": selected_variation.cta.uri,
                "class": "cta-button",
            },
        )
        comment_html = f"<!-- Selected variation: {selected_variation.variation_id} -->"

        return f"\n{h1_html}\n{p_html}\n{a_html}\n{comment_html}\n"


class ContactFormHtmlGenerator(HtmlBlockGenerator):
    """Generates an HTML attribute string for a contact form."""

    def generate_html(
        self, data: Optional[ContactFormConfig], translations: Translations
    ) -> str:
        """Generates a string of HTML data attributes for the contact form.

        This generator is intended to produce attributes that can be merged
        into an existing <form> tag in a template.

        Args:
            data: An optional ContactFormConfig protobuf message.
            translations: A dictionary containing translations.

        Returns:
            A string of HTML attributes, or an HTML comment if configuration
            is not found.
        """
        if not data:
            logger.warning(
                "Contact form configuration not found. Returning comment string."
            )
            return "<!-- Contact form configuration not found -->"

        attrs_dict: Dict[str, str] = {}
        if data.form_action_uri:
            # Ensure value is not None before assigning
            attrs_dict["action"] = data.form_action_uri or ""

        attrs_dict["data-form-action-url"] = data.form_action_uri or ""
        attrs_dict["data-success-message"] = translations.get(
            data.success_message_key, "Message sent!"
        )
        attrs_dict["data-error-message"] = translations.get(
            data.error_message_key, "Error sending message."
        )
        attrs_dict["method"] = "POST"

        attrs_list = []
        for key, value in attrs_dict.items():
            # Use html_utils.escape_html for attribute values for consistency,
            # though protobuf strings are generally not expected to have HTML special chars.
            # Keys are assumed to be safe.
            if value is not None:  # Ensure value is a string before escaping
                escaped_value = escape_html(str(value))
                attrs_list.append(f'{key}="{escaped_value}"')
        return " ".join(attrs_list)


class BlogHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a list of blog posts."""

    def generate_html(self, data: List[BlogPost], translations: Translations) -> str:
        """Generates HTML markup for blog posts.

        Args:
            data: A list of BlogPost protobuf messages.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the blog posts, or an empty
            string if no data is provided.
        """
        if not data:
            return ""
        html_output: List[str] = []
        for post in data:
            title_text: str = translations.get(post.title.key, post.title.key)
            excerpt_text: str = translations.get(post.excerpt.key, post.excerpt.key)
            cta_link_text: str = translations.get(post.cta.text.key, post.cta.text.key)

            title_html = create_element("h3", content=escape_html(title_text))
            excerpt_html = create_element("p", content=escape_html(excerpt_text))
            cta_html = create_element(
                "a",
                content=escape_html(cta_link_text),
                attributes={"href": post.cta.uri, "class": "read-more"},
            )

            div_attrs = {"class": "blog-item"}
            if post.id:
                div_attrs["id"] = post.id

            html_output.append(
                create_element(
                    "div",
                    content=f"\n{title_html}\n{excerpt_html}\n{cta_html}\n",
                    attributes=div_attrs,
                )
            )
        return "\n".join(html_output)
