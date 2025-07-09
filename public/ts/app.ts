// public/ts/app.ts
/**
 * @file Main application orchestrator.
 * Imports and initializes all core application modules (dark mode, translations, SADS styling).
 * Exposes global functions for HTML event handlers if necessary and attaches them.
 */

import {
  initDarkMode,
  toggleDarkMode,
  isDarkModeActive,
} from "./modules/darkMode.js";
import { initTranslations, setLanguage } from "./modules/translation.js"; // getCurrentTranslations not used directly by app.js
import { initSadsEngine, reapplySadsStyles } from "./modules/sadsManager.js";
// eventBus types AppStateEventDetail and LanguageChangedEventDetail are used by other modules,
// but eventBus itself (if it were an actual emitter object) isn't directly used by app.js logic.
import { initMcpComponent } from "./components/mcp.js"; // This is for the SADS AI test component
import { initIdeAgentPanel } from "./components/ide_agent_panel.js"; // New IDE Agent Panel
import { initChatComponent } from "./components/chat.js"; // Import the new chat component initializer
import { initSliderComponent } from "./components/slider.js"; // Import the new slider component initializer

// Define the appGlobal structure for window augmentation
interface AppGlobal {
  handleDarkModeToggle?: () => Promise<void>;
  setAppLanguage?: (lang: string) => Promise<void>;
  // Add other global functions if needed
}

// Augment the global Window interface
declare global {
  interface Window {
    appGlobal: AppGlobal;
  }
}

// Initialize appGlobal on window
window.appGlobal = window.appGlobal || {};

/**
 * Attaches event listeners to interactive elements.
 * Should be called after the DOM is ready and elements are available.
 * @private
 */
function _attachEventListeners(): void {
  // Dark Mode Toggle Button
  const darkModeButton = document.getElementById("dark-mode-toggle");
  if (darkModeButton && window.appGlobal.handleDarkModeToggle) {
    darkModeButton.addEventListener(
      "click",
      window.appGlobal.handleDarkModeToggle
    );
    console.log("Dark mode toggle event listener attached.");
  } else {
    console.warn(
      "Dark mode toggle button or handler not found. Listener not attached."
    );
  }

  // Language Switcher Buttons
  // Example: Assuming language buttons have a common class or parent
  const languageSwitcher = document.getElementById("language-switcher");
  if (languageSwitcher && window.appGlobal.setAppLanguage) {
    const langButtons =
      languageSwitcher.querySelectorAll<HTMLButtonElement>("button[data-lang]");
    langButtons.forEach((button) => {
      const lang = button.dataset.lang;
      if (lang) {
        button.addEventListener("click", () => {
          if (window.appGlobal.setAppLanguage) {
            // Check again for type safety in closure
            window.appGlobal.setAppLanguage(lang);
          }
        });
      }
    });
    console.log("Language switcher event listeners attached.");
  } else {
    console.warn(
      "Language switcher or setAppLanguage handler not found. Listeners not attached."
    );
  }
}

/**
 * Initializes the core application modules in the correct order.
 * This function is set to run when the DOM is fully loaded.
 * @async
 * @private
 */
async function initializeApp(): Promise<void> {
  console.log("Initializing App modules...");

  // 1. Initialize Dark Mode (sets up state and initial body class).
  initDarkMode();

  // 2. Initialize Translations (may depend on dark mode state for initial load).
  await initTranslations(isDarkModeActive());

  // 3. Initialize SADS Engine (applies initial styles based on body class etc.).
  await initSadsEngine();

  // 4. Initialize specific components that require JS interaction.
  initMcpComponent(); // Initialize the SADS AI test MCP component
  initIdeAgentPanel(); // Initialize the new IDE Agent Panel
  initChatComponent(); // Initialize the Chat Component
  initSliderComponent(); // Initialize the Image Slider Component

  // 5. Attach event listeners now that everything is initialized.
  _attachEventListeners();

  console.log(
    `App Initialized: Dark Mode = ${isDarkModeActive()}, Language = ${document.documentElement.lang}`
  );
}

// Define global handlers
window.appGlobal.handleDarkModeToggle = async function (): Promise<void> {
  await toggleDarkMode(); // toggleDarkMode now calls reapplySadsStyles internally
};

window.appGlobal.setAppLanguage = async function (lang: string): Promise<void> {
  if (typeof lang !== "string" || !lang.trim()) {
    console.error(
      "setAppLanguage: lang parameter must be a non-empty string.",
      lang
    );
    return;
  }
  await setLanguage(lang, isDarkModeActive()); // setLanguage updates translations
  await reapplySadsStyles(); // Reapply SADS styles after language change in case text direction/content affects layout
};

// Main entry point: Wait for DOM to be ready, then initialize.
document.addEventListener("DOMContentLoaded", initializeApp);

console.log(
  "app.ts orchestrator script loaded. Initialization will occur on DOMContentLoaded."
);

// Export something to make it a module, if nothing else is exported.
export {};
