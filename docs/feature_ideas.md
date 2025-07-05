# Landing Page Generator: Feature Roadmap & Ideas

## Introduction

This document outlines potential new features and enhancements for the landing page generator. Its purpose is to provide a clear overview of ideas, facilitate discussion, and help prioritize development efforts. Each feature is described with its core concept, benefits, an estimated priority, impact, effort, and a technical implementation sketch. This is a living document and should be updated as new ideas emerge or priorities shift.

## Feature Summary & Prioritization

The table below offers a quick glance at all proposed features, their intended function, and their strategic assessment.

| Feature                               | Summary                                                                       | Priority | Impact | Effort |
| :------------------------------------ | :---------------------------------------------------------------------------- | :------- | :----- | :----- |
| Dynamic Sitemap Generation            | Automatically create `sitemap.xml` for improved SEO discoverability.          | High     | High   | Medium |
| Automated Image Optimization          | Optimize images (compress, convert format) during build for performance.      | High     | High   | Medium |
| Feature                               | Summary                                                                       | Priority | Impact | Effort |
| :------------------------------------ | :---------------------------------------------------------------------------- | :------- | :----- | :----- |
| Dynamic Sitemap Generation            | Automatically create `sitemap.xml` for improved SEO discoverability.          | High     | High   | Medium |
| Automated Image Optimization          | Optimize images (compress, convert format) during build for performance.      | High     | High   | Medium |
| Basic Analytics Integration           | Easily embed analytics tracking snippets (e.g., Google Analytics) via config. | High     | Medium | Low    |
| Versioned Static Assets (CSS/JS)      | Append content hash/timestamp to static asset URLs for cache busting.         | High     | Medium | Low    |
| A/B Testing for Hero Section          | Randomly select hero content at build time for simple A/B tests.              | Medium   | Medium | Medium |
| Customizable Social Media Meta Tags   | Define Open Graph/Twitter tags for richer social media sharing.               | Medium   | Medium | Medium |
| Versioned Static Assets (CSS/JS)      | Append content hash/timestamp to static asset URLs for cache busting.         | High     | Medium | Low    |
| A/B Testing for Hero Section          | Randomly select hero content at build time for simple A/B tests.              | Medium   | Medium | Medium |
| Customizable Social Media Meta Tags   | Define Open Graph/Twitter tags for richer social media sharing.               | Medium   | Medium | Medium |
| Theme Customization via `config.json` | Allow theme selection or basic color palette customization via `config.json`. | Low      | Low    | Medium |

---

## Detailed Feature Proposals

### 1. Dynamic Sitemap Generation

- **Priority**: High
- **Impact**: High
- **Effort**: Medium
- **Concept**: Automatically generate an XML sitemap (`sitemap.xml`) during the build process. This sitemap would list all generated HTML pages (e.g., `index.html`, `index_es.html`, and potentially individual blog post pages if those were ever to become separate HTML files).
- **Benefits**:
  - Improves SEO by making it easier for search engines to discover and index all content on the site.
  - Ensures the sitemap is always up-to-date with the site's structure, especially as new languages or pages are added.
  - No manual sitemap creation or maintenance required.
- **Implementation Sketch**:
  - **Build Script (`build.py`)**:
    - After all HTML files are generated, the script would collect a list of their filenames.
    - It would then construct an XML string conforming to the sitemap protocol (e.g., using `xml.etree.ElementTree`).
    - Each URL in the sitemap would be the absolute URL (requiring a base URL from `config.json` or a new config option).
    - The script would write the XML string to `sitemap.xml` in the root output directory.
  - **Configuration (`public/config.json`)**:
    - Add a `site_base_url` field (e.g., "<https://www.example.com>") to be used for generating absolute URLs in the sitemap.

---

### 2. Automated Image Optimization

- **Priority**: High
- **Impact**: High
- **Effort**: Medium
- **Concept**: Integrate an image optimization step into the build process. When images are referenced in data files (e.g., `hero_item.json`, `portfolio_items.json`), the build script would find these images, create optimized versions (e.g., compressed JPEGs, WebP format), and update the references in the generated HTML to point to these optimized images.
- **Benefits**:
  - Improves page load speed significantly.
  - Reduces bandwidth consumption.
  - Enhances SEO and user experience.
  - Automates a typically manual optimization task.
- **Implementation Sketch**:
  - **Dependencies**: Add a Python image processing library like `Pillow` or `Wand`.
  - **Configuration (`public/config.json`)**:
    - Add an `image_optimization` object:

            ```json
            "image_optimization": {
              "enabled": true,
              "quality": 85, // For JPEGs
              "format": "webp", // "original", "webp" - convert to WebP if possible
              "output_dir": "public/optimized_images/"
            }
            ```

- **Build Script (`build.py`)**:
  - Create a new service, e.g., `ImageOptimizer`.
  - During data loading or just before HTML generation for blocks containing images (Hero, Portfolio, Testimonials):
    - Identify image paths from Protobuf messages (e.g., `Image.src`).
    - If optimization is enabled:
      - Construct a new path for the optimized image in `image_optimization.output_dir`.
      - If the optimized image doesn't exist or the source is newer:
        - Use the chosen library to open the source image, resize (optional, could be another config), convert format (e.g., to WebP), and save it to the output directory with specified quality.
      - Update the `src` field in the Protobuf message _in memory_ to point to the optimized image path.
  - The HTML generation functions would then use these updated paths.
- **File Structure**: Original images might reside in `public/images/` (or specified in data files), and optimized versions would be saved to `public/optimized_images/`. The `.gitignore` should be updated to ignore the `optimized_images` directory.
- **Considerations**:
  - Handling of external image URLs (skip optimization or attempt to download and optimize).
  - Caching of optimized images to avoid reprocessing unchanged images.

---

### 3. Basic Analytics Integration Snippet

- **Priority**: High
- **Impact**: Medium
- **Effort**: Low
- **Concept**: Allow users to easily embed a web analytics tracking snippet (e.g., Google Analytics, Plausible, Simple Analytics) into all generated pages. The tracking ID or relevant configuration would be provided in `config.json`.
- **Benefits**:
  - Enables site owners to gather visitor data without manually editing HTML templates.
  - Centralizes analytics configuration.
  - Can be easily toggled on or off.
- **Implementation Sketch**:
  - **Configuration (`public/config.json`)**: - Add an `analytics` object, e.g.:
    `json
"analytics": {
  "provider": "google_analytics", // or "plausible", "none"
  "tracking_id": "UA-XXXXX-Y", // for GA
  "domain": "yourdomain.com" // for Plausible
}
`

- **Build Script (`build.py`)**:
  - In `assemble_translated_page` (or a similar function that constructs the final HTML), check the `analytics` config.
  - If a provider is specified and configured, inject the appropriate JavaScript snippet into the `<head>` or near the closing `</body>` tag of each HTML page. The snippet would be a template string with placeholders for `tracking_id` or `domain`.

- **HTML Structure**: Ensure the base HTML template (`index.html`) has a clear placeholder or is structured so the script can easily inject the analytics snippet (e.g., before `</head>` or `</body>`).

---

### 4. Versioned Static Assets (CSS/JS)

- **Priority**: High
- **Impact**: Medium
- **Effort**: Low
- **Concept**: Implement a cache-busting mechanism for static assets like `public/style.css` and any JavaScript files. During the build, append a content hash or build timestamp to asset URLs in the generated HTML (e.g., `style.css?v=abcdef12345`).
- **Benefits**:
  - Ensures users always receive the latest version of CSS/JS files after an update, avoiding issues caused by browser caching of stale assets.
  - Improves site reliability when deploying updates.
- **Implementation Sketch**:
  - **Build Script (`build.py`)**:
    - In `BuildOrchestrator` or `DefaultPageBuilder`:
      - When linking `public/style.css` (or any other project-specific JS files if they were added):
        - Calculate a hash (e.g., MD5 or SHA256) of the file's content.
        - Alternatively, use a build timestamp. A content hash is generally preferred as it only changes when the file content changes.
        - Append this hash as a query parameter to the asset URL in the generated HTML:

                    ```html
                    <link rel="stylesheet" href="style.css?v={content_hash}">
                    ```

      - This logic would typically be in `DefaultPageBuilder.assemble_translated_page()` where the final HTML `<head>` is constructed, or wherever the CSS link is added.

  - **Configuration (`public/config.json`)**:
    - Could add a configuration option to enable/disable this or choose the versioning method (hash vs. timestamp), though content hashing is a good default.

            ```json
            "asset_versioning": {
            "enabled": true,
            "method": "content_hash" // "content_hash" or "timestamp"
            }
            ```

- **Helper Function**: A utility function `get_asset_version(file_path, method)` could be created to compute the version string.

---

### 5. A/B Testing for Hero Section

- **Priority**: Medium
- **Impact**: Medium
- **Effort**: Medium
- **Concept**: Allow content creators to define multiple versions of the hero section's content (headline, sub-headline, call-to-action text and link). At build time, one of these variations is randomly selected and injected into the generated HTML pages.
- **Benefits**:
  - Enables simple A/B testing of different messaging for the hero section to see which might lead to better engagement or conversion (though tracking would need to be implemented separately).
  - Allows for easy rotation of hero content without manual HTML edits if multiple valid options exist.
- **Implementation Sketch**:
  - **Protobuf**: `hero_item.proto` was modified. `HeroItemContent` now defines the structure for a single variation (title, subtitle, CTA, `variation_id`). `HeroItem` now contains a list (`repeated`) of `HeroItemContent` messages and a `default_variation_id`.
  - **Data**: `data/hero_item.json` was updated to provide a list of hero content variations. Each variation has a unique `variation_id`.
  - **Build Script**: `build.py`'s `generate_hero_html` function was updated. It now loads the `HeroItem` data (which includes all variations). It then uses the `random.choice()` method to select one `HeroItemContent` variation from the list. The content of this selected variation is used to populate the hero block. A comment indicating the selected `variation_id` is added to the HTML for easier debugging or identification.
  - **Future Enhancements**:
    - Could be extended to allow selection based on an environment variable or a build parameter for more deterministic control over which variation is built.
    - Client-side selection (e.g., via JavaScript) could also be an option for true runtime A/B testing, but this would require more significant changes and potentially a more complex data structure or client-side logic. The current implementation is build-time selection.
    - Integration with analytics to track performance of each variation.
- **Priority**: Medium
- **Impact**: Medium
- **Effort**: Medium
- **Concept**: Allow content creators to define multiple versions of the hero section's content (headline, sub-headline, call-to-action text and link). At build time, one of these variations is randomly selected and injected into the generated HTML pages.
- **Benefits**:
  - Enables simple A/B testing of different messaging for the hero section to see which might lead to better engagement or conversion (though tracking would need to be implemented separately).
  - Allows for easy rotation of hero content without manual HTML edits if multiple valid options exist.
- **Implementation Sketch**:
  - **Protobuf**: `hero_item.proto` was modified. `HeroItemContent` now defines the structure for a single variation (title, subtitle, CTA, `variation_id`). `HeroItem` now contains a list (`repeated`) of `HeroItemContent` messages and a `default_variation_id`.
  - **Data**: `data/hero_item.json` was updated to provide a list of hero content variations. Each variation has a unique `variation_id`.
  - **Build Script**: `build.py`'s `generate_hero_html` function was updated. It now loads the `HeroItem` data (which includes all variations). It then uses the `random.choice()` method to select one `HeroItemContent` variation from the list. The content of this selected variation is used to populate the hero block. A comment indicating the selected `variation_id` is added to the HTML for easier debugging or identification.
  - **Future Enhancements**:
    - Could be extended to allow selection based on an environment variable or a build parameter for more deterministic control over which variation is built.
    - Client-side selection (e.g., via JavaScript) could also be an option for true runtime A/B testing, but this would require more significant changes and potentially a more complex data structure or client-side logic. The current implementation is build-time selection.
    - Integration with analytics to track performance of each variation.

---

### 6. Customizable Social Media Meta Tags

- **Priority**: Medium
- **Impact**: Medium
- **Effort**: Medium
- **Concept**: Allow customization of Open Graph (Facebook, LinkedIn, etc.) and Twitter Card meta tags for each page, with fallbacks to site-wide defaults. This would initially focus on the main `index_<lang>.html` pages.
- **Benefits**:
  - Improves how content appears when shared on social media platforms, potentially increasing engagement.
  - Provides control over titles, descriptions, and images used in social shares.
- **Implementation Sketch**:
  - **Protobuf (`common.proto` or new `meta_tags.proto`)**:
    - Define a `SocialMetaTags` message:

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

- **Data (`data/site_meta.json` or similar)**:
  - A new JSON file to hold site-wide default social meta tags, structured according to `SocialMetaTags`.
  - Potentially extend `hero_item.json` or other page-specific data files to include an optional `social_meta_tags` field if per-page customization beyond simple title/description is desired for specific blocks that might define a "page". For initial implementation, site-wide defaults applied to each generated index page would be simpler.
- **Configuration (`public/config.json`)**:
  - Reference the new `site_meta.json` data file.
  - Possibly add a flag to enable/disable this feature.
- **Build Script (`build.py`)**:
  - Load the default social meta tags.
  - In `assemble_translated_page` (or where the `<head>` is constructed):
    - Retrieve translated values for title, description from the social meta tags data.
    - Construct and inject `<meta>` tags for Open Graph (e.g., `og:title`, `og:description`, `og:image`, `og:url`, `og:type`) and Twitter Card (e.g., `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`).
    - The `og:url` would be the canonical URL for the page being generated.
    - `og:type` could be defaulted to "website".
    - If a page-specific title/description is available (e.g. from Hero block), it could override the default social meta tags for title/description.

---

### 7. Theme Customization via `config.json`

- **Priority**: Low
- **Impact**: Low
- **Effort**: Medium
- **Concept**: Allow users to select from a predefined set of themes or specify basic color palettes directly within `public/config.json`. The build script would then inject theme-specific CSS variables or class names into the main HTML structure or link to a theme-specific CSS file.
- **Benefits**:
  - Enables easy visual customization without needing to directly edit CSS files.
  - Allows for quick switching between different looks (e.g., "dark mode", "light mode", "brand-aligned theme").
  - Content creators can focus on content, while basic styling choices are managed centrally.
- **Implementation Sketch**:
  - **Configuration (`public/config.json`)**:
    - Add a `theme` object:

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

- **CSS**:
  - Define CSS variables in `public/style.css` for common elements (e.g., `--primary-color`, `--background-color`, `--text-color`).
  - Create alternative theme stylesheets (e.g., `public/themes/dark.css`, `public/themes/light.css`) that override these variables or provide entirely different styles.

- **Build Script (`build.py`)**:

      - In `BuildOrchestrator.build_all_languages()` or `DefaultPageBuilder.assemble_translated_page()`:

        - Read the `theme` configuration from `app_config`.
        - If `theme.name` points to a predefined theme, inject a `<link>` tag for the corresponding theme CSS file (e.g., `<link rel="stylesheet" href="themes/dark.css">`) into the `<head>`.
        - Alternatively, if `theme.settings` are provided, generate a `<style>` block in the `<head>` that defines the CSS variables:

                  ```html
                  <style>
                    :root {
                      --primary-color: #1a73e8;
                      /* ... other variables ... */
                    }
                  </style>
                  ```

        - Add a class to the `<body>` tag, e.g., `<body class="theme-dark">`.

- **HTML Structure**: Ensure HTML elements use classes or CSS variables that can be targeted by themes.

---

## Conclusion & Next Steps

The features outlined above represent a range of potential improvements to the landing page generator, from foundational SEO and performance enhancements to user experience and customization options.

**Next Steps:**

1. **Review & Discuss**: The team should review these proposals, particularly the assigned priorities, impact, and effort estimations.
2. **Prioritize for Implementation**: Based on the discussion, decide which features to tackle in upcoming development cycles.
3. **Refine Requirements**: Before starting implementation on a chosen feature, its requirements and implementation sketch may need further refinement.
4. **Contribute New Ideas**: This document should be a living repository. New feature ideas can be added by following the existing format.

By systematically evaluating and implementing these ideas, we can continue to enhance the capabilities and value of the landing page generator.

---

## Newly Brainstormed Feature Ideas (October 2023)

The following ideas were generated during a recent analysis session. They are presented here for consideration and further refinement.

### 8. Dark Mode Toggle/OS Preference Support

- **Priority**: Medium (User Experience)
- **Impact**: Medium
- **Effort**: Medium
- **Concept**: Implement a user-facing dark mode toggle and/or respect the user's OS-level dark mode preference. This would primarily affect the SADS styling system, providing an alternative color scheme for users.
- **Benefits**:
  - Improves user experience by offering visual customization.
  - Reduces eye strain in low-light environments.
  - Respects user preferences for dark themes.
- **Implementation Sketch**:
  - **SADS Engine (`public/js/sads-style-engine.js`)**:
    - Modify to detect OS preference via `window.matchMedia('(prefers-color-scheme: dark)')`.
    - Implement logic to check a `localStorage` item (e.g., `themePreference = 'dark'/'light'`) for manual toggle state.
    - Prioritize manual toggle over OS preference if set.
  - **SADS Theme (`public/js/sads-default-theme.js`)**:
    - Define dark mode color palettes within the theme configuration. This means providing dark alternatives for semantic color attributes (e.g., `bg-primary`, `text-main`, `border-accent`).
    - The SADS engine would select the appropriate palette based on the determined mode.
  - **UI Toggle (Optional but Recommended)**:
    - Add a simple button/switch (e.g., in the header or footer) to `templates/components/header/header.html` or `templates/components/footer/footer.html`.
    - JavaScript associated with this toggle would:
      - Update the `localStorage` item.
      - Trigger a re-application of styles by the SADS engine (e.g., by dispatching a custom event or calling a specific SADS function).
  - **Initial Load**: On page load, the SADS engine applies the correct theme (dark/light) based on OS preference or stored toggle state.

---

### 9. Blog Post Atom/RSS Feed Generation

- **Priority**: Medium (Content Syndication)
- **Impact**: Medium
- **Effort**: Medium
- **Concept**: Automatically generate an Atom or RSS feed (e.g., `atom.xml`) for blog posts during the build process. This allows users and applications to subscribe to blog updates.
- **Benefits**:
  - Enables content syndication and subscription via feed readers.
  - Improves content discoverability and reach.
  - Provides a standard way for other services to ingest blog updates.
- **Implementation Sketch**:
  - **Configuration (`public/config.json`)**:
    - Add `site_base_url` (e.g., "https://www.example.com") for absolute URLs in the feed.
    - Add `feed_filename` (e.g., "atom.xml" or "rss.xml").
    - Add `feed_title` and `feed_author` for feed metadata.
  - **Protobuf (`proto/blog_post.proto`)**:
    - Ensure `BlogPost` message has fields for:
      - `id` (unique identifier for the post, can be derived from filename or a dedicated field).
      - `publication_date` (ISO 8601 format).
      - `summary` or `content_snippet`.
      - `author_name` (optional, could fallback to site-wide author).
  - **Build Script (`build.py`)**:
    - Create a new service/function, e.g., `FeedGenerator`.
    - This service would:
      - Be called after all blog post data (`data/blog_posts.json`) is loaded.
      - Iterate through the `BlogPost` items.
      - Use Python's `xml.etree.ElementTree` or a library like `feedgen` to construct the XML structure for an Atom feed.
      - Each blog post becomes an `<entry>`:
        - `<title>`: Blog post title.
        - `<id>`: Unique ID (e.g., `site_base_url + /blog/post_id`).
        - `<link href>`: Absolute URL to the blog post (requires a way to link to individual posts, which might be a separate feature if posts aren't individual pages yet. If posts are part of a single page, link to that page with an anchor).
        - `<updated>`: Publication date.
        - `<summary>`: Blog post summary.
        - `<author>`: Post author or site author.
      - The main feed elements (`<feed>`, `<title>`, `<updated>`, `<author>`, `<id>`) would use data from `config.json`.
    - Write the generated XML to the specified `feed_filename` in the root output directory.
  - **Linking**: Add a `<link rel="alternate" type="application/atom+xml" href="/atom.xml">` tag to the `<head>` of HTML pages.

---

### 10. Basic Contact Form `mailto:` Submission

- **Priority**: Low (Basic Functionality)
- **Impact**: Low (but provides a functional contact method for purely static sites)
- **Effort**: Low
- **Concept**: Modify the existing contact form to construct and open a `mailto:` link when submitted. This provides a simple, backend-less way for users to send their message via their default email client.
- **Benefits**:
  - Makes the contact form functional on purely static hosting environments where no backend processing is available.
  - Provides a basic way for site owners to receive inquiries.
- **Implementation Sketch**:
  - **Protobuf (`proto/contact_form_config.proto`)**:
    - Add a `recipient_email` field to the `ContactFormConfig` message.
  - **Data (`data/contact_form_config.json`)**:
    - Update this file to include the `recipientEmail` (e.g., "contact@example.com").
  - **JavaScript (`public/js/app.js` or a dedicated script for the contact form)**:
    - Get the contact form element.
    - Add an event listener for the `submit` event.
    - Inside the event listener:
      - Prevent the default form submission (`event.preventDefault()`).
      - Retrieve the values from the form fields (name, email, message).
      - Retrieve the `recipientEmail` from the loaded `contact_form_config.json` data (this data is already being loaded for the form's title/fields, so it should be accessible).
      - Construct a `mailto:` URL. Example:
        `const subject = encodeURIComponent("Contact Form Submission from " + nameField.value);`
        `const body = encodeURIComponent(`Name: ${nameField.value}\\nEmail: ${emailField.value}\\nMessage: ${messageField.value}`);`
              `window.location.href = \`mailto:${recipientEmail}?subject=${subject}&body=${body}\`;`
  - **HTML (`templates/components/contact-form/contact-form.html`)**:
    - No significant changes needed to the HTML structure itself, as the JavaScript will handle the submission. Ensure form fields have appropriate `id` attributes for easy selection in JS.
    - The form's `action` and `method` attributes might become irrelevant or can be removed.
  - **Considerations**:
    - Character limits for `mailto:` URLs can be an issue for very long messages, though typically sufficient for contact forms.
    - User experience: relies on the user having a correctly configured email client.
    - No spam protection inherent to this method.

---

### 11. AI-Powered Personalized Content Blocks

- **Priority**: Experimental
- **Impact**: High
- **Effort**: High
- **Concept**: Dynamically adapt content within various sections of the landing page (e.g., Hero, Features, Testimonials) to better resonate with different anticipated user personas or segments. For a static site generator, this could mean generating multiple distinct versions of the site, each tailored to a specific persona.
- **AI Aspect**:
  - **Persona-Based Content Generation**: An AI (e.g., a large language model like GPT) could be prompted with persona details (e.g., "tech-savvy early adopter," "budget-conscious small business owner") and existing baseline content for a block. The AI would then rewrite or generate new content (headlines, descriptions, calls to action) specifically tailored to that persona's likely interests, pain points, and language.
  - **Content Curation/Selection**: If a predefined set of content variations exists, an AI could help classify them or assist in selecting the most appropriate variation for a given persona during the build configuration for a persona-specific site version.
- **Benefits**:
  - Increased relevance and engagement by speaking more directly to specific user groups.
  - Potentially higher conversion rates by addressing persona-specific needs and motivations.
  - Allows for more targeted marketing campaigns by directing different personas to their tailored landing page versions.
- **High-Level Implementation Sketch**:
  1.  **Persona Definition**: Users define target personas (e.g., in a new `personas.json` file or through an interface).
  2.  **Content Input**: Baseline content for each block is provided as usual (e.g., in `data/feature_items.json`).
  3.  **AI Integration (Build Time)**:
      - During `build.py`, for each defined persona and for each relevant content block:
        - The build script sends the baseline content and persona description to an AI model API.
        - The AI returns tailored content.
      - The build process then generates a separate version of the site (e.g., `index_persona_A.html`, `index_persona_B.html`) using this AI-generated content.
  4.  **Data Structure**: Protobuf messages might need a way to store multiple content variations per item, perhaps tagged by persona.
- **Potential Challenges/Experimental Nature**:
  - **Cost and Speed**: Frequent calls to powerful AI models can be expensive and slow down the build process significantly.
  - **Content Quality Control**: AI-generated content needs careful review to ensure accuracy, brand alignment, and avoidance of biases or nonsensical text.
  - **Over-Personalization**: Risk of creating overly narrow or stereotypical content.
  - **Complexity**: Managing multiple site versions adds complexity.

---

### 12. Generative Component Styling (AI-SADS)

- **Priority**: Experimental
- **Impact**: Medium
- **Effort**: High
- **Concept**: Leverage AI to assist in designing the visual appearance of components by generating or suggesting Semantic Attribute-Driven Styling (SADS) attributes. Users could describe their desired aesthetic or functional style in natural language, and the AI would translate this into concrete `data-sads-*` attributes for the component's HTML.
- **AI Aspect**:
  - **Natural Language to SADS Translation**: An AI model (potentially a fine-tuned LLM or a model trained on code/markup generation) would take a natural language prompt (e.g., "Make this feature list look sleek and professional with high contrast for readability") and the component's basic HTML structure as input.
  - **SADS Attribute Generation**: The AI would output a set of `data-sads-*` attributes to be applied to the HTML elements within the component, consistent with the SADS system's capabilities (defined in `sads-default-theme.js` and `sads-style-engine.js`).
  - **Iterative Refinement**: The system could allow users to iteratively refine the AI's suggestions.
- **Benefits**:
  - Lowers the barrier to styling and theming, allowing users less familiar with CSS or SADS syntax to achieve desired looks.
  - Accelerates the design process by providing quick visual prototypes.
  - Encourages experimentation with the SADS system by showing its expressive potential.
- **High-Level Implementation Sketch**:
  1.  **Interface (CLI or Build-time Config)**: A way for users to input their natural language styling prompts for specific components.
  2.  **AI Model Interaction**:
      - The system sends the prompt and relevant HTML snippet (and potentially the SADS theme definition as context) to an AI model.
      - The AI returns suggested `data-sads-*` attributes or modified HTML with these attributes.
  3.  **Template Update**: The suggested attributes are either manually or automatically applied to the component's HTML template file.
  4.  **SADS Engine**: The existing SADS engine (`public/js/sads-style-engine.js`) would then render these AI-generated attributes.
- **Potential Challenges/Experimental Nature**:
  - **SADS Expressiveness Limits**: The AI can only generate styles that the SADS engine and theme actually support. The current SADS is an MVP.
  - **Model Training/Fine-Tuning**: A general-purpose LLM might struggle with the specific syntax and semantics of SADS without fine-tuning or very detailed prompting.
  - **Determinism and Consistency**: Getting consistent and high-quality styling suggestions can be challenging.
  - **User Interface for Interaction**: Creating an effective UI for prompting and refining styles would be key.

---

### 13. AI-Driven Content & SEO Audit

- **Priority**: Experimental
- **Impact**: High
- **Effort**: Medium-High
- **Concept**: Integrate AI-powered analysis into the build process to audit the website's text content for quality, readability, SEO effectiveness, and translation consistency. The build would produce a report with actionable insights and suggestions.
- **AI Aspect**:
  - **Natural Language Processing (NLP)**: Utilize AI models for:
    - **Readability Analysis**: Calculate scores and suggest simplifications.
    - **SEO Keyword Analysis**: Identify keywords, assess density, suggest related LSI keywords.
    - **Tone and Sentiment Analysis**: Evaluate if content tone aligns with brand voice.
    - **Grammar and Style Checks**: Beyond basic spell checking.
    - **Translation Quality (for i18n)**: Preliminary assessment of translation accuracy and fluency.
- **Benefits**:
  - Improves content quality, making it more engaging and easier to understand.
  - Enhances SEO, potentially leading to better search engine rankings.
  - Helps maintain a consistent brand voice and translation quality.
  - Automates parts of the content review process.
- **High-Level Implementation Sketch**:
  1.  **Content Extraction**: During `build.py`, extract all relevant text content.
  2.  **AI Analysis Service**:
      - Create a module (e.g., `ContentAuditor`) to interface with AI NLP APIs.
      - Send extracted text for analysis based on configured checks.
  3.  **Configuration**: `public/config.json` could have an `ai_audit_config` section.
  4.  **Report Generation**: Build process outputs a report (e.g., `ai_content_audit.html` or console output) with findings and suggestions.
- **Potential Challenges/Experimental Nature**:
  - **Cost of APIs**: NLP APIs can be costly for large amounts of text.
  - **Actionability of Suggestions**: AI suggestions might be generic or require human interpretation.
  - **Contextual Understanding**: AI may lack deep contextual understanding of the specific business domain.
  - **Integration Complexity**: Managing API calls and consolidating results can be complex.
  - **False Positives/Negatives**: AI assessment can be subjective.

---

### 14. Interactive SADS Component Previewer/Editor

- **Priority**: Medium (High for developers working extensively with SADS)
- **Impact**: Medium (Significantly improves SADS usability)
- **Effort**: Medium-High
- **Concept**: A browser-based development tool that allows developers to select a component template (e.g., `features.html`, `hero.html`), view it rendered in isolation, and interactively modify its `data-sads-*` attributes. Changes to SADS attributes would be applied live to the component's preview using the existing SADS JavaScript engine. It could also display the generated CSS for the selected element.
- **Benefits**:
  - **Improved Developer Experience (DX)**: Makes styling with SADS more intuitive and visual, reducing the need to manually edit HTML and refresh the browser repeatedly.
  - **Faster Iteration**: Allows for rapid experimentation with SADS attributes to achieve desired visual styles.
  - **Better SADS Understanding**: Helps developers learn and understand the SADS system by seeing direct cause and effect.
  - **Debugging Aid**: Can help in debugging SADS styling issues by isolating components and inspecting generated styles.
- **Implementation Sketch**:
  1.  **New Go Endpoint (Optional but helpful)**:
      - Create a new Go handler (e.g., `/sads-previewer`) that serves a dedicated HTML page for the tool.
      - This handler could also list available component templates from the `templates/components/` directory.
  2.  **Previewer HTML Page**:
      - A simple HTML page that includes:
        - The SADS engine (`sads-style-engine.js`) and theme (`sads-default-theme.js`).
        - A dropdown/list to select a component template.
        - An iframe or a `div` to render the selected component's HTML.
        - A UI panel (e.g., a sidebar) to display and edit SADS attributes for a selected element within the component.
        - A section to display the CSS generated by SADS for the selected element.
  3.  **JavaScript Logic for the Previewer**:
      - **Component Loading**: When a component is selected, fetch its raw HTML template content (e.g., via an AJAX call to a Go endpoint that reads the file, or if fully client-side, pre-load template strings).
      - **Rendering**: Inject the component's HTML into the preview area. The SADS engine should automatically process it.
      - **Element Selection**: Allow clicking on elements within the rendered component preview.
      - **Attribute Editing**:
        - When an element is selected, parse its `data-sads-*` attributes and populate input fields in the UI panel.
        - When an attribute is changed in the UI, update the corresponding `data-sads-*` attribute on the HTML element in the preview area.
        - Trigger a re-run of the SADS styling logic for the modified element or the whole component (the SADS engine might need a public method for this, like `sadsEngine.refreshElement(element)` or `sadsEngine.applyStyles()`).
      - **CSS Display**: After SADS processes the selected element, find the generated CSS rules (SADS assigns unique classes like `sads-id-X`) and display them.
  4.  **SADS Engine Modifications (Minor)**:
      - Potentially expose a method to re-process a specific element or re-apply all styles on demand.
      - Ensure SADS can run multiple times or on dynamically added content if not already supported.
  5.  **Data Source (for components needing data)**:
      - For components that are data-driven (e.g., features, testimonials), the previewer would need a way to load sample data. This could be a predefined sample JSON structure or a way to select a sample data file. The Go backend could serve this sample data.

---

### 15. Build-time Link Checker & Unused Asset Finder

- **Priority**: High
- **Impact**: Medium (Improves reliability and maintainability)
- **Effort**: Medium
- **Concept**: An automated process integrated into the Go build script (`main.go` or a script it calls) that runs after all HTML pages are generated. It scans these pages for internal links and static asset references, verifying their validity. It can also identify assets present in the project that are not referenced anywhere.
- **Benefits**:
  - **Improved Site Quality**: Prevents broken internal links and missing asset errors, leading to a better user experience.
  - **Reduced Clutter**: Helps identify and remove unused images, scripts, or stylesheets, keeping the project tidy and reducing deployment size.
  - **Automated Maintenance**: Catches common errors automatically during each build, reducing manual checking.
- **Implementation Sketch**:
  1.  **Go Package for HTML Parsing**: Utilize a Go HTML parsing library (e.g., `golang.org/x/net/html`).
  2.  **Integration Point**: In `main.go`, after the loop that generates all language versions of pages.
  3.  **Link Checking Logic (Go)**:
      - Collect all generated HTML file paths (e.g., `index.html`, `index_es.html`).
      - For each HTML file:
        - Parse the HTML.
        - Find all `<a>` tags and extract their `href` attributes.
        - For each `href`:
          - Ignore external links (starting with `http://`, `https://`, `//`).
          - Ignore anchor links (`#foo`).
          - Normalize the path (e.g., resolve relative paths based on the current file's location).
          - Check if the target path corresponds to another generated HTML file or an existing file in `public/`.
          - Report broken links (e.g., log to console with filename and line number if possible).
  4.  **Asset Reference Checking Logic (Go)**:
      - For each HTML file:
        - Find all tags that reference assets (e.g., `<img>` src, `<link>` href for CSS, `<script>` src).
        - Extract the asset paths.
        - Normalize paths.
        - Check if the referenced file exists under `public/` (or the relevant base directory for assets).
        - Report missing assets.
  5.  **Unused Asset Finder Logic (Go)**:
      - Maintain a set of all successfully referenced asset paths during the above checks.
      - Recursively list all files in asset directories (e.g., `public/images/`, `public/js/`, `public/css/` if component CSS files were used).
      - Compare this list with the set of referenced assets.
      - Report files that exist on disk but are not referenced.
  6.  **Configuration (Optional)**:
      - In `public/config.json`, add options like:
        - `"build_checks": {"enable_link_checker": true, "enable_asset_checker": true, "enable_unused_asset_finder": false}`
        - `"asset_checker_ignore_patterns": ["/external-cdn/.*"]`
  7.  **Reporting**: Log findings to the console during the build. Could be enhanced to output a structured report file (e.g., JSON or text).

---

### 16. Dynamic Data Source Plugins/Adapters for Content Blocks

- **Priority**: Medium-High
- **Impact**: High (Transforms content management capabilities)
- **Effort**: High
- **Concept**: Extend the Go backend to support fetching data for content blocks (like blog posts, testimonials, portfolio items) from various sources beyond the current local JSON files (`data/*.json`). This would involve defining a plugin interface in Go, allowing developers to implement adapters for different data sources like Headless CMSs (Contentful, Strapi), Google Sheets, databases, or other APIs.
- **Benefits**:
  - **Enhanced Content Flexibility**: Decouples content from the codebase, allowing non-developers to manage content in familiar tools.
  - **Scalability**: Enables handling larger amounts of content more effectively than managing numerous JSON files.
  - **Real-time Updates (Potentially)**: Could pave the way for fetching data at request time if the generator evolves into a dynamic server, or more frequent updates for static builds.
  - **Integration with Existing Systems**: Allows the landing page generator to integrate with existing content repositories or business systems.
- **Implementation Sketch**:
  1.  **Go Interface for Data Adapters**:
      - Define a Go interface, e.g., `ContentAdapter`:
        ```go
        type ContentAdapter interface {
            FetchData(config map[string]interface{}) (map[string]interface{}, error) // Returns data compatible with Protobuf JSON unmarshaling
            GetDataType() string // e.g., "blog_posts", "testimonial_items"
        }
        ```
      - The `config` map could hold adapter-specific settings (API keys, sheet IDs, endpoint URLs).
  2.  **Adapter Registration**:
      - A way to register available adapters in `main.go`, mapping a source type string (e.g., "google_sheet_adapter", "headless_cms_adapter") to an adapter implementation.
  3.  **Configuration Update (`public/config.json`)**:
      - Modify the `block_data_loaders` section in `config.json`. Instead of just `data_file`, allow specifying a data source adapter:
        ```json
        "block_data_loaders": {
          "blog": {
            "adapter_type": "json_file", // Existing behavior
            "config": { "data_file": "data/blog_posts.json" },
            "message_type_name": "BlogPost",
            "is_list": true
          },
          "testimonials": {
            "adapter_type": "google_sheet_adapter", // New adapter
            "config": {
              "sheet_id": "your_sheet_id",
              "api_key": "your_api_key", // Or use service account
              "range": "Sheet1!A:D"
            },
            "message_type_name": "TestimonialItem",
            "is_list": true
          }
        }
        ```
  4.  **Modify Data Loading Logic (`main.go`)**:
      - In the data loading part of `main.go` (where it currently reads JSON files based on `block_data_loaders`), check for `adapter_type`.
      - If it's "json_file" (or default), use existing file reading logic.
      - If it's a different adapter type, look up the registered adapter, pass its specific `config` from `config.json`, and call its `FetchData` method.
      - The data returned by the adapter must be unmarshalable into the corresponding Protobuf message structure. Adapters would be responsible for transforming source data into this expected structure.
  5.  **Implement Specific Adapters (Examples)**:
      - **`JsonFileAdapter`**: Encapsulates the current JSON file reading logic.
      - **`GoogleSheetAdapter`**:
        - Uses the Google Sheets API client library for Go.
        - Fetches data from the specified sheet and range.
        - Transforms rows/columns into a `[]map[string]interface{}` suitable for Protobuf unmarshaling.
      - **`HeadlessCMSAdapter` (Generic or Specific)**:
        - Uses an HTTP client to fetch data from a CMS API endpoint.
        - Handles authentication.
        - Transforms the API response.
  6.  **Protobuf Schemas Remain Key**: The Protobuf definitions (`.proto` files) would still define the expected structure for the data, regardless of the source. Adapters must ensure their output conforms to these schemas.
  7.  **Error Handling & Caching**:
      - Robust error handling for API failures or data transformation issues.
      - Consider implementing a caching mechanism for fetched data to speed up subsequent builds and reduce API calls (e.g., cache to a local file with a TTL).

---
