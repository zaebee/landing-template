// Global App Logic (app.js)

// --- State ---
window.currentTranslations = {}; // Global for now, or manage via events/callbacks
let isDarkMode = localStorage.getItem("darkMode") === "enabled";

// --- DOM Elements (cache if frequently used, or select when needed) ---
// Note: darkModeToggle is in header.js, but its state update logic is here.
// Consider if body should be passed or selected here.
const body = document.body;

// --- Translation Functions ---
async function fetchTranslations(lang) {
  try {
    const response = await fetch(`public/locales/${lang}.json`);
    if (!response.ok) {
      console.error(`Could not load ${lang}.json: ${response.statusText}`);
      return null;
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching ${lang}.json:`, error);
    return null;
  }
}

function applyTranslationsToDOM(translations) {
  if (!translations) return;
  window.currentTranslations = translations; // Update global/shared translations object
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.getAttribute("data-i18n");
    // Avoid changing the dark mode toggle's text content directly if it's handled by its own UI update
    if (translations[key] && element.id !== "dark-mode-toggle") {
      element.textContent = translations[key];
    }
  });
  // After applying translations, dispatch an event that other components can listen to
  // This helps decouple app.js from specific component update functions like updateHeaderDarkModeButton
  document.dispatchEvent(
    new CustomEvent("appStateChanged", {
      detail: { translationsLoaded: true, darkMode: isDarkMode },
    })
  );
}

// --- Dark Mode ---

// Function to update CSS Custom Properties for the logo based on theme
function updateLogoCssVariables(isCurrentlyDarkMode) {
  if (typeof sadsDefaultTheme === "undefined" || !sadsDefaultTheme.colors) {
    console.warn(
      "SADS: Default theme or colors not available for logo CSS variables."
    );
    return;
  }

  const colors = sadsDefaultTheme.colors;
  const rootStyle = document.documentElement.style;

  const logoColorMappings = {
    "--logo-icon-primary": isCurrentlyDarkMode
      ? colors["logoIconPrimary-dark"]
      : colors["logoIconPrimary"],
    "--logo-icon-accent1": isCurrentlyDarkMode
      ? colors["logoIconAccent1-dark"]
      : colors["logoIconAccent1"],
    "--logo-icon-accent2": isCurrentlyDarkMode
      ? colors["logoIconAccent2-dark"]
      : colors["logoIconAccent2"],
    "--logo-icon-arrow": isCurrentlyDarkMode
      ? colors["logoIconArrow-dark"]
      : colors["logoIconArrow"],
    "--logo-text-color": isCurrentlyDarkMode
      ? colors["logoTextColor-dark"]
      : colors["logoTextColor"],
  };

  for (const [cssVar, colorValue] of Object.entries(logoColorMappings)) {
    if (colorValue) {
      rootStyle.setProperty(cssVar, colorValue);
    } else {
      console.warn(`SADS: Logo color value not found for ${cssVar} in theme.`);
      // Optionally, remove the property or set a fallback
      // rootStyle.removeProperty(cssVar);
    }
  }
}

function applyDarkModePreference() {
  if (isDarkMode) {
    body.classList.add("dark-mode");
  } else {
    body.classList.remove("dark-mode");
  }
  // Dispatch state change event for components like header to update their UI
  document.dispatchEvent(
    new CustomEvent("appStateChanged", {
      detail: {
        darkMode: isDarkMode,
        translationsLoaded: !!window.currentTranslations,
      },
    })
  );
  // Update logo CSS variables whenever dark mode preference is applied
  updateLogoCssVariables(isDarkMode);
}

window.handleDarkModeToggle = function () {
  // Exposed globally for header.js
  isDarkMode = !isDarkMode;
  localStorage.setItem("darkMode", isDarkMode ? "enabled" : "disabled");
  applyDarkModePreference();

  // If SADS engine is present and has an updateTheme or reapplyStyles method
  if (
    typeof sadsEngineInstance !== "undefined" &&
    typeof sadsEngineInstance.updateTheme === "function"
  ) {
    // This is a bit of a hack. Ideally, SADS engine would listen to 'appStateChanged'
    // or take the theme mode as a parameter to re-evaluate colors.
    // For now, re-applying styles might be needed if SADS color mapping depends on body.class.
    // Or, the SADS engine's _mapSemanticValueToActual needs to re-check body.classList.contains('dark-mode')
    // The current SADS engine (v0.1.4) checks document.body.classList.contains('dark-mode') live, so this might be okay.
    // However, to be safe and ensure components redraw if necessary:
    document.querySelectorAll("[data-sads-component]").forEach((comp) => {
      if (typeof window.sadsEngineInstance !== "undefined") {
        window.sadsEngineInstance.applyStylesTo(comp); // Re-apply SADS styles
      }
    });
  }
};

// --- Language Management ---
window.setAppLanguage = async function (lang) {
  // Exposed globally for header.js
  const translations = await fetchTranslations(lang);
  if (translations) {
    applyTranslationsToDOM(translations);
    localStorage.setItem("language", lang);
    document.documentElement.lang = lang;
    // Dispatch event for language switcher UI in header.js to update active button
    document.dispatchEvent(
      new CustomEvent("languageChanged", { detail: { lang: lang } })
    );
  }
};

// --- Initialization ---
async function initializeApp() {
  // Apply dark mode preference on load
  applyDarkModePreference();

  // Set initial language and load translations
  const preferredLang =
    localStorage.getItem("language") || document.documentElement.lang || "en";
  await window.setAppLanguage(preferredLang); // This will also trigger appStateChanged

  // Initialize SADS Engine (if not already done in base.html - move SADS init here)
  if (
    typeof SADSEngine === "function" &&
    typeof window.sadsEngineInstance === "undefined"
  ) {
    window.sadsEngineInstance = new SADSEngine({
      // theme overrides if any
    });
    document.querySelectorAll("[data-sads-component]").forEach((comp) => {
      console.log(
        "SADS: Applying styles from app.js to component:",
        comp.dataset.sadsComponent
      );
      window.sadsEngineInstance.applyStylesTo(comp);
    });
  } else if (
    typeof SADSEngine === "function" &&
    typeof window.sadsEngineInstance !== "undefined"
  ) {
    // If SADS engine was init in base.html, re-apply styles after language/dark mode init
    document.querySelectorAll("[data-sads-component]").forEach((comp) => {
      window.sadsEngineInstance.applyStylesTo(comp);
    });
  }

  console.log(
    "App Initialized: Dark Mode =",
    isDarkMode,
    "Language =",
    document.documentElement.lang
  );
}

// --- Global Event Listeners (if any that app.js should manage) ---
// Example: if other parts of the app need to react to dark mode changes initiated elsewhere.

// --- Expose functions to global scope if needed by inline scripts or other modules not using import/export ---
// window.fetchTranslations = fetchTranslations; // Not needed if only setAppLanguage is global
// window.applyTranslationsToDOM = applyTranslationsToDOM; // Not needed if only setAppLanguage is global
// window.currentTranslations is already global for header.js to use for button labels

// --- Run Initialization ---
// Defer initialization until DOM is fully loaded if this script is in <head>
// If it's at the end of <body>, DOMContentLoaded might be redundant but safe.
document.addEventListener("DOMContentLoaded", initializeApp);
