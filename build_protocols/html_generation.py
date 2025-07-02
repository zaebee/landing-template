import random
from typing import List, Optional  # Added Optional

# Assuming protos are compiled and available in generated.*
from generated.blog_post_pb2 import BlogPost
from generated.contact_form_config_pb2 import ContactFormConfig
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import (  # Changed HeroVariation to HeroItemContent
    HeroItem,
    HeroItemContent,
)
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem

from .interfaces import HtmlBlockGenerator, Translations

# TranslatableString might be in common.proto, but not explicitly used by current functions after re-read.
# If it were, it would be: from generated.common_pb2 import TranslatableString


class PortfolioHtmlGenerator(HtmlBlockGenerator):
    def generate_html(self, items: List[PortfolioItem], translations: Translations) -> str:
        """Generates HTML for portfolio items."""
        if not items:
            return ""
        html_output: List[str] = []
        for item in items:
            title: str = translations.get(item.details.title.key, item.details.title.key)
            description: str = translations.get(
                item.details.description.key, item.details.description.key
            )
            alt_text: str = translations.get(
                item.image.alt_text.key, "Portfolio image"
            )

            html_output.append(
                f"""
            <div class="portfolio-item" id="{item.id if item.id else ''}">
                <img src="{item.image.src}" alt="{alt_text}">
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """
            )
        return "\n".join(html_output)


class TestimonialsHtmlGenerator(HtmlBlockGenerator):
    def generate_html(self, items: List[TestimonialItem], translations: Translations) -> str:
        """Generates HTML for testimonial items."""
        if not items:
            return ""
        html_output: List[str] = []
        for item in items:
            text: str = translations.get(item.text.key, item.text.key)
            author: str = translations.get(item.author.key, item.author.key)
            img_alt: str = translations.get(
                item.author_image.alt_text.key, "User photo"
            )
            html_output.append(
                f"""
            <div class="testimonial-item">
                <img src="{item.author_image.src}" alt="{img_alt}">
                <p>"{text}"</p>
                <h4>{author}</h4>
            </div>
            """
            ) # Added quotes around text for typical testimonial style
        return "\n".join(html_output)


class FeaturesHtmlGenerator(HtmlBlockGenerator):
    def generate_html(self, items: List[FeatureItem], translations: Translations) -> str:
        """Generates HTML for feature items."""
        if not items:
            return ""
        html_output: List[str] = []
        for item in items:
            title: str = translations.get(item.content.title.key, item.content.title.key)
            description: str = translations.get(
                item.content.description.key, item.content.description.key
            )
            # Assuming icon handling is simple or done via CSS/template
            icon_html = ""
            if hasattr(item, 'icon') and item.icon and hasattr(item.icon, 'svg_content') and item.icon.svg_content:
                icon_html = item.icon.svg_content

            html_output.append(
                f"""
            <div class="feature-item">
                {icon_html}
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """
            )
        return "\n".join(html_output)


class HeroHtmlGenerator(HtmlBlockGenerator):
    def generate_html(self, hero_data: Optional[HeroItem], translations: Translations) -> str:
        """Generates HTML for the hero section, selecting a variation."""
        if not hero_data or not hero_data.variations:
            return "<!-- Hero data not found or no variations -->"

        selected_variation: Optional[HeroItemContent] = None # Explicit type

        # Try to find the default variation
        if hero_data.default_variation_id:
            for var in hero_data.variations:
                if var.variation_id == hero_data.default_variation_id:
                    selected_variation = var
                    break

        # If default not found or not specified, and variations exist, pick randomly
        if not selected_variation and hero_data.variations:
            selected_variation = random.choice(hero_data.variations)

        # If still no variation selected (e.g., empty variations list initially)
        if not selected_variation:
            return "<!-- Could not select a hero variation -->"

        title = translations.get(selected_variation.title.key, selected_variation.title.key)
        subtitle = translations.get(
            selected_variation.subtitle.key, selected_variation.subtitle.key
        )
        cta_text = translations.get(
            selected_variation.cta.text.key, selected_variation.cta.text.key
        )

        return f"""
        <h1>{title}</h1>
        <p>{subtitle}</p>
        <a href="{selected_variation.cta.link}" class="cta-button">{cta_text}</a>
        <!-- Selected variation: {selected_variation.variation_id} -->
        """


class ContactFormHtmlGenerator(HtmlBlockGenerator):
    def generate_html(self, config: Optional[ContactFormConfig], translations: Translations) -> str:
        """
        Generates HTML data attributes string for the contact form.
        """
        if not config:
            return "<!-- Contact form configuration not found -->"

        # The original function returned a string of attributes.
        # This is suitable if the block template has <form {{placeholder}} >
        # The interface HtmlBlockGenerator.generate_html expects full HTML string.
        # For now, let's assume this generator's output is still just the attribute string,
        # and the build script will handle placing it.
        # Or, the block template itself must be very simple, just these attributes.
        # Given the name "generate_contact_form_html", it implies it should generate the form.
        # However, the existing code only generates attributes.
        # Let's stick to generating attributes as per original logic for minimal change.
        # This means the placeholder in contact-form.html must be for attributes.

        attrs = []
        # Use form_action_url for the action attribute
        if config.form_action_url:
            attrs.append(f'action="{config.form_action_url}"')

        # Data attributes for AJAX handling
        attrs.append(f'data-form-action-url="{config.form_action_url}"') # Keep for JS if it uses this
        attrs.append(f'data-success-message="{translations.get(config.success_message_key, "Message sent!")}"')
        attrs.append(f'data-error-message="{translations.get(config.error_message_key, "Error sending message.")}"')

        # Default method to POST, as it's common for contact forms.
        # This is not configurable via proto currently.
        attrs.append('method="POST"')

        # No 'id' or other attributes like 'enctype' are defined in the proto, so they are omitted.
        # If an ID is needed, it should be static in the block template or added to proto.
        return " ".join(attrs)


class BlogHtmlGenerator(HtmlBlockGenerator):
    def generate_html(self, posts: List[BlogPost], translations: Translations) -> str:
        """Generates HTML for blog posts."""
        if not posts:
            return ""
        html_output: List[str] = []
        for post in posts:
            title: str = translations.get(post.title.key, post.title.key)
            excerpt: str = translations.get(post.excerpt.key, post.excerpt.key)
            cta_text: str = translations.get(post.cta.text.key, post.cta.text.key)
            html_output.append(
                f"""
            <div class="blog-item" id="{post.id if post.id else ''}">
                <h3>{title}</h3>
                <p>{excerpt}</p>
                <a href="{post.cta.link}" class="read-more">{cta_text}</a>
            </div>
            """
            )
        return "\n".join(html_output)

# The old functions can be removed or aliased if necessary for tests,
# but the build script should use the new classes.
# Example alias (less ideal than direct class usage):
# generate_portfolio_html = PortfolioHtmlGenerator().generate_html
