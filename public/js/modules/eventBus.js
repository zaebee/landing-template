// public/js/modules/eventBus.js
/**
 * @file Placeholder for a potential dedicated event bus.
 * Currently, the application uses `document.dispatchEvent` and `document.addEventListener` directly
 * for global event communication (e.g., 'appStateChanged', 'languageChanged').
 * This file defines common event detail types for documentation and future use.
 */

/**
 * @typedef {Object} AppStateEventDetail
 * @property {boolean} [darkMode] - The current state of dark mode (true if enabled, false if not).
 * @property {boolean} [translationsLoaded] - Whether translations have been successfully loaded (true or false).
 * @global
 */

/**
 * @typedef {Object} LanguageChangedEventDetail
 * @property {string} lang - The new language code (e.g., "en", "es").
 * @global
 */

// No actual event bus implementation is exported from this file at this time.
// The existing pattern of using document.dispatchEvent is maintained.
// If a more complex, namespaced, or feature-rich event bus is required later,
// this file would be the place to implement it. Example (commented out):

/*
const eventEmitter = {
  _events: {},

  dispatch(event, data) {
    if (!this._events[event]) return;
    this._events[event].forEach(callback => callback(data));
  },

  subscribe(event, callback) {
    if (!this._events[event]) {
      this._events[event] = [];
    }
    this._events[event].push(callback);
  },

  unsubscribe(event, callback) {
    if (!this._events[event]) return;
    this._events[event] = this._events[event].filter(cb => cb !== callback);
  }
};

export default eventEmitter;
*/

console.log(
  "eventBus.js loaded (currently a placeholder for type definitions and future use)."
);
