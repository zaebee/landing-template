import json

def main():
    # Read the configuration file
    with open("config.json", "r") as f:
        config = json.load(f)

    # Read the header and footer content
    with open("index.html", "r") as f:
        content = f.read()
        header = content.split("<main>")[0] + "<main>\n"
        footer = "\n</main>" + content.split("</main>")[1]

    # Assemble the blocks
    blocks_content = []
    for block_file in config["blocks"]:
        with open(f"blocks/{block_file}", "r") as f:
            blocks_content.append(f.read())

    # Write the new index.html file
    with open("index.html", "w") as f:
        f.write(header)
        f.write("\n".join(blocks_content))
        f.write(footer)

if __name__ == "__main__":
    main()
