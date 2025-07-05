// public/ts/app.ts
/**
 * @file Main application orchestrator.
 * Imports and initializes all core application modules (dark mode, translations, SADS styling).
 * Exposes global functions for HTML event handlers if necessary.
 */
import { initDarkMode, toggleDarkMode, isDarkModeActive } from './modules/darkMode';
import { initTranslations, setLanguage } from './modules/translation'; // getCurrentTranslations not used directly by app.js
import { initSadsEngine, reapplySadsStyles } from './modules/sadsManager';
// Initialize appGlobal on window
window.appGlobal = window.appGlobal || {};
/**
 * Initializes the core application modules in the correct order.
 * This function is set to run when the DOM is fully loaded.
 * @async
 * @private
 */
async function initializeApp() {
    console.log("Initializing App modules...");
    // 1. Initialize Dark Mode.
    initDarkMode();
    // 2. Initialize Translations.
    await initTranslations(isDarkModeActive());
    // 3. Initialize SADS Engine.
    await initSadsEngine();
    console.log(`App Initialized: Dark Mode = ${isDarkModeActive()}, Language = ${document.documentElement.lang}`);
}
window.appGlobal.handleDarkModeToggle = async function () {
    toggleDarkMode();
    await reapplySadsStyles();
};
window.appGlobal.setAppLanguage = async function (lang) {
    if (typeof lang !== "string" || !lang.trim()) {
        console.error("setAppLanguage: lang parameter must be a non-empty string.", lang);
        return;
    }
    await setLanguage(lang, isDarkModeActive());
    await reapplySadsStyles(); // Ensure this is awaited if setLanguage itself doesn't trigger it reliably enough
};
document.addEventListener("DOMContentLoaded", initializeApp);
console.log("app.ts orchestrator script loaded. Initialization will occur on DOMContentLoaded.");
//# sourceMappingURL=app.js.map