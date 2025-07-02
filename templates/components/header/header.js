// templates/components/header/header.js

document.addEventListener('DOMContentLoaded', () => {
  // Hamburger Menu
  const hamburgerMenu = document.querySelector('.hamburger-menu');
  const navItemsContainer = document.querySelector('.nav-items');

  if (hamburgerMenu && navItemsContainer) {
    hamburgerMenu.addEventListener('click', () => {
      navItemsContainer.classList.toggle('active');
      const isExpanded = navItemsContainer.classList.contains('active');
      hamburgerMenu.setAttribute('aria-expanded', isExpanded);
    });
  }

  // Dark Mode Toggle UI
  const darkModeToggle = document.getElementById('dark-mode-toggle');
  if (darkModeToggle) {
    function updateHeaderDarkModeButtonUI() {
      // window.currentTranslations should be populated by app.js when translations are loaded
      const translations = window.currentTranslations || {};
      // isDarkMode state is managed by app.js, reflected on body class
      const isBodyDarkMode = document.body.classList.contains('dark-mode');

      if (isBodyDarkMode) {
        darkModeToggle.textContent = '☀️';
        darkModeToggle.setAttribute(
          'aria-label',
          translations['light_mode_toggle'] || 'Switch to Light Mode'
        );
      } else {
        darkModeToggle.textContent = '🌙';
        darkModeToggle.setAttribute(
          'aria-label',
          translations['dark_mode_toggle'] || 'Switch to Dark Mode'
        );
      }
    }

    darkModeToggle.addEventListener('click', () => {
      if (typeof window.handleDarkModeToggle === 'function') {
        window.handleDarkModeToggle(); // This function is now in app.js
      } else {
        console.warn('handleDarkModeToggle function not found in app.js.');
      }
    });

    // Listen for state changes from app.js (e.g., after translations load or dark mode changes)
    // This event should be dispatched by app.js after initial load and on any relevant state change.
    document.addEventListener('appStateChanged', (event) => {
        updateHeaderDarkModeButtonUI();
    });

    // Initial call in case appStateChanged was dispatched before this listener was added,
    // or if app.js has already set the initial state.
    updateHeaderDarkModeButtonUI();
  }

  // Language Switcher UI
  const languageSwitcher = document.getElementById('language-switcher');
  if (languageSwitcher) {
    function updateLanguageSwitcherButtonsUI(currentLang) {
        document.querySelectorAll('#language-switcher button').forEach((btn) => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-lang') === currentLang) {
                btn.classList.add('active');
            }
        });
    }

    languageSwitcher.addEventListener('click', (event) => {
      const button = event.target.closest('button[data-lang]');
      if (button) {
        const lang = button.getAttribute('data-lang');
        if (typeof window.setAppLanguage === 'function') {
          window.setAppLanguage(lang); // This function is now in app.js
        } else {
          console.warn('setAppLanguage function not found in app.js.');
        }
      }
    });

    // Listen for language changes from app.js to update button states
    document.addEventListener('languageChanged', (event) => {
        if (event.detail && event.detail.lang) {
            updateLanguageSwitcherButtonsUI(event.detail.lang);
        }
    });

    // Set initial state of buttons based on current language at load time
    // app.js should have set document.documentElement.lang via initializeApp
    const initialLang = document.documentElement.lang || localStorage.getItem('language') || 'en';
    updateLanguageSwitcherButtonsUI(initialLang);
  }
});
