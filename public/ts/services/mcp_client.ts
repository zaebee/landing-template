// public/ts/services/mcp_client.ts

import { Message, Performative, Identifier } from "../../../generated/ts/mcp.js"; // Adjust path as necessary
import {
  TaskRequestPayload,
  TaskAcceptPayload,
  InformResultPayload,
} from "../../../generated/ts/mcp.js"; // Specific payloads
import { Timestamp } from "../../../generated/ts/google/protobuf/timestamp.js";
import { mcpServerUrl as configuredMcpServerUrl } from "../config.js"; // Actual config file

export interface McpEventHandler {
  onOpen?: (event: Event) => void;
  onMessage?: (message: Message) => void;
  onError?: (event: Event) => void;
  onClose?: () => void;
}

export class MCPClient {
  private eventSource: EventSource | null = null;
  private readonly url: string;
  private eventHandler: McpEventHandler | null = null;
  private messageQueue: string[] = []; // Queue for messages to send when connection is ready
  private isConnected: boolean = false;
  private clientAgentId: string;

  constructor(clientAgentId: string, serverUrl?: string) {
    this.url = serverUrl || configuredMcpServerUrl; // Use imported config
    this.clientAgentId = clientAgentId; // Client agent ID is now mandatory
    if (!clientAgentId) {
      throw new Error("MCPClient: clientAgentId is required.");
    }
  }

  public connect(handler: McpEventHandler): void {
    if (this.eventSource) {
      console.warn("MCPClient is already connected or connecting.");
      return;
    }

    this.eventHandler = handler;
    this.eventSource = new EventSource(this.url);

    this.eventSource.onopen = (event) => {
      this.isConnected = true;
      console.log("MCPClient: SSE connection opened.", event);
      if (this.eventHandler?.onOpen) {
        this.eventHandler.onOpen(event);
      }
      this.sendQueuedMessages();
    };

    this.eventSource.onmessage = (event) => {
      // console.log("MCPClient: Raw SSE message received:", event.data);
      try {
        // Assuming server sends messages as base64 encoded binary protobuf
        const binaryData = Uint8Array.from(atob(event.data), (c) =>
          c.charCodeAt(0)
        );
        const message = Message.fromBinary(binaryData);
        // console.log("MCPClient: Parsed MCP Message:", message);
        if (this.eventHandler?.onMessage) {
          this.eventHandler.onMessage(message);
        }
      } catch (error) {
        console.error(
          "MCPClient: Error parsing MCP message:",
          error,
          "Raw data:",
          event.data
        );
      }
    };

    this.eventSource.onerror = (event) => {
      this.isConnected = false;
      console.error("MCPClient: SSE connection error.", event);
      if (this.eventHandler?.onError) {
        this.eventHandler.onError(event);
      }
      // Depending on the error, EventSource might automatically try to reconnect or close.
      // For some errors (like non-200 responses), it closes.
      if (this.eventSource?.readyState === EventSource.CLOSED) {
        this.close();
      }
    };
  }

  private sendQueuedMessages(): void {
    while (this.messageQueue.length > 0) {
      const serializedMessage = this.messageQueue.shift();
      if (serializedMessage) {
        this.sendRaw(serializedMessage);
      }
    }
  }

  private async sendRaw(serializedMessage: string): Promise<void> {
    // SSE is client-pull. To "send" a message, we typically make an HTTP POST request
    // to a different endpoint on the server, not through the EventSource connection itself.
    // The EventSource is for receiving messages from the server.

    // The MCP_SERVER_URL for EventSource might be different from the POST URL.
    // For now, let's assume a convention like /mcp/send for POSTing.
    const postUrl = this.url.replace("/sse", "/send"); // Example convention

    try {
      const response = await fetch(postUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/octet-stream", // Sending binary protobuf
        },
        body: Uint8Array.from(atob(serializedMessage), (c) => c.charCodeAt(0)), // Convert base64 string back to Uint8Array
      });

      if (!response.ok) {
        console.error(
          `MCPClient: Error sending message. Status: ${response.status}`,
          await response.text()
        );
      } else {
        // console.log("MCPClient: Message sent successfully via POST.");
      }
    } catch (error) {
      console.error("MCPClient: Error sending message via POST:", error);
    }
  }

  public sendMessage(
    performative: Performative,
    receiverAgentId: string,
    payload: any,
    ontology: string,
    inReplyTo?: string,
    replyWith?: string
  ): string {
    const messageId = crypto.randomUUID();

    const sender: Identifier = { agentId: this.clientAgentId };
    const receiver: Identifier = { agentId: receiverAgentId };

    let partialMessage: Partial<Message> = {
      mcpVersion: "0.1.0",
      messageId: messageId,
      performative: performative,
      sender: sender,
      receiver: receiver,
      language: "application/protobuf", // Payload is protobuf binary
      ontology: ontology,
      timestamp: Timestamp.now(),
      inReplyTo: inReplyTo || "",
      replyWith: replyWith || "",
    };

    // Assign payload to the correct oneof field
    switch (performative) {
      case Performative.TASK_REQUEST:
        partialMessage.payload = {
          oneofKind: "taskRequestPayload",
          taskRequestPayload: payload as TaskRequestPayload,
        };
        break;
      case Performative.TASK_ACCEPT:
        partialMessage.payload = {
          oneofKind: "taskAcceptPayload",
          taskAcceptPayload: payload as TaskAcceptPayload,
        };
        break;
      case Performative.INFORM_RESULT:
        partialMessage.payload = {
          oneofKind: "informResultPayload",
          informResultPayload: payload as InformResultPayload,
        };
        break;
      // Add cases for other performatives (QueryIf, QueryRef, TaskReject, Failure, NotUnderstood)
      // And IDE specific direct payloads if Message.oneof is structured that way
      // case Performative.IDE_CODE_EXPLANATION_REQUEST: // This is not a performative, but a payload type.
      //     partialMessage.payload = { oneofKind: "ideCodeExplanationRequest", ideCodeExplanationRequest: payload };
      //     break;
      default:
        console.error(
          `MCPClient: Unknown performative for payload assignment: ${Performative[performative]}`
        );
        throw new Error(
          `Unknown performative for payload assignment: ${Performative[performative]}`
        );
    }

    const message = Message.create(partialMessage as Message); // Cast is okay due to oneof logic
    const binaryMessage = Message.toBinary(message);
    const base64Message = btoa(String.fromCharCode(...binaryMessage)); // Convert Uint8Array to base64 string

    if (this.isConnected && this.eventSource?.readyState === EventSource.OPEN) {
      this.sendRaw(base64Message);
    } else {
      console.log("MCPClient: Connection not ready. Queuing message.");
      this.messageQueue.push(base64Message);
      if (
        !this.eventSource ||
        this.eventSource.readyState === EventSource.CLOSED
      ) {
        console.log(
          "MCPClient: Attempting to reconnect as EventSource is closed."
        );
        // This assumes connect() can be safely called again if previously failed or closed.
        // It might be better to have a dedicated reconnect method or manage state more carefully.
        if (this.eventHandler) this.connect(this.eventHandler);
      }
    }
    return messageId;
  }

  public close(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.isConnected = false;
      console.log("MCPClient: SSE connection closed.");
      if (this.eventHandler?.onClose) {
        this.eventHandler.onClose();
      }
    }
    this.messageQueue = []; // Clear queue on close
  }

  // --- Helper methods to construct specific typed payloads ---

  public static createIdentifier(agentId: string): Identifier {
    return { agentId };
  }

  // Example:
  // public createCodeExplanationTaskRequest(
  //     codeSnippet: string,
  //     language: string,
  //     userQuery: string
  // ): TaskRequestPayload {
  //     const ideRequestPayload: IdeCodeExplanationRequest = { // This is from mcp.proto
  //         codeSnippet,
  //         language,
  //         userQuery
  //     };
  //     return {
  //         taskType: "explain_code", // Matches ontology usually
  //         taskDescription: userQuery || `Explain code snippet in ${language}`,
  //         taskParameters: Struct.fromJson(IdeCodeExplanationRequest.toJson(ideRequestPayload)), // Requires Struct import
  //         priority: "medium"
  //     };
  // }
}

// Example Usage (conceptual, will be in UI components)
/*
const mcpClient = new MCPClient('http://localhost:8000/mcp/sse', 'myIDE_user123');

const handler: McpEventHandler = {
    onOpen: () => {
        console.log("Connection opened! Sending a test message.");
        // Example: Sending a TASK_REQUEST for code explanation
        // const taskPayload = mcpClient.createCodeExplanationTaskRequest(
        //     "console.log('hello');",
        //     "javascript",
        //     "Please explain this JavaScript code."
        // );
        // mcpClient.sendMessage(
        //     Performative.TASK_REQUEST,
        //     "jules_agent", // Target agent
        //     taskPayload,
        //     "elizaos:ide:explain_code" // Ontology
        // );
    },
    onMessage: (message: Message) => {
        console.log("Received message from agent:", message);
        if (message.performative === Performative.INFORM_RESULT && message.payload.oneofKind === 'informResultPayload') {
            const informPayload = message.payload.informResultPayload;
            console.log("Result summary:", informPayload.resultSummary);
            // Further processing of informPayload.resultDetails
        }
    },
    onError: (event) => {
        console.error("SSE Error:", event);
    },
    onClose: () => {
        console.log("Connection closed by server or client.close().");
    }
};

mcpClient.connect(handler);

// To send a message later:
// const anotherTask = { ... };
// mcpClient.sendMessage(Performative.TASK_REQUEST, "another_agent", anotherTask, "some:ontology");

// To close:
// mcpClient.close();
*/

// Note: The path to generated files `../../../generated/ts/mcp` and `../../../generated/ts/google/protobuf/timestamp`
// assumes this `mcp_client.ts` file is in `public/ts/services/` and the generated files are in `generated/ts/`.
// This might need adjustment based on actual project structure or tsconfig paths.
// For instance, if `generated/ts` is mapped to `@generated/*` in tsconfig.json,
// imports would be like `import { Message } from "@generated/mcp";`
