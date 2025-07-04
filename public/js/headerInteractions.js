// public/js/headerInteractions.js
/**
 * @file Manages interactions for header elements like dark mode toggle, language switcher, and mobile menu.
 */

document.addEventListener("DOMContentLoaded", () => {
  // console.log('[headerInteractions] Initializing header interactions...'); // Optional: keep for init confirmation

  // --- Dark Mode Toggle ---
  const darkModeToggleButton = document.getElementById("dark-mode-toggle");
  if (darkModeToggleButton) {
    darkModeToggleButton.addEventListener("click", () => {
      // console.log('[headerInteractions] Dark mode toggle button clicked.'); // Debug log
      if (
        window.appGlobal &&
        typeof window.appGlobal.handleDarkModeToggle === "function"
      ) {
        window.appGlobal.handleDarkModeToggle();
      } else {
        console.error(
          "[headerInteractions] Error: window.appGlobal.handleDarkModeToggle is not available."
        ); // Keep error log
      }
    });

    // Listen for app state changes to update the toggle button's appearance
    document.addEventListener("appStateChanged", (event) => {
      if (typeof event.detail.darkMode === "boolean") {
        // console.log('[headerInteractions] appStateChanged event received for dark mode. New state:', event.detail.darkMode); // Debug log
        const isDark = event.detail.darkMode;
        darkModeToggleButton.textContent = isDark ? "☀️" : "🌙";
        darkModeToggleButton.setAttribute(
          "aria-label",
          isDark ? "Switch to Light Mode" : "Switch to Dark Mode"
        );
      }
    });
    // console.log('[headerInteractions] Dark mode toggle listener attached.'); // Optional: keep for init confirmation
  } else {
    console.warn(
      '[headerInteractions] Dark mode toggle button (id="dark-mode-toggle") not found.'
    ); // Keep warning
  }

  // --- Language Switcher ---
  const languageSwitcher = document.getElementById("language-switcher");
  if (languageSwitcher) {
    const langButtons = languageSwitcher.querySelectorAll("button[data-lang]");
    langButtons.forEach((button) => {
      button.addEventListener("click", (event) => {
        const lang = event.currentTarget.dataset.lang;
        // console.log(`[headerInteractions] Language button clicked for lang: "${lang}"`); // Debug log
        if (
          window.appGlobal &&
          typeof window.appGlobal.setAppLanguage === "function"
        ) {
          window.appGlobal.setAppLanguage(lang);
        } else {
          console.error(
            "[headerInteractions] Error: window.appGlobal.setAppLanguage is not available."
          ); // Keep error log
        }
      });
    });

    // Listen for language changes to update button active states
    document.addEventListener("languageChanged", (event) => {
      if (event.detail && event.detail.lang) {
        const currentLang = event.detail.lang;
        // console.log('[headerInteractions] languageChanged event received. Current language:', currentLang); // Debug log
        langButtons.forEach((btn) => {
          if (btn.dataset.lang === currentLang) {
            btn.classList.add("active-lang");
            // console.log(`[headerInteractions] Setting button for lang "${btn.dataset.lang}" to active.`); // Debug log
          } else {
            btn.classList.remove("active-lang");
          }
        });
      }
    });
    // console.log(`[headerInteractions] Language switcher listeners attached to ${langButtons.length} buttons.`); // Optional: keep
  } else {
    console.warn(
      '[headerInteractions] Language switcher (id="language-switcher") not found.'
    ); // Keep warning
  }

  // --- Mobile Menu Toggle ---
  const menuToggleButton = document.querySelector(
    '[data-sads-element="menu-toggle"].hamburger-menu'
  );
  const navItemsContainer = document.querySelector(
    '[data-sads-element="nav-items-container"]'
  );

  if (menuToggleButton && navItemsContainer) {
    menuToggleButton.addEventListener("click", () => {
      // console.log('[headerInteractions] Hamburger menu button clicked.'); // Debug log
      const isExpanded =
        menuToggleButton.getAttribute("aria-expanded") === "true" || false;
      menuToggleButton.setAttribute("aria-expanded", !isExpanded);
      navItemsContainer.classList.toggle("nav-items-container--active");
      menuToggleButton.classList.toggle("hamburger-menu--active");
      // console.log(`[headerInteractions] Nav items container toggled. New expanded state: ${!isExpanded}. Classes:`, navItemsContainer.classList.toString()); // Debug log
    });
    // console.log('[headerInteractions] Mobile menu toggle listener attached.'); // Optional: keep
  } else {
    if (!menuToggleButton)
      console.warn(
        '[headerInteractions] Hamburger menu button ("[data-sads-element="menu-toggle"].hamburger-menu") not found.'
      ); // Keep warning
    if (!navItemsContainer)
      console.warn(
        '[headerInteractions] Nav items container ("[data-sads-element="nav-items-container"]") not found.'
      ); // Keep warning
  }

  // console.log('[headerInteractions] Header interactions initialization complete.'); // Optional: keep
});
