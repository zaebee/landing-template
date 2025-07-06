package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
	"os" // Added for os.Getenv
)

// GenerateSadsRequest is the expected structure for POST requests to /api/generate-sads-from-nl
type GenerateSadsRequest struct {
	HTMLSnippet          string `json:"html_snippet"`
	StylePrompt          string `json:"style_prompt"`
	SadsThemeContextJSON string `json:"sads_theme_context_json"` // JSON string of the theme context
	Provider             string `json:"provider"`                // "openai" or "mistral"
	Model                string `json:"model"`                   // Specific model name for the provider
}

// SadsGenerationResponse is the structure for JSON responses from /api/generate-sads-from-nl
type SadsGenerationResponse struct {
	SadsAttributesString string                       `json:"sads_attributes_string,omitempty"`
	ParsedSadsAttributes map[string]map[string]string `json:"parsed_sads_attributes,omitempty"` // Conceptually SadsStylingSet
	Error                string                       `json:"error,omitempty"`
}

// --- Structs for OpenAI API Interaction ---

// OpenAIMessage represents a message object for the OpenAI Chat API.
type OpenAIMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// OpenAIChatCompletionRequest represents the request payload for OpenAI Chat Completions.
type OpenAIChatCompletionRequest struct {
	Model       string          `json:"model"`
	Messages    []OpenAIMessage `json:"messages"`
	Temperature float32         `json:"temperature,omitempty"`
	MaxTokens   int             `json:"max_tokens,omitempty"`
}

// OpenAIChoice represents a single choice in the OpenAI Chat API response.
type OpenAIChoice struct {
	Index        int           `json:"index"`
	Message      OpenAIMessage `json:"message"`
	FinishReason string        `json:"finish_reason"`
}

// OpenAIUsage represents the usage statistics from the OpenAI Chat API response.
type OpenAIUsage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

// OpenAIChatCompletionResponse represents the full response from OpenAI Chat Completions.
type OpenAIChatCompletionResponse struct {
	ID      string         `json:"id"`
	Object  string         `json:"object"`
	Created int64          `json:"created"`
	Model   string         `json:"model"`
	Choices []OpenAIChoice `json:"choices"`
	Usage   OpenAIUsage    `json:"usage,omitempty"`
	Error   *OpenAIError   `json:"error,omitempty"` // Pointer to allow for null error
}

// OpenAIError represents an error object from the OpenAI API.
type OpenAIError struct {
	Message string `json:"message"`
	Type    string `json:"type"`
	Param   string `json:"param,omitempty"`
	Code    string `json:"code,omitempty"`
}


// --- Structs for Mistral API Interaction ---

// MistralMessage represents a message object for the Mistral API.
// Mistral's API typically uses a similar structure to OpenAI's messages.
type MistralMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// MistralChatCompletionRequest represents the request payload for Mistral Chat Completions.
type MistralChatCompletionRequest struct {
	Model       string           `json:"model"`
	Messages    []MistralMessage `json:"messages"`
	Temperature float32          `json:"temperature,omitempty"`
	MaxTokens   int              `json:"max_tokens,omitempty"`
	// Add other Mistral-specific parameters if needed, e.g., safe_prompt
}

// MistralChoice represents a single choice in the Mistral API response.
type MistralChoice struct {
	Index        int            `json:"index"`
	Message      MistralMessage `json:"message"`
	FinishReason string         `json:"finish_reason"`
}

// MistralUsage represents usage statistics if provided by Mistral API.
// Structure might differ; this is a common pattern.
type MistralUsage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

// MistralChatCompletionResponse represents the full response from Mistral Chat Completions.
type MistralChatCompletionResponse struct {
	ID      string          `json:"id"`
	Object  string          `json:"object"`
	Created int64           `json:"created"`
	Model   string          `json:"model"`
	Choices []MistralChoice `json:"choices"`
	Usage   *MistralUsage   `json:"usage,omitempty"` // Pointer if optional
	// Mistral might have a different error structure, adjust if necessary
}

// Helper function to write JSON responses (will be used by the handler)
func writeJSONResponse(w http.ResponseWriter, statusCode int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	if data != nil {
		if err := json.NewEncoder(w).Encode(data); err != nil {
			// Log error internally, difficult to send error response if headers already sent
			http.Error(w, "Failed to encode JSON response", http.StatusInternalServerError)
			// Consider logging err to server logs
		}
	}
}

// Placeholder for where the actual handler and its logic will go
// func GenerateSadsFromNLHandler(w http.ResponseWriter, r *http.Request) {
//    // To be implemented in a later step
// }

// --- Core LLM Interaction Logic ---

func constructLLMPrompt_Go(htmlSnippet string, stylePrompt string, sadsThemeContextJSON string) (string, error) {
	var themeContext map[string]interface{}
	if err := json.Unmarshal([]byte(sadsThemeContextJSON), &themeContext); err != nil {
		return "", fmt.Errorf("error unmarshalling SADS theme context JSON: %w", err)
	}

	sadsExplanation := "You are an expert in Semantic Attribute-Driven Styling (SADS).\n" +
		"Your task is to generate a string of `data-sads-*` attributes to style the given HTML snippet " +
		"based on the user's style description and the available SADS theme tokens.\n" +
		"The SADS attributes should be space-separated, e.g., `data-sads-bgColor=\"primary\" data-sads-padding=\"m\"`.\n" +
		"Focus on mapping the style description to appropriate SADS attributes and tokens.\n" +
		"If a style cannot be directly represented by a known SADS token from the context, " +
		"you can use a 'custom:<value>' format, e.g., `data-sads-fontSize=\"custom:1.1em\"` or `data-sads-border=\"custom:1px solid #CCC\"`.\n" +
		"Only output the `data-sads-*` attributes string. Do not include any other text, explanations, or HTML markup.\n"

	var contextStrParts []string
	if themeContext != nil {
		categories := []string{"colors", "spacing", "fontSize", "fontWeight", "borderRadius", "shadow"}
		categoryNames := map[string]string{
			"colors":       "color tokens (for bgColor, textColor, borderColor, etc.)",
			"spacing":      "spacing tokens (for padding, margin, gap, etc.)",
			"fontSize":     "fontSize tokens",
			"fontWeight":   "fontWeight tokens",
			"borderRadius": "borderRadius tokens",
			"shadow":       "shadow tokens",
		}

		for _, category := range categories {
			if catMap, ok := themeContext[category].(map[string]interface{}); ok && len(catMap) > 0 {
				var keys []string
				for k := range catMap {
					keys = append(keys, k)
				}
				contextStrParts = append(contextStrParts, fmt.Sprintf("- Available %s: %s", categoryNames[category], strings.Join(keys, ", ")))
			}
		}
	}

	sadsThemeContextStr := "Available SADS theme tokens:\n" + strings.Join(contextStrParts, "\n")
	if len(contextStrParts) == 0 {
		sadsThemeContextStr = "No specific SADS theme tokens provided for discrete values; use general SADS knowledge and custom values where appropriate for tokens."
	}

	sadsPropertiesRefStr := ""
	if themeContext != nil {
		if propsRef, ok := themeContext["sadsPropertiesReference"].(map[string]interface{}); ok && len(propsRef) > 0 {
			sadsPropertiesRefStr = "\n\nSADS Properties Reference (attribute_name: expected_value_type_or_examples):\n"
			for key, desc := range propsRef {
				sadsPropertiesRefStr += fmt.Sprintf("- %s: %v\n", key, desc)
			}
		}
	}

	prompt := fmt.Sprintf("%s\n\n%s%s\n\nHTML SNIPPET:\n```html\n%s\n```\n\nUSER STYLE DESCRIPTION: \"%s\"\n\nGenerated `data-sads-*` attributes string:",
		sadsExplanation, sadsThemeContextStr, sadsPropertiesRefStr, htmlSnippet, stylePrompt,
	)
	return prompt, nil
}

func getSadsAttributesFromLLM_Go(apiKey string, provider string, modelName string, prompt string) (string, error) {
	httpClient := &http.Client{Timeout: 60 * time.Second} // Increased timeout

	if provider == "openai" {
		apiURL := "https://api.openai.com/v1/chat/completions"
		reqBody := OpenAIChatCompletionRequest{
			Model: modelName,
			Messages: []OpenAIMessage{
				{Role: "system", Content: "You are a helpful assistant that generates SADS attributes."},
				{Role: "user", Content: prompt},
			},
			Temperature: 0.2,
			MaxTokens:   150,
		}
		jsonBody, err := json.Marshal(reqBody)
		if err != nil {
			return "", fmt.Errorf("error marshalling OpenAI request body: %w", err)
		}

		req, err := http.NewRequest("POST", apiURL, bytes.NewBuffer(jsonBody))
		if err != nil {
			return "", fmt.Errorf("error creating OpenAI request: %w", err)
		}
		req.Header.Set("Authorization", "Bearer "+apiKey)
		req.Header.Set("Content-Type", "application/json")

		resp, err := httpClient.Do(req)
		if err != nil {
			return "", fmt.Errorf("error sending request to OpenAI: %w", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			var errResp OpenAIChatCompletionResponse // Attempt to parse OpenAI error
			if err := json.NewDecoder(resp.Body).Decode(&errResp); err == nil && errResp.Error != nil {
				return "", fmt.Errorf("OpenAI API error (%d): %s (Type: %s)", resp.StatusCode, errResp.Error.Message, errResp.Error.Type)
			}
			return "", fmt.Errorf("OpenAI API request failed with status %d: %s", resp.StatusCode, http.StatusText(resp.StatusCode))
		}

		var openAIResp OpenAIChatCompletionResponse
		if err := json.NewDecoder(resp.Body).Decode(&openAIResp); err != nil {
			return "", fmt.Errorf("error decoding OpenAI response: %w", err)
		}

		if len(openAIResp.Choices) > 0 && openAIResp.Choices[0].Message.Content != "" {
			return strings.TrimSpace(openAIResp.Choices[0].Message.Content), nil
		}
		return "", fmt.Errorf("no content in OpenAI response choices")

	} else if provider == "mistral" {
		// Note: This requires the Mistral API endpoint and exact request/response structure.
		// This is a conceptual implementation. Consult Mistral's API documentation.
		apiURL := "https://api.mistral.ai/v1/chat/completions" // Common Mistral API endpoint
		reqBody := MistralChatCompletionRequest{
			Model: modelName,
			Messages: []MistralMessage{
				{Role: "user", Content: prompt}, // Mistral typically takes instructions in user role
			},
			Temperature: 0.2,
			MaxTokens:   150,
		}
		jsonBody, err := json.Marshal(reqBody)
		if err != nil {
			return "", fmt.Errorf("error marshalling Mistral request body: %w", err)
		}

		req, err := http.NewRequest("POST", apiURL, bytes.NewBuffer(jsonBody))
		if err != nil {
			return "", fmt.Errorf("error creating Mistral request: %w", err)
		}
		req.Header.Set("Authorization", "Bearer "+apiKey)
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Accept", "application/json")


		resp, err := httpClient.Do(req)
		if err != nil {
			return "", fmt.Errorf("error sending request to Mistral: %w", err)
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			// Try to read body for more error details
			bodyBytes, _ := io.ReadAll(resp.Body)
			return "", fmt.Errorf("Mistral API request failed with status %d: %s. Body: %s", resp.StatusCode, http.StatusText(resp.StatusCode), string(bodyBytes))
		}

		var mistralResp MistralChatCompletionResponse
		if err := json.NewDecoder(resp.Body).Decode(&mistralResp); err != nil {
			return "", fmt.Errorf("error decoding Mistral response: %w", err)
		}

		if len(mistralResp.Choices) > 0 && mistralResp.Choices[0].Message.Content != "" {
			return strings.TrimSpace(mistralResp.Choices[0].Message.Content), nil
		}
		return "", fmt.Errorf("no content in Mistral response choices")
	}

	return "", fmt.Errorf("unsupported LLM provider: %s", provider)
}

// --- SADS String Parser ---

// parseLLMSadsStringToMap_Go parses a string of data-sads-* attributes (from LLM)
// into a structured map that conceptually represents a SadsStylingSet proto message.
func parseLLMSadsStringToMap_Go(sadsAttributesString string, themeContextJSON string) (map[string]interface{}, error) {
	if sadsAttributesString == "" {
		return map[string]interface{}{"attributes": map[string]map[string]string{}}, nil
	}

	var themeContext map[string]interface{}
	if err := json.Unmarshal([]byte(themeContextJSON), &themeContext); err != nil {
		// If theme context is bad, we can still parse but token mapping will be affected.
		// For now, let's allow it and proceed, token mapping will just fail more often.
		// Alternatively, return fmt.Errorf("error unmarshalling SADS theme context JSON for parser: %w", err)
		themeContext = make(map[string]interface{}) // Initialize to empty map to avoid nil panics
		// Consider logging this warning.
	}

	attributesMap := make(map[string]map[string]string)

	// Simple parsing: split by space for attributes, then by '=' for key-value.
	// More robust parsing might use regular expressions, especially if values can contain spaces (though not typical for SADS values).
	rawAttributes := strings.Fields(sadsAttributesString) // strings.Fields handles multiple spaces better

	for _, attr := range rawAttributes {
		if strings.TrimSpace(attr) == "" {
			continue
		}

		parts := strings.SplitN(attr, "=", 2)
		if len(parts) != 2 {
			// Log warning: fmt.Printf("Warning: Skipping malformed attribute '%s'\n", attr)
			continue
		}

		fullKey := strings.TrimSpace(parts[0])
		rawValueWithQuotes := strings.TrimSpace(parts[1])

		if !strings.HasPrefix(fullKey, "data-sads-") {
			// Log warning: fmt.Printf("Warning: Skipping non-SADS attribute '%s'\n", attr)
			continue
		}

		sadsKey := strings.TrimPrefix(fullKey, "data-sads-")
		// Normalize sadsKey from kebab-case to camelCase for map keys if needed
		// Example: bg-color -> bgColor. For this PoC, assume simple keys or direct use.
		// A more robust normalizer might be needed if LLM output varies greatly.
		// For now, let's try a simple kebab to camel for SADS keys
		if strings.Contains(sadsKey, "-") {
			parts := strings.Split(sadsKey, "-")
			sadsKey = parts[0]
			for _, p := range parts[1:] {
				if len(p) > 0 {
					sadsKey += strings.ToUpper(string(p[0])) + p[1:]
				}
			}
		}


		value := strings.Trim(rawValueWithQuotes, "\"") // Remove surrounding quotes

		attrValueDict := make(map[string]string)

		if strings.HasPrefix(value, "custom:") {
			attrValueDict["custom_value"] = strings.TrimPrefix(value, "custom:")
		} else {
			mapped := false
			// Attempt to map to a known token based on sadsKey and themeContext
			// This is a simplified heuristic. A more robust system would use a schema
			// linking sadsKey to its expected token category.
			sadsKeyLower := strings.ToLower(sadsKey)

			if themeContext != nil {
				if colors, ok := themeContext["colors"].(map[string]interface{}); ok {
					if _, tokenExists := colors[value]; tokenExists &&
					   (strings.Contains(sadsKeyLower, "color") || strings.Contains(sadsKeyLower, "bg") || strings.Contains(sadsKeyLower, "border")) {
						attrValueDict["color_token"] = "COLOR_TOKEN_" + strings.ReplaceAll(strings.ToUpper(value), "-", "_")
						mapped = true
					}
				}
				if !mapped { // check other categories if not mapped as color
					if spacing, ok := themeContext["spacing"].(map[string]interface{}); ok {
						if _, tokenExists := spacing[value]; tokenExists &&
						   (strings.Contains(sadsKeyLower, "padding") || strings.Contains(sadsKeyLower, "margin") || strings.Contains(sadsKeyLower, "gap")) {
							attrValueDict["spacing_token"] = "SPACING_TOKEN_" + strings.ReplaceAll(strings.ToUpper(value), "-", "_")
							mapped = true
						}
					}
				}
				if !mapped && (sadsKeyLower == "fontsize" || sadsKeyLower == "font-size") { // fontSizeValue in proto is string
					if fontSizes, ok := themeContext["fontSize"].(map[string]interface{}); ok {
						if _, tokenExists := fontSizes[value]; tokenExists {
							attrValueDict["font_size_value"] = value
							mapped = true
						}
					}
				}
				// Add similar checks for fontWeight, borderRadius using their respective token prefixes
				if !mapped {
					if fontWeight, ok := themeContext["fontWeight"].(map[string]interface{}); ok {
						if _, tokenExists := fontWeight[value]; tokenExists && strings.Contains(sadsKeyLower, "fontweight") {
							attrValueDict["font_weight_token"] = "FONT_WEIGHT_TOKEN_" + strings.ReplaceAll(strings.ToUpper(value), "-", "_")
							mapped = true
						}
					}
				}
				if !mapped {
					if borderRadius, ok := themeContext["borderRadius"].(map[string]interface{}); ok {
						if _, tokenExists := borderRadius[value]; tokenExists && strings.Contains(sadsKeyLower, "borderradius") {
							attrValueDict["border_radius_token"] = "BORDER_RADIUS_TOKEN_" + strings.ReplaceAll(strings.ToUpper(value), "-", "_")
							mapped = true
						}
					}
				}
			}

			if !mapped { // If no token mapping found, treat as custom or direct value
				if sadsKeyLower == "fontsize" || sadsKeyLower == "font-size" { // If it wasn't a token from theme.fontSize
                    attrValueDict["font_size_value"] = value
                } else if _, isDirectValueKey := map[string]bool{ // list of keys that usually take direct values
					"textalign": true, "display": true, "position": true, "overflow": true,
					"cursor": true, "transition": true, "boxsizing": true, "resize": true,
					}[sadsKeyLower]; isDirectValueKey {
                    attrValueDict["custom_value"] = value
                } else {
					// Default to custom_value if no specific logic or token match
					attrValueDict["custom_value"] = value
				}
			}
		}

		if len(attrValueDict) > 0 {
			attributesMap[sadsKey] = attrValueDict
		} else {
			// Log warning: fmt.Printf("Warning: Could not determine value type for SADS key '%s' with value '%s'. Storing as custom.\n", sadsKey, value)
			attributesMap[sadsKey] = map[string]string{"custom_value": value}
		}
	}
	return map[string]interface{}{"attributes": attributesMap}, nil
}

// GenerateSadsFromNLHandler is the HTTP handler for the /api/generate-sads-from-nl endpoint.
func GenerateSadsFromNLHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeJSONResponse(w, http.StatusMethodNotAllowed, SadsGenerationResponse{Error: "Only POST method is allowed"})
		return
	}

	var reqPayload GenerateSadsRequest
	if err := json.NewDecoder(r.Body).Decode(&reqPayload); err != nil {
		writeJSONResponse(w, http.StatusBadRequest, SadsGenerationResponse{Error: "Invalid JSON request body: " + err.Error()})
		return
	}
	defer r.Body.Close()

	if reqPayload.HTMLSnippet == "" || reqPayload.StylePrompt == "" || reqPayload.SadsThemeContextJSON == "" || reqPayload.Provider == "" || reqPayload.Model == "" {
		writeJSONResponse(w, http.StatusBadRequest, SadsGenerationResponse{Error: "Missing required fields in request: html_snippet, style_prompt, sads_theme_context_json, provider, model"})
		return
	}

	apiKey := ""
	if reqPayload.Provider == "openai" {
		apiKey = os.Getenv("OPENAI_API_KEY")
		if apiKey == "" {
			writeJSONResponse(w, http.StatusInternalServerError, SadsGenerationResponse{Error: "OpenAI API key not configured on server"})
			return
		}
	} else if reqPayload.Provider == "mistral" {
		apiKey = os.Getenv("MISTRAL_API_KEY")
		if apiKey == "" {
			writeJSONResponse(w, http.StatusInternalServerError, SadsGenerationResponse{Error: "Mistral API key not configured on server"})
			return
		}
	} else {
		writeJSONResponse(w, http.StatusBadRequest, SadsGenerationResponse{Error: "Unsupported provider: " + reqPayload.Provider})
		return
	}

	// Construct the prompt for the LLM
	llmPrompt, err := constructLLMPrompt_Go(reqPayload.HTMLSnippet, reqPayload.StylePrompt, reqPayload.SadsThemeContextJSON)
	if err != nil {
		writeJSONResponse(w, http.StatusInternalServerError, SadsGenerationResponse{Error: "Failed to construct LLM prompt: " + err.Error()})
		return
	}

	// Call the LLM
	sadsAttributesString, err := getSadsAttributesFromLLM_Go(apiKey, reqPayload.Provider, reqPayload.Model, llmPrompt)
	if err != nil {
		writeJSONResponse(w, http.StatusInternalServerError, SadsGenerationResponse{Error: "Failed to get SADS attributes from LLM: " + err.Error()})
		return
	}
	if sadsAttributesString == "" { // LLM might return empty string on success but no attributes
		writeJSONResponse(w, http.StatusOK, SadsGenerationResponse{SadsAttributesString: "", ParsedSadsAttributes: map[string]map[string]string{}})
		return
	}

	// Parse the LLM's SADS attribute string into a structured map
	parsedSadsMap, err := parseLLMSadsStringToMap_Go(sadsAttributesString, reqPayload.SadsThemeContextJSON)
	if err != nil {
		// Log this error on the server, but still return the raw string if parsing fails,
		// as the LLM did provide a response. Client can decide how to handle parsing failure.
		fmt.Printf("Warning: Failed to parse LLM SADS string into map: %v. Raw string: %s\n", err, sadsAttributesString)
		// Optionally, include a warning in the response or just return the raw string
		writeJSONResponse(w, http.StatusOK, SadsGenerationResponse{
			SadsAttributesString: sadsAttributesString,
			Error:                "Partially successful: LLM responded, but server-side parsing of attributes failed: " + err.Error(),
		})
		return
	}

	// Ensure ParsedSadsAttributes is not nil even if empty
	// The parseLLMSadsStringToMap_Go should return {"attributes": map[...]}
	// So, cast parsedSadsMap["attributes"] to the correct type.
	var finalParsedAttributes map[string]map[string]string
	if attrs, ok := parsedSadsMap["attributes"].(map[string]map[string]string); ok {
		finalParsedAttributes = attrs
	} else if parsedSadsMap["attributes"] != nil { // It's map[string]interface{} or something else
        // Attempt a more careful conversion if needed, or log an issue.
        // For now, if it's not the exact type, we'll send nil or an empty map.
        // This indicates a mismatch between parser output and response struct type.
        // The parser should ideally always return map[string]map[string]string for the "attributes" value.
		fmt.Printf("Warning: parseLLMSadsStringToMap_Go['attributes'] was not of expected type map[string]map[string]string. Got: %T\n", parsedSadsMap["attributes"])
        finalParsedAttributes = make(map[string]map[string]string) // Default to empty
    } else {
		finalParsedAttributes = make(map[string]map[string]string) // Default to empty
	}


	response := SadsGenerationResponse{
		SadsAttributesString: sadsAttributesString,
		ParsedSadsAttributes: finalParsedAttributes,
	}
	writeJSONResponse(w, http.StatusOK, response)
}
