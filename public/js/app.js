document.addEventListener("DOMContentLoaded", () => {
  // Initialize SADS Engine
  // sadsDefaultTheme should be globally available from sads-default-theme.js
  // SADSEngine class should be available from sads-style-engine.js
  if (
    typeof SADSEngine !== "undefined" &&
    typeof sadsDefaultTheme !== "undefined"
  ) {
    const sadsEngine = new SADSEngine(sadsDefaultTheme); // Pass the default theme

    const sadsComponents = document.querySelectorAll("[data-sads-component]");
    sadsComponents.forEach((componentElement) => {
      sadsEngine.applyStylesTo(componentElement);
    });
    console.log(`SADS Engine applied to ${sadsComponents.length} components.`);

    // Handle Dark Mode Toggling interaction with SADS
    // If SADS needs to re-evaluate styles beyond color changes when dark mode is toggled
    const darkModeToggle = document.getElementById("dark-mode-toggle");
    if (darkModeToggle) {
      darkModeToggle.addEventListener("click", () => {
        // SADS engine's _mapSemanticValueToActual already checks body.classList.contains('dark-mode')
        // for color mapping. If other properties needed dynamic updates based on dark mode,
        // a full re-application might be necessary.
        // For now, assuming color changes are the primary concern and handled by the engine.
        // If a full re-render of SADS styles is needed:
        // setTimeout(() => { // Ensure class toggle has taken effect
        //     console.log("Re-applying SADS styles after dark mode toggle.");
        //     sadsComponents.forEach(componentElement => {
        //         sadsEngine.applyStylesTo(componentElement);
        //     });
        // }, 0);
      });
    }
  } else {
    console.error(
      "SADS Engine or Default Theme not found. SADS styling will not be applied."
    );
  }

  // Other global initializations can go here if needed
  // For example, the hamburger menu and contact form logic from base.html could be moved here
  // for better organization, but that's outside the current scope.
});
