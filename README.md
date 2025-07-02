# landing-template

Template site with landing page to track telegram bot user source.

## Structure

The `index.html` is built dynamically from HTML blocks located in the
`blocks/` directory. The order and inclusion of these blocks are defined
in `config.json`.

## Building `index.html`

The `build.py` script uses Protocol Buffers for managing data structures related to blog posts and portfolio items. Therefore, you need to generate the Python stubs from the `.proto` definitions before running the build.

**Prerequisites:**

1. Ensure you have Python and Node.js installed.
2. Install Python dependencies:

    ```bash
    pip install -r requirements.txt
    # For linting and type checking, also install dev dependencies:
    pip install -r requirements-dev.txt
    ```

    *(Note: `requirements.txt` will need to be created or updated if it doesn't include `grpcio-tools` and `protobuf`)*

**Steps to Build:**

1. **Generate Protobuf Stubs (if not already done or if `.proto` files changed):**
    Run the following command to generate the necessary Python files from the `.proto` definitions into the `generated/` directory:

    ```bash
    npm run generate-proto
    ```

    This script handles directory creation, invokes the Protocol Buffer compiler (`protoc`), and ensures the `generated` directory is treated as a Python package.

2. **Run the Build Command:**
    To build or update `index.html` and language-specific versions (e.g., `index_es.html`) after making changes to blocks, `config.json`, or data:

    ```bash
    npm run build
    ```

    This executes `python build.py`, which reads `config.json`, loads data (using the generated Protobuf stubs), assembles HTML blocks, applies translations, and writes the final `index.html` files.

## Customizing Blocks

- **Add a new block**:

    1. Create a new HTML file in the `blocks/` directory (e.g., `my-new-block.html`).
    2. Add the desired HTML content to this file.
    3. Include the filename in the `blocks` array in `config.json` at the desired position.

- **Remove a block**:

    1. Remove the block's filename from the `blocks` array in `config.json`.

- **Reorder blocks**:

    1. Change the order of filenames in the `blocks` array in `config.json`.

After any changes to `blocks/` or `config.json`, remember to run
`npm run build` to regenerate `index.html`.
