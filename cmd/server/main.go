package main

import (
	"flag"
	"log"
	"net/http"
	"os"
	"path/filepath"
)

func main() {
	port := flag.String("port", "8080", "Port to serve on")
	dir := flag.String("dir", ".", "Directory to serve files from")
	flag.Parse()

	currentWorkingDir, err := os.Getwd()
	if err != nil {
		log.Fatalf("Failed to get current working directory: %v", err)
	}

	servePath := filepath.Join(currentWorkingDir, *dir)

	fs := http.FileServer(http.Dir(servePath))
	http.Handle("/", fs)

	log.Printf("Serving directory %s on HTTP port: %s\n", servePath, *port)
	err = http.ListenAndServe(":"+*port, nil)
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
