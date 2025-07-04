// public/js/app.js
/**
 * @file Main application orchestrator.
 * Imports and initializes all core application modules (dark mode, translations, SADS styling).
 * Exposes global functions for HTML event handlers if necessary.
 * Defines global event detail types for documentation.
 */

// Module imports are removed as their functions will be available directly
// in the concatenated main.js scope due to the bundling order.
// import { initDarkMode, toggleDarkMode, isDarkModeActive } from './modules/darkMode.js';
// import { initTranslations, setLanguage, getCurrentTranslations } from './modules/translation.js';
// import { initSadsEngine, reapplySadsStyles } from './modules/sadsManager.js';
// import eventBus from './modules/eventBus.js'; // Event bus module is available but not actively used for dispatch/subscribe yet.

/**
 * @typedef {import('./modules/eventBus.js').AppStateEventDetail} AppStateEventDetail
 * For documentation: This is the structure of the `detail` object for 'appStateChanged' CustomEvents.
 * Properties are optional as different modules might only publish parts of the state.
 * e.g., `{ darkMode?: boolean, translationsLoaded?: boolean }`
 */

/**
 * @typedef {import('./modules/eventBus.js').LanguageChangedEventDetail} LanguageChangedEventDetail
 * For documentation: This is the structure of the `detail` object for 'languageChanged' CustomEvents.
 * e.g., `{ lang: string }`
 */

/**
 * Global namespace for functions that need to be callable from inline HTML event attributes.
 * It's generally preferable to attach event listeners programmatically from JavaScript,
 * but this provides a clear access point if inline handlers are used.
 * @global
 * @namespace appGlobal
 */
window.appGlobal = {};

/**
 * Initializes the core application modules in the correct order.
 * This function is set to run when the DOM is fully loaded.
 * @async
 * @private
 */
async function initializeApp() {
  console.log("Initializing App modules...");

  // 1. Initialize Dark Mode.
  // This sets up the dark mode state and applies initial classes.
  // It dispatches an 'appStateChanged' event with `detail: { darkMode: boolean }`.
  initDarkMode();

  // 2. Initialize Translations.
  // This determines the preferred language, loads translations, and applies them.
  // It requires the current dark mode state to dispatch a complete 'appStateChanged' event.
  // It dispatches 'appStateChanged' with `detail: { translationsLoaded: boolean, darkMode: boolean }`
  // and 'languageChanged' with `detail: { lang: string }`.
  await initTranslations(isDarkModeActive());

  // 3. Initialize SADS (Semantic Attribute-Driven Styling) Engine.
  // This instantiates the SADS engine and performs an initial application of styles
  // to all SADS components on the page.
  initSadsEngine();

  console.log(
    `App Initialized: Dark Mode = ${isDarkModeActive()}, Language = ${document.documentElement.lang}`
  );
}

/**
 * Handles the dark mode toggle action. Calls the `toggleDarkMode` function from the
 * darkMode module and then triggers a re-application of SADS styles.
 * Exposed on `window.appGlobal.handleDarkModeToggle`.
 * @public
 */
window.appGlobal.handleDarkModeToggle = function () {
  toggleDarkMode(); // Manages state, localStorage, DOM class, and dispatches its event.

  // Re-apply SADS styles. The SADS engine checks body.class for dark-mode live
  // during color mapping. This call ensures all SADS properties are re-evaluated
  // and components redraw if necessary.
  reapplySadsStyles();
};

/**
 * Sets the application language. Calls the `setLanguage` function from the translation
 * module and then triggers a re-application of SADS styles.
 * Exposed on `window.appGlobal.setAppLanguage`.
 * @param {string} lang - The language code (e.g., "en", "es") to set.
 * @public
 * @async
 */
window.appGlobal.setAppLanguage = async function (lang) {
  if (typeof lang !== "string" || !lang.trim()) {
    console.error(
      "setAppLanguage: lang parameter must be a non-empty string.",
      lang
    );
    return;
  }
  // Pass the current dark mode state for the 'appStateChanged' event dispatched by `setLanguage`.
  await setLanguage(lang, isDarkModeActive());

  // Re-apply SADS styles as text content changes (e.g., longer translated strings)
  // might affect layout or other SADS-controlled styles.
  reapplySadsStyles();
};

// --- Application Entry Point ---
// Defer initialization until the DOM is fully loaded and parsed.
document.addEventListener("DOMContentLoaded", initializeApp);

console.log(
  "app.js orchestrator script loaded. Initialization will occur on DOMContentLoaded."
);
