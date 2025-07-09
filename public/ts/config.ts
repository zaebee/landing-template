// public/ts/config.ts

// Global application configuration
interface AppConfig {
  mcpServerUrl: string;
  defaultClientAgentIdPrefix: string;
  defaultTargetAgentId: string;
  knownAgents: { [key: string]: string }; // e.g., { jules: "jules_agent_actual_id", eddy: "eddy_agent_actual_id" }
}

// Access configuration from a global object if defined (e.g., by server-rendered script tag)
// Otherwise, use default values. This allows overriding config easily for different environments.
declare global {
  interface Window {
    AppConfig?: Partial<AppConfig>;
  }
}

const defaultConfig: AppConfig = {
  mcpServerUrl: "http://localhost:8000/mcp/sse", // Default SSE endpoint for MCP
  defaultClientAgentIdPrefix: "ide_extension_client_",
  defaultTargetAgentId: "jules", // Default agent to target in the panel
  knownAgents: {
    jules: "jules", // In this PoC, the display name is the agent ID
    eddy: "eddy",
    eliza: "eliza",
  },
};

// Merge defaultConfig with window.AppConfig if it exists
const appConfig: AppConfig = {
  ...defaultConfig,
  ...(window.AppConfig || {}),
};

export const mcpServerUrl = appConfig.mcpServerUrl;
export const clientAgentIdPrefix = appConfig.defaultClientAgentIdPrefix;
export const defaultTargetAgentId = appConfig.defaultTargetAgentId;
export const knownAgents = appConfig.knownAgents;

console.log("App Configuration Loaded:", appConfig);
