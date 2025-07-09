// public/ts/modules/darkMode.ts
/**
 * @file Manages dark mode state, DOM updates, and localStorage persistence.
 * Signals SADS engine to reapply styles on mode change.
 * Dispatches 'appStateChanged' event on document with `detail: { darkMode: boolean }`.
 */

import { reapplySadsStyles } from "./sadsManager.js";

// Assuming AppStateEventDetail might be defined in a shared types file or in app.ts eventually.
// For now, let's define a local version or expect it to be globally available if/when app.js is converted.
interface AppStateEventDetail {
  darkMode?: boolean;
  translationsLoaded?: boolean;
  // other state parts can be added here
}

let isDarkModeEnabled: boolean = false;
const DARK_MODE_STORAGE_KEY = "darkMode";

/**
 * Applies the dark mode preference to the DOM by adding or removing the 'dark-mode' class on the body.
 * This class is used by the SADS engine and potentially other CSS.
 * @private
 */
function _applyDarkModePreferenceToDOM(): void {
  if (isDarkModeEnabled) {
    document.body.classList.add("dark-mode");
  } else {
    document.body.classList.remove("dark-mode");
  }
}

/**
 * Dispatches a custom 'appStateChanged' event.
 * @param eventDetail - The detail object for the event.
 * @private
 */
function _dispatchStateChange(eventDetail: Partial<AppStateEventDetail>): void {
  document.dispatchEvent(
    new CustomEvent("appStateChanged", {
      detail: eventDetail,
    })
  );
}

/**
 * Initializes dark mode based on localStorage preference.
 * Applies the class to the body and dispatches a state change.
 * It does NOT trigger SADS style reapplication itself, assuming SADS init will handle initial styling.
 */
export function initDarkMode(): void {
  const storedPreference = localStorage.getItem(DARK_MODE_STORAGE_KEY);
  isDarkModeEnabled = storedPreference === "enabled";
  _applyDarkModePreferenceToDOM(); // Set body class for SADS engine and CSS
  _dispatchStateChange({ darkMode: isDarkModeEnabled });
  console.log("Dark Mode Initialized. Enabled:", isDarkModeEnabled);
}

/**
 * Toggles dark mode state, updates localStorage, updates the body class,
 * triggers SADS style reapplication, and dispatches a state change.
 * @async
 */
export async function toggleDarkMode(): Promise<void> {
  isDarkModeEnabled = !isDarkModeEnabled;
  localStorage.setItem(
    DARK_MODE_STORAGE_KEY,
    isDarkModeEnabled ? "enabled" : "disabled"
  );
  _applyDarkModePreferenceToDOM(); // Update body class

  // Crucially, tell SADS to re-evaluate styles with the new mode context
  // The SADS engine reads `document.body.classList.contains('dark-mode')`
  if (typeof reapplySadsStyles === "function") {
    await reapplySadsStyles();
  } else {
    console.warn(
      "SADS: reapplySadsStyles function not found. Cannot reapply styles for dark mode toggle."
    );
  }

  _dispatchStateChange({ darkMode: isDarkModeEnabled });
  console.log("Dark Mode Toggled. Enabled:", isDarkModeEnabled);
}

/**
 * Checks if dark mode is currently active.
 * @returns {boolean} True if dark mode is active, false otherwise.
 */
export function isDarkModeActive(): boolean {
  return isDarkModeEnabled;
}
