# Landing Page Generator: Feature Roadmap & Ideas

## Introduction

This document outlines potential new features and enhancements for the landing page generator. Its purpose is to provide a clear overview of ideas, facilitate discussion, and help prioritize development efforts. Each feature is described with its core concept, benefits, an estimated priority, impact, effort, and a technical implementation sketch. This is a living document and should be updated as new ideas emerge or priorities shift.

## Feature Summary & Prioritization

The table below offers a quick glance at all proposed features, their intended function, and their strategic assessment.

| Feature                               | Summary                                                                      | Priority | Impact | Effort |
| :------------------------------------ | :--------------------------------------------------------------------------- | :------- | :----- | :----- |
| Dynamic Sitemap Generation            | Automatically create `sitemap.xml` for improved SEO discoverability.         | High     | High   | Medium |
| Automated Image Optimization          | Optimize images (compress, convert format) during build for performance.   | High     | High   | Medium |
| Basic Analytics Integration           | Easily embed analytics tracking snippets (e.g., Google Analytics) via config. | High     | Medium | Low    |
| Versioned Static Assets (CSS/JS)      | Append content hash/timestamp to static asset URLs for cache busting.        | High     | Medium | Low    |
| A/B Testing for Hero Section          | Randomly select hero content at build time for simple A/B tests.             | Medium   | Medium | Medium |
| Customizable Social Media Meta Tags | Define Open Graph/Twitter tags for richer social media sharing.              | Medium   | Medium | Medium |
| Theme Customization via `config.json` | Allow theme selection or basic color palette customization via `config.json`. | Low      | Low    | Medium |

---

## Detailed Feature Proposals

### 1. Dynamic Sitemap Generation

*   **Priority**: High
*   **Impact**: High
*   **Effort**: Medium
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

### 2. Automated Image Optimization

*   **Priority**: High
*   **Impact**: High
*   **Effort**: Medium
*   **Concept**: Integrate an image optimization step into the build process. When images are referenced in data files (e.g., `hero_item.json`, `portfolio_items.json`), the build script would find these images, create optimized versions (e.g., compressed JPEGs, WebP format), and update the references in the generated HTML to point to these optimized images.
*   **Benefits**:
    *   Improves page load speed significantly.
    *   Reduces bandwidth consumption.
    *   Enhances SEO and user experience.
    *   Automates a typically manual optimization task.
*   **Implementation Sketch**:
    *   **Dependencies**: Add a Python image processing library like `Pillow` or `Wand`.
    *   **Configuration (`public/config.json`)**:
        *   Add an `image_optimization` object:
            ```json
            "image_optimization": {
              "enabled": true,
              "quality": 85, // For JPEGs
              "format": "webp", // "original", "webp" - convert to WebP if possible
              "output_dir": "public/optimized_images/"
            }
            ```
    *   **Build Script (`build.py`)**:
        *   Create a new service, e.g., `ImageOptimizer`.
        *   During data loading or just before HTML generation for blocks containing images (Hero, Portfolio, Testimonials):
            *   Identify image paths from Protobuf messages (e.g., `Image.src`).
            *   If optimization is enabled:
                *   Construct a new path for the optimized image in `image_optimization.output_dir`.
                *   If the optimized image doesn't exist or the source is newer:
                    *   Use the chosen library to open the source image, resize (optional, could be another config), convert format (e.g., to WebP), and save it to the output directory with specified quality.
                *   Update the `src` field in the Protobuf message *in memory* to point to the optimized image path.
        *   The HTML generation functions would then use these updated paths.
    *   **File Structure**: Original images might reside in `public/images/` (or specified in data files), and optimized versions would be saved to `public/optimized_images/`. The `.gitignore` should be updated to ignore the `optimized_images` directory.
    *   **Considerations**:
        *   Handling of external image URLs (skip optimization or attempt to download and optimize).
        *   Caching of optimized images to avoid reprocessing unchanged images.

---

### 3. Basic Analytics Integration Snippet

*   **Priority**: High
*   **Impact**: Medium
*   **Effort**: Low
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

### 4. Versioned Static Assets (CSS/JS)

*   **Priority**: High
*   **Impact**: Medium
*   **Effort**: Low
*   **Concept**: Implement a cache-busting mechanism for static assets like `public/style.css` and any JavaScript files. During the build, append a content hash or build timestamp to asset URLs in the generated HTML (e.g., `style.css?v=abcdef12345`).
*   **Benefits**:
    *   Ensures users always receive the latest version of CSS/JS files after an update, avoiding issues caused by browser caching of stale assets.
    *   Improves site reliability when deploying updates.
*   **Implementation Sketch**:
    *   **Build Script (`build.py`)**:
        *   In `BuildOrchestrator` or `DefaultPageBuilder`:
            *   When linking `public/style.css` (or any other project-specific JS files if they were added):
                *   Calculate a hash (e.g., MD5 or SHA256) of the file's content.
                *   Alternatively, use a build timestamp. A content hash is generally preferred as it only changes when the file content changes.
                *   Append this hash as a query parameter to the asset URL in the generated HTML:
                    ```html
                    <link rel="stylesheet" href="style.css?v={content_hash}">
                    ```
            *   This logic would typically be in `DefaultPageBuilder.assemble_translated_page()` where the final HTML `<head>` is constructed, or wherever the CSS link is added.
    *   **Configuration (`public/config.json`)**:
        *   Could add a configuration option to enable/disable this or choose the versioning method (hash vs. timestamp), though content hashing is a good default.
        ```json
        "asset_versioning": {
          "enabled": true,
          "method": "content_hash" // "content_hash" or "timestamp"
        }
        ```
    *   **Helper Function**: A utility function `get_asset_version(file_path, method)` could be created to compute the version string.

---

### 5. A/B Testing for Hero Section

*   **Priority**: Medium
*   **Impact**: Medium
*   **Effort**: Medium
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

### 6. Customizable Social Media Meta Tags

*   **Priority**: Medium
*   **Impact**: Medium
*   **Effort**: Medium
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

---

### 7. Theme Customization via `config.json`

*   **Priority**: Low
*   **Impact**: Low
*   **Effort**: Medium
*   **Concept**: Allow users to select from a predefined set of themes or specify basic color palettes directly within `public/config.json`. The build script would then inject theme-specific CSS variables or class names into the main HTML structure or link to a theme-specific CSS file.
*   **Benefits**:
    *   Enables easy visual customization without needing to directly edit CSS files.
    *   Allows for quick switching between different looks (e.g., "dark mode", "light mode", "brand-aligned theme").
    *   Content creators can focus on content, while basic styling choices are managed centrally.
*   **Implementation Sketch**:
    *   **Configuration (`public/config.json`)**:
        *   Add a `theme` object:
            ```json
            "theme": {
              "name": "dark", // or "light", "custom"
              "settings": { // Optional, for "custom" theme
                "primary_color": "#1a73e8",
                "secondary_color": "#f0f0f0",
                "background_color": "#121212",
                "text_color": "#e8eaed"
              }
            }
            ```
    *   **CSS**:
        *   Define CSS variables in `public/style.css` for common elements (e.g., `--primary-color`, `--background-color`, `--text-color`).
        *   Create alternative theme stylesheets (e.g., `public/themes/dark.css`, `public/themes/light.css`) that override these variables or provide entirely different styles.
    *   **Build Script (`build.py`)**:
        *   In `BuildOrchestrator.build_all_languages()` or `DefaultPageBuilder.assemble_translated_page()`:
            *   Read the `theme` configuration from `app_config`.
            *   If `theme.name` points to a predefined theme, inject a `<link>` tag for the corresponding theme CSS file (e.g., `<link rel="stylesheet" href="themes/dark.css">`) into the `<head>`.
            *   Alternatively, if `theme.settings` are provided, generate a `<style>` block in the `<head>` that defines the CSS variables:
                ```html
                <style>
                  :root {
                    --primary-color: #1a73e8;
                    /* ... other variables ... */
                  }
                </style>
                ```
            *   Add a class to the `<body>` tag, e.g., `<body class="theme-dark">`.
    *   **HTML Structure**: Ensure HTML elements use classes or CSS variables that can be targeted by themes.

---

## Conclusion & Next Steps

The features outlined above represent a range of potential improvements to the landing page generator, from foundational SEO and performance enhancements to user experience and customization options.

**Next Steps:**

1.  **Review & Discuss**: The team should review these proposals, particularly the assigned priorities, impact, and effort estimations.
2.  **Prioritize for Implementation**: Based on the discussion, decide which features to tackle in upcoming development cycles.
3.  **Refine Requirements**: Before starting implementation on a chosen feature, its requirements and implementation sketch may need further refinement.
4.  **Contribute New Ideas**: This document should be a living repository. New feature ideas can be added by following the existing format.

By systematically evaluating and implementing these ideas, we can continue to enhance the capabilities and value of the landing page generator.
