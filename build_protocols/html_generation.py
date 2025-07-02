import random
from typing import Any, Dict, List, Union

# Assuming protos are compiled and available in generated.*
from generated.blog_post_pb2 import BlogPost
from generated.contact_form_config_pb2 import ContactFormConfig
from generated.feature_item_pb2 import FeatureItem
from generated.hero_item_pb2 import HeroItem
from generated.portfolio_item_pb2 import PortfolioItem
from generated.testimonial_item_pb2 import TestimonialItem

# Type alias from build.py, consider moving to a shared types.py if more are added
Translations = Dict[str, str]


def generate_portfolio_html(
    items: List[PortfolioItem], translations: Translations
) -> str:
    """Generates HTML for portfolio items."""
    html_output: List[str] = []
    for item in items:
        title: str = translations.get(item.details.title.key, item.details.title.key)
        description: str = translations.get(
            item.details.description.key, item.details.description.key
        )
        alt_text: str = translations.get(
            item.image.alt_text.key, "Portfolio image"
        )  # Default alt

        html_output.append(
            f"""
        <div class="portfolio-item">
            <img src="{item.image.src}" alt="{alt_text}">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """
        )
    return "\n".join(html_output)


def generate_testimonials_html(
    items: List[TestimonialItem], translations: Translations
) -> str:
    """Generates HTML for testimonial items."""
    html_output: List[str] = []
    for item in items:
        text: str = translations.get(item.text.key, item.text.key)
        author: str = translations.get(item.author.key, item.author.key)
        img_alt: str = translations.get(
            item.author_image.alt_text.key, "User photo"
        )  # Default alt text
        html_output.append(
            f"""
        <div class="testimonial-item">
            <img src="{item.author_image.src}" alt="{img_alt}">
            <p>{text}</p>
            <h4>{author}</h4>
        </div>
        """
        )
    return "\n".join(html_output)


def generate_features_html(items: List[FeatureItem], translations: Translations) -> str:
    """Generates HTML for feature items."""
    html_output: List[str] = []
    for item in items:
        title: str = translations.get(item.content.title.key, item.content.title.key)
        description: str = translations.get(
            item.content.description.key, item.content.description.key
        )
        html_output.append(
            f"""
        <div class="feature-item">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """
        )
    return "\n".join(html_output)


def generate_hero_html(hero_data: Union[HeroItem, None], translations: Translations) -> str:
    """Generates HTML for the hero section, selecting a variation."""
    if not hero_data or not hero_data.variations:
        return "<!-- Hero data not found or no variations -->"

    selected_variation = None
    if hero_data.variations:
        selected_variation = random.choice(hero_data.variations)

    if not selected_variation:
        default_id = hero_data.default_variation_id
        for var in hero_data.variations:
            if var.variation_id == default_id:
                selected_variation = var
                break
        if not selected_variation and hero_data.variations: # If default_id not found, pick first
            selected_variation = hero_data.variations[0]

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


def generate_contact_form_html(
    config: Union[ContactFormConfig, None], translations: Translations
) -> str:
    """
    Generates HTML for the contact form, including data attributes for AJAX submission.
    """
    if not config:
        return "<!-- Contact form configuration not found -->"

    return (
        f'data-form-action-url="{config.form_action_url}"\n'
        f'    data-success-message="{translations.get(config.success_message_key, "Message sent!")}"\n'
        f'    data-error-message="{translations.get(config.error_message_key, "Error sending message.")}"'
    )


def generate_blog_html(posts: List[BlogPost], translations: Translations) -> str:
    """Generates HTML for blog posts."""
    html_output: List[str] = []
    for post in posts:
        title: str = translations.get(post.title.key, post.title.key)
        excerpt: str = translations.get(post.excerpt.key, post.excerpt.key)
        cta_text: str = translations.get(post.cta.text.key, post.cta.text.key)
        html_output.append(
            f"""
        <div class="blog-item">
            <h3>{title}</h3>
            <p>{excerpt}</p>
            <a href="{post.cta.link}" class="read-more">{cta_text}</a>
        </div>
        """
        )
    return "\n".join(html_output)
