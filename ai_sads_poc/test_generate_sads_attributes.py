import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
from typing import Dict, Any, Optional

# Adjust import path
try:
    from ai_sads_poc.generate_sads_attributes import (
        parse_llm_sads_string_to_dict,
        construct_llm_prompt,
        load_sads_theme_context,
        get_sads_attributes_from_llm,
        main as script_main,
        save_output,
        OpenAI as ActualOpenAI,
        Mistral as ActualMistral
    )
    import ai_sads_poc.generate_sads_attributes as generate_sads_module
except ImportError:
    from .generate_sads_attributes import (
        parse_llm_sads_string_to_dict,
        construct_llm_prompt,
        load_sads_theme_context,
        get_sads_attributes_from_llm,
        main as script_main,
        save_output,
        OpenAI as ActualOpenAI,
        Mistral as ActualMistral
    )
    from . import generate_sads_attributes as generate_sads_module

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
SAMPLE_THEME_PATH = os.path.join(TEST_DATA_DIR, "sample_theme.json")
MALFORMED_JSON_PATH = os.path.join(TEST_DATA_DIR, "malformed.json")
NON_EXISTENT_FILE_PATH = os.path.join(TEST_DATA_DIR, "non_existent.json")

MINIMAL_THEME_CONTEXT: Dict[str, Any] = {
    "colors": {"primary": "#007bff", "secondary": "#6c757d"},
    "spacing": {"s": "0.25rem", "m": "0.5rem"},
    "sadsPropertiesReference": {
        "bgColor": "string", "padding": "string", "textColor": "string",
        "fontSize": "string", "borderRadius": "string", "opacity": "string",
        "margin": "string"
    }
}

class TestParseLlmSadsStringToDict(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(
            parse_llm_sads_string_to_dict("", MINIMAL_THEME_CONTEXT),
            {"attributes": {}, "errors": ["Input SADS string is empty."], "_raw_attributes_for_html": {}}
        )

    def test_simple_valid_attributes(self):
        s = 'data-sads-bgColor="primary" data-sads-padding="m"'
        res = parse_llm_sads_string_to_dict(s, MINIMAL_THEME_CONTEXT)
        self.assertEqual(res["attributes"]["bgColor"], {"color_token": "COLOR_TOKEN_PRIMARY"})
        self.assertEqual(res["attributes"]["padding"], {"spacing_token": "SPACING_TOKEN_M"})
        self.assertEqual(res["_raw_attributes_for_html"], {"data-sads-bgColor": "primary", "data-sads-padding": "m"})

    def test_kebab_case_key_normalization(self):
        theme_ctx = json.loads(json.dumps(MINIMAL_THEME_CONTEXT))
        theme_ctx["borderRadius"] = {"rdToken": "5px"}
        theme_ctx["sadsPropertiesReference"]["borderRadius"] = "token"

        s = 'data-sads-border-radius="rdToken"'
        res = parse_llm_sads_string_to_dict(s, theme_ctx)
        self.assertIn("borderRadius", res["attributes"])
        self.assertEqual(res["attributes"]["borderRadius"], {'border_radius_token': 'BORDER_RADIUS_TOKEN_RDTOKEN'})

    def test_unknown_sads_key_skipped(self):
        s = 'data-sads-unknownProp="test"'
        res = parse_llm_sads_string_to_dict(s, MINIMAL_THEME_CONTEXT)
        self.assertNotIn("unknownProp", res["attributes"])
        self.assertTrue(any("unknown SADS property key 'unknownProp'" in e for e in res["errors"]))

class TestConstructLlmPrompt(unittest.TestCase):
    def test_prompt_construction_with_full_context(self):
        html = "<div></div>"
        style = "red button"
        prompt = construct_llm_prompt(html, style, MINIMAL_THEME_CONTEXT)
        self.assertIn("- Available color tokens (for bgColor, textColor, borderColor, etc.): primary, secondary", prompt)
        self.assertIn("Ensure you only use these SADS property keys: bgColor, padding, textColor, fontSize, borderRadius, opacity, margin", prompt)

class TestLoadSadsThemeContext(unittest.TestCase):
    @patch("builtins.open", new_callable=mock_open, read_data='{"valid": "json"}')
    def test_load_valid_json(self, mock_file):
        self.assertEqual(load_sads_theme_context("dummy.json"), {"valid": "json"})

    def test_file_not_found(self):
        with patch('builtins.print') as mocked_print:
            self.assertIsNone(load_sads_theme_context("nonexistent.json"))
            mocked_print.assert_any_call("Error: SADS theme context file not found at 'nonexistent.json'. Please check the path.")

    @patch("builtins.open", new_callable=mock_open, read_data='invalid json')
    def test_malformed_json(self, mock_file):
        with patch('builtins.print') as mocked_print:
            self.assertIsNone(load_sads_theme_context("bad.json"))
            mocked_print.assert_any_call("Error: Could not decode JSON from 'bad.json'. Please ensure it's valid JSON.")

PATCH_TARGET_GET_CLIENT = "ai_sads_poc.generate_sads_attributes.get_client"

class TestGetSadsAttributesFromLlm(unittest.TestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": "key"})
    @patch(PATCH_TARGET_GET_CLIENT)
    def test_openai_success(self, mock_get_client):
        mock_openai_client = MagicMock(spec=ActualOpenAI)
        mock_openai_client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='data-sads-a="1"'))])
        mock_get_client.return_value = mock_openai_client

        self.assertEqual(get_sads_attributes_from_llm("k", "m", "p", "openai", temperature=0.2, max_tokens=200), 'data-sads-a="1"') # Added temp and max_tokens
        mock_openai_client.chat.completions.create.assert_called_once()

    @patch.dict(os.environ, {"MISTRAL_API_KEY": "key"})
    @patch(PATCH_TARGET_GET_CLIENT)
    def test_mistral_success(self, mock_get_client):
        if getattr(generate_sads_module, 'Mistral', None) is None: self.skipTest("Mistral lib not in source")

        mock_mistral_client = MagicMock(spec=ActualMistral)
        # Correctly mock the chat attribute and its complete method
        mock_chat_object = MagicMock()
        mock_chat_object.complete.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='data-sads-b="2"'))])
        mock_mistral_client.chat = mock_chat_object
        mock_get_client.return_value = mock_mistral_client

        self.assertEqual(get_sads_attributes_from_llm("k", "m", "p", "mistral", temperature=0.2, max_tokens=200), 'data-sads-b="2"') # Added temp and max_tokens
        mock_mistral_client.chat.complete.assert_called_once()


    @patch.dict(os.environ, {"OPENAI_API_KEY": "key"})
    @patch(PATCH_TARGET_GET_CLIENT)
    def test_openai_api_error_prints_and_returns_none(self, mock_get_client):
        mock_openai_client = MagicMock(spec=ActualOpenAI)
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_openai_client
        with patch('builtins.print') as mocked_print:
            self.assertIsNone(get_sads_attributes_from_llm("k", "m", "p", "openai", temperature=0.2, max_tokens=200)) # Added temp and max_tokens
            mocked_print.assert_any_call("Error calling OpenAI API (m): API Error")

PATCH_TARGET_ARGPARSE = "ai_sads_poc.generate_sads_attributes.argparse.ArgumentParser"
PATCH_TARGET_LOAD_THEME = "ai_sads_poc.generate_sads_attributes.load_sads_theme_context"
PATCH_TARGET_GET_LLM_ATTRS = "ai_sads_poc.generate_sads_attributes.get_sads_attributes_from_llm"
PATCH_TARGET_SAVE_OUTPUT = "ai_sads_poc.generate_sads_attributes.save_output"
PATCH_TARGET_LOAD_DOTENV = "ai_sads_poc.generate_sads_attributes.load_dotenv"

class TestMainScriptExecution(unittest.TestCase):
    @patch(PATCH_TARGET_ARGPARSE)
    @patch(PATCH_TARGET_LOAD_THEME, return_value=MINIMAL_THEME_CONTEXT)
    @patch(PATCH_TARGET_GET_LLM_ATTRS, return_value='data-sads-test="val"')
    @patch('builtins.open', new_callable=mock_open, read_data="html")
    @patch(PATCH_TARGET_SAVE_OUTPUT)
    @patch(PATCH_TARGET_LOAD_DOTENV)
    @patch.dict(os.environ, {"OPENAI_API_KEY": "key", "DEFAULT_OPENAI_MODEL": "def_model", "DEFAULT_LLM_TEMPERATURE": "0.5", "DEFAULT_LLM_MAX_TOKENS": "150"})
    def test_main_success_all_mocks(self, mock_dotenv, mock_save, mock_open, mock_get_llm, mock_load_theme, mock_argparse):
        mock_args = MagicMock(html_file="h",style_prompt="s",theme_context_file="t",provider="openai",model=None,output_file="o",temperature=None,max_tokens=None)
        mock_argparse.return_value.parse_args.return_value = mock_args
        mock_dotenv.return_value = True
        with patch('builtins.print'): script_main()

        mock_get_llm.assert_called_once()
        called_args_list = mock_get_llm.call_args_list
        self.assertEqual(len(called_args_list), 1)
        called_args, called_kwargs = called_args_list[0]

        self.assertEqual(called_args[0], "key") # api_key
        self.assertEqual(called_args[1], "def_model")   # model_name from env
        self.assertIn("expert in Semantic Attribute", called_args[2]) # prompt
        self.assertEqual(called_args[3], "openai")      # provider
        self.assertEqual(called_kwargs['temperature'], 0.5) # temperature from env
        self.assertEqual(called_kwargs['max_tokens'], 150)  # max_tokens from env
        mock_save.assert_called_once()

    @patch(PATCH_TARGET_ARGPARSE)
    @patch(PATCH_TARGET_LOAD_DOTENV)
    @patch('builtins.print')
    @patch.dict(os.environ, {}, clear=True)
    def test_main_missing_api_key(self, mock_print, mock_dotenv, mock_argparse):
        mock_args = MagicMock(provider="openai", model="m",temperature=None,max_tokens=None,html_file="h",style_prompt="s",theme_context_file="t",output_file=None)
        mock_argparse.return_value.parse_args.return_value = mock_args
        mock_dotenv.return_value = False # Simulate .env not loaded or not found
        script_main()
        mock_print.assert_any_call("Error: OPENAI_API_KEY not found in environment variables or .env file for OpenAI provider.")

    @patch(PATCH_TARGET_ARGPARSE)
    @patch(PATCH_TARGET_LOAD_DOTENV) # Mock this to control its behavior
    @patch('builtins.open') # Mock open more carefully
    @patch('builtins.print')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "key"})
    def test_main_html_file_not_found(self, mock_print, mock_open_call, mock_dotenv, mock_argparse):
        mock_args = MagicMock(html_file="bad.html", style_prompt="s",theme_context_file="t",provider="openai",model="m",temperature=None,max_tokens=None,output_file=None)
        mock_argparse.return_value.parse_args.return_value = mock_args
        mock_dotenv.return_value = True # Assume .env is fine

        # Make mock_open raise FileNotFoundError only for 'bad.html'
        def open_side_effect(path, mode="r"):
            if path == "bad.html":
                raise FileNotFoundError("Original HTML not found")
            # For other calls (like load_sads_theme_context if not mocked separately, or .env if load_dotenv wasn't mocked)
            return mock_open(read_data="dummy data for other files").return_value
        mock_open_call.side_effect = open_side_effect

        script_main()
        mock_print.assert_any_call("Error: HTML snippet file not found at 'bad.html'. Please check the path.")

if __name__ == "__main__":
    if not os.path.exists(TEST_DATA_DIR):
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
    cleanup_malformed = False
    if not os.path.exists(MALFORMED_JSON_PATH):
        with open(MALFORMED_JSON_PATH, "w") as f: f.write('{"bad",,}')
        cleanup_malformed = True

    try:
        unittest.main()
    finally:
        if cleanup_malformed:
            try: os.remove(MALFORMED_JSON_PATH)
            except OSError: pass
