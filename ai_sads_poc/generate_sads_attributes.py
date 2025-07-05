import argparse
import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# --- Mistral Specific Block ---
from mistralai import (
    Messages,
    Mistral,
    UserMessage,
)
from openai import OpenAI


def load_sads_theme_context(json_file_path: str) -> Optional[Dict[str, Any]]:
    """Loads the simplified SADS theme context from a JSON file."""
    try:
        with open(json_file_path, "r") as f:
            data: Dict[str, Any] = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: SADS theme context file not found at {json_file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file_path}")
        return None


def construct_llm_prompt(
    html_snippet: str, style_prompt: str, sads_theme_context: Optional[Dict[str, Any]]
) -> str:
    """Constructs the prompt for the LLM."""

    # Basic SADS capabilities explanation for the LLM
    sads_explanation: str = (
        "You are an expert in Semantic Attribute-Driven Styling (SADS).\n"
        "Your task is to generate a string of `data-sads-*` attributes to style the given HTML snippet "
        "based on the user's style description and the available SADS theme tokens.\n"
        'The SADS attributes should be space-separated, e.g., `data-sads-bgColor="primary" data-sads-padding="m"`.\n'
        "Focus on mapping the style description to appropriate SADS attributes and tokens.\n"
        "If a style cannot be directly represented by a known SADS token from the context, "
        'you can use a \'custom:<value>\' format, e.g., `data-sads-fontSize="custom:1.1em"` or `data-sads-border="custom:1px solid #CCC"`.\n'
        "Only output the `data-sads-*` attributes string. Do not include any other text, explanations, or HTML markup.\n"
    )

    context_str_parts: List[str] = []
    if sads_theme_context:
        colors_map: Optional[Dict[str, str]] = sads_theme_context.get("colors")
        if colors_map:
            context_str_parts.append(
                f"- Available color tokens (for bgColor, textColor, borderColor, etc.): {', '.join(colors_map.keys())}"
            )

        spacing_map: Optional[Dict[str, str]] = sads_theme_context.get("spacing")
        if spacing_map:
            context_str_parts.append(
                f"- Available spacing tokens (for padding, margin, gap, etc.): {', '.join(spacing_map.keys())}"
            )

        fontSize_map: Optional[Dict[str, str]] = sads_theme_context.get("fontSize")
        if fontSize_map:
            context_str_parts.append(
                f"- Available fontSize tokens: {', '.join(fontSize_map.keys())}"
            )

        fontWeight_map: Optional[Dict[str, str]] = sads_theme_context.get("fontWeight")
        if fontWeight_map:
            context_str_parts.append(
                f"- Available fontWeight tokens: {', '.join(fontWeight_map.keys())}"
            )

        borderRadius_map: Optional[Dict[str, str]] = sads_theme_context.get(
            "borderRadius"
        )
        if borderRadius_map:
            context_str_parts.append(
                f"- Available borderRadius tokens: {', '.join(borderRadius_map.keys())}"
            )

        shadow_map: Optional[Dict[str, str]] = sads_theme_context.get("shadow")
        if shadow_map:
            context_str_parts.append(
                f"- Available shadow tokens: {', '.join(shadow_map.keys())}"
            )
        # Add other theme categories as needed

    sads_theme_context_str: str = (
        "Available SADS theme tokens:\n" + "\n".join(context_str_parts)
        if context_str_parts
        else "No specific SADS theme tokens provided for discrete values; use general SADS knowledge and custom values where appropriate for tokens."
    )

    sads_properties_ref_str: str = ""
    if sads_theme_context:
        properties_ref_map: Optional[Dict[str, str]] = sads_theme_context.get(
            "sadsPropertiesReference"
        )
        if properties_ref_map:
            sads_properties_ref_str = "\n\nSADS Properties Reference (attribute_name: expected_value_type_or_examples):\n"
            for key, desc in properties_ref_map.items():
                sads_properties_ref_str += f"- {key}: {desc}\n"

    prompt: str = (
        f"{sads_explanation}\n\n"
        f"{sads_theme_context_str}"
        f"{sads_properties_ref_str}\n\n"
        f"SADS THEME CONTEXT:\n{sads_theme_context_str}\n\n"  # This line seems redundant, will remove in next step if confirmed
        f"HTML SNIPPET:\n```html\n{html_snippet}\n```\n\n"
        f'USER STYLE DESCRIPTION: "{style_prompt}"\n\n'
        f"Generated `data-sads-*` attributes string:"
    )
    return prompt


def get_sads_attributes_from_llm(
    api_key: str, model_name: str, prompt: str, provider: str = "openai"
) -> Optional[str]:
    """
    Calls the specified LLM API and returns the response content.
    """
    if provider.lower() == "openai":
        try:
            client = OpenAI(api_key=api_key)
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates SADS attributes.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=150,
            )
            response_content: Optional[str] = str(completion.choices[0].message.content)
            return response_content.strip() if response_content else None
            # --- End OpenAI Specific Block ---
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
    elif provider.lower() == "mistral":
        try:
            client = Mistral(api_key=api_key)
            # Note: Mistral's API might not use a "system" prompt in the same way.
            # The main instructions are part of the user prompt.
            messages: List[Messages] = [UserMessage(role="user", content=prompt)]

            chat_response = client.chat.complete(
                model=model_name,  # e.g., "mistral-small-latest", "mistral-medium-latest"
                messages=messages,
                temperature=0.2,
                max_tokens=150,
            )
            if chat_response.choices and chat_response.choices[0].message:
                response_content = str(chat_response.choices[0].message.content).strip()
                return response_content if response_content else None
        except ImportError:
            print(
                "Error: mistralai library not installed. Please run 'pip install mistralai'."
            )
            return None
        except Exception as e:
            print(f"Error calling Mistral API: {e}")
            return None
    print(
        f"Error: Unsupported LLM provider '{provider}'. Supported: 'openai', 'mistral'."
    )
    return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate SADS attributes using an LLM."
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
        default="gpt-3.5-turbo",
        help="LLM model to use (e.g., OpenAI: gpt-3.5-turbo, gpt-4; Mistral: mistral-small-latest).",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "mistral"],
        help="LLM provider ('openai' or 'mistral'). Default: openai",
    )
    args: argparse.Namespace = parser.parse_args()

    load_dotenv()

    api_key: Optional[str] = None
    if args.provider.lower() == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(
                "Error: OPENAI_API_KEY environment variable not set for OpenAI provider."
            )
            return
    elif args.provider.lower() == "mistral":
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            print(
                "Error: MISTRAL_API_KEY environment variable not set for Mistral provider."
            )
            print(
                "Please create a .env file or set the MISTRAL_API_KEY environment variable."
            )
            return
    else:
        print(
            f"Error: Provider '{args.provider}' not recognized by API key loading logic."
        )
        return

    if not api_key:
        print("Error: API key could not be loaded.")
        return

    html_snippet: str
    try:
        with open(args.html_file, "r") as f:
            html_snippet = f.read()
    except FileNotFoundError:
        print(f"Error: HTML snippet file not found at {args.html_file}")
        return

    sads_theme_context: Optional[Dict[str, Any]] = load_sads_theme_context(
        args.theme_context_file
    )
    if sads_theme_context is None:
        return

    llm_prompt: str = construct_llm_prompt(
        html_snippet, args.style_prompt, sads_theme_context
    )

    print("--- Inputs to LLM ---")
    print(f"HTML Snippet:\n{html_snippet}")
    print(f"\nStyle Prompt: {args.style_prompt}")
    print(f"\nSADS Theme Context:\n{json.dumps(sads_theme_context, indent=2)}")
    print(f"\nQuerying {args.provider.capitalize()} LLM ({args.model})...")

    generated_attributes_string: Optional[str] = get_sads_attributes_from_llm(
        api_key, args.model, llm_prompt, args.provider
    )

    print("\n--- LLM Response ---")
    if generated_attributes_string:
        print("Generated SADS Attributes String:")
        print(generated_attributes_string)

        print("\nExample Usage (HTML with injected attributes):")
        if html_snippet.strip().startswith("<") and ">" in html_snippet:
            first_tag_end: int = html_snippet.find(">")
            if first_tag_end != -1:
                modified_html: str = (
                    html_snippet[:first_tag_end]
                    + " "
                    + generated_attributes_string
                    + html_snippet[first_tag_end:]
                )
                print(modified_html)
            else:
                print(
                    f"<{html_snippet.splitlines()[0].split(' ')[0]} {generated_attributes_string}>...</{html_snippet.splitlines()[0].split(' ')[0]}>"
                )
        else:
            print(f"<div {generated_attributes_string}>{html_snippet}</div>")

        structured_sads_data = parse_llm_sads_string_to_dict(
            generated_attributes_string, sads_theme_context
        )
        print("\nParsed SADS Attributes (Conceptual Proto Structure):")
        print(json.dumps(structured_sads_data, indent=2))

    else:
        print("No attributes generated or an error occurred.")


# --- Conceptual SADS String Parser ---
def parse_llm_sads_string_to_dict(
    sads_attributes_string: str, theme_context: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Parses a string of data-sads-* attributes (from LLM) into a structured dictionary
    that conceptually represents a SadsStylingSet proto message.

    Args:
        sads_attributes_string: The raw string from the LLM,
                                e.g., "data-sads-bgColor=\"primary\" data-sads-padding=\"m\""
        theme_context: The SADS theme context to help identify known tokens.

    Returns:
        A dictionary structured like:
        {
            "attributes": {
                "bgColor": {"color_token": "COLOR_TOKEN_PRIMARY"}, // or {"custom_value": "#ABC"}
                "padding": {"spacing_token": "SPACING_TOKEN_M"}    // or {"custom_value": "10px"}
            }
        }
        This conceptually mirrors the SadsStylingSet and SadsAttributeValue protos.
    """
    if not sads_attributes_string:
        return {"attributes": {}}

    attributes_map: Dict[str, Dict[str, str]] = {}

    # Simple parsing: split by space for attributes, then by '=' for key-value.
    # This is naive and might break with complex values or unquoted attributes from LLM.
    # A more robust parser might use regular expressions.
    raw_attributes = sads_attributes_string.strip().split(" ")

    for attr in raw_attributes:
        if not attr.strip():
            continue

        parts = attr.split("=", 1)
        if len(parts) != 2:
            print(f"Warning: Skipping malformed attribute '{attr}'")
            continue

        full_key = parts[0].strip()
        raw_value_with_quotes = parts[1].strip()

        if not full_key.startswith("data-sads-"):
            print(f"Warning: Skipping non-SADS attribute '{attr}'")
            continue
        sads_key = full_key[len("data-sads-") :].strip()
        if "-" in sads_key:
            key_parts = sads_key.split("-")
            sads_key = key_parts[0] + "".join(p.capitalize() for p in key_parts[1:])
        value = raw_value_with_quotes.strip('"')
        attr_value_dict: Dict[str, str] = {}

        if value.startswith("custom:"):
            attr_value_dict["custom_value"] = value[len("custom:") :]
        else:
            mapped = False
            if theme_context:
                if (
                    "colors" in theme_context
                    and value in theme_context["colors"]
                    and any(k in sads_key.lower() for k in ["color", "bg", "border"])
                ):
                    attr_value_dict["color_token"] = (
                        f"COLOR_TOKEN_{value.upper().replace('-', '_')}"
                    )
                    mapped = True
                elif (
                    "spacing" in theme_context
                    and value in theme_context["spacing"]
                    and any(k in sads_key.lower() for k in ["padding", "margin", "gap"])
                ):
                    attr_value_dict["spacing_token"] = (
                        f"SPACING_TOKEN_{value.upper().replace('-', '_')}"
                    )
                    mapped = True
                elif (
                    "fontSize" in theme_context
                    and value in theme_context["fontSize"]
                    and "fontsize" in sads_key.lower()
                ):
                    attr_value_dict["font_size_value"] = value
                    mapped = True
                elif (
                    "fontWeight" in theme_context
                    and value in theme_context["fontWeight"]
                    and "fontweight" in sads_key.lower()
                ):
                    attr_value_dict["font_weight_token"] = (
                        f"FONT_WEIGHT_TOKEN_{value.upper().replace('-', '_')}"
                    )
                    mapped = True
                elif (
                    "borderRadius" in theme_context
                    and value in theme_context["borderRadius"]
                    and "borderradius" in sads_key.lower()
                ):
                    attr_value_dict["border_radius_token"] = (
                        f"BORDER_RADIUS_TOKEN_{value.upper().replace('-', '_')}"
                    )
                    mapped = True
            if not mapped:
                if sads_key.lower() in [
                    "textalign",
                    "display",
                    "position",
                    "overflow",
                    "cursor",
                    "transition",
                    "boxsizing",
                    "resize",
                ]:
                    attr_value_dict["custom_value"] = value
                elif "fontsize" in sads_key.lower():
                    attr_value_dict["font_size_value"] = value
                else:
                    attr_value_dict["custom_value"] = value
        if attr_value_dict:
            attributes_map[sads_key] = attr_value_dict
        else:
            print(
                f"Warning: Could not determine value type for SADS key '{sads_key}' with value '{value}'. Storing as custom."
            )
            attributes_map[sads_key] = {"custom_value": value}
    return {"attributes": attributes_map}


if __name__ == "__main__":
    main()
