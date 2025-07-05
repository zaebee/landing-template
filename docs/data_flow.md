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

## Data Flow in `build.py`

The `build.py` script is responsible for generating the static HTML pages (`index.html`, `index_es.html`, etc.) by assembling HTML blocks and populating them with dynamic data and translations.

```mermaid
graph TD
    A_CFG[Input: public/config.json] --> ORCHESTRATOR{BuildOrchestrator};
    A_DATA[Input: data/*.json] --> DATA_LOADER;
    C_PROTO[Input: proto/*.proto] --> D_PROTOC[Tool: protoc + Plugins];
    D_PROTOC -- Generates Python --> E_PY_STUBS[Generated: generated/*.py];
    D_PROTOC -- Generates TypeScript --> E_TS_PROTO_STUBS[Generated: public/ts/generated_proto/*.ts];
    E_PY_STUBS --> DATA_LOADER[Service: JsonProtoDataLoader];

    TS_SRC[Input: public/ts/**/*.ts] --> TSC_COMPILER[Tool: tsc];
    E_TS_PROTO_STUBS --> TSC_COMPILER;
    TSC_COMPILER --> COMPILED_TS_JS[Generated: public/js/compiled_ts/*.js];

    F_BLOCKS[Input: templates/components/*/*.html] --> ORCHESTRATOR;
    G_LOCALES[Input: public/locales/*.json] --> TRANS_PROVIDER[Service: DefaultTranslationProvider];
    H_BASE_HTML[Input: templates/base.html Base Template] --> PAGE_BUILDER[Service: DefaultPageBuilder];

    DATA_LOADER -- Protobuf Objects --> DATA_CACHE[Service: InMemoryDataCache];
    DATA_CACHE -- Cached Data --> ORCHESTRATOR;
    TRANS_PROVIDER -- Translations --> ORCHESTRATOR;
    PAGE_BUILDER -- Page Structuring Logic --> ORCHESTRATOR;

    subgraph "BuildOrchestrator Core Logic"
        direction LR
        INIT[Load Initial Configs<br>AppConfigManager]
        PRELOAD[Preload Data<br>DataLoader, DataCache]
        LOOP_LANG[Loop Languages]
        LOAD_TRANS[Load Translations<br>TranslationProvider]
        GEN_LANG_CFG[Generate Lang Config<br>AppConfigManager]
        ASSEMBLE_MAIN[Assemble Main Content]
        ASSEMBLE_PAGE[Assemble Full Page<br>PageBuilder]
        WRITE_PAGE[Write Output HTML]
    end

    ORCHESTRATOR -- Uses --> INIT;
    ORCHESTRATOR -- Uses --> PRELOAD;
    ORCHESTRATOR -- Uses --> LOOP_LANG;
    LOOP_LANG -- For each lang --> LOAD_TRANS;
    LOOP_LANG -- For each lang --> GEN_LANG_CFG;
    LOOP_LANG -- For each lang --> ASSEMBLE_MAIN;

    subgraph "Assemble Main Content Per Language"
        direction LR
        LOAD_BLOCK_TPL[Load Block Template]
        GET_CACHED_DATA[Get Cached Data for Block]
        GEN_BLOCK_HTML[Generate HTML for Block<br>HtmlBlockGenerator]
        REPLACE_PLACEHOLDER[Replace Placeholder in Template]
        TRANSLATE_BLOCK[Translate Block Content<br>TranslationProvider]
    end

    ASSEMBLE_MAIN -- Iterates Blocks --> LOAD_BLOCK_TPL;
    LOAD_BLOCK_TPL --> GET_CACHED_DATA;
    GET_CACHED_DATA --> GEN_BLOCK_HTML;
    GEN_BLOCK_HTML --> REPLACE_PLACEHOLDER[Jinja handles this];
    REPLACE_PLACEHOLDER --> TRANSLATE_BLOCK[Jinja handles this];

    ASSEMBLE_MAIN -- Aggregated HTML Parts --> ASSEMBLE_PAGE;
    PAGE_BUILDER -- Provides Header/Footer --> ASSEMBLE_PAGE;
    TRANS_PROVIDER -- Translates Header/Footer --> ASSEMBLE_PAGE;
    ASSEMBLE_PAGE --> WRITE_PAGE;
    WRITE_PAGE --> I_OUTPUT_HTML[Output: index_lang.html];

    HTML_GENERATORS[Services: HtmlBlockGenerators<br>e.g., HeroHtmlGenerator] --> GEN_BLOCK_HTML;

    EXISTING_JS_MODULES[Input: public/js/modules/*.js] --> JS_BUNDLER[Tool: AssetBundler (Python)];
    COMPILED_TS_JS --> JS_BUNDLER;
    JS_BUNDLER --> FINAL_MAIN_JS[Generated: public/dist/main.js];
    FINAL_MAIN_JS --> H_BASE_HTML; // main.js is linked in base.html

    style A_CFG fill:#f9f,stroke:#333,stroke-width:2px
    style A_DATA fill:#f9f,stroke:#333,stroke-width:2px
    style C_PROTO fill:#f9f,stroke:#333,stroke-width:2px
    style TS_SRC fill:#f9f,stroke:#333,stroke-width:2px
    style EXISTING_JS_MODULES fill:#f9f,stroke:#333,stroke-width:2px
    style F_BLOCKS fill:#f9f,stroke:#333,stroke-width:2px
    style G_LOCALES fill:#f9f,stroke:#333,stroke-width:2px
    style H_BASE_HTML fill:#f9f,stroke:#333,stroke-width:2px

    style D_PROTOC fill:#ffc66d,stroke:#333,stroke-width:2px
    style TSC_COMPILER fill:#ffc66d,stroke:#333,stroke-width:2px
    style JS_BUNDLER fill:#ffc66d,stroke:#333,stroke-width:2px

    style E_PY_STUBS fill:#ccf,stroke:#333,stroke-width:2px
    style E_TS_PROTO_STUBS fill:#ccf,stroke:#333,stroke-width:2px
    style COMPILED_TS_JS fill:#ccf,stroke:#333,stroke-width:2px
    style FINAL_MAIN_JS fill:#ccf,stroke:#333,stroke-width:2px

    style I_OUTPUT_HTML fill:#cfc,stroke:#333,stroke-width:2px
    style ORCHESTRATOR fill:#9cf,stroke:#333,stroke-width:4px

    style DATA_LOADER fill:#cde,stroke:#333,stroke-width:2px
    style DATA_CACHE fill:#cde,stroke:#333,stroke-width:2px
    style TRANS_PROVIDER fill:#cde,stroke:#333,stroke-width:2px
    style PAGE_BUILDER fill:#cde,stroke:#333,stroke-width:2px
    style HTML_GENERATORS fill:#cde,stroke:#333,stroke-width:2px

    style INIT fill:#lightgrey,stroke:#333
    style PRELOAD fill:#lightgrey,stroke:#333
    style LOOP_LANG fill:#lightgrey,stroke:#333
    style LOAD_TRANS fill:#lightgrey,stroke:#333
    style GEN_LANG_CFG fill:#lightgrey,stroke:#333
    style ASSEMBLE_MAIN fill:#lightgrey,stroke:#333
    style ASSEMBLE_PAGE fill:#lightgrey,stroke:#333
    style WRITE_PAGE fill:#lightgrey,stroke:#333

    style LOAD_BLOCK_TPL fill:#whitesmoke,stroke:#333
    style GET_CACHED_DATA fill:#whitesmoke,stroke:#333
    style GEN_BLOCK_HTML fill:#whitesmoke,stroke:#333
    style REPLACE_PLACEHOLDER fill:#whitesmoke,stroke:#333
    style TRANSLATE_BLOCK fill:#whitesmoke,stroke:#333
```

### Explanation of Diagram

The diagram illustrates the data flow and component interactions within the `build.py` script, which uses a `BuildOrchestrator` to manage the page generation process. This now includes steps for handling TypeScript source files and generating TypeScript from Protobuf definitions.

1. **Inputs (Pink Nodes)**:
   - **`public/config.json`**: Main configuration file.
   - **`data/*.json`**: JSON content files.
   - **`proto/*.proto`**: Protocol Buffer schema definitions (including `sads_attributes.proto`).
   - **`public/ts/**/\*.ts` (TS_SRC)\*\*: Source TypeScript files for client-side logic (e.g., SADS engine, UI interactions).
   - **`public/js/modules/*.js` (EXISTING_JS_MODULES)**: Existing JavaScript modules.
   - **`templates/components/*/*.html`**: HTML templates for components.
   - **`public/locales/*.json`**: Translation files.
   - **`templates/base.html` (Base Template)**: Main HTML page structure.

2. **Initial Processing & Tools (Orange Nodes)**:
   - **`protoc + Plugins` (D_PROTOC)**: The Protocol Buffer compiler and associated plugins (for Python and TypeScript). It processes `.proto` files.
     - Generates Python stub files: **`generated/*.py` (E_PY_STUBS)**.
     - Generates TypeScript definition files: **`public/ts/generated_proto/*.ts` (E_TS_PROTO_STUBS)**.
   - **`tsc` (TSC_COMPILER)**: The TypeScript compiler. It processes all TypeScript files in `public/ts/` (including source files and generated proto TS files).
     - Generates JavaScript files: **`public/js/compiled_ts/*.js` (COMPILED_TS_JS)**.
   - **`AssetBundler (Python)` (JS_BUNDLER)**: This is part of `build.py`'s logic (`asset_bundling.py`). It concatenates JavaScript files.
     - Takes input from `COMPILED_TS_JS` (compiled TypeScript) and `EXISTING_JS_MODULES`.
     - Produces the final bundled JavaScript: **`public/dist/main.js` (FINAL_MAIN_JS)**.
     - (It also bundles CSS into `public/dist/main.css`, not detailed in this part of the diagram update but functions similarly).

3. **Core Python Services (Light Cyan Nodes in Diagram, some roles adjusted)**:
   - **`JsonProtoDataLoader`**: Reads JSON data, validates against Python Protobuf stubs (`E_PY_STUBS`), converts to Python Protobuf objects.
   - **`InMemoryDataCache`**: Caches loaded Protobuf objects.
   - **`DefaultTranslationProvider`**: Loads translations.
   - **`DefaultPageBuilder`**: Manages the overall HTML page structure. It uses the base `templates/base.html` (via its Jinja environment) and assembles the final page with processed component HTML.
   - **`HtmlBlockGenerators` (e.g., `HeroHtmlGenerator`, `PortfolioHtmlGenerator`)**: A collection of classes, each responsible for generating the specific HTML for a type of content component. They use their own Jinja environment to load and render templates from `templates/components/`, injecting data and translations.

4. **`BuildOrchestrator` (Dark Blue Node)**: The central component in `build.py`.
   - It initializes and coordinates all services.
   - **Core Logic (Grey Subgraph)**:
     - **Load Initial Configs**: Uses `DefaultAppConfigManager` to load `public/config.json` and navigation data.
     - **Preload Data**: Instructs the `JsonProtoDataLoader` to load all necessary dynamic data, which is then stored in `InMemoryDataCache`.
     - **Loop Languages**: Iterates through each supported language defined in `config.json`.
     - **Load Translations**: For the current language, uses `DefaultTranslationProvider` to load the relevant locale file, making translations available.
     - **Generate Lang Config**: Uses `DefaultAppConfigManager` to create a language-specific version of the configuration (e.g., `public/generated_configs/config_en.json`).
     - **Assemble Main Content**: For the current language, orchestrates the generation of HTML for all content blocks. (See "Assemble Main Content Per Language" subgraph).
     - **Assemble Full Page**: Uses `DefaultPageBuilder` to combine the translated header, footer (rendered as part of `base.html`), and the assembled main content into a complete HTML page.
     - **Write Output HTML**: Saves the generated page to a file (e.g., `index_en.html`).

5. **Assemble Main Content Per Language (Light Grey Subgraph)**: This process is executed by `BuildOrchestrator` for each component specified in `config.json`.
   - **`HtmlBlockGenerator` Selection**: The orchestrator selects the appropriate `HtmlBlockGenerator` for the current block.
   - **Get Cached Data**: Retrieves the relevant Protobuf data for this block from `InMemoryDataCache`.
   - **Generate HTML for Component (`GEN_BLOCK_HTML`)**:
     - The selected `HtmlBlockGenerator` is invoked.
     - It uses its Jinja environment to load its specific component template from `templates/components/<component_name>/<component_name>.html` (`LOAD_BLOCK_TPL` effectively happens here).
     - It renders the template, passing in the cached data and the `translations` object. The Jinja template itself handles the injection of data and translation lookups (e.g., `{{ item.title }}`, `{{ translations.get('my_key') }}`).
     - The output is fully formed, translated HTML for that block.
   - The steps `REPLACE_PLACEHOLDER` and `TRANSLATE_BLOCK` (as separate post-processing steps on raw block HTML) are largely subsumed by the Jinja rendering process within the `HtmlBlockGenerator`.

6. **Output (Green Node)**:
   - **`index_lang.html`**: The final, fully assembled, and translated HTML pages for each supported language (e.g., `index.html`, `index_es.html`).

This modular, service-oriented architecture allows for clear separation of concerns: data loading, translation, HTML generation for specific blocks, and overall page assembly are handled by distinct components, orchestrated by `BuildOrchestrator`.
This setup ensures that data handling is strongly typed and structured, improving maintainability and reducing potential errors. The build process is configuration-driven and supports internationalization.
