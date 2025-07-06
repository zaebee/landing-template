import argparse
import json
import os
import re # Added for regex parsing
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

# --- Mistral Specific Block ---
try:
    from mistralai import (
        Messages,
        Mistral,
        UserMessage,
    )
except ImportError:
    Mistral = None # type: ignore
    Messages = None # type: ignore
    UserMessage = None # type: ignore
    # This allows the script to run if mistralai is not installed,
    # as long as mistral provider is not selected.

# --- OpenAI Specific Block ---
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None # type: ignore
    # This allows the script to run if openai is not installed,
    # as long as openai provider is not selected.


def load_sads_theme_context(json_file_path: str) -> Optional[Dict[str, Any]]:
    """Loads the simplified SADS theme context from a JSON file."""
    try:
        with open(json_file_path, "r") as f:
            data: Dict[str, Any] = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: SADS theme context file not found at '{json_file_path}'. Please check the path.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{json_file_path}'. Please ensure it's valid JSON.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while loading SADS theme context: {e}")
        return None


def construct_llm_prompt(
    html_snippet: str, style_prompt: str, sads_theme_context: Optional[Dict[str, Any]]
) -> str:
    """Constructs the prompt for the LLM."""

    sads_explanation: str = (
        "You are an expert in Semantic Attribute-Driven Styling (SADS).\n"
        "Your task is to generate a string of `data-sads-*` attributes to style the given HTML snippet "
        "based on the user's style description and the available SADS theme tokens.\n"
        'The SADS attributes should be space-separated, e.g., `data-sads-bgColor="primary" data-sads-padding="m"`.\n'
        "Focus on mapping the style description to appropriate SADS attributes and tokens.\n"
        "If a style cannot be directly represented by a known SADS token from the context, "
        'you can use a \'custom:<value>\' format, e.g., `data-sads-fontSize="custom:1.1em"` or `data-sads-border="custom:1px solid #CCC"`.\n'
        "Only output the `data-sads-*` attributes string. Do not include any other text, explanations, or HTML markup.\n"
        "Ensure all attribute values are enclosed in double quotes.\n"
    )

    context_str_parts: List[str] = []
    if sads_theme_context:
        # Iterating through common theme categories to build the context string
        token_categories: Dict[str, str] = {
            "colors": "color tokens (for bgColor, textColor, borderColor, etc.)",
            "spacing": "spacing tokens (for padding, margin, gap, etc.)",
            "fontSize": "fontSize tokens",
            "fontWeight": "fontWeight tokens",
            "borderRadius": "borderRadius tokens",
            "shadow": "shadow tokens",
        }
        for category, description in token_categories.items():
            tokens_map: Optional[Dict[str, str]] = sads_theme_context.get(category)
            if tokens_map:
                context_str_parts.append(
                    f"- Available {description}: {', '.join(tokens_map.keys())}"
                )
        # Add other theme categories as needed
    else:
        context_str_parts.append(
            "No SADS theme context provided. Rely on general SADS knowledge and use 'custom:<value>' where specific tokens are unknown."
        )


    sads_theme_context_str: str = (
        "Available SADS theme tokens:\n" + "\n".join(context_str_parts)
        if context_str_parts
        else "No specific SADS theme tokens provided; use general SADS knowledge and custom values where appropriate for tokens."
    )

    sads_properties_ref_str: str = ""
    valid_sads_keys: Optional[List[str]] = None
    if sads_theme_context:
        properties_ref_map: Optional[Dict[str, str]] = sads_theme_context.get(
            "sadsPropertiesReference"
        )
        if properties_ref_map:
            valid_sads_keys = list(properties_ref_map.keys())
            sads_properties_ref_str = "\n\nSADS Properties Reference (attribute_name: expected_value_type_or_examples):\n"
            for key, desc in properties_ref_map.items():
                sads_properties_ref_str += f"- {key}: {desc}\n"
            sads_properties_ref_str += (
                f"\nEnsure you only use these SADS property keys: {', '.join(valid_sads_keys)}.\n"
            )


    prompt: str = (
        f"{sads_explanation}\n\n"
        f"{sads_theme_context_str}"
        f"{sads_properties_ref_str}\n\n"
        # f"SADS THEME CONTEXT (repeated for emphasis):\n{sads_theme_context_str}\n\n" # Removed repetition
        f"HTML SNIPPET:\n```html\n{html_snippet}\n```\n\n"
        f'USER STYLE DESCRIPTION: "{style_prompt}"\n\n'
        f"Generated `data-sads-*` attributes string:"
    )
    return prompt


def get_client(api_key: str, provider: str = "openai") -> Union[OpenAI, Mistral, None]:
    """
    Returns an initialized client for the specified LLM provider.
    Returns None if the provider is unsupported or its library is not installed.
    """
    provider_lower = provider.lower()
    if provider_lower == "openai":
        if OpenAI is None:
            print("Error: OpenAI library not installed. Please run 'pip install openai'.")
            return None
        return OpenAI(api_key=api_key)
    elif provider_lower == "mistral":
        if Mistral is None:
            print("Error: MistralAI library not installed. Please run 'pip install mistralai'.")
            return None
        return Mistral(api_key=api_key)
    else:
        print(f"Error: Unsupported provider '{provider}'. Supported: 'openai', 'mistral'.")
        return None


def get_sads_attributes_from_llm(
    api_key: str,
    model_name: str,
    prompt: str,
    provider: str = "openai",
    temperature: float = 0.2, # Default temperature
    max_tokens: int = 200,    # Default max_tokens
) -> Optional[str]:
    """
    Calls the specified LLM API and returns the response content.
    Handles potential errors during API calls.
    Uses provided temperature and max_tokens.
    """
    try:
        client = get_client(api_key, provider)
        if client is None:
            # Error message already printed by get_client
            return None
    except Exception as e: # Catch potential errors during client initialization if get_client is modified
        print(f"Error initializing LLM client for {provider}: {e}")
        return None

    raw_response_content: Optional[str] = None
    try:
        if isinstance(client, OpenAI):
            completion: Any = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates SADS attributes.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            raw_response_content = completion.choices[0].message.content
        elif Mistral and isinstance(client, Mistral): # Check Mistral is not None
            messages: List[Messages] = [UserMessage(role="user", content=prompt)] # type: ignore
            chat_response: Any = client.chat.complete( # type: ignore
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if chat_response.choices and chat_response.choices[0].message:
                raw_response_content = str(chat_response.choices[0].message.content)
        else:
            # This case should be handled by get_client returning None, but as a safeguard:
            print(f"Error: LLM client for provider '{provider}' is not correctly configured or library missing.")
            return None

    except ImportError as e: # Should be caught by get_client, but good to have defense in depth
        print(f"ImportError during LLM API call for {provider}: {e}. Is the library installed?")
        return None
    except Exception as e:
        print(f"Error calling {provider.capitalize()} API ({model_name}): {e}")
        print("This could be due to an invalid API key, network issues, or a problem with the LLM service.")
        return None

    if not raw_response_content:
        print(f"Warning: LLM ({provider} - {model_name}) returned an empty response.")
        return None

    # Filter out potential preamble/postamble and ensure only attribute string is returned
    # This regex finds parts that look like `data-sads-key="value"`
    sads_like_parts = re.findall(r'data-sads-[a-zA-Z0-9-]+="[^"]+"', raw_response_content)
    if not sads_like_parts:
        print("Warning: LLM response did not contain any parsable data-sads-* attributes.")
        print(f"Raw LLM Response: '{raw_response_content[:200]}{'...' if len(raw_response_content) > 200 else ''}'") # Print snippet of raw response
        return None

    return " ".join(sads_like_parts)


def save_output(filename: str, html_content: str, raw_llm_response: Optional[str], parsed_sads: Dict[str, Any]) -> None:
    """Saves the generated outputs to files."""
    try:
        with open(filename, "w") as f:
            f.write("<!-- Generated HTML with SADS attributes -->\n")
            f.write(html_content)
        print(f"Successfully saved generated HTML to: {filename}")

        if raw_llm_response:
            with open(f"{os.path.splitext(filename)[0]}.raw_llm.txt", "w") as f:
                f.write(raw_llm_response)
            print(f"Successfully saved raw LLM response to: {os.path.splitext(filename)[0]}.raw_llm.txt")

        with open(f"{os.path.splitext(filename)[0]}.parsed_sads.json", "w") as f:
            json.dump(parsed_sads, f, indent=2)
        print(f"Successfully saved parsed SADS JSON to: {os.path.splitext(filename)[0]}.parsed_sads.json")

    except IOError as e:
        print(f"Error: Could not write to output file '{filename}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving output: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate SADS attributes using an LLM. "\
                    "Ensure API keys (OPENAI_API_KEY or MISTRAL_API_KEY) are set in a .env file in this directory.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--html_file", type=str, required=True, help="Path to the HTML snippet file."
    )
    parser.add_argument(
        "--style_prompt",
        type=str,
        required=True,
        help="Natural language style description.",
    )
    parser.add_argument(
        "--theme_context_file",
        type=str,
        required=True,
        help="Path to the JSON file with SADS theme context.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None, # Default will be set based on provider
        help="LLM model to use.\n"
             "OpenAI examples: gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview.\n"
             "Mistral examples: mistral-tiny, mistral-small-latest, mistral-medium-latest.\n"
             "If not set, defaults to gpt-3.5-turbo for OpenAI and mistral-small-latest for Mistral.",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "mistral"],
        help="LLM provider ('openai' or 'mistral'). Default: openai.",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default=None,
        help="(Optional) Path to save the generated HTML with SADS attributes. "
             "Related files (.raw_llm.txt, .parsed_sads.json) will also be saved.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None, # Will use .env or script default if not set
        help="(Optional) LLM temperature. Overrides DEFAULT_LLM_TEMPERATURE from .env or script default (0.2)."
    )
    parser.add_argument(
        "--max_tokens",
        type=int,
        default=None, # Will use .env or script default if not set
        help="(Optional) LLM max tokens. Overrides DEFAULT_LLM_MAX_TOKENS from .env or script default (200)."
    )
    args: argparse.Namespace = parser.parse_args()

    # --- Configuration Loading (from .env or defaults) ---
    env_loaded = load_dotenv() # Load environment variables from .env file
    if not env_loaded:
        print("Info: .env file not found or not loaded. Relying on environment variables set externally for API keys and using script defaults for LLM parameters.")

    default_openai_model = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-3.5-turbo")
    default_mistral_model = os.getenv("DEFAULT_MISTRAL_MODEL", "mistral-small-latest")
    # Temperature and max_tokens will be passed as arguments to get_sads_attributes_from_llm
    # and can also be further made configurable via CLI arguments if needed.

    # Set model based on provider if not specified by user, using defaults from env/script
    if args.model is None:
        if args.provider.lower() == "openai":
            args.model = default_openai_model
        elif args.provider.lower() == "mistral":
            args.model = default_mistral_model

    llm_temperature = args.temperature if args.temperature is not None else float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.2"))
    llm_max_tokens = args.max_tokens if args.max_tokens is not None else int(os.getenv("DEFAULT_LLM_MAX_TOKENS", "200"))

    # --- Dependency Checks ---
    if args.provider.lower() == "openai" and OpenAI is None:
        print("Error: OpenAI provider selected, but 'openai' library is not installed. Please run 'pip install openai'.")
        return
    if args.provider.lower() == "mistral" and Mistral is None:
        print("Error: Mistral provider selected, but 'mistralai' library is not installed. Please run 'pip install mistralai'.")
        return

    # --- API Key Loading ---
    env_loaded = load_dotenv() # Load environment variables from .env file
    if not env_loaded:
        print("Info: .env file not found or not loaded. Relying on environment variables set externally if any.")


    api_key: Optional[str] = None
    provider_lower = args.provider.lower()

    if provider_lower == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not found in environment variables or .env file for OpenAI provider.")
            print("Please ensure it is set to use the OpenAI provider.")
            return
    elif provider_lower == "mistral":
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            print("Error: MISTRAL_API_KEY not found in environment variables or .env file for Mistral provider.")
            print("Please ensure it is set to use the Mistral provider.")
            return
    # Argparse choices should prevent other providers, but as a safeguard:
    elif provider_lower not in ["openai", "mistral"]:
        print(f"Internal Error: Provider '{args.provider}' is not supported by API key loading logic.")
        return


    if not api_key: # Should be caught by the specific checks above
        print(f"Critical Error: API key for provider '{args.provider}' could not be loaded. Exiting.")
        return

    # --- File Inputs ---
    html_snippet: str
    try:
        with open(args.html_file, "r") as f:
            html_snippet = f.read()
    except FileNotFoundError:
        print(f"Error: HTML snippet file not found at '{args.html_file}'. Please check the path.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading HTML file '{args.html_file}': {e}")
        return

    sads_theme_context: Optional[Dict[str, Any]] = load_sads_theme_context(
        args.theme_context_file
    )
    if sads_theme_context is None:
        print("Halting due to issues loading SADS theme context.")
        return

    # --- LLM Interaction ---
    llm_prompt: str = construct_llm_prompt(
        html_snippet, args.style_prompt, sads_theme_context
    )

    print("--- Inputs to LLM ---")
    print(f"Provider: {args.provider.capitalize()}, Model: {args.model}")
    print(f"HTML Snippet File: {args.html_file}")
    # print(f"HTML Snippet Content:\n{html_snippet}") # Can be verbose
    print(f"Style Prompt: {args.style_prompt}")
    # print(f"SADS Theme Context File: {args.theme_context_file}")
    # print(f"SADS Theme Context (brief):\n{json.dumps(sads_theme_context, indent=2, default=lambda o: '<Object>')[:500]}...") # Avoid overly long prints
    # print(f"\nConstructed LLM Prompt (for debugging - first 500 chars):\n{llm_prompt[:500]}...")
    print(f"\nQuerying {args.provider.capitalize()} LLM ({args.model}) with temp={llm_temperature}, max_tokens={llm_max_tokens}...")

    generated_attributes_string: Optional[str] = get_sads_attributes_from_llm(
        api_key,
        args.model,
        llm_prompt,
        args.provider,
        temperature=llm_temperature,
        max_tokens=llm_max_tokens,
    )

    print("\n--- LLM Processing ---")
    if generated_attributes_string:
        print("Raw SADS Attributes String from LLM:")
        print(f"'{generated_attributes_string}'")

        # Parse the string into a structured dictionary
        parsed_sads_data = parse_llm_sads_string_to_dict(
            generated_attributes_string, sads_theme_context
        )
        print("\nParsed SADS Attributes (Conceptual Proto Structure):")
        print(json.dumps(parsed_sads_data, indent=2))

        if not parsed_sads_data.get("attributes"):
            print("\nWarning: LLM provided a response, but no valid SADS attributes could be parsed from it.")
            print("This might indicate the LLM did not follow the format instructions correctly.")
            if args.output_file and generated_attributes_string: # Save raw if output is requested
                 save_output(args.output_file, f"<!-- No SADS attributes generated or parsed for HTML: {html_snippet} -->", generated_attributes_string, parsed_sads_data)
            return # Stop further processing if no attributes parsed

        # --- HTML Output Generation ---
        # More robustly find the first tag to inject attributes
        first_tag_match = re.search(r"<([a-zA-Z0-9\-]+)(\s*[^>]*)>", html_snippet)
        modified_html: str
        final_sads_string_for_html = " ".join([f'{k}="{v}"' for k,v in parsed_sads_data.get("_raw_attributes_for_html", {}).items()])


        if first_tag_match:
            tag_name = first_tag_match.group(1)
            existing_attrs_and_ending = first_tag_match.group(2)
            # Ensure there's a space before adding new attributes if others exist
            spacer = " " if existing_attrs_and_ending.strip() and final_sads_string_for_html else ""

            # Reconstruct the opening tag with new attributes
            # We place SADS attributes at the end of existing attributes in the first tag
            insertion_point = first_tag_match.start() + len(f"<{tag_name}") + len(existing_attrs_and_ending)

            # Find where the original first tag ends to correctly insert
            original_first_tag_end_char_index = html_snippet.find(">", first_tag_match.start())
            if original_first_tag_end_char_index != -1:
                 modified_html = (
                    html_snippet[:original_first_tag_end_char_index] +
                    spacer +
                    final_sads_string_for_html +
                    html_snippet[original_first_tag_end_char_index:]
                )
            else: # Should not happen with valid HTML
                print("Warning: Could not properly locate end of first tag for attribute injection.")
                modified_html = f"<div {final_sads_string_for_html}>{html_snippet}</div>"

        else:
            print("Warning: Could not find a suitable HTML tag in the snippet to inject attributes.")
            print("Wrapping the snippet in a div with the generated attributes.")
            modified_html = f"<div {final_sads_string_for_html}>{html_snippet}</div>"

        print("\n--- Resulting HTML (with injected attributes) ---")
        print(modified_html)

        if args.output_file:
            save_output(args.output_file, modified_html, generated_attributes_string, parsed_sads_data)

    else:
        print("\nNo attributes generated by the LLM or a critical error occurred during LLM communication.")
        print("Please check the logs above for specific error messages from the API or client.")
        if args.output_file: # Save empty/error state if output file requested
            error_html = f"<!-- AI SADS PoC: No attributes generated or an error occurred. Original HTML: {html_snippet} -->"
            save_output(args.output_file, error_html, "No LLM response due to error.", {"attributes": {}, "errors": ["No LLM response or error"]})


# --- Conceptual SADS String Parser ---
def parse_llm_sads_string_to_dict(
    sads_attributes_string: str, theme_context: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Parses a string of data-sads-* attributes (from LLM) into a structured dictionary
    that conceptually represents a SadsStylingSet proto message.
    Uses regex for more robust parsing.

    Args:
        sads_attributes_string: The raw string from the LLM,
                                e.g., "data-sads-bgColor=\"primary\" data-sads-padding=\"m\""
        theme_context: The SADS theme context to help identify known tokens and valid properties.

    Returns:
        A dictionary structured like:
        {
            "attributes": {
                "bgColor": {"color_token": "COLOR_TOKEN_PRIMARY"},
                "padding": {"spacing_token": "SPACING_TOKEN_M"}
            },
            "errors": ["Warning: Skipping malformed attribute '...'", ...],
            "_raw_attributes_for_html": {"data-sads-bgColor": "primary", ...}
        }
    """
    if not sads_attributes_string:
        return {"attributes": {}, "errors": ["Input SADS string is empty."], "_raw_attributes_for_html": {}}

    attributes_map: Dict[str, Dict[str, str]] = {}
    errors: List[str] = []
    raw_attributes_for_html: Dict[str, str] = {} # To store validated attributes for HTML injection

    # Regex to find attributes like data-sads-key="value"
    # It captures the full key (e.g., data-sads-bgColor) and the value (e.g., primary)
    # Handles potential variations in spacing around '='.
    attribute_pattern = re.compile(r'\b(data-sads-([a-zA-Z0-9\-]+))\s*=\s*"([^"]*)"')

    valid_sads_property_keys: Optional[List[str]] = None
    if theme_context and "sadsPropertiesReference" in theme_context:
        valid_sads_property_keys = list(theme_context["sadsPropertiesReference"].keys())

    for match in attribute_pattern.finditer(sads_attributes_string):
        full_key = match.group(1)  # e.g. "data-sads-bgColor"
        sads_key_raw = match.group(2) # e.g. "bgColor" or "border-radius"
        value = match.group(3)      # e.g. "primary"

        # Normalize sads_key from kebab-case to camelCase for internal consistency
        # (e.g., "border-radius" -> "borderRadius")
        if "-" in sads_key_raw:
            key_parts = sads_key_raw.split("-")
            sads_key_camel_case = key_parts[0] + "".join(p.capitalize() for p in key_parts[1:])
        else:
            sads_key_camel_case = sads_key_raw

        # Validate against known SADS properties if available
        if valid_sads_property_keys and sads_key_camel_case not in valid_sads_property_keys:
            errors.append(f"Warning: Skipping attribute with unknown SADS property key '{sads_key_camel_case}' (from '{full_key}'). Check sadsPropertiesReference in theme context.")
            continue

        # Store the validated raw attribute for HTML injection
        raw_attributes_for_html[full_key] = value


        attr_value_dict: Dict[str, str] = {}

        if value.startswith("custom:"):
            custom_val = value[len("custom:") :]
            if not custom_val:
                 errors.append(f"Warning: SADS key '{sads_key_camel_case}' has an empty 'custom:' value. Check LLM output.")
                 # Decide if this should be skipped or stored as empty custom
                 attr_value_dict["custom_value"] = "" # Store as empty custom for now
            else:
                attr_value_dict["custom_value"] = custom_val
        else:
            mapped = False
            if theme_context:
                # More precise mapping based on sads_key_camel_case and expected token categories
                # This requires knowledge of which SADS keys expect which token types.
                # For PoC, we can use heuristics or a predefined map if sadsPropertiesReference implies types.

                # Example: Check if sads_key_camel_case is related to colors
                if "colors" in theme_context and value in theme_context["colors"] and \
                   any(k in sads_key_camel_case.lower() for k in ["color", "bg", "border", "fill", "stroke"]): # Broader heuristic
                    attr_value_dict["color_token"] = f"COLOR_TOKEN_{value.upper().replace('-', '_')}"
                    mapped = True
                elif "spacing" in theme_context and value in theme_context["spacing"] and \
                     any(k in sads_key_camel_case.lower() for k in ["padding", "margin", "gap", "inset", "space"]): # Broader heuristic
                    attr_value_dict["spacing_token"] = f"SPACING_TOKEN_{value.upper().replace('-', '_')}"
                    mapped = True
                elif "fontSize" in theme_context and value in theme_context["fontSize"] and \
                     "fontsize" in sads_key_camel_case.lower():
                    attr_value_dict["font_size_value"] = value # Stores the token key itself
                    mapped = True
                elif "fontWeight" in theme_context and value in theme_context["fontWeight"] and \
                     "fontweight" in sads_key_camel_case.lower():
                    attr_value_dict["font_weight_token"] = f"FONT_WEIGHT_TOKEN_{value.upper().replace('-', '_')}"
                    mapped = True
                elif "borderRadius" in theme_context and value in theme_context["borderRadius"] and \
                     "borderradius" in sads_key_camel_case.lower():
                    attr_value_dict["border_radius_token"] = f"BORDER_RADIUS_TOKEN_{value.upper().replace('-', '_')}"
                    mapped = True
                # Add more specific mappings if sadsPropertiesReference implies value types

            if not mapped:
                # If not a known token and not 'custom:', treat as a direct/literal value or potentially a custom value if it's not a standard CSS keyword for that property
                # SADS properties like 'textAlign', 'display', 'position' often take direct CSS keyword values.
                # Others might be numeric strings (e.g. opacity="0.5", zIndex="10")
                # For this PoC, if not a token, and not 'custom:', we'll generally treat it as a custom_value
                # or a specific direct value if the key implies it.
                if sads_key_camel_case.lower() in [
                    "textalign", "display", "position", "overflow", "cursor",
                    "flexdirection", "justifycontent", "alignitems", "flexwrap",
                    "objectfit", "objectposition", "textdecoration", "texttransform",
                    "visibility", "whitespace", "wordbreak", "boxsizing", "resize", "transition"
                ]:
                    attr_value_dict["direct_value"] = value # Or "keyword_value" / "css_value"
                elif "fontsize" in sads_key_camel_case.lower() and not mapped : # If it wasn't a token
                     attr_value_dict["font_size_value"] = value # Store as is (e.g. "1.2rem", "16px")
                elif "lineheight" in sads_key_camel_case.lower() and not mapped:
                     attr_value_dict["line_height_value"] = value # Store as is (e.g., "1.5", "24px")
                elif "letterspacing" in sads_key_camel_case.lower() and not mapped:
                     attr_value_dict["letter_spacing_value"] = value
                elif "opacity" == sads_key_camel_case.lower():
                    attr_value_dict["opacity_value"] = value # e.g. "0.5"
                elif "zindex" == sads_key_camel_case.lower():
                    attr_value_dict["z_index_value"] = value # e.g. "10"
                else:
                    # Default to custom_value if no specific logic or token match and not a known direct value type
                    errors.append(f"Info: SADS key '{sads_key_camel_case}' with value '{value}' not mapped to a known token type and not 'custom:'. Storing as 'custom_value'.")
                    attr_value_dict["custom_value"] = value

        if attr_value_dict:
            if sads_key_camel_case in attributes_map:
                errors.append(f"Warning: Duplicate SADS key '{sads_key_camel_case}' encountered. Previous value '{attributes_map[sads_key_camel_case]}' will be overwritten by '{attr_value_dict}'.")
            attributes_map[sads_key_camel_case] = attr_value_dict
        else:
            # This case should ideally not be reached if logic above is complete
            errors.append(f"Critical Warning: Could not determine value type for SADS key '{sads_key_camel_case}' with value '{value}'. This is unexpected. Storing as raw custom.")
            attributes_map[sads_key_camel_case] = {"custom_value": value} # Fallback

    # Check if any part of the original string was not parsed by the regex
    # This helps identify if LLM included text not matching the attribute format.
    remaining_text = attribute_pattern.sub("", sads_attributes_string).strip()
    if remaining_text:
        errors.append(f"Warning: LLM response contained text that was not parsed as valid SADS attributes: '{remaining_text[:100]}{'...' if len(remaining_text) > 100 else ''}'")

    if not attributes_map and not errors and sads_attributes_string:
        errors.append("Warning: SADS attribute string was provided, but no attributes could be parsed. Check LLM output format and quoting.")

    for error_msg in errors:
        print(error_msg)


    return {"attributes": attributes_map, "errors": errors, "_raw_attributes_for_html": raw_attributes_for_html}


if __name__ == "__main__":
    main()
