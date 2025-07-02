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
