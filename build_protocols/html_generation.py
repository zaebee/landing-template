"""
HTML block generator classes for various content types.

This module provides concrete implementations of the `HtmlBlockGenerator`
protocol for different kinds of data (e.g., portfolio items, testimonials,
features, hero sections, contact forms, and blog posts). Each generator
takes structured data (typically as protobuf messages) and translation data,
and produces an HTML string representation for that block.
"""

import random
import textwrap
from typing import List, Optional

# Generated protobuf message types
from generated.blog_post_pb2 import BlogPost
from generated.contact_form_config_pb2 import ContactFormConfig
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import HeroItem, HeroItemContent
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem

from .interfaces import HtmlBlockGenerator, Translations


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
            title: str = translations.get(
                item.details.title.key, item.details.title.key
            )
            description: str = translations.get(
                item.details.description.key, item.details.description.key
            )
            alt_text: str = translations.get(item.image.alt_text.key, "Portfolio image")

            html_output.append(
                textwrap.dedent(f"""\
                    <div class="portfolio-item" id="{item.id if item.id else ""}">
                        <img src="{item.image.src}" alt="{alt_text}">
                        <h3>{title}</h3>
                        <p>{description}</p>
                    </div>
                """)
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
            text: str = translations.get(item.text.key, item.text.key)
            author: str = translations.get(item.author.key, item.author.key)
            img_alt: str = translations.get(
                item.author_image.alt_text.key, "User photo"
            )
            html_output.append(
                textwrap.dedent(f"""\
                    <div class="testimonial-item">
                        <img src="{item.author_image.src}" alt="{img_alt}">
                        <p>"{text}"</p>
                        <h4>{author}</h4>
                    </div>
                """)
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
            title: str = translations.get(
                item.content.title.key, item.content.title.key
            )
            description: str = translations.get(
                item.content.description.key, item.content.description.key
            )
            # Icon handling: Assumes icon.svg_content contains raw SVG if present.
            icon_html = ""
            if (
                hasattr(item, "icon")  # Check if icon field exists
                and item.icon  # Check if icon message is set
                and hasattr(
                    item.icon, "svg_content"
                )  # Check if svg_content field exists
                and item.icon.svg_content  # Check if svg_content has a value
            ):
                icon_html = item.icon.svg_content

            html_output.append(
                textwrap.dedent(f"""\
                    <div class="feature-item">
                        {icon_html}
                        <h3>{title}</h3>
                        <p>{description}</p>
                    </div>
                """)
            )
        return "\n".join(html_output)


class HeroHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a hero section, possibly with variations."""

    def generate_html(
        self, data: Optional[HeroItem], translations: Translations
    ) -> str:
        """Generates HTML for the hero section, selecting a variation.

        If a default variation ID is specified in the data and found, it's used.
        Otherwise, if variations exist, one is chosen randomly.

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

        title = translations.get(
            selected_variation.title.key, selected_variation.title.key
        )
        subtitle = translations.get(
            selected_variation.subtitle.key, selected_variation.subtitle.key
        )
        cta_text = translations.get(
            selected_variation.cta.text.key, selected_variation.cta.text.key
        )

        return textwrap.dedent(f"""\
            <h1>{title}</h1>
            <p>{subtitle}</p>
            <a href="{selected_variation.cta.uri}" class="cta-button">{cta_text}</a>
            <!-- Selected variation: {selected_variation.variation_id} -->
        """)


class ContactFormHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML data attributes string for a contact form."""

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
            return "<!-- Contact form configuration not found -->"

        attrs = []
        if data.form_action_uri:
            attrs.append(f'action="{data.form_action_uri}"')

        # These data attributes are for client-side JavaScript to use.
        attrs.append(f'data-form-action-url="{data.form_action_uri}"')
        attrs.append(
            f'data-success-message="{translations.get(data.success_message_key, "Message sent!")}"'
        )
        attrs.append(
            f'data-error-message="{translations.get(data.error_message_key, "Error sending message.")}"'
        )
        attrs.append('method="POST"')  # Standard method for form submission
        return " ".join(attrs)


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
            title: str = translations.get(post.title.key, post.title.key)
            excerpt: str = translations.get(post.excerpt.key, post.excerpt.key)
            cta_text: str = translations.get(post.cta.text.key, post.cta.text.key)
            html_output.append(
                textwrap.dedent(f"""\
                    <div class="blog-item" id="{post.id if post.id else ""}">
                        <h3>{title}</h3>
                        <p>{excerpt}</p>
                        <a href="{post.cta.uri}" class="read-more">{cta_text}</a>
                    </div>
                """)
            )
        return "\n".join(html_output)
