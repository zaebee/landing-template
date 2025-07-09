// public/ts/components/ide_agent_panel.ts
import { MCPClient, McpEventHandler } from "../services/mcp_client.js";
import {
  Message,
  Performative,
  TaskRequestPayload,
  InformResultPayload,
  IdeCodeExplanationRequest,
  IdeRefactorSuggestionRequest,
  Identifier,
  TaskStatus,
  IdeCodeExplanationResponse,
  IdeRefactorSuggestionResponse,
} from "../../../generated/ts/mcp.js"; // Adjust path as necessary
import { Struct } from "../../../generated/ts/google/protobuf/struct.js";
import { Timestamp } from "../../../generated/ts/google/protobuf/timestamp.js";
// import { قيمة } from "@protobuf-ts/runtime"; // Removed problematic import. Use message.payload.oneofKind directly.
import {
  mcpServerUrl,
  clientAgentIdPrefix,
  defaultTargetAgentId,
} from "../config.js";

interface ActiveRequest {
  messageId: string;
  ontology: string;
  description: string; // For UI feedback
}

export function initIdeAgentPanel(): void {
  const panel = document.querySelector<HTMLElement>(
    '[data-sads-component="ide-agent-panel"]'
  );
  if (!panel) {
    // console.log("IDE Agent Panel component not found on this page.");
    return;
  }

  const statusArea = panel.querySelector<HTMLElement>(
    '[data-sads-element="status-area"]'
  );
  const agentIdInput = panel.querySelector<HTMLInputElement>(
    '[data-sads-element="agent-id-input"]'
  );
  const codeSnippetInput = panel.querySelector<HTMLTextAreaElement>(
    '[data-sads-element="code-snippet-input"]'
  );
  const userQueryInput = panel.querySelector<HTMLInputElement>(
    '[data-sads-element="user-query-input"]'
  );

  if (agentIdInput) {
    agentIdInput.value = defaultTargetAgentId; // Set default from config
  }
  const explainCodeButton = panel.querySelector<HTMLButtonElement>(
    '[data-sads-element="explain-code-button"]'
  );
  const refactorCodeButton = panel.querySelector<HTMLButtonElement>(
    '[data-sads-element="refactor-code-button"]'
  );
  const responseArea = panel.querySelector<HTMLElement>(
    '[data-sads-element="response-area"]'
  );

  // New elements for Generate SADS from NL
  const genSadsHtmlSnippetInput = panel.querySelector<HTMLTextAreaElement>(
    '[data-sads-element="gen-sads-html-snippet-input"]'
  );
  const genSadsStylePromptInput = panel.querySelector<HTMLInputElement>(
    '[data-sads-element="gen-sads-style-prompt-input"]'
  );
  const genSadsThemeContextInput = panel.querySelector<HTMLTextAreaElement>(
    '[data-sads-element="gen-sads-theme-context-input"]'
  );
  const genSadsProviderInput = panel.querySelector<HTMLInputElement>(
    '[data-sads-element="gen-sads-provider-input"]'
  );
  const genSadsModelInput = panel.querySelector<HTMLInputElement>(
    '[data-sads-element="gen-sads-model-input"]'
  );
  const generateSadsButton = panel.querySelector<HTMLButtonElement>(
    '[data-sads-element="generate-sads-button"]'
  );

  if (
    !statusArea ||
    !agentIdInput ||
    !codeSnippetInput ||
    !userQueryInput ||
    !explainCodeButton ||
    !refactorCodeButton ||
    !responseArea ||
    // Check new elements for SADS NL
    !genSadsHtmlSnippetInput ||
    !genSadsStylePromptInput ||
    !genSadsThemeContextInput ||
    !genSadsProviderInput ||
    !genSadsModelInput ||
    !generateSadsButton
  ) {
    console.error(
      "IDE Agent Panel is missing one or more critical elements (standard or SADS NL)."
    );
    if (statusArea)
      statusArea.textContent =
        "Error: Panel elements missing (standard or SADS NL).";
    return;
  }

  // Set default values for SADS NL provider and model if elements exist
  if (genSadsProviderInput) genSadsProviderInput.value = "openai";
  if (genSadsModelInput) genSadsModelInput.value = "gpt-3.5-turbo";


  // Generate a unique client agent ID for this session/panel instance
  const clientAgentId = `${clientAgentIdPrefix}${Math.random().toString(36).substring(2, 9)}`;
  // Pass only clientAgentId to constructor, serverUrl is picked from config by MCPClient itself
  const mcpClient = new MCPClient(
    clientAgentId,
    `${mcpServerUrl}?agentId=${clientAgentId}`
  );

  let activeRequests: ActiveRequest[] = [];

  const updateStatus = (text: string, isError: boolean = false) => {
    if (statusArea) {
      statusArea.textContent = text;
      statusArea.setAttribute(
        "data-sads-text-color",
        isError ? "text-negative" : "text-secondary"
      );
      // TODO: Reapply SADS if colors change dynamically (import reapplySadsStyles)
    }
  };

  const displayResponse = (text: string) => {
    if (responseArea) {
      responseArea.textContent = text;
    }
  };

  const appendResponse = (text: string) => {
    if (responseArea) {
      responseArea.textContent += "\n" + text;
    }
  };

  const mcpEventHandler: McpEventHandler = {
    onOpen: () => {
      // Corrected: Removed invalid underscore parameter
      updateStatus(`Connected to MCP Server as ${clientAgentId}. Ready.`); // Corrected: Added backticks
    },
    onMessage: (message: Message) => {
      console.log("IDE Panel: Received MCP Message:", message);
      const matchingRequest = activeRequests.find(
        (req) => req.messageId === message.inReplyTo
      );

      if (message.performative === Performative.TASK_ACCEPT) {
        if (message.payload.oneofKind === "taskAcceptPayload") {
          const acceptPayload = message.payload.taskAcceptPayload;
          updateStatus(
            `Agent ${message.sender?.agentId} accepted task: ${matchingRequest?.description || message.inReplyTo}. ${acceptPayload.comments}`
          );
        }
      } else if (message.performative === Performative.INFORM_RESULT) {
        if (message.payload.oneofKind === "informResultPayload") {
          const informPayload = message.payload.informResultPayload;
          let responseText = `Result from ${message.sender?.agentId} for task ${matchingRequest?.description || message.inReplyTo}:\n`;
          responseText += `Status: ${TaskStatus[informPayload.taskStatus]}\nSummary: ${informPayload.resultSummary}\n`;

          if (informPayload.resultDetails) {
            const details = Struct.toJson(informPayload.resultDetails); // Convert Struct to JS object
            responseText += "Details:\n" + JSON.stringify(details, null, 2);

            // Try to parse specific IDE responses
            // Type guard for JsonObject
            if (
              typeof details === "object" &&
              details !== null &&
              !Array.isArray(details)
            ) {
              if (
                matchingRequest?.ontology === "elizaos:ide:explain_code" &&
                "ide_code_explanation_response" in details
              ) {
                const explRespFromDetails =
                  details.ide_code_explanation_response;
                if (
                  typeof explRespFromDetails === "object" &&
                  explRespFromDetails !== null &&
                  "explanation_text" in explRespFromDetails
                ) {
                  responseText = `Explanation from ${message.sender?.agentId}:\n${(explRespFromDetails as any).explanation_text}`;
                }
              } else if (
                matchingRequest?.ontology ===
                  "elizaos:ide:refactor_suggestion" &&
                "ide_refactor_suggestion_response" in details
              ) {
                const refactorRespFromDetails =
                  details.ide_refactor_suggestion_response;
                if (
                  typeof refactorRespFromDetails === "object" &&
                  refactorRespFromDetails !== null
                ) {
                  const refactorResp = refactorRespFromDetails as any;
                  responseText = `Refactor suggestions from ${message.sender?.agentId}:\nOriginal: ${refactorResp.original_snippet}\n`;
                  if (Array.isArray(refactorResp.suggestions)) {
                    refactorResp.suggestions.forEach((sug: any) => {
                      responseText += `  - ${sug.description} (Type: ${sug.change_type}, Confidence: ${sug.confidence})\n    Diff: ${sug.suggested_code_diff}\n`;
                    });
                  }
                }
              } else if (matchingRequest?.ontology === "elizaos:lpg:generate_sads_from_nl") {
                // Specific handling for SADS NL response
                if (typeof details === "object" && details !== null) {
                  const sadsResult = details as any; // Cast for easier access
                  responseText = `SADS Generation Result from ${message.sender?.agentId}:\n`;
                  if (sadsResult.sads_attributes_string) {
                    responseText += `SADS Attributes String:\n${sadsResult.sads_attributes_string}\n\n`;
                  }
                  if (sadsResult.parsed_sads_attributes) {
                    responseText += `Parsed SADS Attributes:\n${JSON.stringify(sadsResult.parsed_sads_attributes, null, 2)}\n`;
                  }
                  if (sadsResult.error) { // If the API itself reported an error in its valid JSON response
                     responseText += `\nAPI Error: ${sadsResult.error}\n`;
                  }
                }
              }
            }
          }
          displayResponse(responseText);
          activeRequests = activeRequests.filter(
            (req) => req.messageId !== message.inReplyTo
          );
        }
      } else if (message.performative === Performative.TASK_REJECT) {
        if (message.payload.oneofKind === "taskRejectPayload") {
          const rejectPayload = message.payload.taskRejectPayload;
          displayResponse(
            `Task rejected by ${message.sender?.agentId}: ${rejectPayload.reasonText} (Code: ${rejectPayload.reasonCode})`
          );
          updateStatus(`Task rejected by ${message.sender?.agentId}.`, true);
          activeRequests = activeRequests.filter(
            (req) => req.messageId !== message.inReplyTo
          );
        }
      } else if (message.performative === Performative.FAILURE) {
        if (message.payload.oneofKind === "failurePayload") {
          const failurePayload = message.payload.failurePayload;
          displayResponse(
            `Agent ${message.sender?.agentId} reported failure: ${failurePayload.errorText} (Code: ${failurePayload.errorCode})`
          );
          updateStatus(
            `Agent failure for task ${matchingRequest?.description}.`,
            true
          );
          activeRequests = activeRequests.filter(
            (req) => req.messageId !== message.inReplyTo
          );
        }
      } else {
        appendResponse(
          `Received ${Performative[message.performative]} from ${message.sender?.agentId}.`
        );
      }
    },
    onError: (event) => {
      console.error("IDE Panel: MCP Connection Error", event);
      updateStatus("Error: Connection to MCP Server failed.", true);
    },
    onClose: () => {
      updateStatus("Disconnected from MCP Server.");
    },
  };

  mcpClient.connect(mcpEventHandler);

  const handleRequest = (
    ontology: string,
    description: string,
    createPayloadSpecifics: () => Record<string, any>
  ) => {
    const targetAgent = agentIdInput.value.trim();
    const codeSnippet = codeSnippetInput.value;
    const userQuery = userQueryInput.value.trim();

    if (!targetAgent) {
      alert("Please enter a target agent ID.");
      return;
    }
    if (
      !codeSnippet &&
      (ontology === "elizaos:ide:explain_code" ||
        ontology === "elizaos:ide:refactor_suggestion")
    ) {
      alert("Please enter a code snippet for this action.");
      return;
    }
    if (!userQuery && ontology === "elizaos:ide:explain_code") {
      // Query is important for explanation
      alert("Please enter a query for explanation.");
      return;
    }

    const taskSpecificParams = createPayloadSpecifics();

    const taskParameters = Struct.fromJson(taskSpecificParams);

    const requestPayload: TaskRequestPayload = {
      taskType: ontology, // Or a more specific task_type string if ontology is broader
      taskDescription: description + (userQuery ? ` (${userQuery})` : ""),
      taskParameters: taskParameters,
      priority: "medium",
    };

    try {
      const messageId = mcpClient.sendMessage(
        Performative.TASK_REQUEST,
        targetAgent,
        requestPayload,
        ontology // The ontology here often matches taskType or is more general
      );
      activeRequests.push({ messageId, ontology, description });
      updateStatus(
        `Sent '${description}' request to ${targetAgent}. Waiting for acceptance...`
      );
      displayResponse(
        `Sent '${description}' request (ID: ${messageId}) to agent '${targetAgent}'. Waiting for response...`
      );
    } catch (e) {
      updateStatus(`Error sending request: ${(e as Error).message}`, true);
      console.error("Error sending request:", e);
    }
  };

  explainCodeButton.addEventListener("click", () => {
    const codeSnippet = codeSnippetInput.value;
    const userQuery = userQueryInput.value.trim() || "Explain this code.";
    const language = "unknown"; // TODO: Add language detection or input

    handleRequest("elizaos:ide:explain_code", "Code Explanation", () => {
      const idePayload: IdeCodeExplanationRequest = {
        codeSnippet: codeSnippet,
        language: language,
        userQuery: userQuery,
      };
      // Convert the typed object to a plain JS object for Struct.fromJson
      return IdeCodeExplanationRequest.toJson(idePayload) as Record<
        string,
        any
      >;
    });
  });

  refactorCodeButton.addEventListener("click", () => {
    const codeSnippet = codeSnippetInput.value;
    const userQuery =
      userQueryInput.value.trim() || "Suggest refactorings for this code.";
    const language = "unknown"; // TODO: Add language detection or input

    handleRequest(
      "elizaos:ide:refactor_suggestion",
      "Refactor Suggestion",
      () => {
        const idePayload: IdeRefactorSuggestionRequest = {
          codeSnippet: codeSnippet,
          language: language,
          userQuery: userQuery,
        };
        return IdeRefactorSuggestionRequest.toJson(idePayload) as Record<
          string,
          any
        >;
      }
    );
  });

  generateSadsButton.addEventListener("click", () => {
    const htmlSnippet = genSadsHtmlSnippetInput.value;
    const stylePrompt = genSadsStylePromptInput.value;
    const sadsThemeContextJson = genSadsThemeContextInput.value;
    const provider = genSadsProviderInput.value;
    const model = genSadsModelInput.value;

    if (!htmlSnippet.trim()) {
      alert("Please enter an HTML snippet.");
      return;
    }
    if (!stylePrompt.trim()) {
      alert("Please enter a style prompt.");
      return;
    }
    if (!sadsThemeContextJson.trim()) {
      alert("Please enter SADS Theme Context JSON.");
      // You could also try to parse it here to validate JSON
      return;
    }
     if (!provider.trim()) {
      alert("Please enter a provider (e.g., openai).");
      return;
    }
     if (!model.trim()) {
      alert("Please enter a model (e.g., gpt-3.5-turbo).");
      return;
    }

    handleRequest(
      "elizaos:lpg:generate_sads_from_nl",
      "Generate SADS from NL",
      () => {
        // This structure must match what the Go API handler (GenerateSadsRequest)
        // and the MCP service (simulateAgentProcessing) expect.
        return {
          html_snippet: htmlSnippet,
          style_prompt: stylePrompt,
          sads_theme_context_json: sadsThemeContextJson,
          provider: provider,
          model: model,
        };
      }
    );
  });

  updateStatus("Panel initialized. Waiting for connection...");
  console.log("IDE Agent Panel Initialized. Client Agent ID:", clientAgentId);
}

// Assuming app.ts will call initIdeAgentPanel() after DOMContentLoaded
// For SADS styles to apply, ensure reapplySadsStyles() is called after dynamic content changes if needed.
// This might require importing `reapplySadsStyles` from `../modules/sadsManager.js`
// and calling it in `updateStatus` or `displayResponse` if they change SADS attributes.
// For now, existing SADS attributes on elements should be picked up on initial load.

// Path alias note:
// Imports like `../../../generated/ts/mcp` are relative.
// If tsconfig.json has path aliases like `"@generated/*": ["generated/ts/*"]`,
// then imports would be `import { Message } from '@generated/mcp';`
// And `../../../generated/ts/google/protobuf/struct` would be `@generated/google/protobuf/struct`.
// This requires `baseUrl` to be set in tsconfig.json (e.g. "public/ts" or "."),
// and the `paths` correctly mapping.
// For current setup, relative paths are used.
