// DNA Visualizer Component JS

/**
 * Renders a DNA sequence into a specified container element.
 * Each nucleotide is represented by a styled span.
 *
 * @param {HTMLElement} container The DOM element to render the sequence into.
 * @param {string} sequence A string representing the DNA sequence (e.g., "ATGCGTTA").
 */
function renderDnaSequence(container, sequence) {
  if (!container) {
    console.error("DNA sequence container not found.");
    return;
  }
  if (typeof sequence !== "string") {
    console.error("DNA sequence must be a string.");
    container.innerHTML =
      '<p style="color: red;">Error: Invalid sequence data.</p>';
    return;
  }

  container.innerHTML = ""; // Clear any existing content

  const upperSequence = sequence.toUpperCase();

  for (let i = 0; i < upperSequence.length; i++) {
    const nucleotideChar = upperSequence[i];
    const span = document.createElement("span");
    span.classList.add("nucleotide");
    let typeClass = "";

    switch (nucleotideChar) {
      case "A":
        typeClass = "nucleotide-a";
        break;
      case "T":
        typeClass = "nucleotide-t";
        break;
      case "G":
        typeClass = "nucleotide-g";
        break;
      case "C":
        typeClass = "nucleotide-c";
        break;
      default:
        typeClass = "nucleotide-unknown"; // Handle N, X, or other characters
        break;
    }
    span.classList.add(typeClass);
    span.textContent = nucleotideChar;
    container.appendChild(span);
  }
}

// Example of how to initialize and use the function:
// This part would typically run on DOMContentLoaded or be part of a component initialization logic.
document.addEventListener("DOMContentLoaded", () => {
  const dnaVisualizerElements = document.querySelectorAll(
    '[data-sads-component="dna-visualizer"]'
  );
  dnaVisualizerElements.forEach((element) => {
    const sequenceContainer = element.querySelector(
      '[data-sads-element="sequence-container"]'
    );
    // The 'data-sequence' attribute should be on the 'element' itself (the one with data-sads-component)
    const sequenceData = element.dataset.sequence;

    if (sequenceContainer && typeof sequenceData === "string") {
      renderDnaSequence(sequenceContainer, sequenceData);
    } else if (sequenceContainer && !sequenceData) {
      // sequenceData might be undefined if attribute is missing
      console.warn(
        "DNA visualizer component found, but missing or invalid data-sequence attribute.",
        element
      );
      // Optionally render a message or default sequence if data-sequence is missing
      // renderDnaSequence(sequenceContainer, "ERROR"); // Example: render an error sequence
    } else if (!sequenceContainer) {
      console.error(
        "DNA visualizer component found, but missing its sequence container element.",
        element
      );
    }
  });
});
