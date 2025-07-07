interface SADSEngine {
  [key: string]: any;
}

interface SadsManager {
  initSadsEngine(): Promise<void>;
  reapplySadsStyles(): Promise<void>;
  [key: string]: any;
}

interface SadsDefaultTheme {
  [key: string]: any;
}

// Extend Window interface to include SADS globals
// Ensure this file is treated as a module by TypeScript for global augmentation to work.
// Adding an export {} at the end of the file achieves this.
declare global {
  interface Window {
    SADSEngine?: SADSEngine;
    sadsManager?: SadsManager;
    SADS_DEFAULT_THEME?: SadsDefaultTheme;
  }
}

class SadsPreviewerApp {
  private rootElement: HTMLElement;
  private componentSelector: HTMLSelectElement;
  private componentRenderTarget: HTMLDivElement;
  private attributesDisplay: HTMLPreElement;

  constructor(rootElement: HTMLElement) {
    this.rootElement = rootElement;

    const selector = this.rootElement.querySelector(
      "#component-selector"
    ) as HTMLSelectElement | null;
    const renderTarget = this.rootElement.querySelector(
      "#component-render-target"
    ) as HTMLDivElement | null;
    const attrDisplay = this.rootElement.querySelector(
      "#attributes-display"
    ) as HTMLPreElement | null;

    if (!selector || !renderTarget || !attrDisplay) {
      console.error(
        "Essential DOM elements not found within the provided root for SADS Previewer."
      );
      if (renderTarget) {
        renderTarget.innerHTML =
          '<p style="color: red;">Error: Previewer DOM setup failed within root. Essential elements missing.</p>';
      }
      // Throw an error or set a flag to prevent init() if critical elements are missing
      // For now, assigning to potentially null and init will handle this with null checks or assertions
      this.componentSelector = null as any; // Initialize to satisfy compiler, error handled
      this.componentRenderTarget = renderTarget as any;
      this.attributesDisplay = null as any;
      return;
    }
    this.componentSelector = selector;
    this.componentRenderTarget = renderTarget;
    this.attributesDisplay = attrDisplay;

    this.init();
  }

  private init(): void {
    if (
      !this.componentSelector ||
      !this.componentRenderTarget ||
      !this.attributesDisplay
    ) {
      // This check is redundant if constructor exits, but good for safety
      console.error(
        "Cannot initialize SadsPreviewerApp due to missing critical elements."
      );
      return;
    }

    if (
      typeof window.SADSEngine === "undefined" ||
      typeof window.sadsManager === "undefined" ||
      typeof window.SADS_DEFAULT_THEME === "undefined"
    ) {
      console.error(
        "SADS Engine, Manager, or Default Theme not loaded. Previewer may not function correctly."
      );
      this.componentRenderTarget.innerHTML =
        '<p style="color: red;">Error: SADS scripts not loaded. Previewer functionality is limited.</p>';
    } else {
      window.sadsManager
        .initSadsEngine()
        .then(() => {
          console.log("SADS Engine initialized by previewer instance.");
        })
        .catch((error: Error) => {
          console.error(
            "Error initializing SADS Engine in previewer instance:",
            error.message
          );
        });
    }

    fetch("/api/sads/components")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json() as Promise<string[]>;
      })
      .then((components) => {
        this.componentSelector.innerHTML =
          '<option value="">-- Select a Component --</option>';
        components.forEach((componentName) => {
          const option = document.createElement("option");
          option.value = componentName;
          option.textContent =
            componentName.charAt(0).toUpperCase() + componentName.slice(1);
          this.componentSelector.appendChild(option);
        });
      })
      .catch((error: Error) => {
        console.error("Error fetching component list:", error);
        this.componentSelector.innerHTML =
          '<option value="">-- Error Loading --</option>';
        this.attributesDisplay.textContent = `Error loading components: ${error.message}`;
      });

    this.componentSelector.addEventListener("change", (event) => {
      const selectElement = event.target as HTMLSelectElement;
      const componentName = selectElement.value;

      if (!componentName) {
        this.componentRenderTarget.innerHTML = "";
        this.attributesDisplay.textContent = "No element selected.";
        return;
      }

      this.componentRenderTarget.innerHTML = `<p>Loading ${componentName}...</p>`;
      this.attributesDisplay.textContent = "Loading component...";

      fetch(`/api/sads/component/${componentName}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error(
              `HTTP error! status: ${response.status} for ${componentName}`
            );
          }
          return response.text();
        })
        .then((htmlContent) => {
          this.componentRenderTarget.innerHTML = htmlContent;
          if (
            window.sadsManager &&
            typeof window.sadsManager.reapplySadsStyles === "function"
          ) {
            window.sadsManager
              .reapplySadsStyles()
              .then(() => {
                console.log(`SADS styles reapplied for ${componentName}`);
              })
              .catch((error: Error) => {
                console.error(
                  `Error reapplying SADS styles for ${componentName}:`,
                  error.message
                );
              });
          } else {
            console.warn(
              "sadsManager.reapplySadsStyles() is not available. SADS styles might not be applied to dynamic content."
            );
          }
          this.attributesDisplay.textContent =
            "Click on an element in the preview to see its SADS attributes.";
        })
        .catch((error: Error) => {
          console.error(`Error fetching component ${componentName}:`, error);
          this.componentRenderTarget.innerHTML = `<p style="color: red;">Error loading component ${componentName}: ${error.message}</p>`;
          this.attributesDisplay.textContent = `Error loading component: ${error.message}`;
        });
    });

    this.componentRenderTarget.addEventListener("click", (event) => {
      const clickTarget = event.target as HTMLElement;
      const targetElement = clickTarget.closest(
        "[data-sads-component], [data-sads-element], [data-sads-padding]"
      ) as HTMLElement | null;

      if (
        !targetElement ||
        !this.componentRenderTarget.contains(targetElement)
      ) {
        this.attributesDisplay.textContent =
          "Clicked outside a recognized SADS element or component not fully loaded.";
        return;
      }

      const sadsAttributes: { [key: string]: string } = {};
      let hasSadsAttributes = false;
      for (const attr of Array.from(targetElement.attributes)) {
        if (attr.name.startsWith("data-sads-")) {
          sadsAttributes[attr.name] = attr.value;
          hasSadsAttributes = true;
        }
      }

      if (hasSadsAttributes) {
        let displayText = `Element: <${targetElement.tagName.toLowerCase()}>\n\n`;
        displayText += JSON.stringify(sadsAttributes, null, 2);
        this.attributesDisplay.textContent = displayText;
      } else {
        this.attributesDisplay.textContent = `Element: <${targetElement.tagName.toLowerCase()}>\n\nNo data-sads-* attributes found on this specific element. Try its parent or children.`;
      }
    });
  }
}

// The instantiation will be handled in sads_previewer.html like:
// <script type="module">
//  import './public/ts/sadsPreviewer.js'; // ensure SadsPreviewerApp is on window or exported
//  document.addEventListener("DOMContentLoaded", () => {
//    const previewerRootElement = document.getElementById("sads-previewer-main-container");
//    if (previewerRootElement) {
//      new SadsPreviewerApp(previewerRootElement);
//    } else {
//      console.error("SADS Previewer root element not found.");
//    }
//  });
// </script>
// SadsPreviewerApp will now self-initialize. No need to expose it globally.

document.addEventListener("DOMContentLoaded", () => {
  const previewerRootElement = document.getElementById(
    "sads-previewer-container"
  );
  if (previewerRootElement) {
    // Check if SADS globals are ready before instantiating.
    // This is a simple check; a more robust solution might involve promises or events
    // if script loading order of sadsManager etc. is not guaranteed before this.
    // However, all are type="module" defer, so they should parse, then execute in order before DOMContentLoaded.
    if (window.sadsManager && window.SADSEngine && window.SADS_DEFAULT_THEME) {
      new SadsPreviewerApp(previewerRootElement);
    } else {
      console.error(
        "SADS core scripts (manager, engine, theme) not ready on DOMContentLoaded. SADS Previewer will not initialize."
      );
      const body = document.querySelector("body");
      if (body) {
        body.innerHTML =
          '<p style="color: red; font-family: sans-serif; padding: 20px;">Critical Error: SADS core scripts not ready. Previewer initialization failed.</p>';
      }
    }
  } else {
    console.error(
      "SADS Previewer root element (#sads-previewer-container) not found. Previewer will not initialize."
    );
    const body = document.querySelector("body");
    if (body) {
      body.innerHTML =
        '<p style="color: red; font-family: sans-serif; padding: 20px;">Critical Error: SADS Previewer application could not find its root HTML element. Initialization failed.</p>';
    }
  }
});

// Add this to ensure the file is treated as a module by TypeScript.
export {};
