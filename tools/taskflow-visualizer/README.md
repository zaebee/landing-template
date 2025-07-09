# Task Flow Visualizer (Go CLI Tool)

This directory contains a Go command-line tool that can parse a task flow definition written in YAML and generate a static HTML page visualizing the flow as a Mermaid.js graph.

**Note:** The primary method for visualizing task flows is now via the `<task-flow-viewer>` Web Component. See documentation at `public/js/components/README.md` (relative path from repository root: `../../public/js/components/README.md`). This Go tool can still be useful for generating static HTML files or for backend processing of flow definitions if needed.

## Prerequisites

- Go (version 1.16 or later recommended)

## Ontology

The tool expects YAML files that conform to the task flow ontology defined by this project. An example flow definition can be found at `../../../examples/task_flows/generate_sads_from_nl.flow.yaml`.

## Build

Navigate to this directory (`tools/taskflow-visualizer`) and run:
```bash
go build -o taskflow-visualizer
```

## Usage

```bash
./taskflow-visualizer -flowfile <path_to_flow.yaml> -output <path_to_output.html>
```

**Flags:**
- `-flowfile string`: Path to the input task flow YAML file. (Default relative to executable's run location: `examples/task_flows/generate_sads_from_nl.flow.yaml`)
- `-output string`: Path to the output HTML file. (Default: `output/task_flow_visualization.html`)

**Example (from repository root):**
```bash
./tools/taskflow-visualizer/taskflow-visualizer -flowfile examples/task_flows/generate_sads_from_nl.flow.yaml -output output/sads_flow_static.html
```
Open the generated HTML file in a browser. It requires an internet connection for the Mermaid.js CDN.

## Functionality

The Go tool performs these main steps:
1.  **Parses YAML:** Reads the flow definition YAML into Go structs (`types/taskflow_types.go`).
2.  **Generates Mermaid Markdown:** Converts the parsed structure into Mermaid graph syntax (`mermaid/mermaid_generator.go`).
3.  **Generates HTML Page:** Embeds the Mermaid markdown into a basic HTML template (`htmlgen/html_generator.go`).

This tool formed the basis for the client-side JavaScript logic now present in the Web Component.
```
