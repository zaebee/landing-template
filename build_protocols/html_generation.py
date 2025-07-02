import random
from typing import List, Optional

from generated.blog_post_pb2 import BlogPost
from generated.contact_form_config_pb2 import ContactFormConfig
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import (
    HeroItem,
    HeroItemContent,
)
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem

from .interfaces import HtmlBlockGenerator, Translations


class PortfolioHtmlGenerator(HtmlBlockGenerator):
    def generate_html(
        self, data: List[PortfolioItem], translations: Translations
    ) -> str:
        """Generates HTML for portfolio items."""
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
    def generate_html(
        self, data: List[TestimonialItem], translations: Translations
    ) -> str:
        """Generates HTML for testimonial items."""
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
                f"""
            <div class="testimonial-item">
                <img src="{item.author_image.src}" alt="{img_alt}">
                <p>"{text}"</p>
                <h4>{author}</h4>
            </div>
            """
            )
        return "\n".join(html_output)


class FeaturesHtmlGenerator(HtmlBlockGenerator):
    def generate_html(self, data: List[FeatureItem], translations: Translations) -> str:
        """Generates HTML for feature items."""
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
            # Assuming icon handling is simple or done via CSS/template
            icon_html = ""
            if (
                hasattr(item, "icon")
                and item.icon
                and hasattr(item.icon, "svg_content")
                and item.icon.svg_content
            ):
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
    def generate_html(
        self, data: Optional[HeroItem], translations: Translations
    ) -> str:
        """Generates HTML for the hero section, selecting a variation."""
        if not data or not data.variations:
            return "<!-- Hero data not found or no variations -->"

        selected_variation: Optional[HeroItemContent] = None  # Explicit type

        # Try to find the default variation
        if data.default_variation_id:
            for var in data.variations:
                if var.variation_id == data.default_variation_id:
                    selected_variation = var
                    break

        # If default not found or not specified, and variations exist, pick randomly
        if not selected_variation and data.variations:
            selected_variation = random.choice(data.variations)

        # If still no variation selected (e.g., empty variations list initially)
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

        return f"""
        <h1>{title}</h1>
        <p>{subtitle}</p>
        <a href="{selected_variation.cta.uri}" class="cta-button">{cta_text}</a>
        <!-- Selected variation: {selected_variation.variation_id} -->
        """


class ContactFormHtmlGenerator(HtmlBlockGenerator):
    def generate_html(
        self, data: Optional[ContactFormConfig], translations: Translations
    ) -> str:
        """
        Generates HTML data attributes string for the contact form.
        """
        if not data:
            return "<!-- Contact form configuration not found -->"

        attrs = []
        # Use form_action_url for the action attribute
        if data.form_action_uri:
            attrs.append(f'action="{data.form_action_uri}"')

        attrs.append(f'data-form-action-url="{data.form_action_uri}"')
        attrs.append(
            f'data-success-message="{translations.get(data.success_message_key, "Message sent!")}"'
        )
        attrs.append(
            f'data-error-message="{translations.get(data.error_message_key, "Error sending message.")}"'
        )

        attrs.append('method="POST"')
        return " ".join(attrs)


class BlogHtmlGenerator(HtmlBlockGenerator):
    def generate_html(self, data: List[BlogPost], translations: Translations) -> str:
        """Generates HTML for blog posts."""
        if not data:
            return ""
        html_output: List[str] = []
        for post in data:
            title: str = translations.get(post.title.key, post.title.key)
            excerpt: str = translations.get(post.excerpt.key, post.excerpt.key)
            cta_text: str = translations.get(post.cta.text.key, post.cta.text.key)
            html_output.append(
                f"""
            <div class="blog-item" id="{post.id if post.id else ''}">
                <h3>{title}</h3>
                <p>{excerpt}</p>
                <a href="{post.cta.uri}" class="read-more">{cta_text}</a>
            </div>
            """
            )
        return "\n".join(html_output)
