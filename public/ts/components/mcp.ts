// public/ts/components/mcp.ts
import { reapplySadsStyles } from "../modules/sadsManager.js";
import { MCPClient, McpEventHandler } from "../services/mcp_client.js";
import {
  Message,
  Performative,
  TaskRequestPayload,
  InformResultPayload,
} from "../../../generated/ts/mcp.js"; // Adjust if your generated files are elsewhere
import { Struct } from "../../../generated/ts/google/protobuf/struct.js"; // For Struct
import { mcpServerUrl } from "../config.js";

const MCP_COMPONENT_SELECTOR = '[data-sads-component="mcp"]';
const STYLE_PROMPT_SELECTOR = '[data-sads-element="mcp-style-prompt"]';
const GENERATE_BUTTON_SELECTOR = '[data-sads-element="mcp-generate-button"]';
const MESSAGE_AREA_SELECTOR = '[data-sads-element="mcp-message-area"]';
const TARGET_AREA_SELECTOR = '[data-sads-element="mcp-target-area"]';

const SADS_GENERATION_ONTOLOGY = "elizaos:sads:generate_attributes";
const SADS_GENERATOR_AGENT_ID = "sads_generator_agent"; // Server-side agent
const MCP_CLIENT_AGENT_ID = "sads_ui_mcp_client_" + Date.now(); // Basic unique ID

let mcpClient: MCPClient | null = null;
let sadsThemeContext: string | null = null;
// const pendingRequests: Map<string, (message: Message) => void> = new Map(); // Old way

interface ActiveSadsRequest {
  messageId: string;
  startTime: number;
  // Add any other contextual info needed for SADS requests if necessary
}
let activeRequests: ActiveSadsRequest[] = [];

async function fetchSadsThemeContext(): Promise<string> {
  if (sadsThemeContext) {
    return sadsThemeContext;
  }
  try {
    const response = await fetch("/public/sads_theme_context.json"); // Assuming step 5 will make this available
    if (!response.ok) {
      throw new Error(
        `Failed to fetch SADS theme context: ${response.statusText}`
      );
    }
    const context = await response.json();
    sadsThemeContext = JSON.stringify(context);
    return sadsThemeContext;
  } catch (error) {
    console.error("Error fetching SADS theme context:", error);
    throw error; // Propagate error to be handled by UI
  }
}

function applySadsAttributes(targetEl: HTMLElement, sadsAttributes: string) {
  // Clear existing sads attributes from the target element
  for (let i = targetEl.attributes.length - 1; i >= 0; i--) {
    const attr = targetEl.attributes[i];
    if (attr.name.startsWith("data-sads-")) {
      if (
        attr.name !== "data-sads-scope" &&
        attr.name !== "data-sads-component" &&
        attr.name !== "data-sads-element" &&
        attr.name !== "data-sads-id"
      ) {
        targetEl.removeAttribute(attr.name);
      }
    }
  }

  // Apply new SADS attributes
  const attributes = sadsAttributes.match(
    /data-sads-[^=]+=(?:'[^']*'|"[^"]*")/g
  );
  if (attributes) {
    attributes.forEach((attr) => {
      const parts = attr.match(/^([^=]+)=(.*)$/);
      if (parts && parts.length === 3) {
        const name = parts[1];
        let value = parts[2];
        if (
          (value.startsWith("'") && value.endsWith("'")) ||
          (value.startsWith('"') && value.endsWith('"'))
        ) {
          value = value.substring(1, value.length - 1);
        }
        targetEl.setAttribute(name, value);
      }
    });
  }
}

/**
 * Initializes the MCP component, setting up event listeners and MCPClient.
 */
export function initMcpComponent(): void {
  const mcpComponent = document.querySelector<HTMLElement>(
    MCP_COMPONENT_SELECTOR
  );
  if (!mcpComponent) return;

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
    console.error("MCP component missing critical elements.");
    if (messageAreaEl) {
      messageAreaEl.textContent =
        "Error: Component elements missing. Cannot initialize.";
      messageAreaEl.setAttribute("data-sads-text-color", "text-negative");
    }
    return;
  }

  // Initialize MCPClient
  mcpClient = new MCPClient(MCP_CLIENT_AGENT_ID, mcpServerUrl);
  const mcpEventHandler: McpEventHandler = {
    onOpen: () => {
      console.log("MCP Connection Opened for SADS component.");
      messageAreaEl.textContent = "MCP connected. Ready for SADS generation.";
      messageAreaEl.setAttribute("data-sads-text-color", "text-neutral");
      reapplySadsStyles();
    },
    onMessage: (message: Message) => {
      console.log("MCP Message Received in SADS component:", message);
      const requestIndex = activeRequests.findIndex(
        (req) => req.messageId === message.inReplyTo
      );

      if (
        requestIndex === -1 &&
        message.performative !== Performative.TASK_ACCEPT
      ) {
        // TASK_ACCEPT might arrive before the request is fully tracked or if multiple accepts are sent.
        // Or it could be a message not related to a pending request.
        console.warn(
          "Received message for an unknown or already handled request:",
          message
        );
        return;
      }

      const matchingRequest =
        requestIndex !== -1 ? activeRequests[requestIndex] : undefined;

      try {
        switch (message.performative) {
          case Performative.TASK_ACCEPT:
            if (message.payload.oneofKind === "taskAcceptPayload") {
              const acceptPayload = message.payload.taskAcceptPayload;
              messageAreaEl.textContent = `Agent ${message.sender?.agentId} accepted SADS generation task. ${acceptPayload.comments || ""}`;
              messageAreaEl.setAttribute(
                "data-sads-text-color",
                "text-neutral"
              );
            }
            // Do not remove from activeRequests here, wait for INFORM_RESULT or FAILURE
            break;

          case Performative.INFORM_RESULT:
            if (message.payload.oneofKind === "informResultPayload") {
              const informPayload = message.payload.informResultPayload;
              const resultDetails = informPayload.resultDetails
                ? Struct.toJson(informPayload.resultDetails)
                : {};

              // @ts-ignore Struct.toJson returns any
              const sadsAttributes =
                resultDetails?.sads_attributes_string as string;
              // @ts-ignore
              const error = resultDetails?.error as string;

              if (error) {
                throw new Error(error);
              }

              if (sadsAttributes) {
                applySadsAttributes(targetAreaEl, sadsAttributes);
                messageAreaEl.textContent =
                  "SADS attributes applied successfully via MCP!";
                messageAreaEl.setAttribute(
                  "data-sads-text-color",
                  "text-positive"
                );
              } else {
                messageAreaEl.textContent =
                  "Received empty SADS attributes via MCP.";
                messageAreaEl.setAttribute(
                  "data-sads-text-color",
                  "text-warning"
                );
              }
              if (matchingRequest) activeRequests.splice(requestIndex, 1);
            } else {
              throw new Error(
                "INFORM_RESULT received without InformResultPayload"
              );
            }
            break;

          case Performative.FAILURE:
          case Performative.TASK_REJECT:
            let errorMsg = "SADS generation failed or was rejected by agent.";
            if (message.payload.oneofKind === "failurePayload") {
              errorMsg = `SADS Generation Error (Agent Failure ${message.sender?.agentId || "Unknown"}): ${message.payload.failurePayload.errorText || "No details."}`;
            } else if (message.payload.oneofKind === "taskRejectPayload") {
              errorMsg = `SADS Generation Task Rejected (Agent ${message.sender?.agentId || "Unknown"}): ${message.payload.taskRejectPayload.reasonText || "No reason given."}`;
            }
            throw new Error(errorMsg);

          default:
            console.warn(
              `Received unexpected performative: ${Performative[message.performative]} from ${message.sender?.agentId}`
            );
            // Optionally keep the request in activeRequests or remove it based on policy for unhandled performatives
            return; // Don't proceed to common finally block for UI if it's not a final state for this request
        }
      } catch (err) {
        console.error("Error processing SADS response from MCP:", err);
        messageAreaEl.textContent = `Error: ${(err as Error).message}`;
        messageAreaEl.setAttribute("data-sads-text-color", "text-negative");
        if (matchingRequest) activeRequests.splice(requestIndex, 1);
      } finally {
        // Only re-enable button if the request is no longer active (i.e., it was a final response)
        const stillActive = activeRequests.some(
          (req) => req.messageId === matchingRequest?.messageId
        );
        if (
          !stillActive &&
          (message.performative === Performative.INFORM_RESULT ||
            message.performative === Performative.FAILURE ||
            message.performative === Performative.TASK_REJECT)
        ) {
          generateButtonEl.disabled = false;
          generateButtonEl.removeAttribute("data-sads-opacity");
        }
        reapplySadsStyles();
      }
    },
    onError: (event) => {
      console.error("MCP Connection Error in SADS component:", event);
      messageAreaEl.textContent = "MCP Connection Error. Please refresh.";
      messageAreaEl.setAttribute("data-sads-text-color", "text-negative");
      reapplySadsStyles();
    },
    onClose: () => {
      console.log("MCP Connection Closed for SADS component.");
      messageAreaEl.textContent = "MCP Connection Closed.";
      messageAreaEl.setAttribute("data-sads-text-color", "text-warning"); // Or neutral
      reapplySadsStyles();
    },
  };

  if (messageAreaEl) {
    // Initial message before connect() is called
    messageAreaEl.textContent =
      "MCP component initializing. Attempting to connect...";
    messageAreaEl.setAttribute("data-sads-text-color", "text-neutral");
    Promise.resolve().then(reapplySadsStyles);
  }
  mcpClient.connect(mcpEventHandler);

  generateButtonEl.addEventListener("click", async () => {
    if (!mcpClient) {
      messageAreaEl.textContent = "MCP client not initialized.";
      messageAreaEl.setAttribute("data-sads-text-color", "text-negative");
      await reapplySadsStyles();
      return;
    }

    const stylePrompt = stylePromptEl.value.trim();
    if (!stylePrompt) {
      messageAreaEl.textContent = "Please enter a style prompt.";
      messageAreaEl.setAttribute("data-sads-text-color", "text-warning");
      await reapplySadsStyles();
      return;
    }

    const htmlSnippet = targetAreaEl.innerHTML;
    let currentThemeContext: string;
    try {
      currentThemeContext = await fetchSadsThemeContext();
    } catch (error) {
      messageAreaEl.textContent = `Error: ${(error as Error).message}`;
      messageAreaEl.setAttribute("data-sads-text-color", "text-negative");
      await reapplySadsStyles();
      return;
    }

    messageAreaEl.textContent = "Requesting SADS generation via MCP...";
    messageAreaEl.setAttribute("data-sads-text-color", "text-neutral");
    generateButtonEl.disabled = true;
    generateButtonEl.setAttribute("data-sads-opacity", "custom:0.5");
    await reapplySadsStyles();

    const taskParameters = Struct.fromJson({
      html_snippet: htmlSnippet,
      style_prompt: stylePrompt,
      sads_theme_context_json: currentThemeContext,
      provider: "openai", // Hardcoded for now
      model: "gpt-3.5-turbo", // Hardcoded for now
    });

    const taskRequestPayload: TaskRequestPayload = {
      taskType: SADS_GENERATION_ONTOLOGY, // Using ontology as task_type for routing
      taskDescription: "Generate SADS attributes based on HTML and prompt",
      taskParameters: taskParameters,
      priority: "medium",
    };

    const messageId = mcpClient.sendMessage(
      Performative.TASK_REQUEST,
      SADS_GENERATOR_AGENT_ID,
      taskRequestPayload,
      SADS_GENERATION_ONTOLOGY
    );

    // Add to active requests
    activeRequests.push({ messageId, startTime: Date.now() });
    // The actual response handling logic will be moved to onMessage in the next step.
    // For now, the old pendingRequests.set logic is effectively orphaned and will be removed.

    // Timeout for the request - will be adapted in the next step to work with activeRequests
    setTimeout(() => {
      const requestIndex = activeRequests.findIndex(
        (req) => req.messageId === messageId
      );
      if (requestIndex !== -1) {
        activeRequests.splice(requestIndex, 1); // Remove from active requests
        messageAreaEl.textContent = "SADS generation request timed out.";
        messageAreaEl.setAttribute("data-sads-text-color", "text-warning");
        generateButtonEl.disabled = false;
        generateButtonEl.removeAttribute("data-sads-opacity");
        reapplySadsStyles();
        console.log(
          `Request ${messageId} timed out and removed from activeRequests.`
        );
      }
    }, 30000); // 30-second timeout
  });

  if (messageAreaEl) {
    messageAreaEl.textContent =
      "MCP component ready. Enter style prompt and click generate.";
    messageAreaEl.setAttribute("data-sads-text-color", "text-neutral");
    Promise.resolve().then(reapplySadsStyles);
  }
}
