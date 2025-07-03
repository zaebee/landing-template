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
from generated.common_pb2 import I18nString # Added import
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
        if not data:
            return ""
        template = self.jinja_env.get_template("components/portfolio/portfolio.html") # Updated path
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
        if not data:
            return ""
        template = self.jinja_env.get_template("components/testimonials/testimonials.html") # Updated path
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
        if not data:
            return ""
        template = self.jinja_env.get_template("components/features/features.html") # Updated path
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
        if not data or not data.variations:
            return "<!-- Hero data not found or no variations -->"

        selected_variation: Optional[HeroItemContent] = None

        # Attempt to find and set the selected_variation
        if data.default_variation_id:
            for var in data.variations:
                if var.variation_id == data.default_variation_id:
                    selected_variation = var
                    break

        # If no specific variation was found yet (e.g. default_variation_id didn't match or wasn't set)
        # and variations are available, pick one randomly. (This condition also ensures data.variations is not empty)
        if not selected_variation: # Already know data.variations is not empty from the guard clause
            selected_variation = random.choice(data.variations)

        template = self.jinja_env.get_template("components/hero/hero.html") # Updated path
        # The template expects `hero_item` as the context variable for the selected variation
        return str(
            template.render(hero_item=selected_variation, translations=translations)
        )


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
        if not data:
            return ""
        template = self.jinja_env.get_template("components/contact-form/contact-form.html") # Updated path
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
        if not data:
            return ""
        template = self.jinja_env.get_template("components/blog/blog.html") # Updated path
        return str(template.render(items=data, translations=translations))


class DnaVisualizerHtmlGenerator(HtmlBlockGenerator):
    """Generates HTML for the DNA visualizer component using Jinja2."""

    def __init__(self, jinja_env: Environment):
        self.jinja_env = jinja_env

    def generate_html(
        self, data: Optional[I18nString], translations: Translations # data/dna.json is parsed as I18nString
    ) -> str:
        """Generates HTML markup for the DNA visualizer.

        Args:
            data: An I18nString message, potentially from dna.json. Currently unused for sequence.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the DNA visualizer.
        """
        # For now, data is not used, but the signature requires it.
        # Future enhancements might pass DNA sequence data here.
        template = self.jinja_env.get_template("components/dna-visualizer/dna-visualizer.html")
        # Pass any necessary context. For now, only translations.
        # If the component expects specific data (e.g. a dna_sequence variable),
        # it would be passed here.
        return str(template.render(translations=translations, dna_sequence_data=None)) # Pass dna_sequence_data as None for now
