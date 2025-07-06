import os
import json
import re
from flask import Flask, render_template, request as flask_request

# Assuming generate_sads_attributes is in the same directory or PYTHONPATH is set up
try:
    from generate_sads_attributes import (
        construct_llm_prompt,
        get_sads_attributes_from_llm,
        parse_llm_sads_string_to_dict,
        load_sads_theme_context,
    )
except ImportError:
    # Fallback for local dev if script is directly in ai_sads_poc
    from .generate_sads_attributes import (
        construct_llm_prompt,
        get_sads_attributes_from_llm,
        parse_llm_sads_string_to_dict,
        load_sads_theme_context,
    )

from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()  # Load environment variables from .env

# Path to the SADS theme context (assuming it's in the same directory as the script)
# For a real app, this path might need to be more robust or configurable
SADS_THEME_CONTEXT_FILE = os.path.join(os.path.dirname(__file__), "sads_theme_context.json")
# Load theme context once at startup
SADS_THEME_CONTEXT = load_sads_theme_context(SADS_THEME_CONTEXT_FILE)
if SADS_THEME_CONTEXT is None:
    print("CRITICAL: Web app could not load SADS Theme Context. Functionality will be impaired.")
    # Fallback to an empty context to prevent crashes, but UI should indicate error
    SADS_THEME_CONTEXT = {}


def generate_sads_for_webrequest(
    html_snippet: str,
    style_prompt: str,
    provider: str,
    model_name: Optional[str],
    temperature: float,
    max_tokens: int
) -> Dict:
    """
    Core logic to generate SADS attributes, adapted for web requests.
    Returns a dictionary with results or error information.
    """
    output = {
        "generated_attributes_string": None,
        "modified_html": None,
        "parsed_sads_data": None,
        "error": None,
        "raw_llm_response_for_debug": None, # For more detailed debugging if needed
    }

    api_key = None
    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not model_name: model_name = os.getenv("DEFAULT_OPENAI_MODEL", "gpt-3.5-turbo")
    elif provider == "mistral":
        api_key = os.getenv("MISTRAL_API_KEY")
        if not model_name: model_name = os.getenv("DEFAULT_MISTRAL_MODEL", "mistral-small-latest")

    if not model_name: # Should be set by defaults if provider was valid
        output["error"] = "Model name could not be determined."
        return output

    if not api_key:
        output["error"] = f"API key for {provider} not found. Please set it in the .env file."
        return output

    if SADS_THEME_CONTEXT is None or not SADS_THEME_CONTEXT:
        output["error"] = "SADS Theme Context is not loaded. Cannot generate attributes."
        return output

    llm_prompt = construct_llm_prompt(html_snippet, style_prompt, SADS_THEME_CONTEXT)

    generated_attributes_string = get_sads_attributes_from_llm(
        api_key, model_name, llm_prompt, provider, temperature, max_tokens
    )
    output["raw_llm_response_for_debug"] = generated_attributes_string # Store for debugging

    if not generated_attributes_string:
        output["error"] = "LLM did not return any attributes or an error occurred during LLM communication."
        return output

    output["generated_attributes_string"] = generated_attributes_string
    parsed_sads_data = parse_llm_sads_string_to_dict(generated_attributes_string, SADS_THEME_CONTEXT)
    output["parsed_sads_data"] = parsed_sads_data

    if parsed_sads_data.get("errors"):
        # Append parsing errors to the main error string for display
        output["error"] = (output["error"] + "; " if output["error"] else "") + \
                          "Parsing Warnings/Errors: " + ", ".join(parsed_sads_data["errors"][:3]) # Show first 3

    # Try to inject into HTML
    final_sads_string_for_html = " ".join(
        [f'{k}="{v}"' for k, v in parsed_sads_data.get("_raw_attributes_for_html", {}).items()]
    )

    if final_sads_string_for_html:
        first_tag_match = re.search(r"<([a-zA-Z0-9\-]+)(\s*[^>]*)>", html_snippet)
        if first_tag_match:
            original_first_tag_end_char_index = html_snippet.find(">", first_tag_match.start())
            if original_first_tag_end_char_index != -1:
                output["modified_html"] = (
                    html_snippet[:original_first_tag_end_char_index] + " " +
                    final_sads_string_for_html +
                    html_snippet[original_first_tag_end_char_index:]
                )
            else:
                 output["modified_html"] = f"<div {final_sads_string_for_html}>{html_snippet}</div>" # Fallback
        else:
            output["modified_html"] = f"<div {final_sads_string_for_html}>{html_snippet}</div>" # Fallback
    else:
        output["modified_html"] = f"<!-- No valid SADS attributes were parsed to inject. Original HTML below: -->\n{html_snippet}"
        if not output["error"]: # If no other error, add one
             output["error"] = (output["error"] + "; " if output["error"] else "") + "No valid SADS attributes were parsed to inject into HTML."


    return output

@app.route("/", methods=["GET", "POST"])
def index():
    if flask_request.method == "POST":
        html_snippet = flask_request.form.get("html_snippet", "").strip()
        style_prompt = flask_request.form.get("style_prompt", "").strip()
        provider = flask_request.form.get("provider", "openai")
        model_name = flask_request.form.get("model_name", "").strip() # Allow user to specify, or default based on provider

        try:
            temperature = float(flask_request.form.get("temperature", os.getenv("DEFAULT_LLM_TEMPERATURE", "0.2")))
        except ValueError:
            temperature = float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.2"))

        try:
            max_tokens = int(flask_request.form.get("max_tokens", os.getenv("DEFAULT_LLM_MAX_TOKENS", "200")))
        except ValueError:
            max_tokens = int(os.getenv("DEFAULT_LLM_MAX_TOKENS", "200"))

        if not html_snippet or not style_prompt:
            # Pass current values back to template for stickiness
            return render_template("index.html", error="HTML snippet and Style prompt are required.",
                                   html_snippet=html_snippet, style_prompt=style_prompt,
                                   provider=provider, model_name=model_name,
                                   temperature=temperature, max_tokens=max_tokens)

        result = generate_sads_for_webrequest(
            html_snippet, style_prompt, provider, model_name, temperature, max_tokens
        )

        return render_template(
            "index.html",
            html_snippet=html_snippet,
            style_prompt=style_prompt,
            provider=provider,
            model_name=model_name if model_name else ("Default for " + provider),
            temperature=temperature,
            max_tokens=max_tokens,
            generated_attributes_string=result.get("generated_attributes_string"),
            modified_html=result.get("modified_html"),
            parsed_sads_json=json.dumps(result.get("parsed_sads_data"), indent=2) if result.get("parsed_sads_data") else None,
            error=result.get("error"),
        )

    # Default values for GET request
    default_temp = float(os.getenv("DEFAULT_LLM_TEMPERATURE", "0.2"))
    default_tokens = int(os.getenv("DEFAULT_LLM_MAX_TOKENS", "200"))
    return render_template("index.html", provider="openai", temperature=default_temp, max_tokens=default_tokens)

if __name__ == "__main__":
    # Make sure to create a 'templates' folder in the same directory as app.py
    # and add an 'index.html' file there.
    if not os.path.exists(os.path.join(os.path.dirname(__file__), "templates")):
        os.makedirs(os.path.join(os.path.dirname(__file__), "templates"))
        print("Created 'templates' directory. Please add an 'index.html' file there.")

    app.run(debug=True, port=5001) # Using port 5001 to avoid potential conflicts
