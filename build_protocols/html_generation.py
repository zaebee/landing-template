"""
HTML block generator classes for various content types.

This module provides concrete implementations of the `HtmlBlockGenerator`
protocol for different kinds of data (e.g., portfolio items, testimonials,
features, hero sections, contact forms, and blog posts). Each generator
takes structured data (typically as protobuf messages) and translation data,
and produces an HTML string representation for that block.
"""

import random
from typing import Any, Callable, Dict, List, Optional, Type

from jinja2 import Environment

# Generated protobuf message types
from generated.blog_post_pb2 import BlogPost
from generated.contact_form_config_pb2 import ContactFormConfig
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import HeroItem, HeroItemContent
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem

from .interfaces import HtmlBlockGenerator, Translations

# Registry for HTML block generators
HTML_GENERATOR_REGISTRY: Dict[str, Type[HtmlBlockGenerator]] = {}


def register_html_generator(
    block_name: str, template_to_render: str, data_key: str = "items"
) -> Callable[[Type[HtmlBlockGenerator]], Type[HtmlBlockGenerator]]:
    """
    A decorator to register an HTML generator class for a specific block name,
    associate it with a template file, and define the data key for the template.
    """

    def decorator(cls: Type[HtmlBlockGenerator]) -> Type[HtmlBlockGenerator]:
        if block_name in HTML_GENERATOR_REGISTRY:
            # Use a simple print for warnings if logging is not set up
            print(
                f"Warning: HTML generator for block '{block_name}' is being overridden by {cls.__name__}"
            )
        HTML_GENERATOR_REGISTRY[block_name] = cls
        cls.template_to_render = template_to_render
        cls.data_key_for_template = data_key  # Store the data key on the class
        return cls

    return decorator


class BaseHtmlGenerator(HtmlBlockGenerator):
    """
    A base class for common HTML block generators that provides a default
    implementation for __init__ and generate_html.
    """

    template_to_render: str  # Expected to be set by decorator or subclass
    data_key_for_template: str = "items"  # Default key for passing data to template

    def __init__(self, jinja_env: Environment):
        self.jinja_env = jinja_env

    def generate_html(self, data: Any, translations: Translations) -> str:
        """
        Generates an HTML string for a content block using a common pattern.
        Assumes 'template_to_render' and 'data_key_for_template' are set
        (usually by the @register_html_generator decorator on the subclass).
        """
        if not data:
            # This basic guard might need to be overridden by subclasses
            # if they handle 'None' data differently (e.g. Hero, ContactForm)
            return ""

        # Ensure template_to_render is set, which should be guaranteed by the decorator
        # and protocol, but a runtime check or better initialization could be added if needed.
        if (
            not hasattr(self.__class__, "template_to_render")
            or not self.__class__.template_to_render
        ):
            raise ValueError(
                f"template_to_render not set for {self.__class__.__name__}"
            )

        template = self.jinja_env.get_template(self.__class__.template_to_render)

        context = {
            self.__class__.data_key_for_template: data,
            "translations": translations,
        }
        return str(template.render(**context))


@register_html_generator(
    block_name="portfolio.html", template_to_render="blocks/portfolio.html"
)  # data_key="items" is default
class PortfolioHtmlGenerator(BaseHtmlGenerator):
    """Generates HTML for a list of portfolio items using Jinja2."""

    # __init__ is inherited from BaseHtmlGenerator

    # Override generate_html for specific type hinting, if desired,
    # otherwise, the BaseHtmlGenerator.generate_html would be sufficient if data_key matches.
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
        # Since data_key_for_template defaults to "items" in BaseHtmlGenerator
        # and this class uses "items", we can rely on the superclass method.
        return super().generate_html(data, translations)


@register_html_generator(
    block_name="testimonials.html", template_to_render="blocks/testimonials.html"
)  # data_key="items" is default
class TestimonialsHtmlGenerator(BaseHtmlGenerator):
    """Generates HTML for a list of testimonial items using Jinja2."""

    # __init__ is inherited

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
        return super().generate_html(data, translations)


@register_html_generator(
    block_name="features.html", template_to_render="components/features/features.html"
)  # data_key="items" is default
class FeaturesHtmlGenerator(BaseHtmlGenerator):
    """Generates HTML for a list of feature items using Jinja2."""

    # __init__ is inherited

    def generate_html(self, data: List[FeatureItem], translations: Translations) -> str:
        """Generates HTML markup for feature items.

        Args:
            data: A list of FeatureItem protobuf messages.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the feature items.
        """
        return super().generate_html(data, translations)


@register_html_generator(
    block_name="hero.html", template_to_render="blocks/hero.html"
)  # No data_key needed as it has custom generate_html
class HeroHtmlGenerator(BaseHtmlGenerator):
    """Generates HTML for a hero section using Jinja2."""

    # __init__ is inherited from BaseHtmlGenerator

    # generate_html is custom due to variation logic
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
        if (
            not selected_variation
        ):  # Already know data.variations is not empty from the guard clause
            selected_variation = random.choice(data.variations)

        template = self.jinja_env.get_template(self.__class__.template_to_render)
        # The template expects `hero_item` as the context variable for the selected variation
        return str(
            template.render(hero_item=selected_variation, translations=translations)
        )


@register_html_generator(
    block_name="contact-form.html",
    template_to_render="blocks/contact-form.html",
    data_key="config",
)
class ContactFormHtmlGenerator(BaseHtmlGenerator):
    """Generates HTML for a contact form section using Jinja2."""

    # __init__ is inherited

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
        # BaseHtmlGenerator.generate_html handles the 'if not data'
        # and rendering using the 'data_key_for_template' which is now "config".
        return super().generate_html(data, translations)


@register_html_generator(
    block_name="blog.html", template_to_render="components/blog/blog.html"
)
class BlogHtmlGenerator(BaseHtmlGenerator):
    """Generates HTML for a list of blog posts using Jinja2, utilizing SADS attributes."""

    # __init__ is inherited

    def generate_html(self, data: List[BlogPost], translations: Translations) -> str:
        """Generates HTML markup for blog posts.

        Args:
            data: A list of BlogPost protobuf messages.
            translations: A dictionary containing translations.

        Returns:
            An HTML string representing the blog posts.
        """
        return super().generate_html(data, translations)
