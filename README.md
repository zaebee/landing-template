# landing-template

Template website with landing page to track telegram bot user source.

## Structure

The `index.html` is built dynamically from HTML blocks located in the
`blocks/` directory. The order and inclusion of these blocks are defined
in `config.json`.

## Building `index.html`

To build or update `index.html` after making changes to the blocks or
`config.json`, run the following command:

```bash
npm run build
```

This will execute the `build.py` script, which reads `config.json` and
assembles the blocks into `index.html`.

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
