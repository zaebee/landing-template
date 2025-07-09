package mermaid

import (
	"fmt"
	"strings"

	"landing-page-generator/tools/taskflow-visualizer/types" // Adjusted import path
)

// GenerateMermaidMarkdown generates Mermaid graph syntax from a TaskFlowDefinition.
func GenerateMermaidMarkdown(flow *types.TaskFlowDefinition) (string, error) {
	if flow == nil {
		return "", fmt.Errorf("input TaskFlowDefinition is nil")
	}

	var sb strings.Builder

	sb.WriteString("graph TD\n") // Top-Down graph

	// Subgraph for the main flow (optional, but can help group)
	// sb.WriteString(fmt.Sprintf("    subgraph %s_v%s [%s]\n", flow.ID, flow.Version, flow.Name))
	// sb.WriteString("        direction LR\n") // Optional: if stages flow better Left-to-Right visually

	// Define Trigger node
	triggerID := SanitizeMermaidID(flow.Trigger.ID)
	triggerName := SanitizeMermaidLabel(fmt.Sprintf("%s (%s)", flow.Trigger.ID, flow.Trigger.Type))
	sb.WriteString(fmt.Sprintf("    %s[%s]\n", triggerID, triggerName))

	// Define all stage nodes first
	for _, stage := range flow.Stages {
		stageID := SanitizeMermaidID(stage.ID)
		stageLabel := SanitizeMermaidLabel(fmt.Sprintf("%s (%s)", stage.Name, stage.StageType))

		switch stage.StageType {
		case "DecisionPoint":
			sb.WriteString(fmt.Sprintf("    %s{%s}\n", stageID, stageLabel)) // Diamond shape
		case "Transformation", "ActionCall": // Add other types that should be standard boxes
			sb.WriteString(fmt.Sprintf("    %s[%s]\n", stageID, stageLabel)) // Default rectangle
		default:
			sb.WriteString(fmt.Sprintf("    %s(%s)\n", stageID, stageLabel)) // Stadium shape for others/default
		}
	}
	// sb.WriteString("    end\n") // End subgraph

	// Define connections from Trigger to initial stages
	// This assumes initial stages have no dependencies or depend on a conceptual "trigger" ID.
	// For simplicity, we'll connect trigger to stages with no explicit dependencies for now.
	// A more robust way would be to have stages explicitly depend on trigger.ID if that's the model.
	initialStageFound := false
	for _, stage := range flow.Stages {
		if len(stage.Dependencies) == 0 {
			sb.WriteString(fmt.Sprintf("    %s --> %s\n", triggerID, SanitizeMermaidID(stage.ID)))
			initialStageFound = true
		}
	}
	if !initialStageFound && len(flow.Stages) > 0 {
		// If no stages explicitly have zero dependencies, perhaps link trigger to the first stage in the list as a fallback?
		// Or, this indicates a flow definition issue if no clear start after trigger.
		// For now, we'll just proceed. The user might define dependencies on the trigger.ID.
	}


	// Define connections between stages based on dependencies and decision branches
	for _, stage := range flow.Stages {
		currentStageID := SanitizeMermaidID(stage.ID)

		// Dependencies
		for _, depID := range stage.Dependencies {
			sanitizedDepID := SanitizeMermaidID(depID)
			// Check if dependency is the trigger itself
			if sanitizedDepID == triggerID {
				sb.WriteString(fmt.Sprintf("    %s --> %s\n", triggerID, currentStageID))
			} else {
				// Ensure the dependency stage exists to avoid pointing to nothing (Mermaid handles this gracefully usually)
				sb.WriteString(fmt.Sprintf("    %s --> %s\n", sanitizedDepID, currentStageID))
			}
		}

		// DecisionPoint branches
		if stage.StageType == "DecisionPoint" {
			for _, branch := range stage.Branches {
				branchLabel := SanitizeMermaidLabel(branch.Condition)
				if branch.Description != "" {
					branchLabel = SanitizeMermaidLabel(fmt.Sprintf("%s [%s]", branch.Condition, branch.Description))
				}
				nextStageID := SanitizeMermaidID(branch.NextStageID)
				sb.WriteString(fmt.Sprintf("    %s -- \"%s\" --> %s\n", currentStageID, branchLabel, nextStageID))
			}
			if stage.DefaultBranchNextStageID != "" {
				defaultNextStageID := SanitizeMermaidID(stage.DefaultBranchNextStageID)
				sb.WriteString(fmt.Sprintf("    %s -- \"Default\" --> %s\n", currentStageID, defaultNextStageID))
			}
		}
	}

	return sb.String(), nil
}

// SanitizeMermaidID ensures the ID is valid for Mermaid.
// Mermaid IDs should not contain spaces or special characters that might break syntax.
// They are typically alphanumeric.
func SanitizeMermaidID(id string) string {
	// Replace common problematic characters. This is a basic sanitizer.
	id = strings.ReplaceAll(id, "-", "_")
	id = strings.ReplaceAll(id, " ", "_")
	id = strings.ReplaceAll(id, ":", "_")
	id = strings.ReplaceAll(id, "/", "_")
	// Add more replacements if needed, or use a regex for stricter alphanumeric enforcement.
	// For example, a regex `[^a-zA-Z0-9_]` could replace all non-alphanumeric/underscore chars.
	return id
}

// SanitizeMermaidLabel ensures the label content is safe for Mermaid strings.
// Primarily, it escapes quotation marks within the label.
func SanitizeMermaidLabel(label string) string {
	// Escape quotes for Mermaid labels, which are typically enclosed in quotes in the syntax.
	// Mermaid uses " (double quotes) for labels with spaces/special chars.
	// If a label contains a quote, it needs to be escaped, e.g., using HTML entity `#quot;`
	// or by ensuring the generator uses appropriate quote marks if the library handles internal escapes.
	// For text within `""`, `"` needs to be `&quot;` or `#quot;`.
	label = strings.ReplaceAll(label, "\"", "#quot;") // #quot; is an HTML entity that Mermaid seems to handle well.
	// Potentially escape other characters if they cause issues.
	return label
}
