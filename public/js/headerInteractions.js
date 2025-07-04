// public/js/headerInteractions.js
/**
 * @file Manages interactions for header elements like dark mode toggle, language switcher, and mobile menu.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Helper to console.log messages for this script
  function logHeader(message, ...args) {
    console.log('[headerInteractions]', message, ...args);
  }

  logHeader('Initializing header interactions...');

  // --- Dark Mode Toggle ---
  const darkModeToggleButton = document.getElementById('dark-mode-toggle');
  if (darkModeToggleButton) {
    darkModeToggleButton.addEventListener('click', () => {
      logHeader('Dark mode toggle button clicked.');
      if (window.appGlobal && typeof window.appGlobal.handleDarkModeToggle === 'function') {
        window.appGlobal.handleDarkModeToggle();
      } else {
        logHeader('Error: window.appGlobal.handleDarkModeToggle is not available.');
      }
    });

    // Listen for app state changes to update the toggle button's appearance
    document.addEventListener('appStateChanged', (event) => {
      if (typeof event.detail.darkMode === 'boolean') {
        logHeader('appStateChanged event received for dark mode. New state:', event.detail.darkMode);
        const isDark = event.detail.darkMode;
        darkModeToggleButton.textContent = isDark ? '☀️' : '🌙';
        darkModeToggleButton.setAttribute('aria-label', isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode');
        // Potentially update a class for styling if needed, e.g., if SADS cannot style the icon change directly
        // darkModeToggleButton.classList.toggle('dark-mode-active', isDark);
      }
    });
    logHeader('Dark mode toggle listener attached.');
  } else {
    logHeader('Dark mode toggle button (id="dark-mode-toggle") not found.');
  }

  // --- Language Switcher ---
  const languageSwitcher = document.getElementById('language-switcher');
  if (languageSwitcher) {
    const langButtons = languageSwitcher.querySelectorAll('button[data-lang]');
    langButtons.forEach(button => {
      button.addEventListener('click', (event) => {
        const lang = event.currentTarget.dataset.lang;
        logHeader(`Language button clicked for lang: "${lang}"`);
        if (window.appGlobal && typeof window.appGlobal.setAppLanguage === 'function') {
          window.appGlobal.setAppLanguage(lang);
        } else {
          logHeader('Error: window.appGlobal.setAppLanguage is not available.');
        }
      });
    });

    // Listen for language changes to update button active states
    document.addEventListener('languageChanged', (event) => {
      if (event.detail && event.detail.lang) {
        const currentLang = event.detail.lang;
        logHeader('languageChanged event received. Current language:', currentLang);
        langButtons.forEach(btn => {
          if (btn.dataset.lang === currentLang) {
            // Example: Add an 'active' class or modify SADS attributes if possible
            // For now, just log. Styling active state needs specific implementation.
            btn.classList.add('active-lang'); // Add a generic class
             logHeader(`Setting button for lang "${btn.dataset.lang}" to active.`);
          } else {
            btn.classList.remove('active-lang');
          }
        });
      }
    });
    logHeader(`Language switcher listeners attached to ${langButtons.length} buttons.`);
  } else {
    logHeader('Language switcher (id="language-switcher") not found.');
  }

  // --- Mobile Menu Toggle ---
  const menuToggleButton = document.querySelector('[data-sads-element="menu-toggle"].hamburger-menu');
  const navItemsContainer = document.querySelector('[data-sads-element="nav-items-container"]');

  if (menuToggleButton && navItemsContainer) {
    menuToggleButton.addEventListener('click', () => {
      logHeader('Hamburger menu button clicked.');
      const isExpanded = menuToggleButton.getAttribute('aria-expanded') === 'true' || false;
      menuToggleButton.setAttribute('aria-expanded', !isExpanded);

      // Toggle a class that controls visibility.
      // The actual display change (none to flex/block) should be handled by CSS rules for this class.
      // SADS responsive rules handle initial display:none for mobile. We need JS to toggle it on click.
      navItemsContainer.classList.toggle('nav-items-container--active'); // For visibility
      menuToggleButton.classList.toggle('hamburger-menu--active'); // For styling the hamburger icon (e.g., to an X)

      logHeader(`Nav items container toggled. New expanded state: ${!isExpanded}. Classes:`, navItemsContainer.classList.toString());
    });
    logHeader('Mobile menu toggle listener attached.');
  } else {
    if (!menuToggleButton) logHeader('Hamburger menu button ("[data-sads-element="menu-toggle"].hamburger-menu") not found.');
    if (!navItemsContainer) logHeader('Nav items container ("[data-sads-element="nav-items-container"]") not found.');
  }

  logHeader('Header interactions initialization complete.');
});
