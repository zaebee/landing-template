# Landing Page Generator

This project provides a flexible and configurable system for generating static landing pages. It is designed to be data-driven, supporting internationalization and dynamic content blocks. The primary use case is generating landing pages, for instance, to track user sources for a Telegram bot or similar applications.

## Overview

The core functionality revolves around a Python build script (`build.py`) that assembles HTML pages (e.g., `index.html`, `index_es.html`) from:

- **HTML Component Templates**: Located in `templates/components/<component_name>/` (e.g., `features.html`, `header.html`), these are Jinja2 templates for different sections and parts of a page.
- **Styling**: (Experimental Setup) All components, including Header, Footer, and content blocks (Features, Testimonials, Blog, Contact Form), currently use an experimental Semantic Attribute-Driven Styling (SADS) system. Styles are defined by `data-sads-*` attributes in HTML and processed by a JavaScript engine. See `docs/styling_approach.md` for details.
- **Configuration**: `public/config.json` defines which blocks to include, their order, supported languages, and other site-wide settings.
- **Dynamic Data**: Content for blocks (text, images, links) is stored in JSON files within the `data/` directory. These files adhere to schemas defined by Protocol Buffers.
- **Translations**: Locale strings for internationalization are managed in `public/locales/`.
- **Protocol Buffers**: Schemas for dynamic data are defined in `.proto` files in the `proto/` directory. These ensure data consistency and are used to generate Python data classes.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python** (version 3.8+ recommended)
- **Node.js** (for running npm scripts, primarily for Protocol Buffer generation)
- **pip** (Python package installer)
- **npm** (Node package manager, usually comes with Node.js)
- **Python** (version 3.8+ recommended)
- **Node.js** (for running npm scripts, primarily for Protocol Buffer generation)
- **pip** (Python package installer)
- **npm** (Node package manager, usually comes with Node.js)

### Installation

1. **Clone the repository (if you haven't already):**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Python dependencies:**
   This project uses `uv` for Python package management if available (as per `format.sh`), but `pip` with `requirements.txt` is the standard.

   ```bash
   pip install -r requirements.txt
   ```

   For development, including tools for linting and type checking, also install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

   _Note: Ensure `requirements.txt` includes `grpcio-tools` and `protobuf` for Protocol Buffer compilation._

### Build Process

The website generation involves two main steps:

1. **Generate Protocol Buffer Stubs:**
   If you modify any `.proto` files or are setting up the project for the first time, you need to compile them into Python code.

   ```bash
   npm run generate-proto
   ```

   This command executes `protoc` (the Protocol Buffer compiler) using the configurations in `package.json`. It generates Python files in the `generated/` directory, which `build.py` uses to handle structured data.

2. **Build the HTML Pages:**
   To generate or update `index.html` and its language-specific variants (e.g., `index_es.html`):

   ```bash
   npm run build
   ```

   This command runs the main `python build.py` script. The script performs the following actions:
   - Reads the main configuration from `public/config.json`.
   - Loads dynamic content from `data/*.json` files, validating it against the generated Protobuf structures.
   - Loads HTML component templates from `templates/components/`.
   - For each supported language:
     - Loads translations from `public/locales/{lang}.json`.
     - Generates HTML for each content block, populating it with data and translating text.
     - Assembles the blocks into a complete page based on the base `index.html` template.
     - Writes the final page to the root directory (e.g., `index.html`, `index_es.html`).
     - Generates a language-specific configuration file (e.g., `public/generated_configs/config_en.json`).

   _A note on Protobuf imports in `build.py`_: The script modifies `sys.path` at runtime to include the `generated/` directory. This allows Python to find the auto-generated Protobuf modules.

## Customization

You can customize various aspects of the generated site:

### Content Blocks

- **Adding a New Block:**
  1. Create an HTML file for your block in `templates/components/<your-block-name>/<your-block-name>.html` (e.g., `templates/components/my-custom-block/my-custom-block.html`).
  2. Add the desired HTML structure. For SADS-styled blocks, use `data-sads-*` attributes. For traditional CSS, create a corresponding CSS file.
  3. Update `public/config.json` by adding the block's template name (e.g., `my-custom-block.html`) to the `blocks` array in the desired order.
  4. If the block uses dynamic data:
     - Define a Protobuf message for its data structure in a new `.proto` file or an existing one.
     - Create a corresponding JSON data file in `data/`.
     - Update `build.py`:
       - Import the new Protobuf message.
       - Add a configuration entry in `_get_dynamic_data_loaders_config()` within `BuildOrchestrator`.
       - Create a new `HtmlBlockGenerator` class for your block in `build_protocols/html_generation.py` and add an instance to the `html_generators` dictionary in `build.py`.
     - Remember to run `npm run generate-proto` after adding/modifying `.proto` files.

- **Removing a Block:**
  1. Remove the block's template name from the `blocks` array in `public/config.json`.
  2. Optionally, delete the HTML template file from `templates/components/<your-block-name>/` and any associated CSS, data, or proto files if no longer needed.

- **Reordering Blocks:**
  1. Change the order of block template names in the `blocks` array in `public/config.json`.

### Site Configuration

Modify `public/config.json` to change:

- `site_name_key`: I18n key for the site name (used in `<title>`).
- `default_lang`: The default language for the site (e.g., "en"). Files for this language will be named `index.html`.
- `supported_langs`: A list of language codes (e.g., `["en", "es"]`) for which pages will be generated.
- `blocks`: The list and order of HTML blocks to include in the pages.
- `navigation_data_file`: Path to the JSON file containing navigation link data.
- Other settings as new features (like theming, analytics) are added.
- `site_name_key`: I18n key for the site name (used in `<title>`).
- `default_lang`: The default language for the site (e.g., "en"). Files for this language will be named `index.html`.
- `supported_langs`: A list of language codes (e.g., `["en", "es"]`) for which pages will be generated.
- `blocks`: The list and order of HTML blocks to include in the pages.
- `navigation_data_file`: Path to the JSON file containing navigation link data.
- Other settings as new features (like theming, analytics) are added.

### Dynamic Content

- Edit JSON files in the `data/` directory to change text, images, links, etc., for corresponding blocks. Ensure the structure matches the Protobuf definitions.

### Translations

- Add or modify translation keys and values in the JSON files within `public/locales/` (e.g., `public/locales/en.json`).
- Add or modify translation keys and values in the JSON files within `public/locales/` (e.g., `public/locales/en.json`).

### Styles

(Experimental Setup) The project currently uses the Semantic Attribute-Driven Styling (SADS) system for all components:

- **All Components (Header, Footer, Features, Testimonials, Blog, Contact Form):** Styles are primarily controlled by `data-sads-*` attributes in their HTML templates (`templates/components/<component_name>/<component_name>.html`) and the SADS engine logic in `public/js/sads-style-engine.js`.
- **Global Base Styles:** Minimal global styles are in `public/style.css`.
- SADS styles are injected dynamically. (Note: The `header.css` and `footer.css` files still exist but are not the primary styling mechanism in this experimental SADS setup; `public/dist/main.css` will bundle them if they contain styles, but SADS attributes in the HTML take precedence for SADS-controlled properties).
- Refer to `docs/styling_approach.md` for a detailed explanation of SADS.

After making any of these changes, **always run `npm run build`** to regenerate the HTML files and see your updates.

## Further Information

- **Data Structures**: See `docs/data_flow.md` and the `.proto` files in `proto/` for details on how data is structured.
- **Feature Ideas**: Check `docs/feature_ideas.md` for planned or potential enhancements.
- **Linting and Formatting**: Run `format.sh` to apply consistent code styling. (Requires `shfmt`, `prettier`, `stylelint`, `black`, `isort`, `autoflake`).
