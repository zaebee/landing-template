"""
HTML block generator classes for various content types.

This module provides concrete implementations of the `HtmlBlockGenerator`
protocol for different kinds of data (e.g., portfolio items, testimonials,
features, hero sections, contact forms, and blog posts). Each generator
takes structured data (typically as protobuf messages) and translation data,
and produces an HTML string representation for that block.
"""

import random
from typing import List, Optional

from jinja2 import Environment

# Generated protobuf message types
from generated.blog_post_pb2 import BlogPost
from generated.contact_form_config_pb2 import ContactFormConfig
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import HeroItem, HeroItemContent
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem

from .interfaces import HtmlBlockGenerator, Translations


class PortfolioHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a list of portfolio items using Jinja2."""

    def __init__(self, jinja_env: Environment):
        self.jinja_env = jinja_env

    def generate_html(
        self, data: List[PortfolioItem], translations: Translations
    ) -> str:
        """Generates HTML markup for portfolio items.

        Args:
            data: A list of PortfolioItem protobuf messages.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the portfolio items.
        """
        template = self.jinja_env.get_template("blocks/portfolio.html")
        return str(template.render(items=data, translations=translations))


class TestimonialsHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a list of testimonial items using Jinja2."""

    def __init__(self, jinja_env: Environment):
        self.jinja_env = jinja_env

    def generate_html(
        self, data: List[TestimonialItem], translations: Translations
    ) -> str:
        """Generates HTML markup for testimonial items.

        Args:
            data: A list of TestimonialItem protobuf messages.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the testimonial items.
        """
        template = self.jinja_env.get_template("blocks/testimonials.html")
        return str(template.render(items=data, translations=translations))


class FeaturesHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a list of feature items using Jinja2."""

    def __init__(self, jinja_env: Environment):
        self.jinja_env = jinja_env

    def generate_html(self, data: List[FeatureItem], translations: Translations) -> str:
        """Generates HTML markup for feature items.

        Args:
            data: A list of FeatureItem protobuf messages.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the feature items.
        """
        template = self.jinja_env.get_template("blocks/features.html")
        return str(template.render(items=data, translations=translations))


class HeroHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a hero section using Jinja2."""

    def __init__(self, jinja_env: Environment):
        self.jinja_env = jinja_env

    def generate_html(
        self, data: Optional[HeroItem], translations: Translations
    ) -> str:
        """Generates HTML for the hero section, selecting a variation.

        Args:
            data: An optional HeroItem protobuf message.
            translations: A dictionary containing translations.

        Returns:
            An HTML string for the hero section.
        """
        selected_variation: Optional[HeroItemContent] = None  # Define type once at the correct scope

        if not data or not data.variations:
            # selected_variation remains None, which is handled by the template
            pass
        else:
            # Attempt to find and set the selected_variation
            if data.default_variation_id:
                for var in data.variations:
                    if var.variation_id == data.default_variation_id:
                        selected_variation = var
                        break

            # If no specific variation was found yet (e.g. default_variation_id didn't match or wasn't set)
            # and variations are available, pick one randomly.
            if not selected_variation and data.variations:
                selected_variation = random.choice(data.variations)

        template = self.jinja_env.get_template("blocks/hero.html")
        # The template expects `hero_item` as the context variable for the selected variation
        return str(template.render(hero_item=selected_variation, translations=translations))


class ContactFormHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a contact form section using Jinja2."""

    def __init__(self, jinja_env: Environment):
        self.jinja_env = jinja_env

    def generate_html(
        self, data: Optional[ContactFormConfig], translations: Translations
    ) -> str:
        """Generates HTML markup for the contact form section.

        Args:
            data: An optional ContactFormConfig protobuf message.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the contact form section.
        """
        template = self.jinja_env.get_template("blocks/contact-form.html")
        # The template expects `config` for the ContactFormConfig data
        return str(template.render(config=data, translations=translations))


class BlogHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for a list of blog posts using Jinja2."""

    def __init__(self, jinja_env: Environment):
        self.jinja_env = jinja_env

    def generate_html(self, data: List[BlogPost], translations: Translations) -> str:
        """Generates HTML markup for blog posts.

        Args:
            data: A list of BlogPost protobuf messages.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the blog posts.
        """
        template = self.jinja_env.get_template("blocks/blog.html")
        return str(template.render(items=data, translations=translations))
