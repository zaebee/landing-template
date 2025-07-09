# Task Flow Visualizer

This tool parses a task flow definition written in YAML (following a specific ontology) and generates an HTML page that visualizes the flow as a Mermaid.js graph.

## Prerequisites

- Go (version 1.16 or later recommended)
- An internet connection (for the browser to fetch the Mermaid.js library from a CDN when viewing the HTML)

## Ontology

The visualizer expects YAML files that conform to the task flow ontology defined by this project. Key elements include:
- `TaskFlowDefinition` (root)
- `Trigger`
- `DataElement`
- `Stage` (with various types like `Transformation`, `ActionCall`, `DecisionPoint`)

An example flow definition can be found at `../../../examples/task_flows/generate_sads_from_nl.flow.yaml`. (Note: Relative path from this README's location).

## Directory Structure

- `main.go`: The main application.
- `types/taskflow_types.go`: Go struct definitions for the task flow ontology.
- `parser/parser.go`: YAML parsing logic.
- `mermaid/mermaid_generator.go`: Logic to generate Mermaid markdown from parsed data.
- `htmlgen/html_generator.go`: Logic to generate the final HTML page.

## Build

To build the visualizer, navigate to this directory (`tools/taskflow-visualizer`) in your terminal and run:

```bash
go build -o taskflow-visualizer
```

This will create an executable named `taskflow-visualizer` (or `taskflow-visualizer.exe` on Windows).

## Usage

Run the visualizer from the command line, specifying the input YAML flow definition file and the desired output HTML file path.

```bash
./taskflow-visualizer -flowfile <path_to_flow.yaml> -output <path_to_output.html>
```

**Flags:**

- `-flowfile string`: Path to the input task flow YAML file.
  (default: `examples/task_flows/generate_sads_from_nl.flow.yaml`)
  *Note: The default path is relative to where you run the executable. If you run it from the repository root, it would be `examples/task_flows/generate_sads_from_nl.flow.yaml`. If you run it from `tools/taskflow-visualizer/`, the relative path to the example would be `../../examples/task_flows/generate_sads_from_nl.flow.yaml`.*
- `-output string`: Path to the output HTML file.
  (default: `output/task_flow_visualization.html`)

**Example (running from the `tools/taskflow-visualizer` directory):**

```bash
./taskflow-visualizer -flowfile ../../examples/task_flows/generate_sads_from_nl.flow.yaml -output ../../output/sads_flow.html
```

Or, if you are in the repository root:
```bash
./tools/taskflow-visualizer/taskflow-visualizer -flowfile examples/task_flows/generate_sads_from_nl.flow.yaml -output output/sads_flow.html
```

After running, open the generated HTML file (e.g., `output/sads_flow.html`) in a web browser to view the diagram.

## Output Directory

The tool will attempt to create the output directory if it doesn't exist (e.g., the `output/` directory in the default output path).

## Current Limitations (Proof of Concept)

- The visualization currently focuses on the main flow paths and decision branches. Explicit visualization of `on_error` paths defined in the YAML (that are not part of standard dependencies) is limited in the current Mermaid generator.
- Styling is very basic.
- The full richness of the ontology (e.g., detailed inputs/outputs per stage, specific action details) is parsed but not yet fully rendered in detail alongside the Mermaid graph. This version focuses on the graph structure.
```
