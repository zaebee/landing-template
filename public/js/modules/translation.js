// public/js/modules/translation.js
/**
 * @file Manages language selection, translation fetching, DOM updates, and localStorage persistence.
 * Dispatches 'appStateChanged' event with `detail: { translationsLoaded: boolean, darkMode: boolean }`
 * and 'languageChanged' event with `detail: { lang: string }`.
 */

/**
 * @typedef {Object<string, string>} TranslationsObject
 *   An object where keys are translation keys (strings) and values are translated strings.
 */

/**
 * @typedef {import('../app.js').AppStateEventDetail} AppStateEventDetail
 * @typedef {import('../app.js').LanguageChangedEventDetail} LanguageChangedEventDetail
 */

/**
 * Stores the currently loaded translations.
 * @type {TranslationsObject}
 */
let currentTranslations = {};

/**
 * Key used for storing language preference in localStorage.
 * @type {string}
 * @constant
 */
const LANGUAGE_STORAGE_KEY = "language";

/**
 * Fetches translation data (JSON object) for the given language code.
 * @param {string} lang - The language code (e.g., "en", "es").
 * @returns {Promise<TranslationsObject|null>} A promise that resolves to the translations object, or null if fetching fails.
 * @private
 */
async function _fetchTranslations(lang) {
  try {
    const response = await fetch(`public/locales/${lang}.json`);
    if (!response.ok) {
      console.error(`Could not load translation file for language "${lang}": ${response.statusText}`);
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching translation file for language "${lang}":`, error);
    return null;
  }
}

/**
 * Applies the loaded translations to DOM elements that have a `data-i18n` attribute.
 * The value of `data-i18n` is used as the key in the translations object.
 * @param {TranslationsObject} translations - The translations object to apply.
 * @private
 */
function _applyTranslationsToDOM(translations) {
  if (!translations || Object.keys(translations).length === 0) {
    console.warn("[translation] Attempted to apply empty or null translations to DOM.");
    return;
  }
  console.log("[translation] _applyTranslationsToDOM called with translations:", translations);
  currentTranslations = translations; // Update internal state

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.getAttribute("data-i18n");
    // The check for 'dark-mode-toggle' is specific to the current project structure
    // to prevent this generic translation logic from overwriting its specialized text/icon.
    if (translations[key] && element.id !== "dark-mode-toggle") {
      element.textContent = translations[key];
    } else if (!translations[key] && element.id !== "dark-mode-toggle") {
      // console.warn(`[translation] Translation key "${key}" not found for element:`, element); // Original log
    }
  });
  console.log("[translation] Finished applying translations to DOM.");
}

/**
 * Dispatches 'appStateChanged' and 'languageChanged' custom events on the document.
 * @param {string} lang - The language code that was just applied (e.g., "en", "es").
 * @param {boolean} currentDarkModeState - The current dark mode state, passed from the orchestrator.
 * @private
 */
function _dispatchStateAndLanguageChange(lang, currentDarkModeState) {
  console.log(`[translation] _dispatchStateAndLanguageChange called. Lang: ${lang}, DM State: ${currentDarkModeState}`);
  /** @type {Partial<AppStateEventDetail>} */
  const appStateDetail = {
    translationsLoaded: true,
    darkMode: currentDarkModeState,
  };
  document.dispatchEvent(new CustomEvent("appStateChanged", { detail: appStateDetail }));

  /** @type {LanguageChangedEventDetail} */
  const langChangedDetail = { lang: lang };
  document.dispatchEvent(new CustomEvent("languageChanged", { detail: langChangedDetail }));
}

/**
 * Initializes the translation functionality.
 * Determines the preferred language (from localStorage, `document.documentElement.lang`, or fallback to "en"),
 * then calls `setLanguage` to load and apply translations.
 * @param {boolean} currentDarkModeState - The current dark mode state, needed for dispatching a complete 'appStateChanged' event.
 * @public
 */
async function initTranslations(currentDarkModeState) {
  const preferredLang =
    localStorage.getItem(LANGUAGE_STORAGE_KEY) ||
    document.documentElement.lang || // Usually set by <html lang="...">
    "en";
  await setLanguage(preferredLang, currentDarkModeState, true); // isInitialLoad = true
  console.log("Translations Initialized. Language:", preferredLang);
}

/**
 * Sets the application language. Fetches the new translations, applies them to the DOM,
 * updates localStorage, sets the `lang` attribute on the `<html>` element,
 * and dispatches relevant events.
 * @param {string} lang - The language code to set (e.g., "en", "es").
 * @param {boolean} currentDarkModeState - The current dark mode state for event dispatch.
 * @param {boolean} [isInitialLoad=false] - True if this is part of the initial application load sequence.
 * @public
 */
async function setLanguage(lang, currentDarkModeState, isInitialLoad = false) {
  console.log(`[translation] setLanguage called. Lang: ${lang}, DM State: ${currentDarkModeState}, InitialLoad: ${isInitialLoad}`);
  if (!lang) {
    console.error("[translation] setLanguage called with no language code provided.");
    return;
  }
  const translations = await _fetchTranslations(lang);
  console.log(`[translation] Fetched translations for ${lang}:`, translations);
  if (translations) {
    _applyTranslationsToDOM(translations);
    localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
    document.documentElement.lang = lang;
    _dispatchStateAndLanguageChange(lang, currentDarkModeState);
    if (!isInitialLoad) {
      // console.log(`[translation] Language set to: ${lang}`); // Original log
    }
  } else {
    // console.error(`[translation] Failed to set language to "${lang}" - translations could not be loaded or were empty.`); // Original log
  }
}

/**
 * Returns the currently loaded set of translations.
 * @returns {TranslationsObject} The current translations object.
 * @public
 */
function getCurrentTranslations() {
  return { ...currentTranslations }; // Return a copy to prevent external modification
}
