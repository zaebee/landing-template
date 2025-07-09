package main

import (
	"flag"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"landing-page-generator/pkg/api"
	"landing-page-generator/pkg/mcp"
)

func main() {
	port := flag.String("port", "8000", "Port to serve on")
	dir := flag.String("dir", ".", "Directory to serve files from (for web UI)")
	flag.Parse()

	currentWorkingDir, err := os.Getwd()
	if err != nil {
		log.Fatalf("Failed to get current working directory: %v", err)
	}
	servePath := filepath.Join(currentWorkingDir, *dir)

	// Initialize MCP Service
	mcpService := mcp.NewService(*port) // Corrected to use NewService

	// Setup HTTP handlers
	// Static file serving
	http.Handle("/public/", http.StripPrefix("/public/", http.FileServer(http.Dir(filepath.Join(servePath, "public")))))
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/" {
			http.ServeFile(w, r, filepath.Join(servePath, "index.html"))
			return
		}
		// Adjusted to serve other root files like mcp_debug_panel.html if they are in the root 'dir'
		// For files specifically in 'public', the /public/ handler above will take care of them.
		// This logic assumes that if it's not `/` and not caught by `/public/`, it might be another root file.
		// However, `mcp_debug_panel.html` is in `public`, so it should be accessed via `/public/mcp_debug_panel.html`.
		// The original server logic was a bit ambiguous here.
		// If specific root files like `favicon.svg` (if it were in root) need to be served,
		// they would need explicit handling or be in `public`.
		// For now, this mostly serves index.html and relies on /public/ for other assets.
		http.NotFound(w, r)
	})

	// MCP Handlers
	http.HandleFunc("/mcp/sse", mcpService.SseHandler) // Assuming SseHandler is public
	http.HandleFunc("/mcp/send", mcpService.SendHandler) // Assuming SendHandler is public

	// API Handlers (from api package)
	// Example: http.HandleFunc("/api/generate-sads-from-nl", api.GenerateSadsFromNLHandler)
	// Ensure GenerateSadsFromNLHandler is exported and correctly imported.
	// The original api_handlers.go didn't have its handler registered in the old main.go,
	// so we add it here as per standard practice.
	http.HandleFunc("/api/generate-sads-from-nl", api.GenerateSadsFromNLHandler)


	log.Printf("Serving UI from %s (e.g. /public/mcp_debug_panel.html) and services on HTTP port: %s\n", servePath, *port)
	err = http.ListenAndServe(":"+*port, nil)
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
