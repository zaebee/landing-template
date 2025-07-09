package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath" // For creating output directory if it doesn't exist

	"landing-page-generator/tools/taskflow-visualizer/htmlgen"
	"landing-page-generator/tools/taskflow-visualizer/mermaid"
	"landing-page-generator/tools/taskflow-visualizer/parser"
	// Assuming the types package is implicitly used by the above packages
)

func main() {
	// Define command-line flags
	inputFile := flag.String("flowfile", "examples/task_flows/generate_sads_from_nl.flow.yaml", "Path to the input task flow YAML file.")
	outputFile := flag.String("output", "output/task_flow_visualization.html", "Path to the output HTML file.")
	// templateDir := flag.String("templatedir", "./templates", "Directory containing HTML templates (if we were using external templates).")

	flag.Parse()

	// 1. Parse the Task Flow YAML
	log.Printf("Parsing task flow YAML from: %s\n", *inputFile)
	flowDefinition, err := parser.ParseTaskFlowFromFile(*inputFile)
	if err != nil {
		log.Fatalf("Error parsing YAML file: %v\n", err)
	}
	log.Println("Successfully parsed YAML file.")

	// 2. Generate Mermaid Markdown
	log.Println("Generating Mermaid markdown...")
	mermaidMarkdown, err := mermaid.GenerateMermaidMarkdown(flowDefinition)
	if err != nil {
		log.Fatalf("Error generating Mermaid markdown: %v\n", err)
	}
	log.Println("Successfully generated Mermaid markdown.")
	// For debugging, print the markdown:
	// fmt.Println("\n--- Mermaid Markdown ---\n", mermaidMarkdown, "\n----------------------\n")


	// 3. Generate HTML Page
	log.Printf("Generating HTML page to: %s\n", *outputFile)

	// Ensure output directory exists
	outputDir := filepath.Dir(*outputFile)
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		log.Fatalf("Error creating output directory %s: %v\n", outputDir, err)
	}

	file, err := os.Create(*outputFile)
	if err != nil {
		log.Fatalf("Error creating output HTML file %s: %v\n", *outputFile, err)
	}
	defer file.Close()

	pageData := htmlgen.HTMLPageData{
		MermaidMarkdown: mermaidMarkdown,
		FlowName:        flowDefinition.Name, // Pass flow name for potential use in HTML title/header
	}

	err = htmlgen.GenerateHTMLPage(file, pageData)
	if err != nil {
		log.Fatalf("Error generating HTML page: %v\n", err)
	}
	log.Println("Successfully generated HTML page.")
	log.Printf("Visualization saved to: %s\n", *outputFile)
}
