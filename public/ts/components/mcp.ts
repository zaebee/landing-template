// public/ts/components/mcp.ts
import { reapplySadsStyles } from "../modules/sadsManager.js";

const MCP_COMPONENT_SELECTOR = '[data-sads-component="mcp"]';
const STYLE_PROMPT_SELECTOR = '[data-sads-element="mcp-style-prompt"]';
const GENERATE_BUTTON_SELECTOR = '[data-sads-element="mcp-generate-button"]';
const MESSAGE_AREA_SELECTOR = '[data-sads-element="mcp-message-area"]';
const TARGET_AREA_SELECTOR = '[data-sads-element="mcp-target-area"]'; // This is the element to get HTML from and apply styles to.

interface AiSadsRequest {
  html_snippet: string;
  style_prompt: string;
  // Potentially add theme_context if the API requires it and it can be sourced from frontend
}

interface AiSadsResponse {
  sads_attributes: string; // e.g., "data-sads-bgColor='primary' data-sads-padding='m'"
  error?: string;
}

/**
 * Initializes the MCP component, setting up event listeners.
 */
export function initMcpComponent(): void {
  const mcpComponent = document.querySelector<HTMLElement>(
    MCP_COMPONENT_SELECTOR
  );
  if (!mcpComponent) {
    // console.warn("MCP component not found on this page.");
    return;
  }

  const stylePromptEl = mcpComponent.querySelector<HTMLTextAreaElement>(
    STYLE_PROMPT_SELECTOR
  );
  const generateButtonEl = mcpComponent.querySelector<HTMLButtonElement>(
    GENERATE_BUTTON_SELECTOR
  );
  const messageAreaEl = mcpComponent.querySelector<HTMLElement>(
    MESSAGE_AREA_SELECTOR
  );
  const targetAreaEl =
    mcpComponent.querySelector<HTMLElement>(TARGET_AREA_SELECTOR);

  if (!stylePromptEl || !generateButtonEl || !messageAreaEl || !targetAreaEl) {
    console.error(
      "MCP component is missing one or more critical elements. Aborting initialization.",
      {
        stylePromptEl,
        generateButtonEl,
        messageAreaEl,
        targetAreaEl,
      }
    );
    if (messageAreaEl) {
      messageAreaEl.textContent =
        "Error: Component elements missing. Cannot initialize.";
      messageAreaEl.setAttribute("data-sads-text-color", "text-negative");
    }
    return;
  }

  generateButtonEl.addEventListener("click", async () => {
    const stylePrompt = stylePromptEl.value.trim();
    if (!stylePrompt) {
      messageAreaEl.textContent = "Please enter a style prompt.";
      messageAreaEl.setAttribute("data-sads-text-color", "text-warning");
      await reapplySadsStyles(); // To apply warning color
      return;
    }

    // Get the inner HTML of the target area to send to the AI
    // Or, we can send a predefined snippet if the AI is meant to style a generic structure
    // For this iteration, let's send the current content of the target area.
    const htmlSnippet = targetAreaEl.innerHTML;

    messageAreaEl.textContent = "Generating styles...";
    messageAreaEl.setAttribute("data-sads-text-color", "text-neutral");
    generateButtonEl.disabled = true;
    generateButtonEl.setAttribute("data-sads-opacity", "custom:0.5");
    await reapplySadsStyles();

    try {
      const requestPayload: AiSadsRequest = {
        html_snippet: htmlSnippet,
        style_prompt: stylePrompt,
      };

      // Log the request being sent
      // console.log("Sending request to AI SADS PoC:", JSON.stringify(requestPayload, null, 2));

      const response = await fetch("/api/generate-sads-attributes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestPayload),
      });

      if (!response.ok) {
        let errorMsg = `Error: ${response.status} ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMsg = errorData.error || errorData.message || errorMsg;
        } catch (e) {
          // Ignore if error response is not JSON
        }
        throw new Error(errorMsg);
      }

      const result = (await response.json()) as AiSadsResponse;
      // console.log("Received response from AI SADS PoC:", JSON.stringify(result, null, 2));

      if (result.error) {
        throw new Error(result.error);
      }

      if (result.sads_attributes) {
        // Clear existing sads attributes from the target element
        for (let i = targetAreaEl.attributes.length - 1; i >= 0; i--) {
          const attr = targetAreaEl.attributes[i];
          if (attr.name.startsWith("data-sads-")) {
            // Keep scope and component/element defining attributes
            if (
              attr.name !== "data-sads-scope" &&
              attr.name !== "data-sads-component" &&
              attr.name !== "data-sads-element" &&
              attr.name !== "data-sads-id"
            ) {
              targetAreaEl.removeAttribute(attr.name);
            }
          }
        }

        // Apply new SADS attributes. The attribute string is space-separated: "data-sads-foo='bar' data-sads-baz='qux'"
        const attributes = result.sads_attributes.match(
          /data-sads-[^=]+=(?:'[^']*'|"[^"]*")/g
        );
        if (attributes) {
          attributes.forEach((attr) => {
            const parts = attr.match(/^([^=]+)=(.*)$/);
            if (parts && parts.length === 3) {
              const name = parts[1];
              let value = parts[2];
              // Remove quotes from value
              if (
                (value.startsWith("'") && value.endsWith("'")) ||
                (value.startsWith('"') && value.endsWith('"'))
              ) {
                value = value.substring(1, value.length - 1);
              }
              targetAreaEl.setAttribute(name, value);
            }
          });
        }

        messageAreaEl.textContent = "Styles applied successfully!";
        messageAreaEl.setAttribute("data-sads-text-color", "text-positive");
      } else {
        messageAreaEl.textContent =
          "Received empty attributes. No changes applied.";
        messageAreaEl.setAttribute("data-sads-text-color", "text-warning");
      }
    } catch (error) {
      console.error("Error generating SADS attributes:", error);
      messageAreaEl.textContent = `Error: ${error instanceof Error ? error.message : String(error)}`;
      messageAreaEl.setAttribute("data-sads-text-color", "text-negative");
    } finally {
      generateButtonEl.disabled = false;
      generateButtonEl.removeAttribute("data-sads-opacity");
      await reapplySadsStyles(); // Crucial to apply new SADS attributes or clear opacity/colors
    }
  });

  // console.log("MCP Component Initialized");
  if (messageAreaEl) {
    messageAreaEl.textContent =
      "MCP component ready. Enter a style prompt and click generate.";
    messageAreaEl.setAttribute("data-sads-text-color", "text-neutral");
    // Initial reapply is good practice if attributes were set in HTML for the message area
    Promise.resolve().then(reapplySadsStyles);
  }
}

// Self-initialize if this script is loaded directly and the component exists.
// However, a more robust approach is to call initMcpComponent from app.ts after DOMContentLoaded.
// For now, let's assume app.ts will handle calling this.
// if (document.readyState === "loading") {
//   document.addEventListener("DOMContentLoaded", initMcpComponent);
// } else {
//   initMcpComponent();
// }
