// public/ts/modules/darkMode.ts
/**
 * @file Manages dark mode state, DOM updates, and localStorage persistence.
 * Dispatches 'appStateChanged' event on document with `detail: { darkMode: boolean }`.
 */

// Assuming AppStateEventDetail might be defined in a shared types file or in app.ts eventually.
// For now, let's define a local version or expect it to be globally available if/when app.js is converted.
interface AppStateEventDetail {
  darkMode?: boolean;
  translationsLoaded?: boolean;
  // other state parts can be added here
}


let isDarkModeEnabled: boolean = false;
const DARK_MODE_STORAGE_KEY = "darkMode";

function _applyDarkModePreferenceToDOM(): void {
  if (isDarkModeEnabled) {
    document.body.classList.add("dark-mode");
  } else {
    document.body.classList.remove("dark-mode");
  }
}

function _dispatchStateChange(eventDetail: Partial<AppStateEventDetail>): void {
  document.dispatchEvent(
    new CustomEvent("appStateChanged", {
      detail: eventDetail,
    })
  );
}

export function initDarkMode(): void {
  const storedPreference = localStorage.getItem(DARK_MODE_STORAGE_KEY);
  isDarkModeEnabled = storedPreference === "enabled";
  _applyDarkModePreferenceToDOM();
  _dispatchStateChange({ darkMode: isDarkModeEnabled });
}

export function toggleDarkMode(): void {
  isDarkModeEnabled = !isDarkModeEnabled;
  localStorage.setItem(
    DARK_MODE_STORAGE_KEY,
    isDarkModeEnabled ? "enabled" : "disabled"
  );
  _applyDarkModePreferenceToDOM();
  _dispatchStateChange({ darkMode: isDarkModeEnabled });
  console.log("Dark Mode Toggled. Enabled:", isDarkModeEnabled);
}

export function isDarkModeActive(): boolean {
  return isDarkModeEnabled;
}
