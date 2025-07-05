// public/ts/modules/translation.ts
/**
 * @file Manages language selection, translation fetching, DOM updates, and localStorage persistence.
 * Dispatches 'appStateChanged' event with `detail: { translationsLoaded: boolean, darkMode: boolean }`
 * and 'languageChanged' event with `detail: { lang: string }`.
 */

import type { AppStateEventDetail, LanguageChangedEventDetail } from './eventBus'; // Assuming types are in eventBus.ts

interface TranslationsObject {
  [key: string]: string;
}

let currentTranslations: TranslationsObject = {};
const LANGUAGE_STORAGE_KEY = "language";

async function _fetchTranslations(lang: string): Promise<TranslationsObject | null> {
  try {
    const response = await fetch(`public/locales/${lang}.json`);
    if (!response.ok) {
      console.error(
        `Could not load translation file for language "${lang}": ${response.statusText}`
      );
      return null;
    }
    return await response.json() as TranslationsObject;
  } catch (error) {
    console.error(
      `Error fetching translation file for language "${lang}":`,
      error
    );
    return null;
  }
}

function _applyTranslationsToDOM(translations: TranslationsObject): void {
  if (!translations || Object.keys(translations).length === 0) {
    console.warn(
      "[translation] Attempted to apply empty or null translations to DOM."
    );
    return;
  }
  currentTranslations = translations; // Update internal state

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.getAttribute("data-i18n");
    if (key && translations[key] && element.id !== "dark-mode-toggle") {
      element.textContent = translations[key];
    } else if (key && !translations[key] && element.id !== "dark-mode-toggle") {
      // console.warn(`[translation] Translation key "${key}" not found for element:`, element);
    }
  });
}

function _dispatchStateAndLanguageChange(lang: string, currentDarkModeState: boolean): void {
  const appStateDetail: Partial<AppStateEventDetail> = {
    translationsLoaded: true,
    darkMode: currentDarkModeState,
  };
  document.dispatchEvent(
    new CustomEvent("appStateChanged", { detail: appStateDetail })
  );

  const langChangedDetail: LanguageChangedEventDetail = { lang: lang };
  document.dispatchEvent(
    new CustomEvent("languageChanged", { detail: langChangedDetail })
  );
}

export async function initTranslations(currentDarkModeState: boolean): Promise<void> {
  const preferredLang =
    localStorage.getItem(LANGUAGE_STORAGE_KEY) ||
    document.documentElement.lang ||
    "en";
  await setLanguage(preferredLang, currentDarkModeState, true);
  console.log("Translations Initialized. Language:", preferredLang);
}

export async function setLanguage(lang: string, currentDarkModeState: boolean, isInitialLoad: boolean = false): Promise<void> {
  if (!lang) {
    console.error("setLanguage called with no language code provided.");
    return;
  }
  const translations = await _fetchTranslations(lang);
  if (translations) {
    _applyTranslationsToDOM(translations);
    localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
    document.documentElement.lang = lang;
    _dispatchStateAndLanguageChange(lang, currentDarkModeState);
    if (!isInitialLoad) {
      // console.log(`[translation] Language set to: ${lang}`);
    }
  } else {
    // console.error(`[translation] Failed to set language to "${lang}" - translations could not be loaded or were empty.`);
  }
}

export function getCurrentTranslations(): TranslationsObject {
  return { ...currentTranslations }; // Return a copy
}
