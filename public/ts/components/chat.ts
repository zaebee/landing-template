// public/ts/components/chat.ts
import { MCPClient, McpEventHandler } from "../services/mcp_client.js";
import {
  Message,
  Performative,
  TaskRequestPayload,
  InformResultPayload,
  ChatMessage, // Will be generated from proto
} from "../../../generated/ts/mcp.js";
import { Struct } from "../../../generated/ts/google/protobuf/struct.js";
import { Timestamp } from "../../../generated/ts/google/protobuf/timestamp.js";
import { mcpServerUrl } from "../config.js";
import { reapplySadsStyles } from "../modules/sadsManager.js";

const CHAT_COMPONENT_SELECTOR = '[data-sads-component="chat"]';
const CHAT_MESSAGES_SELECTOR = '[data-sads-element="messages"]'; // Will add id="chat-messages-list"
const CHAT_INPUT_SELECTOR = '[data-sads-element="input"]'; // Will add id="chat-message-input"
const CHAT_FORM_SELECTOR = '[data-sads-element="input-form"]'; // Will add id="chat-form"
const CHAT_SEND_BTN_SELECTOR = '[data-sads-element="send-btn"]'; // Will add id="chat-send-button"

const CHAT_HANDLER_AGENT_ID = "chat_service"; // Agent ID on the server that handles chat broadcasts
const CHAT_MESSAGE_TASK_TYPE = "elizaos:chat:message";
const CHAT_BROADCAST_ONTOLOGY = "elizaos:chat:message_broadcast";

let mcpClient: MCPClient | null = null;
let chatMessagesEl: HTMLElement | null = null;
let chatInputEl: HTMLInputElement | null = null;
let chatFormEl: HTMLFormElement | null = null;

// Generate a simple unique ID for this chat client
const clientAgentId = "chat_client_" + Date.now() + "_" + Math.random().toString(36).substring(2, 7);
let currentUserName = `User_${Math.random().toString(36).substring(2, 7)}`; // Simple random user name

function displayMessage(chatMessage: ChatMessage): void {
  if (!chatMessagesEl) return;

  const messageDiv = document.createElement("div");
  messageDiv.setAttribute("data-sads-element", "message");
  messageDiv.setAttribute("data-sads-padding", "s");
  messageDiv.setAttribute("data-sads-margin-bottom", "s");

  // Basic styling differentiation for own messages vs others - can be enhanced
  if (chatMessage.userId === clientAgentId) {
    messageDiv.setAttribute("data-sads-bg-color", "surface-accent"); // Example: own messages have a different bg
    messageDiv.setAttribute("data-sads-border-radius", "s");
    messageDiv.setAttribute("data-sads-align-self", "flex-end"); // Align own messages to the right
     messageDiv.style.marginLeft = "auto"; // Basic right alignment
  } else {
    messageDiv.style.marginRight = "auto"; // Basic left alignment for others
  }


  const senderSpan = document.createElement("span");
  senderSpan.setAttribute("data-sads-font-weight", "bold");
  senderSpan.textContent = `${chatMessage.userName || chatMessage.userId}: `;

  const textNode = document.createTextNode(chatMessage.text);

  messageDiv.appendChild(senderSpan);
  messageDiv.appendChild(textNode);

  chatMessagesEl.appendChild(messageDiv);
  chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight; // Scroll to bottom

  // Important: Reapply SADS styles if new SADS attributes were added dynamically
  // or if the structure significantly changed affecting SADS.
  // For simple text appends, might not be strictly needed unless new SADS attributes are on messageDiv
  reapplySadsStyles(); // Apply styles globally
}

async function handleSendMessage(event: Event): Promise<void> {
  event.preventDefault();
  if (!mcpClient || !chatInputEl || !chatInputEl.value.trim()) {
    console.warn("MCP client not ready or input is empty.");
    return;
  }

  const messageText = chatInputEl.value.trim();

  const chatMessageProto: ChatMessage = {
    userId: clientAgentId,
    userName: currentUserName, // Store and allow changing this later
    text: messageText,
    timestamp: Timestamp.now(),
  };

  // We need to pack ChatMessage into a google.protobuf.Struct
  // The Go backend expects fields directly in task_parameters
  const taskParameters = Struct.fromJson({
    user_id: chatMessageProto.userId,
    user_name: chatMessageProto.userName,
    text: chatMessageProto.text,
    // Ensure timestamp is not undefined. Timestamp.now() should guarantee this.
    // If Timestamp.toJson itself can't handle a direct Timestamp object, this might need conversion.
    // However, the error was about chatMessageProto.timestamp being potentially undefined.
    timestamp: Timestamp.toJson(chatMessageProto.timestamp!), // Added non-null assertion as Timestamp.now() should provide a value
  });

  const taskRequestPayload: TaskRequestPayload = {
    taskType: CHAT_MESSAGE_TASK_TYPE,
    taskDescription: "User sending a chat message",
    taskParameters: taskParameters,
    priority: "medium",
  };

  mcpClient.sendMessage(
    Performative.TASK_REQUEST,
    CHAT_HANDLER_AGENT_ID, // Server-side agent responsible for chat
    taskRequestPayload,
    CHAT_MESSAGE_TASK_TYPE // Using task_type as ontology for this request
  );

  chatInputEl.value = ""; // Clear input field
}

export function initChatComponent(): void {
  const chatComponent = document.querySelector<HTMLElement>(CHAT_COMPONENT_SELECTOR);
  if (!chatComponent) {
    // console.log("Chat component not found on this page.");
    return;
  }

  // Assign IDs to elements for easier selection if not already present
  // This is a bit of a workaround; ideally templates have stable IDs.
  chatMessagesEl = chatComponent.querySelector<HTMLElement>(CHAT_MESSAGES_SELECTOR);
  if (chatMessagesEl && !chatMessagesEl.id) chatMessagesEl.id = "chat-messages-list";

  chatInputEl = chatComponent.querySelector<HTMLInputElement>(CHAT_INPUT_SELECTOR);
  if (chatInputEl && !chatInputEl.id) chatInputEl.id = "chat-message-input";

  chatFormEl = chatComponent.querySelector<HTMLFormElement>(CHAT_FORM_SELECTOR);
  if (chatFormEl && !chatFormEl.id) chatFormEl.id = "chat-form";

  const sendButtonEl = chatComponent.querySelector<HTMLButtonElement>(CHAT_SEND_BTN_SELECTOR);
  if (sendButtonEl && !sendButtonEl.id) sendButtonEl.id = "chat-send-button";


  if (!chatMessagesEl || !chatInputEl || !chatFormEl) {
    console.error("Chat component missing critical elements (messages area, input, or form).");
    return;
  }

  // Clear any static example messages
  chatMessagesEl.innerHTML = "";


  // Prompt for username
  const name = prompt("Enter your name for chat:", currentUserName);
  if (name && name.trim() !== "") {
    currentUserName = name.trim();
  }


  mcpClient = new MCPClient(clientAgentId, mcpServerUrl);

  const mcpEventHandler: McpEventHandler = {
    onOpen: () => {
      console.log(`MCP Connection Opened for Chat (Client ID: ${clientAgentId}, User: ${currentUserName}).`);
      const statusMsg = document.createElement("div");
      statusMsg.textContent = "Connected to chat service.";
      statusMsg.setAttribute("data-sads-text-style", "italic");
      statusMsg.setAttribute("data-sads-text-color", "text-neutral-subtle");
      statusMsg.setAttribute("data-sads-padding", "xs");
      chatMessagesEl?.appendChild(statusMsg);
      reapplySadsStyles();
    },
    onMessage: (message: Message) => {
      // console.log("Chat MCP Message Received:", message);
      if (
        message.performative === Performative.INFORM_RESULT &&
        message.ontology === CHAT_BROADCAST_ONTOLOGY &&
        message.payload.oneofKind === "informResultPayload"
      ) {
        const informPayload = message.payload.informResultPayload as InformResultPayload;
        if (informPayload.resultDetails) {
          const resultDetailsJson = Struct.toJson(informPayload.resultDetails);

          // Add null check for resultDetailsJson and type assertion for property access
          if (resultDetailsJson && typeof resultDetailsJson === 'object' && !Array.isArray(resultDetailsJson)) {
            const chatData = resultDetailsJson as Record<string, any>;
            const receivedChatMessage: Partial<ChatMessage> = {
              userId: chatData.user_id as string,
              userName: chatData.user_name as string,
              text: chatData.text as string,
              // Timestamp handling: Convert from string if needed, or use as is for display.
              // Example: timestamp: chatData.timestamp ? Timestamp.fromDate(new Date(chatData.timestamp as string)) : undefined
            };

            // Basic validation
            if (receivedChatMessage.text) {
               displayMessage(receivedChatMessage as ChatMessage); // Cast after validation
            } else {
              console.warn("Received chat broadcast with missing text field:", resultDetailsJson);
            }
          } else {
            console.warn("Received chat broadcast with invalid resultDetails structure:", resultDetailsJson);
          }
        }
      }
    },
    onError: (event) => {
      console.error("Chat MCP Connection Error:", event);
      const statusMsg = document.createElement("div");
      statusMsg.textContent = "Chat connection error.";
      statusMsg.setAttribute("data-sads-text-style", "italic");
      statusMsg.setAttribute("data-sads-text-color", "text-negative");
      statusMsg.setAttribute("data-sads-padding", "xs");
      chatMessagesEl?.appendChild(statusMsg);
      reapplySadsStyles();
    },
    onClose: () => {
      console.log("Chat MCP Connection Closed.");
       const statusMsg = document.createElement("div");
      statusMsg.textContent = "Chat connection closed.";
      statusMsg.setAttribute("data-sads-text-style", "italic");
      statusMsg.setAttribute("data-sads-text-color", "text-warning");
      statusMsg.setAttribute("data-sads-padding", "xs");
      chatMessagesEl?.appendChild(statusMsg);
      reapplySadsStyles();
    },
  };

  mcpClient.connect(mcpEventHandler);

  chatFormEl.addEventListener("submit", handleSendMessage);

  console.log("Chat component initialized.");
}
