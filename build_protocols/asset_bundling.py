"""
Handles bundling of CSS and JavaScript assets for the project.
"""
import os


def bundle_component_css(project_root: str) -> None:
    """Finds all component CSS files and bundles them into a single file."""
    print("Bundling component CSS files...")
    component_css_dir = os.path.join(project_root, "templates", "components")
    output_dir = os.path.join(project_root, "public", "dist")
    output_file_path = os.path.join(output_dir, "main.css")

    os.makedirs(output_dir, exist_ok=True)
    css_contents = []

    for component_name in os.listdir(component_css_dir):
        component_dir_path = os.path.join(component_css_dir, component_name)
        if os.path.isdir(component_dir_path):
            css_file_path = os.path.join(component_dir_path, f"{component_name}.css")
            if os.path.exists(css_file_path):
                try:
                    with open(css_file_path, "r", encoding="utf-8") as f:
                        css_contents.append(f.read())
                    print(f"Read CSS from: {css_file_path}")
                except IOError as e:
                    print(f"Error reading CSS file {css_file_path}: {e}")

    if not css_contents:
        print("No component CSS files found to bundle.")
        # Create an empty main.css if no components have CSS
        # to avoid missing file errors if base.html links to it.
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write("/* No component CSS found or bundled. */")
            print(f"Created empty CSS bundle: {output_file_path}")
        except IOError as e:
            print(f"Error creating empty CSS bundle {output_file_path}: {e}")
        return

    try:
        with open(output_file_path, "w", encoding="utf-8") as outfile:
            outfile.write("\n\n/* --- Component CSS Bundle --- */\n\n")
            for content in css_contents:
                outfile.write(content)
                outfile.write("\n\n/* --- End of component CSS --- */\n\n")
        print(f"Successfully bundled CSS to: {output_file_path}")
    except IOError as e:
        print(f"Error writing bundled CSS to {output_file_path}: {e}")

def bundle_component_js(project_root: str) -> None:
    """Finds all component JS files and shared JS, bundles them."""
    print("Bundling JavaScript files...")
    js_files_to_bundle = []

    # 1. Component-specific JS
    component_js_dir = os.path.join(project_root, "templates", "components")
    for component_name in os.listdir(component_js_dir):
        component_dir_path = os.path.join(component_js_dir, component_name)
        if os.path.isdir(component_dir_path):
            js_file_path = os.path.join(component_dir_path, f"{component_name}.js")
            if os.path.exists(js_file_path):
                js_files_to_bundle.append(js_file_path)
                print(f"Found component JS: {js_file_path}")

    # 2. Shared/Global JS
    shared_js_dir = os.path.join(project_root, "public", "js")

    # Order of shared JS is important:
    # 1. Default theme for SADS
    # 2. SADS engine
    # 3. Main application logic (app.js)
    # 4. Component-specific JS (added earlier)

    sads_default_theme_path = os.path.join(shared_js_dir, "sads-default-theme.js")
    if os.path.exists(sads_default_theme_path):
        js_files_to_bundle.insert(0, sads_default_theme_path)
        print(f"Found SADS Default Theme JS: {sads_default_theme_path}")
    else:
        print(f"Warning: SADS Default Theme JS not found at {sads_default_theme_path}")

    sads_engine_path = os.path.join(shared_js_dir, "sads-style-engine.js")
    if os.path.exists(sads_engine_path):
        # Insert after default theme if present, otherwise at the beginning
        insert_idx = 1 if sads_default_theme_path in js_files_to_bundle else 0
        js_files_to_bundle.insert(insert_idx, sads_engine_path)
        print(f"Found SADS Engine JS: {sads_engine_path}")
    else:
        print(f"Warning: SADS Engine JS not found at {sads_engine_path}")

    app_js_path = os.path.join(shared_js_dir, "app.js")
    if os.path.exists(app_js_path):
        # Insert after default theme and SADS engine if present
        insert_idx = 0
        if sads_default_theme_path in js_files_to_bundle:
            insert_idx +=1
        if sads_engine_path in js_files_to_bundle:
            insert_idx +=1
        js_files_to_bundle.insert(insert_idx, app_js_path)
        print(f"Found shared App JS: {app_js_path}")
    else:
        print(f"Warning: App JS not found at {app_js_path}")

    output_dir = os.path.join(project_root, "public", "dist")
    output_file_path = os.path.join(output_dir, "main.js")
    os.makedirs(output_dir, exist_ok=True)

    if not js_files_to_bundle:
        print("No JavaScript files found to bundle.")
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write("// No JavaScript files found or bundled.")
            print(f"Created empty JS bundle: {output_file_path}")
        except IOError as e:
            print(f"Error creating empty JS bundle {output_file_path}: {e}")
        return

    js_contents = []
    for file_path in js_files_to_bundle:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                js_contents.append(f.read())
        except IOError as e:
            print(f"Error reading JS file {file_path}: {e}")

    try:
        with open(output_file_path, "w", encoding="utf-8") as outfile:
            outfile.write("\n// --- JavaScript Bundle --- //\n\n")
            for i, content in enumerate(js_contents):
                original_path = js_files_to_bundle[i]
                outfile.write(f"\n// --- Source: {os.path.basename(original_path)} --- //\n")
                outfile.write(content)
                outfile.write("\n// --- End Source --- //\n\n")
        print(f"Successfully bundled JavaScript to: {output_file_path}")
    except IOError as e:
        print(f"Error writing bundled JavaScript to {output_file_path}: {e}")
