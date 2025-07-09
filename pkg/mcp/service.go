package mcp

import (
	// "bytes" // Removed unused import
	"encoding/base64"
	// "flag" // No longer used in this package
	"fmt"
	"io"
	"log"
	"net/http"
	// "os" // No longer used in this package
	// "path/filepath" // No longer used in this package
	"sync"
	"time"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/structpb"
	"google.golang.org/protobuf/types/known/timestamppb"

	pb "landing-page-generator/generated/go"
)

// client represents a single SSE client connection.
// Note: Unexported because it's only used within the mcp package.
type client struct {
	id         string
	agentID    string // Agent ID this client represents (e.g., from initial handshake or first message)
	conn       http.ResponseWriter
	flusher    http.Flusher
	sendChan   chan []byte // Channel for messages to be sent to this client
	closedChan chan struct{} // Channel to signal client disconnection
}

// Service handles MCP communication.
// Note: Exported as it's the main entry point for this package.
type Service struct {
	clients    map[string]*client
	mu         sync.Mutex
	serverPort string
}

// NewMCPService creates a new MCP Service.
// Note: Renamed to NewService to follow Go conventions (package name often omitted for constructors).
func NewService(port string) *Service {
	return &Service{
		clients:    make(map[string]*client),
		serverPort: port,
	}
}

// SseHandler handles new SSE client connections.
// Note: Exported as it's used by main.go.
func (s *Service) SseHandler(w http.ResponseWriter, r *http.Request) {
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming unsupported!", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("Access-Control-Allow-Origin", "*") // For development

	// For PoC, client ID can be simple. In production, use something more robust.
	// Or extract from an initial handshake message if we implement that.
	clientSSEID := fmt.Sprintf("client-%d-%d", time.Now().UnixNano(), r.RemoteAddr) // More unique client ID for server logs
	clientAgentProvidedID := r.URL.Query().Get("agentId")

	if clientAgentProvidedID == "" {
		log.Printf("MCP Service: SSE client connected from %s without agentId query parameter. Closing.", r.RemoteAddr)
		http.Error(w, "agentId query parameter is required for SSE connection", http.StatusBadRequest)
		return
	}

	log.Printf("MCP Service: New SSE client connected: %s (Agent ID: %s)", clientSSEID, clientAgentProvidedID)

	c := &client{ // Renamed variable to 'c' to avoid conflict with package name if it were 'client'
		id:         clientSSEID,
		agentID:    clientAgentProvidedID, // Store the agentID provided by the client
		conn:       w,
		flusher:    flusher,
		sendChan:   make(chan []byte, 256), // Buffered channel
		closedChan: make(chan struct{}),
	}

	s.mu.Lock()
	s.clients[c.id] = c
	s.mu.Unlock()

	defer func() {
		s.mu.Lock()
		delete(s.clients, c.id)
		s.mu.Unlock()
		close(c.sendChan) // Close the send channel for this client
		log.Printf("MCP Service: SSE client disconnected: %s (Agent: %s)", c.id, c.agentID)
	}()

	// Send an initial connection confirmation event (optional)
	// Send back the agentID it connected with for confirmation.
	fmt.Fprintf(w, "event: mcp_connected\ndata: %s\n\n", c.agentID)
	flusher.Flush()


	// Keep connection open and listen for messages to send or disconnection
	for {
		select {
		case <-r.Context().Done(): // Client closed connection
			return
		case <-c.closedChan: // Server initiated close (e.g. duplicate agentID)
			return
		case msgBytes, ok := <-c.sendChan:
			if !ok { // Channel closed
				return
			}
			// SSE messages are typically base64 encoded binary protobuf
			encodedMsg := base64.StdEncoding.EncodeToString(msgBytes)
			_, err := fmt.Fprintf(w, "data: %s\n\n", encodedMsg)
			if err != nil {
				log.Printf("MCP Service: Error writing to client %s: %v", c.id, err)
				return // Error writing, close connection
			}
			flusher.Flush()
		case <-time.After(30 * time.Second): // Keep-alive ping (optional)
			// fmt.Fprintf(w, "event: ping\ndata: %s\n\n", time.Now().Format(time.RFC3339))
			// flusher.Flush()
			// No explicit ping needed if messages are frequent enough or client handles timeouts
		}
	}
}

// SendHandler handles incoming MCP messages via HTTP POST.
// Note: Exported as it's used by main.go.
func (s *Service) SendHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Only POST method is allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Error reading request body", http.StatusInternalServerError)
		return
	}
	defer r.Body.Close()

	// Body is expected to be raw binary protobuf
	mcpMsg := &pb.Message{}
	if err := proto.Unmarshal(body, mcpMsg); err != nil {
		log.Printf("MCP Service: Error unmarshalling protobuf: %v. Received raw: %s", err, base64.StdEncoding.EncodeToString(body))
		http.Error(w, fmt.Sprintf("Error unmarshalling protobuf: %v", err), http.StatusBadRequest)
		return
	}

	log.Printf("MCP Service: Received MCP message via POST: ID=%s, Performative=%s, Sender=%s, Receiver=%s, Ontology=%s",
		mcpMsg.MessageId, mcpMsg.Performative, mcpMsg.Sender.GetAgentId(), mcpMsg.Receiver.GetAgentId(), mcpMsg.Ontology)

	// Associate SSE client with sender agent ID if not already done.
	// This is a simplified way for PoC. A real system might have authentication.
	// For now, we assume the first POST from an agent on an SSE session implicitly "claims" it.
	// This is flawed if one client sends messages on behalf of multiple agents.
	// A better way is if the client includes its SSE clientID in the POST, or establishes agentID on SSE connect.
	// For simplicity: find a client that doesn't have an agentID yet and assign it, or find the matching one.
	// This part is tricky and needs refinement for a robust system.
	// For now, we'll primarily use the sender_id from the message to route the *response*.

	// --- Mock Agent Logic & Response Generation ---
	go s.simulateAgentProcessing(mcpMsg) // simulateAgentProcessing is now unexported

	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "Message received")
}

// simulateAgentProcessing is an unexported helper method.
func (s *Service) simulateAgentProcessing(incomingMsg *pb.Message) {
	// Simulate delay
	time.Sleep(1 * time.Second)

	// Who is the original sender (now the receiver of our response)?
	originalSenderAgentID := incomingMsg.Sender.GetAgentId()
	if originalSenderAgentID == "" {
		log.Println("MCP Service: Cannot respond, original sender agentID is empty in incoming message.")
		return
	}

	var responseMessages []*pb.Message

	// Mock TASK_ACCEPT
	acceptMsg := &pb.Message{
		McpVersion: "0.1.0",
		MessageId:  fmt.Sprintf("server-accept-%s", incomingMsg.MessageId),
		Performative: pb.Performative_TASK_ACCEPT,
		Sender:     &pb.Identifier{AgentId: incomingMsg.Receiver.GetAgentId()}, // Agent (e.g. Jules) sends this
		Receiver:   &pb.Identifier{AgentId: originalSenderAgentID},      // To original requester
		InReplyTo:  incomingMsg.MessageId,
		Language:   "application/protobuf",
		Ontology:   "elizaos:ontology:general/task_acceptance",
		Timestamp:  timestamppb.Now(),
		Payload: &pb.Message_TaskAcceptPayload{
			TaskAcceptPayload: &pb.TaskAcceptPayload{
				Status:   "accepted",
				Comments: "Task accepted by mock agent " + incomingMsg.Receiver.GetAgentId(),
			},
		},
	}
	responseMessages = append(responseMessages, acceptMsg)

	// Simulate more delay for task processing
	time.Sleep(2 * time.Second)

	// Mock INFORM_RESULT
	resultDetailsMap := map[string]interface{}{
		"status_text": "Mock processing complete.",
	}

	// Check for the new chat message ontology
	taskRequestPayload, ok := incomingMsg.GetPayload().(*pb.Message_TaskRequestPayload)
	if !ok {
		log.Printf("MCP Service: Received message is not a TaskRequestPayload, skipping special processing. Performative: %s", incomingMsg.Performative)
		// Fall through to generic processing if any, or just handle standard responses.
		// For now, we assume non-TaskRequest payloads don't need this specific handling.
	} else if taskRequestPayload.TaskRequestPayload.GetTaskType() == "elizaos:chat:message" {
		log.Printf("MCP Service: Received chat message from %s", originalSenderAgentID)

		chatMessageStruct := taskRequestPayload.TaskRequestPayload.GetTaskParameters()
		if chatMessageStruct == nil {
			log.Printf("MCP Service: Chat message from %s has no parameters.", originalSenderAgentID)
			// Optionally send a FAILURE back to the sender
			return
		}

		// The chatMessageStruct itself is the pb.ChatMessage, but wrapped in a structpb.Struct.
		// We need to ensure the client sends it correctly, likely as a single field within the struct.
		// For example, client might send: task_parameters: {"chat_message": {"user_id": "...", "text": "..."}}
		// Or, if the client sends the ChatMessage fields directly as top-level fields in task_parameters:
		// task_parameters: {"user_id": "...", "text": "...", "user_name": "...", "timestamp": "..."}

		// Let's assume the client sends the ChatMessage fields directly as task_parameters.
		// We'll reconstruct a pb.ChatMessage from the structpb.Struct fields.
		// This is a bit manual; a cleaner way might be for the client to send
		// a single field in task_parameters, e.g., "chat_message_data", which is a serialized ChatMessage.
		// For now, direct field extraction:
		userID := chatMessageStruct.Fields["user_id"].GetStringValue()
		userName := chatMessageStruct.Fields["user_name"].GetStringValue()
		text := chatMessageStruct.Fields["text"].GetStringValue()
		// Timestamp handling: client will send it as string, convert to timestamppb.Timestamp
		// For simplicity, we'll use server time for broadcast messages for now.
		// A more robust solution would parse the client's timestamp.

		if userID == "" || text == "" {
			log.Printf("MCP Service: Invalid chat message from %s. Missing user_id or text.", originalSenderAgentID)
			// Optionally send a FAILURE back
			return
		}

		// Construct the ChatMessage protobuf object to be broadcast
		// We use current server time for broadcast consistency.
		// The original sender's timestamp is available if needed: chatMessageStruct.Fields["timestamp"]
		broadcastChatMessage := &pb.ChatMessage{
			UserId:    userID,
			UserName:  userName, // If not provided, client might need to send it or server looks it up
			Text:      text,
			Timestamp: timestamppb.Now(), // Server timestamp for broadcast
		}

		// Convert the pb.ChatMessage to a structpb.Value so it can be embedded in result_details
		// One way is to convert pb.ChatMessage to map[string]interface{} then to structpb.Struct
		chatMessageMap := map[string]interface{}{
			"user_id":   broadcastChatMessage.UserId,
			"user_name": broadcastChatMessage.UserName,
			"text":      broadcastChatMessage.Text,
			"timestamp": broadcastChatMessage.Timestamp.AsTime().Format(time.RFC3339Nano), // Send as string
		}
		chatMessageForDetails, err := structpb.NewStruct(chatMessageMap)
		if err != nil {
			log.Printf("MCP Service: Error creating Struct for broadcast ChatMessage: %v", err)
			return
		}

		// Create the INFORM_RESULT message to broadcast
		broadcastInformMsg := &pb.Message{
			McpVersion:   "0.1.0",
			MessageId:    fmt.Sprintf("server-chat-broadcast-%s", incomingMsg.MessageId),
			Performative: pb.Performative_INFORM_RESULT,
			Sender:       &pb.Identifier{AgentId: "chat_service"}, // Or incomingMsg.Receiver.GetAgentId() if that's the chat "room"
			// Receiver is not set for broadcast, handled by broadcastMessageToAll
			Language:  "application/protobuf",
			Ontology:  "elizaos:chat:message_broadcast", // New ontology for clients to identify chat broadcasts
			Timestamp: timestamppb.Now(),
			Payload: &pb.Message_InformResultPayload{
				InformResultPayload: &pb.InformResultPayload{
					TaskStatus:    pb.TaskStatus_TASK_SUCCESS, // Or a more suitable status for broadcast
					ResultSummary: fmt.Sprintf("New chat message from %s", userName),
					ResultDetails: chatMessageForDetails,
				},
			},
		}

		// Broadcast this message to all clients
		s.broadcastMessageToAll(broadcastInformMsg, originalSenderAgentID) // Pass originalSenderAgentID to optionally exclude them

		// Chat messages don't typically get a direct TASK_ACCEPT or INFORM_RESULT back to the sender in the same way
		// other tasks do. The broadcast itself is the result.
		// So, we might not need to add to `responseMessages` for the original sender here,
		// unless we want to send a specific confirmation that their message was broadcast.
		// For now, skip direct response to sender, they will receive the broadcast.
		return // End chat message processing here

	} else if incomingMsg.Ontology == "elizaos:ide:explain_code" {
		// Assuming task_parameters had IdeCodeExplanationRequest
		// For PoC, just create a mock explanation
		var codeSnippet string
		if reqPayload, ok := incomingMsg.GetPayload().(*pb.Message_TaskRequestPayload); ok {
			if params := reqPayload.TaskRequestPayload.GetTaskParameters(); params != nil {
				if snippetVal, ok := params.Fields["code_snippet"]; ok {
					codeSnippet = snippetVal.GetStringValue()
				}
			}
		}

		explanationResp := &pb.IdeCodeExplanationResponse{
			ExplanationText: fmt.Sprintf("This is a mock explanation for your code snippet:\n```\n%s\n```\nThe agent %s thinks it's interesting!", codeSnippet, incomingMsg.Receiver.GetAgentId()),
			Language:        "plaintext", // Or derive from request
		}
		// Store as a map[string]interface{} directly.
		// The final structpb.NewStruct(resultDetailsMap) will handle the conversion.
		resultDetailsMap["ide_code_explanation_response"] = map[string]interface{}{
			"explanation_text": explanationResp.ExplanationText,
			"language":         explanationResp.Language,
		}
		// Note: The previous mapErr check for this specific struct conversion is removed
		// as direct map assignment won't fail in the same way structpb.NewStruct could.
		// Any issues with the content of this map would be caught by the later, all-encompassing
		// structpb.NewStruct(resultDetailsMap) call.

	} else if incomingMsg.Ontology == "elizaos:ide:refactor_suggestion" {
		refactorResp := &pb.IdeRefactorSuggestionResponse{
			OriginalSnippet: "Original code snippet here...",
			Suggestions: []*pb.RefactoringSuggestion{
				{
					ChangeType:        "rename_variable",
					Description:       "Consider renaming 'x' to 'index' for clarity.",
					SuggestedCodeDiff: "- var x = 10;\n+ var index = 10;",
					Confidence:        0.8,
				},
			},
		}
		suggestionsList := []interface{}{}
		for _, sug := range refactorResp.Suggestions {
			suggestionsList = append(suggestionsList, map[string]interface{}{
				"change_type":         sug.ChangeType,
				"description":         sug.Description,
				"suggested_code_diff": sug.SuggestedCodeDiff,
				"confidence":          sug.Confidence,
			})
		}
		// Store as a map[string]interface{} directly.
		// The final structpb.NewStruct(resultDetailsMap) will handle the conversion.
		resultDetailsMap["ide_refactor_suggestion_response"] = map[string]interface{}{
			"original_snippet": refactorResp.OriginalSnippet,
			"suggestions":      suggestionsList,
		}
	}

	// This part is for non-chat message responses
	resultDetailsStruct, err := structpb.NewStruct(resultDetailsMap)
	if err != nil {
		log.Printf("MCP Service: Error creating Struct for InformResult: %v", err)
		resultDetailsStruct, _ = structpb.NewStruct(map[string]interface{}{"error": "failed to prepare detailed result"})
	}

	informMsg := &pb.Message{
		McpVersion:   "0.1.0",
		MessageId:    fmt.Sprintf("server-inform-%s", incomingMsg.MessageId),
		Performative: pb.Performative_INFORM_RESULT,
		Sender:       &pb.Identifier{AgentId: incomingMsg.Receiver.GetAgentId()},
		Receiver:     &pb.Identifier{AgentId: originalSenderAgentID},
		InReplyTo:    incomingMsg.MessageId,
		Language:     "application/protobuf",
		Ontology:     "elizaos:ontology:general/inform_result",
		Timestamp:    timestamppb.Now(),
		Payload: &pb.Message_InformResultPayload{
			InformResultPayload: &pb.InformResultPayload{
				TaskStatus:    pb.TaskStatus_TASK_SUCCESS,
				ResultSummary: "Mock agent " + incomingMsg.Receiver.GetAgentId() + " processed the request.",
				ResultDetails: resultDetailsStruct,
			},
		},
	}
	responseMessages = append(responseMessages, informMsg)

	// Send the responses (only for non-chat messages now)
	for _, respMsg := range responseMessages {
		s.sendMessageToAgent(originalSenderAgentID, respMsg)
	}
}

// sendMessageToAgent serializes and sends an MCP message to a specific agent via SSE.
func (s *Service) sendMessageToAgent(targetAgentID string, msg *pb.Message) {
	msgBytes, err := proto.Marshal(msg)
	if err != nil {
		log.Printf("MCP Service: Error marshalling response protobuf for agent %s: %v", targetAgentID, err)
		return
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	foundClient := false
	for _, client := range s.clients {
		if client.agentID == targetAgentID {
			select {
			case client.sendChan <- msgBytes:
				log.Printf("MCP Service: Sent message ID %s to agent %s (Client SSE ID: %s)", msg.MessageId, targetAgentID, client.id)
				foundClient = true
			default:
				log.Printf("MCP Service: Client %s (Agent: %s) send channel full for message ID %s. Dropping.", client.id, targetAgentID, msg.MessageId)
			}
			// Assuming one agentID maps to one client. If multiple clients can have the same agentID,
			// we might need to send to all or break after first. For now, this is okay.
			// break
		}
	}

	if !foundClient {
		log.Printf("MCP Service: No SSE client found for agent %s to send message ID %s. Message not sent.", targetAgentID, msg.MessageId)
	}
}

// broadcastMessageToAll sends a message to all connected SSE clients, optionally excluding one.
func (s *Service) broadcastMessageToAll(msg *pb.Message, excludeAgentID ...string) {
	msgBytes, err := proto.Marshal(msg)
	if err != nil {
		log.Printf("MCP Service: Error marshalling broadcast protobuf: %v", err)
		return
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	var excluded string
	if len(excludeAgentID) > 0 {
		excluded = excludeAgentID[0]
	}

	log.Printf("MCP Service: Broadcasting message ID %s to all clients (excluding %s if specified)", msg.MessageId, excluded)

	for _, client := range s.clients {
		if excluded != "" && client.agentID == excluded {
			// log.Printf("MCP Service: Skipping broadcast to sender %s (Client SSE ID: %s)", excluded, client.id)
			continue // Optionally skip sending the message back to the original sender
		}
		select {
		case client.sendChan <- msgBytes:
			log.Printf("MCP Service: Broadcast message ID %s sent to client %s (Agent: %s)", msg.MessageId, client.id, client.agentID)
		default:
			log.Printf("MCP Service: Client %s (Agent: %s) send channel full for broadcast message ID %s. Dropping.", client.id, client.agentID, msg.MessageId)
		}
	}
}


// Note: The main function, along with its related setup (flags, static file serving),
// has been moved to cmd/server/main.go. This file now only contains MCP service-specific logic.

// TODO for robust server:
// - Server's sseHandler should perhaps reject connections if an agentID is already connected (or handle multiple connections per agent gracefully).
// - Proper payload parsing for incoming TaskRequestPayload.task_parameters (which is a Struct)
//   to extract specific request details like code_snippet, language from IdeCodeExplanationRequest.
//   Currently, it's only partially done for logging in simulateAgentProcessing.
// - Proper construction of result_details (Struct) for outgoing InformResultPayload.
//   This means converting specific response structs (like IdeCodeExplanationResponse) into map[string]interface{}
//   and then into structpb.Struct. Current map approach is basic.
// - More sophisticated agent simulation or routing to actual agent logic.
// - Security: Authentication, authorization.
// - Error handling in simulateAgentProcessing for protobuf marshalling of responses.
