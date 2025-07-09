# ElizaOS IDE Agent Interaction Extension (MCP via SADS Panel)

This document describes the proof-of-concept (PoC) IDE agent interaction panel that uses the Multi-Agent Communication Protocol (MCP) to communicate with ElizaOS agents like Jules (for coding) and Eddy (for documentation).

## Overview

The extension provides a user interface (a SADS-styled panel) within a web page (`public/mcp_debug_panel.html` for this PoC) that allows developers to:

- Connect to an ElizaOS MCP server.
- Send requests to specific ElizaOS agents (e.g., "Explain this code", "Suggest refactoring").
- Receive and display responses from these agents.

Communication is based on the definitions in `MCP_DRAFT.md` and uses Protobuf messages transmitted over an SSE (Server-Sent Events) connection for server-to-client messages and HTTP POST for client-to-server messages.

## Key Components

- **MCP Protobuf Definitions (`proto/mcp.proto`):** Defines the structure of messages exchanged between the IDE panel and ElizaOS agents. Includes messages for `TASK_REQUEST`, `TASK_ACCEPT`, `INFORM_RESULT`, and specific payloads for IDE interactions like `IdeCodeExplanationRequest`, `IdeRefactorSuggestionRequest`, etc.
- **TypeScript MCP Client (`public/ts/services/mcp_client.ts`):** Handles:
  - Establishing an SSE connection to the MCP server (includes sending its `clientAgentId` as a query parameter, e.g., `http://localhost:8000/mcp/sse?agentId=...`).
  - Serializing outgoing MCP messages (as binary Protobuf) and sending them via HTTP POST to an `/mcp/send` endpoint.
  - Receiving incoming MCP messages (as base64-encoded binary Protobuf) over SSE and deserializing them.
  - Managing message correlation using `message_id` and `in_reply_to`.
- **SADS UI Panel (`templates/components/ide_agent_panel/ide_agent_panel.html` & `public/ts/components/ide_agent_panel.ts`):**
  - Provides input fields for target agent ID, code snippets, and user queries.
  - Buttons to trigger actions like "Ask to Explain" and "Suggest Refactor".
  - Displays connection status and agent responses.
  - Uses `MCPClient` to interact with the server.
- **Configuration (`public/ts/config.ts`):**
  - Allows configuring the MCP server URL (defaults to `http://localhost:8000/mcp/sse`).
  - Defines a prefix for client agent IDs and a default target agent ID for the panel.
- **Mock Go MCP Server Handler (`cmd/server/main.go`):**
  - Implements an SSE endpoint (`/mcp/sse`) for clients to connect.
  - Implements an HTTP POST endpoint (`/mcp/send`) for clients to send MCP messages.
  - Deserializes incoming messages.
  - Simulates agent responses (`TASK_ACCEPT`, `INFORM_RESULT`) with mock data based on the request's ontology.
  - Sends responses back to the originating client over their SSE connection (relies on the `agentId` query parameter from the client's SSE connection for routing).

## Installation (Conceptual for PoC)

This component is part of a larger web application. To "install" or run this PoC:

1.  **Prerequisites:**
    - Go installed (for the server).
    - Node.js and npm installed (for building TypeScript and managing dependencies).
    - Protobuf compiler (`protoc`) and Go protobuf plugin (`protoc-gen-go`) installed.
2.  **Build the project:**
    - Install npm dependencies: `npm install`
    - Generate Protobuf files: `npm run generate-proto` (or the more robust direct `protoc` commands discussed during development).
    - Compile TypeScript: `npm run compile:ts`
    - (The full `npm run build` also includes `go run main.go` for static site generation, which is not strictly needed for just running the MCP server and test panel if `public/mcp_debug_panel.html` is accessed directly).
3.  **Run the MCP Server:**
    - Start the Go server from the project root: `go run cmd/server/main.go`
    - This will serve static files (including `public/mcp_debug_panel.html`) and the MCP endpoints on port 8000 by default.

## Configuration

- **MCP Server URL:**
  - The primary configuration is the `mcpServerUrl` found in `public/ts/config.ts`.
  - Default: `http://localhost:8000/mcp/sse`
  - This can be overridden by setting `window.AppConfig = { mcpServerUrl: "your_url" };` in `public/mcp_debug_panel.html` before the main application script is loaded.
- **Client Agent ID Prefix:**
  - `defaultClientAgentIdPrefix` in `public/ts/config.ts`. Each panel instance generates a unique ID like `ide_extension_client_xxxxxx`.
- **Default Target Agent ID:**
  - `defaultTargetAgentId` in `public/ts/config.ts` (e.g., "jules"). This pre-fills the "Target Agent ID" input in the panel.

## Usage

1.  Ensure the MCP server (`cmd/server/main.go`) is running.
2.  Open `public/mcp_debug_panel.html` in your web browser (e.g., `http://localhost:8000/public/mcp_debug_panel.html`).
3.  The panel will attempt to connect to the MCP server. The status should update to "Connected".
4.  **Enter Target Agent ID:** Specify which ElizaOS agent to send the request to (e.g., "jules", "eddy").
5.  **Enter Code Snippet:** If applicable (for code explanation or refactoring), paste the code into the text area.
6.  **Enter User Query:** Provide a natural language query or instruction for the agent (e.g., "Explain this code", "What does this function do?", "Suggest improvements for this class").
7.  **Click Action Button:**
    - **"Ask to Explain":** Sends a `TASK_REQUEST` with ontology `elizaos:ide:explain_code`.
    - **"Suggest Refactor":** Sends a `TASK_REQUEST` with ontology `elizaos:ide:refactor_suggestion`.
8.  **View Responses:**
    - The panel will display status updates (e.g., "Task accepted by agent...").
    - The final agent response (`INFORM_RESULT`) will be shown in the "Agent Response" area. This includes mock explanations or refactoring suggestions from the server.

## Assumptions about ElizaOS MCP Server Implementation

This PoC client and its integrated mock server make the following assumptions:

1.  **SSE Endpoint:** An SSE endpoint (e.g., `/mcp/sse`) is available for server-to-client communication.
    - Clients identify themselves by passing an `agentId` query parameter (e.g., `/mcp/sse?agentId=ide_client_123`). The server uses this `agentId` to route targeted messages back to the correct SSE client.
2.  **HTTP POST for Sending:** An HTTP POST endpoint (e.g., `/mcp/send`) is available for clients to send MCP messages to the server. Messages are sent as binary Protobuf in the request body.
3.  **Message Format:** Messages exchanged over SSE (from server) are base64-encoded binary Protobuf.
4.  **Agent Routing:** The server is capable of routing `TASK_REQUEST` messages to the appropriate agent based on the `receiver.agent_id` field in the MCP message. (The PoC server simulates this by having the mock agent use the `receiver.agent_id` as its own ID when responding).
5.  **Ontologies:** ElizaOS agents understand the ontologies used by the client:
    - `elizaos:ide:explain_code`
    - `elizaos:ide:refactor_suggestion`
    - And general task management ontologies from `MCP_DRAFT.md`.
6.  **Payload Structure:** Agents can parse `TaskRequestPayload.task_parameters` (which is a `google.protobuf.Struct`) containing specific IDE request structures like `IdeCodeExplanationRequest` or `IdeRefactorSuggestionRequest`. Similarly, agents provide results within `InformResultPayload.result_details` (also a `Struct`) containing structures like `IdeCodeExplanationResponse` or `IdeRefactorSuggestionResponse`.

## Error Handling (Basic)

- Connection errors to the MCP server are displayed in the status area.
- Errors during message serialization/deserialization or sending are logged to the browser console.
- Agent-reported errors (`TASK_REJECT`, `FAILURE`, or `INFORM_RESULT` with `task_status: FAILURE`) are displayed in the response area.

## This PoC provides a foundational framework for IDE-agent interaction using MCP. Further development would involve more robust error handling, richer UI capabilities, and integration with actual ElizaOS agent logic beyond the current mock server.
