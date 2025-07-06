# AI-Assisted SADS Attribute Generation PoC

This directory contains a Proof-of-Concept (PoC) script to explore using a Large Language Model (LLM) to generate `data-sads-*` attributes based on natural language style descriptions and a simple HTML snippet.

## Objective

To test the feasibility of translating human-readable style prompts into SADS attributes that can be used by the SADS engine.

## Setup

1.  **Create a Python Virtual Environment (Recommended):**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

2.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set OpenAI API Key:**
    This script uses the OpenAI API. You need to set your API key as an environment variable named `OPENAI_API_KEY`.
    Create a `.env` file in this `ai_sads_poc` directory. Add the appropriate API key for the LLM provider you intend to use:

    ```env
    # For OpenAI:
    OPENAI_API_KEY="your_openai_api_key_here"

    # For Mistral AI (if you adapt the script):
    # MISTRAL_API_KEY="your_mistral_api_key_here"
    ```

    The script will load the relevant key based on the chosen provider.

    Additionally, you can configure default LLM parameters in the `.env` file. These will be used if not overridden by command-line arguments:
    ```env
    # --- Optional LLM Configuration ---
    # Default model names (if --model CLI argument is not provided)
    # DEFAULT_OPENAI_MODEL="gpt-3.5-turbo"
    # DEFAULT_MISTRAL_MODEL="mistral-small-latest"

    # Default LLM parameters (can be overridden by CLI arguments --temperature and --max_tokens)
    # DEFAULT_LLM_TEMPERATURE="0.2"
    # DEFAULT_LLM_MAX_TOKENS="200"
    ```

## Usage

The script `generate_sads_attributes.py` accepts command-line arguments to specify the input HTML, the styling prompt, the theme context, the LLM provider, model, and other LLM parameters.

**Command Structure:**

```bash
python generate_sads_attributes.py \
    --html_file <path_to_html_file> \
    --style_prompt "<your_style_description>" \
    --theme_context_file <path_to_theme_json> \
    [--provider <openai|mistral>] \
    [--model <model_name>] \
    [--temperature <float_value>] \
    [--max_tokens <int_value>] \
    [--output_file <path_to_output_html>]
```

**Core Arguments:**

- `--html_file`: (Required) Path to a file containing the HTML snippet.
  - Example: `sample_html_snippet.html`
- `--style_prompt`: (Required) Natural language string describing the desired style.
  - Example: `"Make this look like a warning box."`
- `--theme_context_file`: (Required) Path to a JSON file with SADS theme context.
  - Example: `sads_theme_context.json`

**Optional LLM & Output Arguments:**

- `--provider`: LLM provider. Choices: `openai`, `mistral`.
  - Default: `openai`.
  - Example: `--provider mistral`
- `--model`: Specific LLM model to use.
  - Default for OpenAI: `gpt-3.5-turbo` (or `DEFAULT_OPENAI_MODEL` from `.env`).
  - Default for Mistral: `mistral-small-latest` (or `DEFAULT_MISTRAL_MODEL` from `.env`).
  - Example: `--model gpt-4-turbo-preview`
- `--temperature`: LLM temperature for generation (float).
  - Default: `0.2` (or `DEFAULT_LLM_TEMPERATURE` from `.env`).
  - Example: `--temperature 0.5`
- `--max_tokens`: LLM maximum tokens for the response (integer).
  - Default: `200` (or `DEFAULT_LLM_MAX_TOKENS` from `.env`).
  - Example: `--max_tokens 250`
- `--output_file`: Path to save the generated HTML with injected SADS attributes.
  - If provided, related files (`.raw_llm.txt`, `.parsed_sads.json`) will also be saved in the same location with corresponding extensions.
  - Example: `--output_file generated_output/styled_snippet.html`


**Example Invocation:**

```bash
python generate_sads_attributes.py \
    --html_file sample_html_snippet.html \
    --style_prompt "Make the button stand out with a primary color background, white text, and medium padding. The overall div should have a light surface background and some margin." \
    --theme_context_file sads_theme_context.json
```

The script will print:

1.  Information about the inputs and LLM parameters being used.
2.  The raw `data-sads-*` attribute string from the LLM (if successful).
3.  The input HTML with the generated SADS attributes injected into its first tag.
4.  A structured Python dictionary of the parsed SADS attributes (conceptually mirroring SADS Protobuf messages).
5.  Any warnings or errors encountered during parsing or LLM communication.

If `--output_file` is specified, the script will also save:
- The modified HTML to the specified path.
- The raw LLM response to `<output_path_stem>.raw_llm.txt`.
- The parsed SADS JSON structure to `<output_path_stem>.parsed_sads.json`.

**Recent Script Enhancements:**

- **Improved Stability & UX:**
    - Enhanced validation of LLM responses, using regular expressions for more robust parsing of `data-sads-*` attributes.
    - More informative error messages for API issues, file handling, and parsing errors.
    - Added `--output_file` option to save results.
- **Configuration Management:**
    - API keys are loaded from `.env`.
    - Default model names, temperature, and max_tokens can be set in `.env` and overridden by CLI arguments.
- **Unit Tests:**
    - A suite of unit tests (`test_generate_sads_attributes.py`) has been added to cover core functionalities, improving reliability.
- **Type Hints & Parsing:** The script maintains type hints and the structured output parser for converting LLM responses to a dictionary.

## Files

- `generate_sads_attributes.py`: The main Python script for this PoC.
- `requirements.txt`: Python dependencies (`openai`, `python-dotenv`, `mistralai`).
- `README.md`: This file.
- `.env`: File for API keys and optional default configurations (user-created, based on `.env.example` if provided, or instructions here).
- `sample_html_snippet.html`: An example HTML input file.
- `sads_theme_context.json`: An example SADS theme context.
- `test_generate_sads_attributes.py`: Unit tests for the script.
- `test_data/`: Directory containing sample files for testing.

## Initial Findings & Observations (Template)

_(User: Please replace this section with your actual findings after running experiments.)_

This section outlines expected or potential findings from running this PoC.

**LLM Used:** (e.g., GPT-3.5-turbo, GPT-4) - _User to specify_

**1. Prompt Effectiveness:**

- **Clarity of Instructions:** The LLM is generally expected to understand the request to output `data-sads-*` attributes due to the explicit instructions in the prompt ("Only output the `data-sads-*` attributes string...").
- **Contextual Understanding:**
  - The inclusion of available SADS tokens (colors, spacing, etc.) in the prompt is crucial. The LLM's ability to correctly use these predefined tokens vs. defaulting to `custom:<value>` will be a key observation point.
  - The `sadsPropertiesReference` is intended to guide the LLM towards valid SADS property keys (e.g., `bgColor`, `padding`, not `background-color`). Its effectiveness should be monitored.
- **Natural Language Interpretation:** The LLM's ability to translate varied natural language style descriptions (e.g., "make it pop", "subtle warning", "modern and clean") into concrete SADS attributes will vary. More abstract prompts may yield less predictable or less useful results compared to more direct prompts (e.g., "blue background, medium padding").

**2. Quality of Generated SADS Attributes:**

- **Syntactic Correctness:** Are the generated attributes in the correct format (`data-sads-propertyKey="value"`)? LLMs are usually good at mimicking formats.
- **Token Usage:** Does the LLM correctly pick valid tokens from the provided context (e.g., `data-sads-bgColor="primary"`) or does it hallucinate tokens? Does it appropriately use `custom:<value>` when a token isn't suitable or available?
- **Relevance to Prompt:** How well do the generated SADS attributes match the intent of the natural language style prompt?
- **Completeness:** Does the LLM generate a reasonable set of attributes to achieve the described style, or does it miss key aspects (e.g., forgetting text color when setting a dark background)?
- **Over-Generation:** Does the LLM sometimes generate too many attributes or redundant ones?

**3. Challenges Encountered (Anticipated):**

- **LLM Verbosity/Chattiness:** While the script now filters for `data-sads-*` patterns, extremely verbose or off-topic LLM responses might still lead to no usable attributes being extracted. The raw LLM output saving helps diagnose this.
- **Specificity of SADS:** The LLM's adherence to SADS principles (valid keys from `sadsPropertiesReference`, correct token usage) is better guided but still relies heavily on the prompt and the model's capabilities. The parser now warns about unknown SADS keys if a reference is provided.
- **Complex HTML Structures:** The current PoC uses a simple HTML snippet. Applying styles selectively to nested elements within a more complex structure via a single natural language prompt (without targeting specific inner elements in the prompt) would be significantly harder for the LLM. The prompt currently implies styling the main container of the snippet.
- **Iteration for Complex Styles:** Achieving a desired complex style might require iterative prompting or more detailed natural language input, which this basic script doesn't facilitate.
- **Cost/Latency:** API calls have associated costs and latency. For a build-time tool, this would be a factor if used extensively.

**4. Potential Prompt/Context Refinements:**

- **Negative Constraints:** Adding examples of what _not_ to do (e.g., "Do not output CSS properties directly").
- **Few-Shot Examples:** Providing 1-2 examples of (HTML snippet + style prompt + SADS theme context) -> desired SADS attribute string within the main prompt could significantly improve LLM performance and adherence to format.
- **More Granular Theme Context:** If the LLM struggles, providing an even more detailed breakdown of which SADS properties accept which types of tokens might be needed.
- **Targeting Specific Elements:** For more complex HTML, the prompt would need to support a way to specify which part of the HTML the style description applies to, or the LLM would need to infer this (which is harder).

**Overall Feasibility (Initial Thoughts):**

- For simple components and clear style descriptions, generating a plausible starting set of SADS attributes seems feasible.
- The quality will heavily depend on the LLM model used (e.g., GPT-4 likely better than GPT-3.5-turbo) and the quality/detail of the prompt engineering.
- It's unlikely to be a perfect, one-shot solution for complex styling but could be a useful "first draft" generator or assistant, especially for users less familiar with SADS syntax.

This PoC should provide valuable insights into these areas.

## Adapting for Mistral (or other LLMs)

The `generate_sads_attributes.py` script is primarily set up to use the OpenAI API via the `openai` Python library. It includes a command-line argument `--provider` which defaults to `openai` but also accepts `mistral`.

To use Mistral (or adapt for another LLM provider):

1.  **Install Necessary Client Library:**
    For Mistral, you would typically install their official Python client:

    ```bash
    pip install mistralai
    ```

    The `requirements.txt` file has been updated to include `mistralai`.

2.  **Set API Key Environment Variable:**
    The script expects an API key for the chosen provider. For Mistral, you need to set `MISTRAL_API_KEY` in your `.env` file (in the `ai_sads_poc` directory):

    ```env
    # For Mistral AI:
    MISTRAL_API_KEY="your_mistral_api_key_here"
    ```

    Ensure your `.env` file also has `OPENAI_API_KEY` if you intend to switch between providers or use OpenAI as the default.

3.  **Script `generate_sads_attributes.py` is Ready for Mistral:**
    - The `get_sads_attributes_from_llm` function in the script now contains a functional implementation for the Mistral provider.
    - It correctly imports `MistralClient` and `ChatMessage` from the `mistralai` library.
    - It initializes the client and makes the API call as expected.
    - You can run the script with `--provider mistral` and specify a Mistral model with `--model <your_mistral_model_name>` (e.g., `mistral-small-latest`).

4.  **Prompt Engineering (If Needed):**
    Different LLMs can respond differently to the same prompt. If the results from Mistral (or another LLM) are not optimal, you might need to adjust the prompt construction logic in the `construct_llm_prompt` function to better suit that specific model's characteristics or how it best interprets instructions and context.

By following these steps, you can adapt the PoC to work with Mistral or a similar LLM provider that offers a Python client library.
