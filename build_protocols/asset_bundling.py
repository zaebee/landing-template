"""
Handles bundling of CSS and JavaScript assets for the project.
"""
import os
from typing import List, Optional

# Assuming AssetBundler interface will be in build_protocols.interfaces
# from .interfaces import AssetBundler
# For now, we'll define it structurally. If interfaces.py is importable, use above.

class DefaultAssetBundler: # Implements AssetBundler (structurally)
    """
    Default implementation for bundling CSS and JavaScript assets.
    """

    def bundle_css(self, project_root: str, output_dir: str) -> Optional[str]:
        """Finds all component CSS files and bundles them into a single file."""
        print("Bundling component CSS files...")
        component_css_dir = os.path.join(project_root, "templates", "components")
        # output_dir is now passed as an argument
        output_file_path = os.path.join(output_dir, "main.css")

        os.makedirs(output_dir, exist_ok=True)
        css_contents: List[str] = []

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
                        # Optionally, return None here if any read fails
                        # For now, we'll try to bundle what we can

        if not css_contents:
            print("No component CSS files found to bundle.")
            try:
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write("/* No component CSS found or bundled. */")
                print(f"Created empty CSS bundle: {output_file_path}")
                return output_file_path # Return path to empty bundle
            except IOError as e:
                print(f"Error creating empty CSS bundle {output_file_path}: {e}")
                return None

        try:
            with open(output_file_path, "w", encoding="utf-8") as outfile:
                outfile.write("\n\n/* --- Component CSS Bundle --- */\n\n")
                for content in css_contents:
                    outfile.write(content)
                    outfile.write("\n\n/* --- End of component CSS --- */\n\n")
            print(f"Successfully bundled CSS to: {output_file_path}")
            return output_file_path
        except IOError as e:
            print(f"Error writing bundled CSS to {output_file_path}: {e}")
            return None

    def bundle_js(self, project_root: str, output_dir: str) -> Optional[str]:
        """Finds all component JS files and shared JS, bundles them."""
        print("Bundling JavaScript files...")
        js_files_to_bundle: List[str] = []

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

        sads_default_theme_path = os.path.join(shared_js_dir, "sads-default-theme.js")
        sads_engine_path = os.path.join(shared_js_dir, "sads-style-engine.js")
        app_js_path = os.path.join(shared_js_dir, "app.js")

        # Ordered list for insertion
        ordered_shared_js = []
        if os.path.exists(sads_default_theme_path):
            ordered_shared_js.append(sads_default_theme_path)
            print(f"Found SADS Default Theme JS: {sads_default_theme_path}")
        else:
            print(f"Warning: SADS Default Theme JS not found at {sads_default_theme_path}")

        if os.path.exists(sads_engine_path):
            ordered_shared_js.append(sads_engine_path)
            print(f"Found SADS Engine JS: {sads_engine_path}")
        else:
            print(f"Warning: SADS Engine JS not found at {sads_engine_path}")

        if os.path.exists(app_js_path):
            ordered_shared_js.append(app_js_path)
            print(f"Found shared App JS: {app_js_path}")
        else:
            print(f"Warning: App JS not found at {app_js_path}")

        # Prepend shared JS to component JS
        js_files_to_bundle = ordered_shared_js + js_files_to_bundle

        # output_dir is now passed as an argument
        output_file_path = os.path.join(output_dir, "main.js")
        os.makedirs(output_dir, exist_ok=True)

        if not js_files_to_bundle:
            print("No JavaScript files found to bundle.")
            try:
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write("// No JavaScript files found or bundled.")
                print(f"Created empty JS bundle: {output_file_path}")
                return output_file_path # Return path to empty bundle
            except IOError as e:
                print(f"Error creating empty JS bundle {output_file_path}: {e}")
                return None

        js_contents: List[str] = []
        for file_path in js_files_to_bundle:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    js_contents.append(f.read())
            except IOError as e:
                print(f"Error reading JS file {file_path}: {e}")
                # Optionally, return None here

        try:
            with open(output_file_path, "w", encoding="utf-8") as outfile:
                outfile.write("\n// --- JavaScript Bundle --- //\n\n")
                for i, content in enumerate(js_contents):
                    original_path = js_files_to_bundle[i]
                    outfile.write(f"\n// --- Source: {os.path.basename(original_path)} --- //\n")
                    outfile.write(content)
                    outfile.write("\n// --- End Source --- //\n\n")
            print(f"Successfully bundled JavaScript to: {output_file_path}")
            return output_file_path
        except IOError as e:
            print(f"Error writing bundled JavaScript to {output_file_path}: {e}")
            return None
