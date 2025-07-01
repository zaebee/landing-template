"""
Builds the index.html file from configured blocks.
"""

import json


def main():
    """Reads config, assembles blocks, and writes new index.html."""
    # Read the configuration file
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    # Read the header and footer content
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
        header = content.split("<main>")[0] + "<main>\n"
        footer = "\n</main>" + content.split("</main>")[1]

    # Assemble the blocks
    blocks_content = []
    for block_file in config["blocks"]:
        with open(f"blocks/{block_file}", "r", encoding="utf-8") as f:
            blocks_content.append(f.read())

    # Write the new index.html file
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(blocks_content))
        f.write(footer)


if __name__ == "__main__":
    main()
