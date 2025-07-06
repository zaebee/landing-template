// public/ts/modules/eventBus.ts
/**
 * @file Placeholder for a potential dedicated event bus.
 * Currently, the application uses `document.dispatchEvent` and `document.addEventListener` directly
 * for global event communication (e.g., 'appStateChanged', 'languageChanged').
 * This file defines common event detail types for documentation and future use.
 */

export interface AppStateEventDetail {
  darkMode?: boolean; // The current state of dark mode (true if enabled, false if not).
  translationsLoaded?: boolean; // Whether translations have been successfully loaded (true or false).
  // Add other state parts as needed, e.g.
  // currentLanguage?: string;
}

export interface LanguageChangedEventDetail {
  lang: string; // The new language code (e.g., "en", "es").
}

// No actual event bus implementation is exported from this file at this time.
// The existing pattern of using document.dispatchEvent is maintained.
// If a more complex, namespaced, or feature-rich event bus is required later,
// this file would be the place to implement it.

/*
interface EventCallback<T = any> {
  (data: T): void;
}

interface EventMap {
  [eventName: string]: EventCallback[];
}

const eventEmitter = {
  _events: {} as EventMap,

  dispatch<T>(event: string, data: T): void {
    if (!this._events[event]) return;
    this._events[event].forEach(callback => callback(data));
  },

  subscribe<T>(event: string, callback: EventCallback<T>): void {
    if (!this._events[event]) {
      this._events[event] = [];
    }
    this._events[event].push(callback);
  },

  unsubscribe<T>(event: string, callback: EventCallback<T>): void {
    if (!this._events[event]) return;
    this._events[event] = this._events[event].filter(cb => cb !== callback);
  }
};

export default eventEmitter;
*/

console.log(
  "eventBus.ts loaded (currently a placeholder for type definitions and future use)."
);
