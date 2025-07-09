package parser

import (
	"io/ioutil"
	"os" // Used for os.ReadFile in Go 1.16+

	"gopkg.in/yaml.v3"
	"landing-page-generator/tools/taskflow-visualizer/types" // Adjusted import path
)

// ParseTaskFlowFromFile reads a YAML file from the given file path,
// parses it, and returns a TaskFlowDefinition struct.
func ParseTaskFlowFromFile(filePath string) (*types.TaskFlowDefinition, error) {
	// Use os.ReadFile (Go 1.16+) for simplicity if ioutil.ReadFile is deprecated
	// For broader compatibility, ioutil.ReadFile is fine.
	yamlFile, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	var flowDefinition types.TaskFlowDefinition
	err = yaml.Unmarshal(yamlFile, &flowDefinition)
	if err != nil {
		return nil, err
	}

	return &flowDefinition, nil
}
