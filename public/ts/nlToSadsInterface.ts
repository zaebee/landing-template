// public/ts/nlToSadsInterface.ts
import { SADSEngine } from './sads-style-engine'; // Assuming SADSEngine is exported

interface SadsAttributes {
    [key: string]: string; // e.g., "data-sads-bg-color": "text-accent"
}

class NLToSadsInterface {
    private sadsEngine: SADSEngine;
    private inputElement: HTMLInputElement | null;
    private submitButton: HTMLButtonElement | null;
    private targetElement: HTMLElement | null;

    constructor(sadsEngine: SADSEngine, inputId: string, buttonId: string, targetId: string) {
        this.sadsEngine = sadsEngine;
        this.inputElement = document.getElementById(inputId) as HTMLInputElement | null;
        this.submitButton = document.getElementById(buttonId) as HTMLButtonElement | null;
        this.targetElement = document.getElementById(targetId) as HTMLElement | null;

        if (!this.inputElement || !this.submitButton || !this.targetElement) {
            console.error("NLToSadsInterface: Could not find all required DOM elements. Ensure IDs are correct and elements exist.");
            // Optionally throw an error or disable functionality
            return;
        }

        this.init();
    }

    private init(): void {
        // Ensure submitButton is not null before adding event listener
        if (this.submitButton) {
            this.submitButton.addEventListener('click', () => this.handleSubmit());
        } else {
            console.error("NLToSadsInterface: Submit button not found, cannot initialize.");
        }
    }

    private async handleSubmit(): Promise<void> {
        if (!this.inputElement || !this.targetElement) {
            console.warn("NLToSadsInterface: Input or target element not available for handleSubmit.");
            return;
        }

        const nlText = this.inputElement.value;
        if (!nlText.trim()) {
            // Consider providing user feedback directly in the UI instead of alert
            alert("Please enter a style description.");
            return;
        }

        try {
            const sadsAttrs = await this.fetchSadsAttributesFromNL(nlText);
            this.applyAttributesToTarget(sadsAttrs);
        } catch (error) {
            console.error("Error processing natural language input:", error);
            // Consider providing user feedback directly in the UI
            alert("Failed to apply styles. See console for details.");
        }
    }

    // This will call the MOCKED API
    private async fetchSadsAttributesFromNL(nlText: string): Promise<SadsAttributes> {
        console.log(`Sending to mock API: "${nlText}"`);
        // In a real scenario, this would be:
        // const response = await fetch('/api/nl-to-sads', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify({ query: nlText })
        // });
        // if (!response.ok) throw new Error('API request failed');
        // return response.json();

        // Mocked implementation will be filled here
        return this.mockNlToSadsApi(nlText);
    }

    // Mock API function
    private mockNlToSadsApi(nlText: string): Promise<SadsAttributes> {
        return new Promise((resolve) => {
            const lowerText = nlText.toLowerCase();
            const attributes: SadsAttributes = {};

            console.log(`Mock API processing: "${nlText}"`);

            // Simple keyword-based logic for mocking
            // Attributes returned should be camelCase keys for dataset properties,
            // e.g., "sadsBgColor" for "data-sads-bg-color"
            if (lowerText.includes("blue")) {
                attributes["sadsBgColor"] = "text-accent";
            } else if (lowerText.includes("red")) {
                attributes["sadsBgColor"] = "custom:red";
            } else if (lowerText.includes("green")) {
                attributes["sadsBgColor"] = "custom:green";
            } else if (lowerText.includes("dark surface")) {
                attributes["sadsBgColor"] = "surface-dark";
            }


            if (lowerText.includes("round")) {
                attributes["sadsBorderRadius"] = "l";
            } else if (lowerText.includes("square")) {
                attributes["sadsBorderRadius"] = "none";
            }

            if (lowerText.includes("large text")) {
                attributes["sadsFontSize"] = "l";
            } else if (lowerText.includes("small text")) {
                attributes["sadsFontSize"] = "s";
            }

            if (lowerText.includes("primary text color")) {
                attributes["sadsTextColor"] = "text-primary";
            } else if (lowerText.includes("accent text color")) {
                attributes["sadsTextColor"] = "text-accent";
            }

            if (lowerText.includes("padding") || lowerText.includes("padded")) {
                if (lowerText.includes("small padding")) {
                    attributes["sadsPadding"] = "s";
                } else if (lowerText.includes("large padding")) {
                    attributes["sadsPadding"] = "l";
                } else {
                    attributes["sadsPadding"] = "m"; // Default medium padding
                }
            }

            if (lowerText.includes("subtle shadow")) {
                attributes["sadsShadow"] = "subtle";
            } else if (lowerText.includes("medium shadow")) {
                attributes["sadsShadow"] = "medium";
            } else if (lowerText.includes("no shadow")) {
                attributes["sadsShadow"] = "none";
            }


            // Simulate network delay
            setTimeout(() => {
                console.log("Mock API response:", attributes);
                resolve(attributes);
            }, 300); // Reduced delay slightly
        });
    }

    private applyAttributesToTarget(attributes: SadsAttributes): void {
        if (!this.targetElement) {
            console.warn("NLToSadsInterface: Target element not available for applying attributes.");
            return;
        }

        // Clear previous SADS attributes to avoid conflicts, or merge carefully.
        // For simplicity, let's clear all data-sads-* attributes first.
        // Keep data-sads-component and other non-styling sads attributes if any.
        const datasetKeys = Object.keys(this.targetElement.dataset);
        for (const key of datasetKeys) {
            // A more robust check might be needed if there are other data-sads-* attributes
            // that are not for direct styling and should be preserved.
            // For now, preserving only 'sadsComponent'.
            if (key.startsWith('sads') && key.toLowerCase() !== 'sadscomponent') {
                delete this.targetElement.dataset[key];
            }
        }

        for (const attrName in attributes) {
            if (Object.prototype.hasOwnProperty.call(attributes, attrName)) {
                let datasetKey = attrName;
                // Convert kebab-case (data-sads-bg-color) to camelCase (sadsBgColor) for dataset access
                if (datasetKey.startsWith("data-")) {
                    datasetKey = datasetKey.substring("data-".length);
                }
                // now datasetKey is like "sads-bg-color" or "sadsBgColor" (if API returns camelCase)
                // Convert "sads-bg-color" to "sadsBgColor"
                datasetKey = datasetKey.replace(/-([a-z])/g, (g) => g[1].toUpperCase());

                this.targetElement.dataset[datasetKey] = attributes[attrName];
            }
        }

        console.log("Applied SADS attributes to target. Current dataset:", this.targetElement.dataset);

        // Trigger SADS engine to re-process styles for the target element
        this.sadsEngine.applyStylesTo(this.targetElement);
    }
}

export { NLToSadsInterface };

// Example Initialization (would typically be in an app.js or similar entry point)
// This requires sads-style-engine.ts and sads-default-theme.ts to be compiled and their exports available.
//
// import { sadsDefaultTheme } from './sads-default-theme';
//
// if (typeof window !== 'undefined' && typeof document !== 'undefined') {
//     document.addEventListener('DOMContentLoaded', () => {
//         // Ensure SADSEngine and sadsDefaultTheme are available, e.g., via globals from bundled JS
//         // This is a simplified example; a real app would use module imports if possible post-bundling.
//         const engine = new (window as any).SADSEngine({}, (window as any).sadsDefaultTheme);
//         const nlInterface = new NLToSadsInterface(engine, 'nl-input', 'nl-submit-button', 'sads-target-element');
//
//         const targetElement = document.getElementById('sads-target-element') as HTMLElement | null;
//         if (targetElement && engine) {
//             engine.applyStylesTo(targetElement); // Apply initial SADS styles if any
//         }
//     });
// }
