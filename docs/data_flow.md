# Data Flow and Protobuf Definitions

This document outlines the structure of our data entities defined using Protocol Buffers and how they are utilized within the `build.py` script to generate dynamic HTML content.

## Protobuf Message Definitions

We use Protocol Buffers to define the schema for our dynamic data entities. Common types like `I18nString` (for internationalized strings), `Image`, `CTA` (Call To Action), and `TitledBlock` are defined in `common.proto`.

### `BlogPost` (`blog_post.proto`)

Represents a single blog post item. Loaded as a list from `data/blog_posts.json`.

```proto
message BlogPost {
  string id = 1;                // Unique identifier
  I18nString title = 2;         // Title of the blog post
  I18nString excerpt = 3;       // Short summary of the post
  CTA cta = 4;                  // Call to action (e.g., "Read More")
}
```

### `PortfolioItem` (`portfolio_item.proto`)

Represents a single portfolio item. Loaded as a list from `data/portfolio_items.json`.

```proto
message PortfolioItem {
  string id = 1;                // Unique identifier
  Image image = 2;              // Image for the portfolio item
  TitledBlock details = 3;      // Title and description for the item
}
```

### `HeroItem` (`hero_item.proto`)

Represents the content for the hero section, supporting multiple variations for A/B testing or content rotation. Loaded as a single `HeroItem` message from `data/hero_item.json`.

```proto
message HeroItemContent {
  I18nString title = 1;         // Main headline for this variation
  I18nString subtitle = 2;      // Supporting text for this variation
  CTA cta = 3;                  // Primary call to action for this variation
  string variation_id = 4;      // Unique identifier for this variation
}

message HeroItem {
  repeated HeroItemContent variations = 1; // A list of content variations for the hero section
  string default_variation_id = 2;         // ID of the variation to use if specific selection logic isn't applied
}
```

_Note: The `build.py` script randomly selects one of the `variations` at build time._

### `FeatureItem` (`feature_item.proto`)

Represents a feature list item. Loaded as a list from `data/feature_items.json`.

```proto
message FeatureItem {
  TitledBlock content = 1;      // Title and description of the feature
}
```

### `TestimonialItem` (`testimonial_item.proto`)

Represents a single testimonial. Loaded as a list from `data/testimonial_items.json`.

```proto
message TestimonialItem {
  I18nString text = 1;          // The testimonial quote
  I18nString author = 2;        // Author of the testimonial
  Image author_image = 3;       // Image of the author
}
```

### `ContactFormConfig` (`contact_form_config.proto`)

Defines the configuration for the contact form. Loaded as a single item from `data/contact_form_config.json`.

```proto
message ContactFormConfig {
  string form_action_uri = 1;     // The URI where the form data will be submitted
  string success_message_key = 2; // I18n key for the success message
  string error_message_key = 3;   // I18n key for the error message
}
```

### `NavItem` and `Navigation` (`nav_item.proto`)

Define the structure for navigation links. `Navigation` is loaded as a single item from `data/navigation.json`.

### `SadsAttributeValue`, `SadsStylingSet`, etc. (`sads_attributes.proto`)

Defines the schema for SADS (Semantic Attribute-Driven Styling) attributes, including enums for semantic tokens (like spacing, colors) and messages for structuring styling rules. These definitions are used to generate TypeScript types for the SADS engine and can be used by other tools or systems (e.g., AI, Go/WASM SADS engine) that interact with SADS.

```proto
// Message for a single navigation item.
message NavItem {
  I18nString label = 1;       // Using I18nString for the label
  string href = 2;            // URL or anchor link (e.g., "#features")
  string animation_hint = 3;  // Optional: hint for animation type
}

// Message for the overall navigation structure.
message Navigation {
  repeated NavItem items = 1;
}
```

## Data Flow in `build.py` (Python-based Build)

The `build.py` script is responsible for generating the static HTML pages (e.g., `index.html`, `index_es.html`) by assembling HTML blocks defined in Jinja2 templates, populating them with dynamic data from JSON files (via Protobuf messages), and applying translations.

```mermaid
graph TD
    A_CFG[Input: public/config.json] --> BUILD_PY{build.py BuildOrchestrator};
    A_DATA[Input: data/*.json] --> PY_DATA_HANDLING;
    C_PROTO[Input: proto/*.proto] --> D_PROTOC[Tool: protoc];
    D_PROTOC -- protoc-gen-python --> E_PY_STUBS[Generated: generated/*.py <br> (Protobuf Python stubs)];
    E_PY_STUBS --> PY_DATA_HANDLING[Python Data Handling Logic <br> (JsonProtoDataLoader)];
    F_TEMPLATES[Input: templates/**/*.html <br> (Jinja2 Templates)] --> JINJA_ENV[Jinja2 Environment];
    G_LOCALES[Input: public/locales/*.json] --> PY_TRANSLATION_SVC[Python Translation Service <br> (DefaultTranslationProvider)];
    H_BASE_HTML[Input: templates/base.html <br> (Jinja2 Base Template)] --> PY_PAGE_BUILDER[Python Page Assembly Logic <br> (DefaultPageBuilder)];

    JINJA_ENV --> PY_PAGE_BUILDER;
    JINJA_ENV --> PY_HTML_GENERATORS[Python HTML Block Generators <br> (uses HTML_GENERATOR_REGISTRY)];

    PY_DATA_HANDLING -- Protobuf Messages --> PY_DATA_CACHE[Python Data Cache <br> (InMemoryDataCache)];
    PY_DATA_CACHE -- Cached Data --> BUILD_PY;
    PY_TRANSLATION_SVC -- Translations --> BUILD_PY;
    PY_PAGE_BUILDER -- Page Structuring Logic --> BUILD_PY;

    subgraph "build.py - BuildOrchestrator Core Logic"
        direction LR
        INIT_CONFIG[Load Initial Configurations <br> (App Config, Nav, SiteLogo)]
        PRELOAD_DATA_CACHE[Preload Data Cache <br> (JSON to Proto Messages)]
        COMPILE_WASM[Compile Go WASM Module (Optional)]
        BUNDLE_ASSETS[Bundle CSS & JS, Copy WASM <br> (DefaultAssetBundler)]
        LOOP_LANG[Loop Supported Languages]
        LOAD_TRANS_FOR_LANG[Load Translations for Language]
        GEN_LANG_CONFIG_JSON[Generate Language-Specific config_lang.json]
        ASSEMBLE_MAIN_CONTENT_FOR_LANG[Assemble Main Content Blocks for Language]
        ASSEMBLE_FULL_HTML_PAGE[Assemble Full HTML Page <br> (using DefaultPageBuilder & base.html)]
        WRITE_HTML_FILE[Write Output HTML File (index_lang.html)]
    end

    BUILD_PY -- Uses --> INIT_CONFIG;
    BUILD_PY -- Uses --> PRELOAD_DATA_CACHE;
    BUILD_PY -- Uses --> COMPILE_WASM;
    BUILD_PY -- Uses --> BUNDLE_ASSETS;
    BUILD_PY -- Uses --> LOOP_LANG;
    LOOP_LANG -- For each lang --> LOAD_TRANS_FOR_LANG;
    LOOP_LANG -- For each lang --> GEN_LANG_CONFIG_JSON;
    LOOP_LANG -- For each lang --> ASSEMBLE_MAIN_CONTENT_FOR_LANG;

    subgraph "Assemble Main Content Blocks (Python + Jinja2)"
        direction LR
        GET_BLOCK_GENERATOR[Get HTMLBlockGenerator for Block <br> (from HTML_GENERATOR_REGISTRY)]
        GET_CACHED_PROTO_DATA[Get Cached Protobuf Data for Block]
        RENDER_BLOCK_HTML_JINJA[Render HTML for Block <br> (Jinja2 Execution via Generator)]
    end

    ASSEMBLE_MAIN_CONTENT_FOR_LANG -- Iterates Blocks --> GET_BLOCK_GENERATOR;
    GET_BLOCK_GENERATOR -- Uses --> PY_HTML_GENERATORS;
    GET_BLOCK_GENERATOR --> GET_CACHED_PROTO_DATA;
    GET_CACHED_PROTO_DATA --> RENDER_BLOCK_HTML_JINJA;
    RENDER_BLOCK_HTML_JINJA -- HTML String --> ASSEMBLE_MAIN_CONTENT_FOR_LANG;

    ASSEMBLE_MAIN_CONTENT_FOR_LANG -- Aggregated HTML String --> ASSEMBLE_FULL_HTML_PAGE;
    PY_PAGE_BUILDER -- Provides Header/Footer Logic via Jinja2 base --> ASSEMBLE_FULL_HTML_PAGE;
    PY_TRANSLATION_SVC -- Provides Translations to Jinja2 Context --> RENDER_BLOCK_HTML_JINJA;
    PY_TRANSLATION_SVC -- Provides Translations to Jinja2 Context --> ASSEMBLE_FULL_HTML_PAGE;
    ASSEMBLE_FULL_HTML_PAGE --> WRITE_HTML_FILE;
    WRITE_HTML_FILE --> I_OUTPUT_HTML[Output: index_lang.html];
    GEN_LANG_CONFIG_JSON --> J_LANG_CONFIG_OUTPUT[Output: public/generated_configs/config_lang.json];

    TS_SRC[Input: public/ts/*.ts] --> TSC[Tool: TypeScript Compiler (tsc)];
    TSC --> COMPILED_TS_JS[Generated: public/js (compiled from TS)];
    COMPILED_TS_JS --> JS_BUNDLER_PY[Python AssetBundler];
    EXISTING_JS_MODULES[Input: public/js/modules/*.js] --> JS_BUNDLER_PY;
    CSS_FILES[Input: templates/components/*/*.css, public/style.css] --> CSS_BUNDLER_PY[Python AssetBundler];

    JS_BUNDLER_PY --> FINAL_MAIN_JS[Generated: public/dist/assets/main.bundle.js];
    CSS_BUNDLER_PY --> FINAL_MAIN_CSS[Generated: public/dist/assets/main.bundle.css];
    FINAL_MAIN_JS --> H_BASE_HTML; // Linked in base.html
    FINAL_MAIN_CSS --> H_BASE_HTML; // Linked in base.html

    GO_WASM_SRC[Input: sads_wasm_poc/*.go] --> GO_COMPILER[Tool: Go Compiler (for WASM)];
    GO_COMPILER --> WASM_OUTPUT[Generated: sads_wasm_poc/sads_poc.wasm];
    WASM_OUTPUT --> WASM_COPIER_PY[Python AssetBundler];
    WASM_COPIER_PY --> FINAL_WASM_ASSET[Generated: public/dist/assets/wasm/sads_poc.wasm];
    FINAL_WASM_ASSET --> H_BASE_HTML; // Loaded by JS in base.html

    style A_CFG fill:#f9f,stroke:#333,stroke-width:2px
    style A_DATA fill:#f9f,stroke:#333,stroke-width:2px
    style C_PROTO fill:#f9f,stroke:#333,stroke-width:2px
    style TS_SRC fill:#f9f,stroke:#333,stroke-width:2px
    style EXISTING_JS_MODULES fill:#f9f,stroke:#333,stroke-width:2px
    style CSS_FILES fill:#f9f,stroke:#333,stroke-width:2px
    style F_TEMPLATES fill:#f9f,stroke:#333,stroke-width:2px
    style G_LOCALES fill:#f9f,stroke:#333,stroke-width:2px
    style H_BASE_HTML fill:#f9f,stroke:#333,stroke-width:2px
    style GO_WASM_SRC fill:#f9f,stroke:#333,stroke-width:2px

    style D_PROTOC fill:#ffc66d,stroke:#333,stroke-width:2px
    style TSC fill:#ffc66d,stroke:#333,stroke-width:2px
    style GO_COMPILER fill:#ffc66d,stroke:#333,stroke-width:2px

    style E_PY_STUBS fill:#ccf,stroke:#333,stroke-width:2px
    style COMPILED_TS_JS fill:#ccf,stroke:#333,stroke-width:2px
    style WASM_OUTPUT fill:#ccf,stroke:#333,stroke-width:2px
    style I_OUTPUT_HTML fill:#cfc,stroke:#333,stroke-width:2px
    style J_LANG_CONFIG_OUTPUT fill:#cfc,stroke:#333,stroke-width:2px
    style FINAL_MAIN_JS fill:#cfc,stroke:#333,stroke-width:2px
    style FINAL_MAIN_CSS fill:#cfc,stroke:#333,stroke-width:2px
    style FINAL_WASM_ASSET fill:#cfc,stroke:#333,stroke-width:2px

    style BUILD_PY fill:#9cf,stroke:#333,stroke-width:4px

    style PY_DATA_HANDLING fill:#cde,stroke:#333,stroke-width:2px
    style PY_DATA_CACHE fill:#cde,stroke:#333,stroke-width:2px
    style PY_TRANSLATION_SVC fill:#cde,stroke:#333,stroke-width:2px
    style PY_PAGE_BUILDER fill:#cde,stroke:#333,stroke-width:2px
    style PY_HTML_GENERATORS fill:#cde,stroke:#333,stroke-width:2px
    style JINJA_ENV fill:#cde,stroke:#333,stroke-width:2px
    style JS_BUNDLER_PY fill:#cde,stroke:#333,stroke-width:2px
    style CSS_BUNDLER_PY fill:#cde,stroke:#333,stroke-width:2px
    style WASM_COPIER_PY fill:#cde,stroke:#333,stroke-width:2px


    style INIT_CONFIG fill:#lightgrey,stroke:#333
    style PRELOAD_DATA_CACHE fill:#lightgrey,stroke:#333
    style COMPILE_WASM fill:#lightgrey,stroke:#333
    style BUNDLE_ASSETS fill:#lightgrey,stroke:#333
    style LOOP_LANG fill:#lightgrey,stroke:#333
    style LOAD_TRANS_FOR_LANG fill:#lightgrey,stroke:#333
    style GEN_LANG_CONFIG_JSON fill:#lightgrey,stroke:#333
    style ASSEMBLE_MAIN_CONTENT_FOR_LANG fill:#lightgrey,stroke:#333
    style ASSEMBLE_FULL_HTML_PAGE fill:#lightgrey,stroke:#333
    style WRITE_HTML_FILE fill:#lightgrey,stroke:#333

    style GET_BLOCK_GENERATOR fill:#whitesmoke,stroke:#333
    style GET_CACHED_PROTO_DATA fill:#whitesmoke,stroke:#333
    style RENDER_BLOCK_HTML_JINJA fill:#whitesmoke,stroke:#333
```

### Explanation of Diagram (Python-based Build)

The diagram illustrates the data flow and component interactions within the Python-based `build.py` script, which serves as the build orchestrator for generating static HTML pages. This process uses Jinja2 for templating, Protobuf for data structuring, and various Python modules for different aspects of the build.

1.  **Inputs (Pink Nodes)**:
    - **`public/config.json`**: Main configuration file defining site settings, supported languages, block order, data file references, and paths to Protobuf message types.
    - **`data/*.json`**: JSON files containing content for dynamic blocks (e.g., hero text, portfolio items), structured according to Protobuf definitions.
    - **`proto/*.proto`**: Protocol Buffer files defining the schema for the data in `data/*.json`.
    - **`templates/**/\*.html`**: Jinja2 HTML template files, including `base.html`(overall page structure) and component templates (e.g.,`templates/components/hero/hero.html`).
    - **`public/locales/*.json`**: JSON files holding translations for different languages.
    - **`public/ts/*.ts`**: TypeScript source files for client-side scripting.
    - **`public/js/modules/*.js`**: Existing JavaScript module files.
    - **`templates/components/*/*.css`, `public/style.css`**: CSS files for styling.
    - **`sads_wasm_poc/*.go`**: Go source files for the SADS WASM module.

2.  **Initial Processing & Tools (Orange Nodes)**:
    - **`protoc`**: The Protocol Buffer compiler.
    - **`protoc-gen-python`**: A `protoc` plugin used to generate Python source files (`_pb2.py`) from `.proto` definitions. These are output to the `generated/` directory.
    - **`tsc` (TypeScript Compiler)**: Compiles TypeScript files (`*.ts`) into JavaScript files, typically output into `public/js/`.
    - **`Go Compiler`**: Compiles Go source files into a WASM module (`sads_poc.wasm`).

3.  **Generated Intermediate Files (Light Blue Nodes)**:
    - **`generated/*.py`**: Python files generated by `protoc`, containing class definitions for Protobuf messages.
    - **`public/js/*.js` (from TS)**: JavaScript files compiled from TypeScript.
    - **`sads_wasm_poc/sads_poc.wasm`**: The compiled WebAssembly module.

4.  **Core Python Services/Logic (Light Cyan Nodes)**:
    - **`Python Data Handling Logic (JsonProtoDataLoader)`**: (`build_protocols/data_loading.py`) Responsible for:
      - Reading JSON files from `data/`.
      - Unmarshalling JSON data into Python Protobuf message objects (using the generated `_pb2.py` stubs).
    - **`Python Data Cache (InMemoryDataCache)`**: (`build_protocols/data_loading.py`) An in-memory cache (Python dictionary) to store loaded Protobuf message objects, avoiding redundant file reads and parsing.
    - **`Python Translation Service (DefaultTranslationProvider)`**: (`build_protocols/translation.py`) Loads translation strings from `public/locales/*.json` for the current language.
    - **`Jinja2 Environment`**: Initialized in `build.py` to load and manage Jinja2 templates from the `templates/` directory.
    - **`Python HTML Block Generators`**: (`build_protocols/html_generation.py`) A collection of classes (e.g., `PortfolioHtmlGenerator`, `HeroHtmlGenerator`) inheriting from `BaseHtmlGenerator`. Each generator is responsible for rendering a specific component's HTML using its associated Jinja2 template and data. They are registered in `HTML_GENERATOR_REGISTRY`.
    - **`Python Page Assembly Logic (DefaultPageBuilder)`**: (`build_protocols/page_assembly.py`) Uses the Jinja2 `base.html` template to assemble the final HTML page, incorporating the main content (concatenated HTML from block generators), navigation data, site logo data, and translations.
    - **`Python AssetBundler (DefaultAssetBundler)`**: (`build_protocols/asset_bundling.py`) Handles:
      - **`JS_BUNDLER_PY`**: Concatenating/minifying JavaScript files (compiled TS and existing JS modules) into a single bundle (e.g., `main.bundle.js`).
      - **`CSS_BUNDLER_PY`**: Concatenating/minifying CSS files into a single bundle (e.g., `main.bundle.css`).
      - **`WASM_COPIER_PY`**: Copying the compiled WASM module and related JavaScript (e.g., `wasm_exec.js`) to the distribution directory.

5.  **`build.py` - BuildOrchestrator (Dark Blue Node)**: The central Python script that drives the static site generation.
    - It initializes and coordinates all services and steps.
    - **Core Logic (Grey Subgraph "build.py - BuildOrchestrator Core Logic")**:
      - **Load Initial Configurations**: Reads `public/config.json` using `DefaultAppConfigManager` to get site-wide settings, language lists, block configurations (including Protobuf message type names for each block), navigation data file path, and site logo data file path. Loads navigation and site logo data into Protobuf messages.
      - **Preload Data Cache**: Iterates through block configurations, resolves Protobuf message type names to actual Python classes (from `generated/` modules), loads relevant JSON data files using `JsonProtoDataLoader`, and stores the resulting Protobuf message objects in `InMemoryDataCache`.
      - **Compile Go WASM Module**: Executes the Go compiler to build the `sads_poc.wasm` module.
      - **Bundle Assets**: Invokes `DefaultAssetBundler` to process CSS, JS, and WASM files, outputting them to `public/dist/assets/`.
      - **Loop Supported Languages**: Iterates through each language specified in `public/config.json`.
      - **Load Translations for Language**: For the current language, loads the corresponding locale file using `DefaultTranslationProvider`.
      - **Generate Language-Specific `config_lang.json`**: Creates a language-specific JSON configuration file (e.g., `public/generated_configs/config_en.json`) for client-side use, using `DefaultAppConfigManager`.
      - **Assemble Main Content Blocks for Language**: For the current language, iterates through the blocks defined in `config.json`. (See "Assemble Main Content Blocks (Python + Jinja2)" subgraph).
      - **Assemble Full HTML Page**: Uses `DefaultPageBuilder` and the Jinja2 `base.html` template to combine the header, footer, site logo, navigation, and the assembled main content blocks into a complete HTML page.
      - **Write Output HTML File**: Saves the fully rendered HTML page (e.g., `index.html` for the default language, `index_es.html` for Spanish).

6.  **Assemble Main Content Blocks (Python + Jinja2) (Light Grey Subgraph)**: This process is managed by `BuildOrchestrator` for each component/block.
    - **Get HTMLBlockGenerator for Block**: Retrieves the appropriate generator class from `HTML_GENERATOR_REGISTRY` based on the block's configured template name.
    - **Get Cached Protobuf Data for Block**: Fetches the necessary Protobuf message data (previously loaded and cached) for the current block from `InMemoryDataCache`.
    - **Render HTML for Block (Jinja2 Execution via Generator)**: The selected `HtmlBlockGenerator` instance uses its `generate_html` method. This method typically loads its specific Jinja2 template (e.g., `components/hero/hero.html`) and renders it with the Protobuf data and current language translations, producing an HTML string for that block.

7.  **Outputs (Green Nodes)**:
    - **`index_lang.html`**: Final, fully assembled, and translated static HTML pages for each language.
    - **`public/generated_configs/config_lang.json`**: Language-specific configuration files for client-side JavaScript.
    - **`public/dist/assets/main.bundle.js`**: Bundled JavaScript.
    - **`public/dist/assets/main.bundle.css`**: Bundled CSS.
    - **`public/dist/assets/wasm/sads_poc.wasm`**: Copied WASM module.

This Python-centric architecture leverages Jinja2 for flexible templating, Protobuf for robust data definition, and a modular system of Python classes and protocols (`build_protocols/`) to manage different aspects of the build process.
