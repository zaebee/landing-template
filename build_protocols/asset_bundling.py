"""
Handles bundling of CSS and JavaScript assets for the project,
and copying of WebAssembly related assets.
"""

import os
import shutil  # Added for file copying
from typing import List, Optional

# Assuming AssetBundler interface will be in build_protocols.interfaces
# from .interfaces import AssetBundler
# For now, we'll define it structurally. If interfaces.py is importable, use above.


class DefaultAssetBundler:  # Implements AssetBundler (structurally)
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
                css_file_path = os.path.join(
                    component_dir_path, f"{component_name}.css"
                )
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
                return output_file_path  # Return path to empty bundle
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
        modules_dir = os.path.join(shared_js_dir, "modules")

        # Define the order of shared and module JS files
        # Modules are expected to use ES6 export/import, but for bundling they are simply concatenated.
        # The `app.js` (orchestrator) should be last among these core files to ensure
        # module contents are defined before app.js tries to use them (even if imports are hoisted).
        # However, true ES6 module loading behavior in the browser is different from simple concatenation.
        # For this script, concatenation order matters if modules define global objects or
        # if app.js executes code at the top level that depends on modules being "loaded".
        # Given current module structure (defining functions/vars, not immediate top-level execution
        # that depends on others), this order should be fine for concatenation.

        # Directory for compiled TypeScript files
        compiled_ts_dir = os.path.join(shared_js_dir, "compiled_ts")

        shared_js_paths_ordered = [
            # Compiled TypeScript files
            os.path.join(compiled_ts_dir, "sads-default-theme.js"),
            os.path.join(compiled_ts_dir, "sads-style-engine.js"),
            os.path.join(
                compiled_ts_dir, "nlToSadsInterface.js"
            ),  # New NL to SADS interface
            # Original JS modules
            os.path.join(modules_dir, "eventBus.js"),
            os.path.join(modules_dir, "darkMode.js"),
            os.path.join(modules_dir, "translation.js"),
            os.path.join(
                modules_dir, "sadsManager.js"
            ),  # sadsManager uses SADSEngine, so must come after compiled SADS files
            # Main app orchestrator and other specific JS files
            os.path.join(shared_js_dir, "app.js"),
            os.path.join(shared_js_dir, "headerInteractions.js"),
        ]

        processed_shared_js = []
        for path in shared_js_paths_ordered:
            if os.path.exists(path):
                processed_shared_js.append(path)
                print(f"Found JS: {path}")
            else:
                # app.js is critical, others might be optional if project evolves
                if os.path.basename(path) in [
                    "app.js",
                    "sads-style-engine.js",
                    "sads-default-theme.js",
                ]:
                    print(f"ERROR: Critical JS file not found: {path}")
                    # Depending on strictness, might want to return None or raise error
                else:
                    print(f"Warning: Optional JS file not found: {path}")

        # Prepend shared JS (now including modules in order) to component JS
        js_files_to_bundle = processed_shared_js + js_files_to_bundle

        # output_dir is now passed as an argument
        output_file_path = os.path.join(output_dir, "main.js")
        os.makedirs(output_dir, exist_ok=True)

        if not js_files_to_bundle:
            print("No JavaScript files found to bundle.")
            try:
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write("// No JavaScript files found or bundled.")
                print(f"Created empty JS bundle: {output_file_path}")
                return output_file_path  # Return path to empty bundle
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
                    outfile.write(
                        f"\n// --- Source: {os.path.basename(original_path)} --- //\n"
                    )
                    outfile.write(content)
                    outfile.write("\n// --- End Source --- //\n\n")
            print(f"Successfully bundled JavaScript to: {output_file_path}")
            return output_file_path
        except IOError as e:
            print(f"Error writing bundled JavaScript to {output_file_path}: {e}")
            return None

import subprocess # For running go env

    def _get_goroot(self) -> Optional[str]:
        """Helper function to get GOROOT environment variable."""
        try:
            process = subprocess.run(["go", "env", "GOROOT"], capture_output=True, text=True, check=True)
            goroot_path = process.stdout.strip()
            # Basic validation for the path
            if os.path.isdir(goroot_path):
                return goroot_path
            else:
                print(f"Warning: 'go env GOROOT' provided a path that is not a directory: {goroot_path}")
                return None
        except subprocess.CalledProcessError as e:
            print(f"Error getting GOROOT (go command failed): {e}. Stdout: {e.stdout}. Stderr: {e.stderr}")
            return None
        except FileNotFoundError:
            print("Error getting GOROOT: 'go' command not found. Please ensure Go is installed and in your PATH.")
            return None
        except Exception as e: # Catch any other unexpected errors
            print(f"An unexpected error occurred while getting GOROOT: {e}")
            return None

    def copy_wasm_assets(self, project_root: str, assets_base_output_dir: str) -> bool:
        """
        Copies WASM related assets:
        - sads_poc.wasm from sads_wasm_poc/ to public/dist/assets/wasm/
        - wasm_exec.js from $(go env GOROOT)/misc/wasm/wasm_exec.js to:
            1. sads_wasm_poc/ (for local test harness use)
            2. public/dist/assets/wasm/ (for the main application)

        Args:
            project_root: The root directory of the project.
            assets_base_output_dir: The base directory for assets (e.g., 'public/dist/assets').
                                    WASM files will be placed in a 'wasm' subdirectory here.
        Returns:
            True if essential assets (sads_poc.wasm and wasm_exec.js for main app) were copied successfully, False otherwise.
        """
        print(f"Starting WASM asset copying. Base output directory for assets: {assets_base_output_dir}")

        all_essential_copied = True

        # --- Determine GOROOT ---
        goroot = self._get_goroot()
        if not goroot:
            print("Critical: Could not determine GOROOT. wasm_exec.js will not be copied from Go installation.")
            # Depending on strictness, we could set all_essential_copied to False here
            # if wasm_exec.js from GOROOT is considered essential for the build.
            # For now, we'll let it try to copy sads_poc.wasm and potentially a local wasm_exec.js
        else:
            print(f"Using GOROOT: {goroot}")

        # --- Define paths ---
        # Destination for wasm_exec.js and sads_poc.wasm for the main application
        wasm_output_dir_main_app = os.path.join(assets_base_output_dir, "wasm")
        # Directory for sads_wasm_poc (source for sads_poc.wasm, dest for local wasm_exec.js)
        sads_wasm_poc_dir = os.path.join(project_root, "sads_wasm_poc")

        os.makedirs(wasm_output_dir_main_app, exist_ok=True)
        # sads_wasm_poc_dir should already exist, but ensure for safety if scripts are run oddly
        os.makedirs(sads_wasm_poc_dir, exist_ok=True)

        # --- 1. Copy sads_poc.wasm to public/dist/assets/wasm/ ---
        sads_poc_wasm_source = os.path.join(sads_wasm_poc_dir, "sads_poc.wasm")
        sads_poc_wasm_dest_main_app = os.path.join(wasm_output_dir_main_app, "sads_poc.wasm")

        if os.path.exists(sads_poc_wasm_source):
            try:
                shutil.copy2(sads_poc_wasm_source, sads_poc_wasm_dest_main_app)
                print(f"Successfully copied {sads_poc_wasm_source} to {sads_poc_wasm_dest_main_app}")
            except IOError as e:
                print(f"Error copying sads_poc.wasm to {sads_poc_wasm_dest_main_app}: {e}")
                all_essential_copied = False
        else:
            print(f"Error: Essential WASM asset sads_poc.wasm not found at {sads_poc_wasm_source}. Skipping.")
            all_essential_copied = False

        # --- 2. Copy wasm_exec.js ---
        wasm_exec_js_filename = "wasm_exec.js"
        wasm_exec_js_source_from_goroot = None
        if goroot:
            wasm_exec_js_source_from_goroot = os.path.join(goroot, "misc", "wasm", wasm_exec_js_filename)

        # Destination for sads_wasm_poc/ (local harness)
        wasm_exec_js_dest_sads_poc = os.path.join(sads_wasm_poc_dir, wasm_exec_js_filename)
        # Destination for public/dist/assets/wasm/ (main app)
        wasm_exec_js_dest_main_app = os.path.join(wasm_output_dir_main_app, wasm_exec_js_filename)

        if wasm_exec_js_source_from_goroot and os.path.exists(wasm_exec_js_source_from_goroot):
            # Copy to sads_wasm_poc/
            try:
                shutil.copy2(wasm_exec_js_source_from_goroot, wasm_exec_js_dest_sads_poc)
                print(f"Successfully copied {wasm_exec_js_source_from_goroot} to {wasm_exec_js_dest_sads_poc}")
            except IOError as e:
                print(f"Error copying wasm_exec.js from GOROOT to {wasm_exec_js_dest_sads_poc}: {e}")
                # This copy isn't strictly essential for the main app build if the next one succeeds.

            # Copy to public/dist/assets/wasm/
            try:
                shutil.copy2(wasm_exec_js_source_from_goroot, wasm_exec_js_dest_main_app)
                print(f"Successfully copied {wasm_exec_js_source_from_goroot} to {wasm_exec_js_dest_main_app}")
            except IOError as e:
                print(f"Error copying wasm_exec.js from GOROOT to {wasm_exec_js_dest_main_app}: {e}")
                all_essential_copied = False # Essential for the main app
        else:
            if goroot : # goroot was found but wasm_exec.js was not in it
                 print(f"Error: Essential asset wasm_exec.js not found at {wasm_exec_js_source_from_goroot}.")
            else: # goroot itself was not found
                 print(f"Error: GOROOT not found, cannot locate wasm_exec.js from Go installation.")
            all_essential_copied = False # Essential for the main app

            # Fallback: Check if wasm_exec.js already exists in sads_wasm_poc_dir (e.g. from a previous run or manual placement)
            # If so, and GOROOT failed, still try to copy it to the main app's assets.
            if os.path.exists(wasm_exec_js_dest_sads_poc):
                print(f"Found {wasm_exec_js_filename} in {sads_wasm_poc_dir}. Attempting to use it as fallback for main app.")
                try:
                    shutil.copy2(wasm_exec_js_dest_sads_poc, wasm_exec_js_dest_main_app)
                    print(f"Successfully copied (fallback) {wasm_exec_js_dest_sads_poc} to {wasm_exec_js_dest_main_app}")
                    all_essential_copied = True # If fallback succeeds, consider it copied for the app.
                except IOError as e:
                    print(f"Error copying (fallback) {wasm_exec_js_dest_sads_poc} to {wasm_exec_js_dest_main_app}: {e}")
                    # Keep all_essential_copied as False if this also fails.
            else:
                print(f"wasm_exec.js also not found as a fallback in {sads_wasm_poc_dir}.")


        if all_essential_copied:
            print(f"All essential WASM assets processed for {wasm_output_dir_main_app} and {sads_wasm_poc_dir}")
        else:
            print("Failed to process one or more essential WASM assets for the main application.")

        return all_essential_copied
