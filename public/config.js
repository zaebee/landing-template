(async () => {
  try {
    // Determine the current language (e.g., from document.documentElement.lang or a default)
    const lang = document.documentElement.lang || "en";
    const response = await fetch(`public/generated_configs/config_${lang}.json`);
    if (!response.ok) {
      throw new Error(`Failed to fetch config_${lang}.json: ${response.statusText}`);
    }
    const config = await response.json();

    // Expose the contact form specific part of the config globally
    // Adjust the path within the config object as necessary based on its actual structure
    if (config && config.block_data_loaders && config.block_data_loaders["components/contact-form/contact-form.html"]) {
      const contactFormLoaderConfig = config.block_data_loaders["components/contact-form/contact-form.html"];
      if (contactFormLoaderConfig.data_file) {
        const contactDataResponse = await fetch(contactFormLoaderConfig.data_file);
        if (!contactDataResponse.ok) {
          throw new Error(`Failed to fetch ${contactFormLoaderConfig.data_file}: ${contactDataResponse.statusText}`);
        }
        window.contactFormConfig = await contactDataResponse.json();
        console.log("Contact form config loaded:", window.contactFormConfig);
      } else {
        console.warn("Contact form data_file not specified in config.");
        window.contactFormConfig = {}; // Provide a default empty object
      }
    } else {
      console.warn("Contact form configuration not found in site config or structure is unexpected.");
      window.contactFormConfig = {}; // Provide a default empty object
    }

    // For the base_url error, let's try to get it from the main config if available
    // This is a guess, the actual base_url might come from elsewhere or need to be defined differently
    if (config && config.base_url) {
        window.siteConfig = { base_url: config.base_url };
    } else {
        // Fallback or default if not in config_*.json
        // The error `Cannot read properties of undefined (reading 'base_url')` suggests something expects `window.siteConfig.base_url`
        // or similar. If `config_*.json` doesn't provide it, we might need a default or another source.
        // For now, let's set a sensible default if nothing else is found.
        window.siteConfig = window.siteConfig || {}; // Ensure siteConfig exists
        if (!window.siteConfig.base_url) {
            window.siteConfig.base_url = "/"; // Default to root if not specified
            console.log("siteConfig.base_url was not found in config_*.json, defaulted to '/'");
        }
    }

  } catch (error) {
    console.error("Error loading contact form config:", error);
    window.contactFormConfig = {}; // Provide a default empty object in case of error
    window.siteConfig = window.siteConfig || { base_url: "/" }; // Default siteConfig on error
  }
})();
