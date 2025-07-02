## Feature Ideas

This document outlines potential new features for the landing page generator.

### 1. A/B Testing for Hero Section

*   **Concept**: Allow content creators to define multiple versions of the hero section's content (headline, sub-headline, call-to-action text and link). At build time, one of these variations is randomly selected and injected into the generated HTML pages.
*   **Benefits**:
    *   Enables simple A/B testing of different messaging for the hero section to see which might lead to better engagement or conversion (though tracking would need to be implemented separately).
    *   Allows for easy rotation of hero content without manual HTML edits if multiple valid options exist.
*   **Implementation Sketch**:
    *   **Protobuf**: `hero_item.proto` was modified. `HeroItemContent` now defines the structure for a single variation (title, subtitle, CTA, `variation_id`). `HeroItem` now contains a list (`repeated`) of `HeroItemContent` messages and a `default_variation_id`.
    *   **Data**: `data/hero_item.json` was updated to provide a list of hero content variations. Each variation has a unique `variation_id`.
    *   **Build Script**: `build.py`'s `generate_hero_html` function was updated. It now loads the `HeroItem` data (which includes all variations). It then uses the `random.choice()` method to select one `HeroItemContent` variation from the list. The content of this selected variation is used to populate the hero block. A comment indicating the selected `variation_id` is added to the HTML for easier debugging or identification.
    *   **Future Enhancements**:
        *   Could be extended to allow selection based on an environment variable or a build parameter for more deterministic control over which variation is built.
        *   Client-side selection (e.g., via JavaScript) could also be an option for true runtime A/B testing, but this would require more significant changes and potentially a more complex data structure or client-side logic. The current implementation is build-time selection.
        *   Integration with analytics to track performance of each variation.

---

### 2. Dynamic Sitemap Generation

*   **Concept**: Automatically generate an XML sitemap (`sitemap.xml`) during the build process. This sitemap would list all generated HTML pages (e.g., `index.html`, `index_es.html`, and potentially individual blog post pages if those were ever to become separate HTML files).
*   **Benefits**:
    *   Improves SEO by making it easier for search engines to discover and index all content on the site.
    *   Ensures the sitemap is always up-to-date with the site's structure, especially as new languages or pages are added.
    *   No manual sitemap creation or maintenance required.
*   **Implementation Sketch**:
    *   **Build Script (`build.py`)**:
        *   After all HTML files are generated, the script would collect a list of their filenames.
        *   It would then construct an XML string conforming to the sitemap protocol (e.g., using `xml.etree.ElementTree`).
        *   Each URL in the sitemap would be the absolute URL (requiring a base URL from `config.json` or a new config option).
        *   The script would write the XML string to `sitemap.xml` in the root output directory.
    *   **Configuration (`public/config.json`)**:
        *   Add a `site_base_url` field (e.g., "https://www.example.com") to be used for generating absolute URLs in the sitemap.

---

### 3. Basic Analytics Integration Snippet

*   **Concept**: Allow users to easily embed a web analytics tracking snippet (e.g., Google Analytics, Plausible, Simple Analytics) into all generated pages. The tracking ID or relevant configuration would be provided in `config.json`.
*   **Benefits**:
    *   Enables site owners to gather visitor data without manually editing HTML templates.
    *   Centralizes analytics configuration.
    *   Can be easily toggled on or off.
*   **Implementation Sketch**:
    *   **Configuration (`public/config.json`)**:
        *   Add an `analytics` object, e.g.:
            ```json
            "analytics": {
              "provider": "google_analytics", // or "plausible", "none"
              "tracking_id": "UA-XXXXX-Y", // for GA
              "domain": "yourdomain.com" // for Plausible
            }
            ```
    *   **Build Script (`build.py`)**:
        *   In `assemble_translated_page` (or a similar function that constructs the final HTML), check the `analytics` config.
        *   If a provider is specified and configured, inject the appropriate JavaScript snippet into the `<head>` or near the closing `</body>` tag of each HTML page. The snippet would be a template string with placeholders for `tracking_id` or `domain`.
    *   **HTML Structure**: Ensure the base HTML template (`index.html`) has a clear placeholder or is structured so the script can easily inject the analytics snippet (e.g., before `</head>` or `</body>`).

---

### 4. Customizable Social Media Meta Tags

*   **Concept**: Allow customization of Open Graph (Facebook, LinkedIn, etc.) and Twitter Card meta tags for each page, with fallbacks to site-wide defaults. This would initially focus on the main `index_<lang>.html` pages.
*   **Benefits**:
    *   Improves how content appears when shared on social media platforms, potentially increasing engagement.
    *   Provides control over titles, descriptions, and images used in social shares.
*   **Implementation Sketch**:
    *   **Protobuf (`common.proto` or new `meta_tags.proto`)**:
        *   Define a `SocialMetaTags` message:
            ```proto
            message SocialMetaTags {
              I18nString og_title = 1;
              I18nString og_description = 2;
              Image og_image = 3; // Reusing common.Image
              I18nString twitter_title = 4;
              I18nString twitter_description = 5;
              Image twitter_image = 6;
              string twitter_card_type = 7; // e.g., "summary", "summary_large_image"
            }
            ```
    *   **Data (`data/site_meta.json` or similar)**:
        *   A new JSON file to hold site-wide default social meta tags, structured according to `SocialMetaTags`.
        *   Potentially extend `hero_item.json` or other page-specific data files to include an optional `social_meta_tags` field if per-page customization beyond simple title/description is desired for specific blocks that might define a "page". For initial implementation, site-wide defaults applied to each generated index page would be simpler.
    *   **Configuration (`public/config.json`)**:
        *   Reference the new `site_meta.json` data file.
        *   Possibly add a flag to enable/disable this feature.
    *   **Build Script (`build.py`)**:
        *   Load the default social meta tags.
        *   In `assemble_translated_page` (or where the `<head>` is constructed):
            *   Retrieve translated values for title, description from the social meta tags data.
            *   Construct and inject `<meta>` tags for Open Graph (e.g., `og:title`, `og:description`, `og:image`, `og:url`, `og:type`) and Twitter Card (e.g., `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`).
            *   The `og:url` would be the canonical URL for the page being generated.
            *   `og:type` could be defaulted to "website".
            *   If a page-specific title/description is available (e.g. from Hero block), it could override the default social meta tags for title/description.
