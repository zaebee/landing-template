// public/ts/modules/darkMode.ts
/**
 * @file Manages dark mode state, DOM updates, and localStorage persistence.
 * Dispatches 'appStateChanged' event on document with `detail: { darkMode: boolean }`.
 */
let isDarkModeEnabled = false;
const DARK_MODE_STORAGE_KEY = "darkMode";
function _applyDarkModePreferenceToDOM() {
    if (isDarkModeEnabled) {
        document.body.classList.add("dark-mode");
    }
    else {
        document.body.classList.remove("dark-mode");
    }
}
function _dispatchStateChange(eventDetail) {
    document.dispatchEvent(new CustomEvent("appStateChanged", {
        detail: eventDetail,
    }));
}
export function initDarkMode() {
    const storedPreference = localStorage.getItem(DARK_MODE_STORAGE_KEY);
    isDarkModeEnabled = storedPreference === "enabled";
    _applyDarkModePreferenceToDOM();
    _dispatchStateChange({ darkMode: isDarkModeEnabled });
}
export function toggleDarkMode() {
    isDarkModeEnabled = !isDarkModeEnabled;
    localStorage.setItem(DARK_MODE_STORAGE_KEY, isDarkModeEnabled ? "enabled" : "disabled");
    _applyDarkModePreferenceToDOM();
    _dispatchStateChange({ darkMode: isDarkModeEnabled });
    console.log("Dark Mode Toggled. Enabled:", isDarkModeEnabled);
}
export function isDarkModeActive() {
    return isDarkModeEnabled;
}
//# sourceMappingURL=darkMode.js.map