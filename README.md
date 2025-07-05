# Landing Page Generator

This project provides a flexible and configurable system for generating static landing pages. It is designed to be data-driven, supporting internationalization and dynamic content blocks. The primary use case is generating landing pages, for instance, to track user sources for a Telegram bot or similar applications.

## Overview

The core functionality revolves around a Go build script (`main.go`) that assembles HTML pages (e.g., `index.html`, `index_es.html`) from:

- **HTML Component Templates**: Located in `templates/components/<component_name>/` (e.g., `features.html`, `header.html`), these are Jinja2 templates for different sections and parts of a page.
- **Styling**: (Experimental Setup) All components, including Header, Footer, and content blocks (Features, Testimonials, Blog, Contact Form), currently use an experimental Semantic Attribute-Driven Styling (SADS) system. Styles are defined by `data-sads-*` attributes in HTML and processed by a JavaScript engine. See `docs/styling_approach.md` for details.
- **Configuration**: `public/config.json` defines which blocks to include, their order, supported languages, and other site-wide settings.
- **Dynamic Data**: Content for blocks (text, images, links) is stored in JSON files within the `data/` directory. These files adhere to schemas defined by Protocol Buffers.
- **Translations**: Locale strings for internationalization are managed in `public/locales/`.
- **Protocol Buffers**: Schemas for dynamic data are defined in `.proto` files in the `proto/` directory. These ensure data consistency and are used to generate Python data classes.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Go**: Version 1.18+ recommended. (Used for the main build script `main.go` and for compiling SADS Go/WASM modules).
- **Protocol Buffer Compiler (`protoc`)**: Version 3+. Essential for generating code from `.proto` files.
- **JavaScript Runtime & Package Manager**:
    - **Node.js & npm**: LTS versions recommended if you choose this route. `npm` is used for running scripts defined in `package.json` (like `generate-proto`, `format`, `build`).
    - **Bun**: Can be used as an alternative to Node.js/npm for running scripts and managing JavaScript dependencies (if any were to be added to `package.json`).
- **Python Environment Manager (Optional but Recommended for `build.py` and linting tools)**:
    - **uv**: A fast Python installer and resolver. If you intend to use or develop the Python scripts in `build_protocols/` or run the full `format.sh` script (which uses Python-based linters like `black`, `isort`, `autoflake`), `uv` can be used to manage these Python tool dependencies, typically defined in `pyproject.toml`. For example: `uv pip install -r requirements-dev.txt` (if you generate one from `pyproject.toml`) or `uv venv && uv pip sync`.
    - Alternatively, standard Python `venv` and `pip` can be used.

### Installation

1.  **Clone the repository (if you haven't already):**

```bash
git clone <repository-url>
cd <repository-directory>
```

2.  **Install Go dependencies & tools:**
    The Go build script uses Go modules. Dependencies like Pongo2 (for `main.go`) will be downloaded automatically when you build or run the Go program.

    **Important for Go Protobuf Generation:**
    Ensure you have the Go Protocol Buffer generator plugins installed globally and available in your system's `PATH`. `protoc` needs to find these executables.
    ```bash
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
    ```
    After installation, verify that your Go binary path (usually `$GOPATH/bin` or `$HOME/go/bin`) is correctly added to your system's `PATH` environment variable. A new terminal session might be required for `PATH` changes to take effect. If `protoc` cannot find these plugins, the `npm run generate-proto` command will fail.

3.  **Install JavaScript/Build Tooling Dependencies:**
    If using `npm`:
    ```bash
    npm install
    ```
    If using `bun`:
    ```bash
    bun install
    ```
    This installs development tools like Prettier (used in `format.sh`) and any other JS dependencies defined in `package.json`.

4.  **Setup Python Development Environment (Optional, for `build.py` / linters):**
    If you plan to work with `build.py` or the Python-based linters in `format.sh`, set up a Python environment using `uv` (recommended) or `venv`/`pip` with the dependencies from `pyproject.toml` (e.g., by generating a `requirements-dev.txt` or using `uv pip sync`).
    Example with `uv`:
    ```bash
    uv venv .venv
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows
    uv pip install -e .[dev]   # Install project and dev dependencies
    ```

### Build Process

The website generation involves two main steps:

1. **Generate Protocol Buffer Stubs (Go):**
   If you modify any `.proto` files or are setting up the project for the first time, you need to compile them into Go code.

   ```bash
   npm run generate-proto
   ```

   This command executes `protoc` (the Protocol Buffer compiler) using the configurations in `package.json`. It generates Go files in the `generated/go/` directory, which `main.go` uses to handle structured data.

2. **Build the HTML Pages:**
   To generate or update `index.html` and its language-specific variants (e.g., `index_es.html`):

   ```bash
   npm run build
   ```

   This command runs the main `go run main.go` script (or `main.exe` if compiled). The script performs the following actions:

   - Reads the main configuration from `public/config.json`.
   - Loads dynamic content from `data/*.json` files, validating it against the generated Protobuf structures.
   - Loads HTML component templates from `templates/components/`.
   - For each supported language:
     - Loads translations from `public/locales/{lang}.json`.
     - Generates HTML for each content block, populating it with data and translating text.
     - Assembles the blocks into a complete page based on the base `index.html` template.
     - Writes the final page to the root directory (e.g., `index.html`, `index_es.html`).
     - Generates a language-specific configuration file (e.g., `public/generated_configs/config_en.json`).

   _A note on Protobuf imports in `main.go`_: The Go script imports the generated protobuf package directly (e.g., `import pb "landing-page-generator/generated/go"`). Ensure your `go.mod` file correctly names the module (e.g., `module landing-page-generator`).

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
     - Update `main.go`:
       - Ensure the new Protobuf message type is registered in the `protoRegistry` in `main.go`.
       - If you're not using the `GenericBlockGenerator`, you might need to create a new specific `HtmlBlockGenerator` struct that implements the `HtmlBlockGenerator` interface and add an instance to the `htmlGenerators` map in `main()`. The `GenericBlockGenerator` should handle most cases if the Pongo2 template is set up correctly.
       - Update `public/config.json`'s `block_data_loaders` section for your new block, specifying its `data_file`, `message_type_name`, and whether it `is_list`.
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
