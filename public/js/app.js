document.addEventListener("DOMContentLoaded", () => {
  // Assuming sadsDefaultTheme is globally available from sads-default-theme.js
  // and SADSEngine is globally available from sads-style-engine.js
  if (typeof SADSEngine === "undefined") {
    console.error(
      "SADS: SADSEngine not found. Make sure sads-style-engine.js is loaded."
    );
    return;
  }

  let themeConfig = {};
  if (typeof sadsDefaultTheme !== "undefined") {
    themeConfig = sadsDefaultTheme;
  } else {
    console.warn(
      "SADS: sadsDefaultTheme not found. Using empty theme for engine initialization."
    );
  }

  const sadsEngine = new SADSEngine(themeConfig);

  const sadsComponents = document.querySelectorAll("[data-sads-component]");
  sadsComponents.forEach((component) => {
    sadsEngine.applyStylesTo(component);
  });

  // Optional: Expose a function to re-apply styles if components are added dynamically
  // and also for dark mode toggling.
  window.sadsRefreshStyles = () => {
    // Re-initialize the engine or update its theme if necessary before re-applying
    // For this version, applyStylesTo should re-evaluate based on current body class for dark mode
    const currentEngine = new SADSEngine(themeConfig); // Re-create to get fresh dark mode check
    document.querySelectorAll("[data-sads-component]").forEach((component) => {
      currentEngine.applyStylesTo(component);
    });
  };

  console.log("SADS: Engine initialized and styles applied to components.");
});

// Dark mode toggle functionality
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  // Re-apply SADS styles as theme values might change based on dark mode
  if (window.sadsRefreshStyles) {
    window.sadsRefreshStyles(); // This will re-apply all SADS rules
  }
  console.log("SADS: Dark mode toggled. Styles refreshed.");
}

// Example: Make toggleDarkMode globally available for manual testing or attaching to a button
window.toggleSadsDarkMode = toggleDarkMode;

// Initial style application for dark mode if the class is already present on body
// (e.g., set by server-side or local storage preference)
// This needs to run after SADSEngine and sadsDefaultTheme might be defined,
// but also needs to ensure it doesn't conflict with the DOMContentLoaded one.
// A simple way is to call refresh if dark mode is on.
// The DOMContentLoaded listener will handle the initial application regardless.
// However, sadsRefreshStyles itself creates a new engine.
// The SADSEngine constructor already clears previous rules.

// Let's ensure the initial body class is respected by the first run.
// The SADSEngine constructor and applyStylesTo should handle this correctly
// as long as the 'dark-mode' class is on the body *before* the engine runs.
// So, no special handling here might be needed if sads-style-engine.js is robust.

// The sads-style-engine.js _mapSemanticValueToActual checks:
// const isDarkMode = document.body.classList.contains("dark-mode");
// So, as long as the class is on the body when applyStylesTo is called, it should be fine.
// The DOMContentLoaded ensures this.
// The toggleDarkMode function also calls sadsRefreshStyles which recreates the engine
// and re-applies styles, correctly picking up the new body class.
// This seems okay.
