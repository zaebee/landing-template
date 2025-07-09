package types

// TaskFlowDefinition corresponds to the root of the YAML
type TaskFlowDefinition struct {
	ID           string        `yaml:"id"`
	Version      string        `yaml:"version"`
	Name         string        `yaml:"name"`
	Description  string        `yaml:"description,omitempty"`
	Author       string        `yaml:"author,omitempty"`
	Trigger      Trigger       `yaml:"trigger"`
	DataElements []DataElement `yaml:"data_elements,omitempty"`
	Stages       []Stage       `yaml:"stages"`
}

// Trigger describes what initiates the task flow
type Trigger struct {
	ID             string                 `yaml:"id"`
	Type           string                 `yaml:"type"`
	Description    string                 `yaml:"description,omitempty"`
	FilterCriteria map[string]interface{} `yaml:"filter_criteria,omitempty"` // Kept generic for now
	Outputs        []TriggerOutputMapping `yaml:"outputs,omitempty"`
}

// TriggerOutputMapping defines how trigger data maps to DataElements
type TriggerOutputMapping struct {
	SourcePath    string `yaml:"source_path"`
	DataElementID string `yaml:"data_element_id"`
	Description   string `yaml:"description,omitempty"`
}

// DataElement describes a piece of data in the flow
type DataElement struct {
	ID               string      `yaml:"id"`
	Name             string      `yaml:"name,omitempty"`
	Description      string      `yaml:"description,omitempty"`
	DataType         string      `yaml:"data_type"`
	SchemaDefinition interface{} `yaml:"schema_definition,omitempty"` // string or map
	IsSensitive      bool        `yaml:"is_sensitive,omitempty"`
}

// Stage represents a single step in the task flow
type Stage struct {
	ID                       string               `yaml:"id"`
	Name                     string               `yaml:"name"`
	StageType                string               `yaml:"stage_type"`
	Description              string               `yaml:"description,omitempty"`
	Dependencies             []string             `yaml:"dependencies,omitempty"`
	Inputs                   []StageInputMapping  `yaml:"inputs,omitempty"`
	Outputs                  []StageOutputMapping `yaml:"outputs,omitempty"`
	OnError                  []ErrorHandlingRule  `yaml:"on_error,omitempty"`
	TimeoutSeconds           int                  `yaml:"timeout_seconds,omitempty"`

	// Fields for specific stage types - using interface{} or map for details for now
	TransformEngine          string                 `yaml:"transform_engine,omitempty"`    // For Transformation
	TransformLogic           interface{}            `yaml:"transform_logic,omitempty"`     // For Transformation (could be string or map)
	ActionType               string                 `yaml:"action_type,omitempty"`         // For ActionCall
	ActionDetails            map[string]interface{} `yaml:"action_details,omitempty"`      // For ActionCall (map)
	DecisionLogicEngine      string                 `yaml:"decision_logic_engine,omitempty"` // For DecisionPoint
	Branches                 []DecisionBranch       `yaml:"branches,omitempty"`              // For DecisionPoint
	DefaultBranchNextStageID string                 `yaml:"default_branch_next_stage_id,omitempty"` // For DecisionPoint
}

// StageInputMapping defines data consumed by a stage
type StageInputMapping struct {
	DataElementID string `yaml:"data_element_id"`
	AsName        string `yaml:"as_name,omitempty"`
	IsRequired    bool   `yaml:"is_required,omitempty"`
}

// StageOutputMapping defines data produced by a stage
type StageOutputMapping struct {
	DataElementID string `yaml:"data_element_id"`
	ProducedAs    string `yaml:"produced_as,omitempty"`
}

// ErrorHandlingRule defines error handling for a stage
type ErrorHandlingRule struct {
	ErrorPattern             string                 `yaml:"error_pattern"`
	Action                   string                 `yaml:"action"`
	ActionParams             map[string]interface{} `yaml:"action_params,omitempty"`
	OutputErrorDataElementID string                 `yaml:"output_error_data_element_id,omitempty"`
}

// DecisionBranch defines a conditional branch for a DecisionPoint stage
type DecisionBranch struct {
	Condition     string `yaml:"condition"` // Simplified to string for now, could be map for complex conditions
	NextStageID   string `yaml:"next_stage_id"`
	Description   string `yaml:"description,omitempty"`
}
