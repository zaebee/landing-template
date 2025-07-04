// public/js/modules/darkMode.js
/**
 * @file Manages dark mode state, DOM updates, and localStorage persistence.
 * Dispatches 'appStateChanged' event on document with `detail: { darkMode: boolean }`.
 */

/**
 * @typedef {import('../app.js').AppStateEventDetail} AppStateEventDetail
 */

/**
 * Stores the current state of dark mode.
 * @type {boolean}
 */
let isDarkModeEnabled = false;

/**
 * Key used for storing dark mode preference in localStorage.
 * @type {string}
 * @constant
 */
const DARK_MODE_STORAGE_KEY = "darkMode";

/**
 * Applies the dark mode preference to the `document.body` by adding or removing the 'dark-mode' class.
 * @private
 */
function _applyDarkModePreferenceToDOM() {
  if (isDarkModeEnabled) {
    document.body.classList.add("dark-mode");
  } else {
    document.body.classList.remove("dark-mode");
  }
}

/**
 * Dispatches an 'appStateChanged' custom event on the document.
 * The event detail includes the current dark mode state.
 * @param {Partial<AppStateEventDetail>} eventDetail - The detail for the event.
 * @private
 */
function _dispatchStateChange(eventDetail) {
  document.dispatchEvent(
    new CustomEvent("appStateChanged", {
      detail: eventDetail,
    })
  );
}

/**
 * Initializes the dark mode functionality.
 * Reads preference from localStorage, applies it to the DOM, and dispatches an initial state event.
 * This function is typically called once when the application starts.
 * The `initialTranslationsLoaded` parameter was removed as `translation.js` handles its own event details.
 * The `appStateChanged` event dispatched here will only contain `darkMode` status.
 * `app.js` will ensure `initTranslations` is called, which dispatches its own `appStateChanged` with translation status.
 */
function initDarkMode() {
  const storedPreference = localStorage.getItem(DARK_MODE_STORAGE_KEY);
  isDarkModeEnabled = storedPreference === "enabled";
  _applyDarkModePreferenceToDOM();

  // Dispatch initial dark mode state.
  // Other parts of the state (like translationsLoaded) will be added by their respective modules
  // or by the orchestrator (app.js) when it has the full picture.
  // For now, this module only authoritatively knows about `darkMode`.
  _dispatchStateChange({ darkMode: isDarkModeEnabled });
  console.log("Dark Mode Initialized. Enabled:", isDarkModeEnabled);
}

/**
 * Toggles the dark mode state (on to off, or off to on).
 * Updates localStorage, applies the change to the DOM, and dispatches an 'appStateChanged' event.
 */
function toggleDarkMode() {
  isDarkModeEnabled = !isDarkModeEnabled;
  localStorage.setItem(DARK_MODE_STORAGE_KEY, isDarkModeEnabled ? "enabled" : "disabled");
  _applyDarkModePreferenceToDOM();
  _dispatchStateChange({ darkMode: isDarkModeEnabled });
  console.log("Dark Mode Toggled. Enabled:", isDarkModeEnabled);
}

/**
 * Returns the current activation state of dark mode.
 * @returns {boolean} True if dark mode is currently enabled, false otherwise.
 */
function isDarkModeActive() {
  return isDarkModeEnabled;
}
