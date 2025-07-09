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

	if incomingMsg.Ontology == "elizaos:ide:explain_code" {
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
			Language: "plaintext", // Or derive from request
		}
        // Removed problematic structPayload and ProtoReflect approach.
        // Using the simpler map approach directly.
        explanationMap, mapErr := structpb.NewStruct(map[string]interface{}{
            "explanation_text": explanationResp.ExplanationText,
            "language": explanationResp.Language,
        })
		if mapErr == nil {
			resultDetailsMap["ide_code_explanation_response"] = explanationMap
		} else {
			log.Printf("MCP Service: Error creating Struct for IdeCodeExplanationResponse: %v", mapErr)
			// Optionally add a simpler error placeholder to resultDetailsMap
			resultDetailsMap["ide_code_explanation_response_error"] = "Failed to structure explanation response"
		}

	} else if incomingMsg.Ontology == "elizaos:ide:refactor_suggestion" {
		 refactorResp := &pb.IdeRefactorSuggestionResponse{
            OriginalSnippet: "Original code snippet here...",
            Suggestions: []*pb.RefactoringSuggestion{
                {
                    ChangeType: "rename_variable",
                    Description: "Consider renaming 'x' to 'index' for clarity.",
                    SuggestedCodeDiff: "- var x = 10;\n+ var index = 10;",
                    Confidence: 0.8,
                },
            },
        }
        // Convert to map for Struct
         suggestionsList := []interface{}{}
        for _, sug := range refactorResp.Suggestions {
            suggestionsList = append(suggestionsList, map[string]interface{}{
                "change_type": sug.ChangeType,
                "description": sug.Description,
                "suggested_code_diff": sug.SuggestedCodeDiff,
                "confidence": sug.Confidence,
            })
        }
        refactorMap, _ := structpb.NewStruct(map[string]interface{}{
            "original_snippet": refactorResp.OriginalSnippet,
            "suggestions": suggestionsList,
        })
        resultDetailsMap["ide_refactor_suggestion_response"] = refactorMap
	}


	resultDetailsStruct, err := structpb.NewStruct(resultDetailsMap)
	if err != nil {
		log.Printf("MCP Service: Error creating Struct for InformResult: %v", err)
		// Send a FAILURE message instead or simplify details
		resultDetailsStruct, _ = structpb.NewStruct(map[string]interface{}{"error": "failed to prepare detailed result"})
	}


	informMsg := &pb.Message{
		McpVersion: "0.1.0",
		MessageId:  fmt.Sprintf("server-inform-%s", incomingMsg.MessageId),
		Performative: pb.Performative_INFORM_RESULT,
		Sender:     &pb.Identifier{AgentId: incomingMsg.Receiver.GetAgentId()}, // Agent (e.g. Jules) sends this
		Receiver:   &pb.Identifier{AgentId: originalSenderAgentID},      // To original requester
		InReplyTo:  incomingMsg.MessageId,
		Language:   "application/protobuf",
		Ontology:   "elizaos:ontology:general/inform_result", // Generic, or specific to the original request's domain
		Timestamp:  timestamppb.Now(),
		Payload: &pb.Message_InformResultPayload{
			InformResultPayload: &pb.InformResultPayload{
				TaskStatus:    pb.TaskStatus_TASK_SUCCESS,
				ResultSummary: "Mock agent " + incomingMsg.Receiver.GetAgentId() + " processed the request.",
				ResultDetails: resultDetailsStruct,
			},
		},
	}
	responseMessages = append(responseMessages, informMsg)

	// Send the responses
	for _, respMsg :=  range responseMessages {
		s.sendMessageToAgent(originalSenderAgentID, respMsg)
	}
}

// sendMessageToAgent serializes and sends an MCP message to a specific agent via SSE.
// Note: Unexported as it's an internal helper.
func (s *Service) sendMessageToAgent(targetAgentID string, msg *pb.Message) {
	msgBytes, err := proto.Marshal(msg)
	if err != nil {
		log.Printf("MCP Service: Error marshalling response protobuf for agent %s: %v", targetAgentID, err)
		return
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	foundClient := false
	for _, c := range s.clients { // Renamed loop variable
		// This logic is simplified: it sends to ALL clients that have claimed the targetAgentID
		// Or, if client.agentID is not yet set, it might not send.
		// A more robust system needs better client identification and agentID mapping.
		// For PoC, if the client's agentID matches the targetAgentID of the message, send it.
		// The client.agentID should ideally be set when the client connects and identifies itself.
		// For now, the MCPClient sets its sender.agent_id. We need to map this to an sse client.
		// Let's assume the client.agentID is set by the first message it sends via POST.
		// This is still imperfect.
		// A simpler broadcast for PoC to all clients might be easier if routing is complex.

		// For this PoC, we'll search for a client whose agentID matches the targetAgentID.
		// This agentID would have been set on the client struct when it first sent a message via POST.
		// Now client.agentID is set from the SSE query parameter.
		// We send the message if the targetAgentID (which is the original sender of the request)
		// matches the agentID this SSE client registered with.
		if c.agentID == targetAgentID {
			select {
			case c.sendChan <- msgBytes:
				log.Printf("MCP Service: Sent message ID %s to agent %s (Client SSE ID: %s)", msg.MessageId, targetAgentID, c.id)
				foundClient = true
			default:
				log.Printf("MCP Service: Client %s (Agent: %s) send channel full for message ID %s. Dropping.", c.id, targetAgentID, msg.MessageId)
			}
		}
	}

	if !foundClient {
		log.Printf("MCP Service: No SSE client found for agent %s to send message ID %s. Message not sent.", targetAgentID, msg.MessageId)
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
