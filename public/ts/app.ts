// public/ts/app.ts
/**
 * @file Main application orchestrator.
 * Imports and initializes all core application modules (dark mode, translations, SADS styling).
 * Exposes global functions for HTML event handlers if necessary.
 */

import { initDarkMode, toggleDarkMode, isDarkModeActive } from './modules/darkMode';
import { initTranslations, setLanguage } from './modules/translation'; // getCurrentTranslations not used directly by app.js
import { initSadsEngine, reapplySadsStyles } from './modules/sadsManager';
// eventBus types AppStateEventDetail and LanguageChangedEventDetail are used by other modules,
// but eventBus itself (if it were an actual emitter object) isn't directly used by app.js logic.

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
 * Initializes the core application modules in the correct order.
 * This function is set to run when the DOM is fully loaded.
 * @async
 * @private
 */
async function initializeApp(): Promise<void> {
  console.log("Initializing App modules...");

  // 1. Initialize Dark Mode.
  initDarkMode();

  // 2. Initialize Translations.
  await initTranslations(isDarkModeActive());

  // 3. Initialize SADS Engine.
  await initSadsEngine();

  console.log(
    `App Initialized: Dark Mode = ${isDarkModeActive()}, Language = ${document.documentElement.lang}`
  );
}

window.appGlobal.handleDarkModeToggle = async function (): Promise<void> {
  toggleDarkMode();
  await reapplySadsStyles();
};

window.appGlobal.setAppLanguage = async function (lang: string): Promise<void> {
  if (typeof lang !== "string" || !lang.trim()) {
    console.error("setAppLanguage: lang parameter must be a non-empty string.", lang);
    return;
  }
  await setLanguage(lang, isDarkModeActive());
  await reapplySadsStyles(); // Ensure this is awaited if setLanguage itself doesn't trigger it reliably enough
};

document.addEventListener("DOMContentLoaded", initializeApp);

console.log("app.ts orchestrator script loaded. Initialization will occur on DOMContentLoaded.");

// Export something to make it a module, if nothing else is exported.
// This can be useful if other TS files might want to import types or utilities from app.ts in the future,
// though for now, its primary role is to orchestrate and attach to window.
export {};
