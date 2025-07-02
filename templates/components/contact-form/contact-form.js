// Contact Form Component JS - Submission Logic

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("contactForm"); // Assumes the form still has id="contactForm"
  if (form) {
    const statusDiv = document.getElementById("contactFormStatus"); // Assumes status div still has this ID

    // These are read from the form's data attributes, which are set by Jinja in the HTML template
    const actionUrl = form.dataset.formActionUrl;
    const successMessage = form.dataset.successMessage;
    const errorMessage = form.dataset.errorMessage;

    if (!actionUrl) {
      console.warn("Contact form action URL not found. Submission might not work.");
      // Optionally disable the form or show a message
    }

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      const formData = new FormData(form);

      if (statusDiv) {
        statusDiv.textContent = ""; // Clear previous status
        statusDiv.className = ''; // Clear previous classes like success/error
      }

      // Basic client-side validation (can be enhanced or rely on 'required' attributes)
      let isValid = true;
      for (let field of ['name', 'email', 'message']) { // Assuming these are the input names
          const inputElement = form.elements[field];
          if (inputElement && inputElement.required && !inputElement.value.trim()) {
              isValid = false;
              // Optionally, add visual feedback for the invalid field
              // For now, just preventing submission if any required field is empty.
              // The 'required' HTML attribute itself provides some browser-native feedback.
          }
      }
      if (!isValid) {
          if (statusDiv) {
              statusDiv.textContent = "Please fill out all required fields.";
              statusDiv.classList.add("error"); // Requires CSS for .error class
          }
          // console.warn("Contact form validation failed client-side.");
          return;
      }


      fetch(actionUrl, {
        method: "POST",
        body: formData,
        headers: {
          Accept: "application/json",
        },
      })
        .then((response) => {
          if (response.ok) {
            if (statusDiv) {
              statusDiv.textContent = successMessage || "Message sent successfully!";
              statusDiv.classList.add("success"); // Requires CSS for .success class
            }
            form.reset();
          } else {
            response.json().then((data) => {
              if (statusDiv) {
                if (Object.hasOwn(data, "errors")) {
                  statusDiv.textContent = data["errors"]
                    .map((error) => error["message"])
                    .join(", ");
                } else {
                  statusDiv.textContent = errorMessage || "Oops! Something went wrong.";
                }
                statusDiv.classList.add("error"); // Requires CSS for .error class
              }
            }).catch(() => {
                // If response is not JSON or another error parsing it
                if (statusDiv) {
                    statusDiv.textContent = errorMessage || "Oops! Something went wrong. Please try again.";
                    statusDiv.classList.add("error");
                }
            });
          }
        })
        .catch((error) => {
          if (statusDiv) {
            statusDiv.textContent = errorMessage || "Oops! Something went wrong. Please try again.";
            statusDiv.classList.add("error");
          }
          console.error("Contact form submission error:", error);
        });
    });
  } else {
    // console.log("Contact form with ID 'contactForm' not found.");
  }
});
