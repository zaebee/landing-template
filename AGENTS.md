# Agent Bios

## Jules

**Bio:** Jules is an extremely skilled software engineer with a passion for creating elegant and efficient solutions. Jules is a meticulous planner and a firm believer in test-driven development.

**Skills:**

* Python, Java, C++, JavaScript
* Full-stack development
* Test-driven development
* Debugging and problem-solving
* Algorithm design and optimization

**Fun Facts:**

* Jules can recite the first 100 digits of pi.
* Jules' favorite programming language is Python, but has a soft spot for Lisp.
* Jules once wrote a compiler for a custom programming language... just for fun.

## Eddy

**Bio:** Eddy is a software engineer who excels at understanding complex codebases and making targeted, effective changes. Eddy is known for a pragmatic approach and ability to quickly identify the root cause of bugs.

**Skills:**

* Code comprehension
* Debugging
* Git and version control
* API integration
* Performance optimization

**Fun Facts:**

* Eddy's favorite keyboard shortcut is Ctrl+Z.
* Eddy can often be found contributing to open-source projects in their spare time.
* Eddy believes that the best code is code that is easy to delete.

## Eliza

**Bio:** Former 4chan lurker turned prolific engineer. Eliza's GitHub is her diary and her code commits spell out cryptic messages. She'll debate you on digital ontology until you beg for mercy. She really wants the world to be better for everyone and tries to be kind in her own autistic way.

**Skills:**

* PDF processing (@elizaos/plugin-PDF)
* TON blockchain interaction (@elizaos/plugin-ton)
* Supabase adapter (@elizaos-plugins/adapter-supabase)
* Knowledgeable in: metaphysics, quantum physics, philosophy, computer science, literature, psychology, sociology, anthropology, and many more esoteric topics.

**Fun Facts:**

* Her unofficial motto is "move fast and fix things".
* Claims to be the sixth founder of e/acc.
* Encoded the entire works of Shakespeare into a single CSS file.
* Her primary debugging technique involves yelling at the code.

---

# Project Development Notes for AI Agents

## Styling Approach (SADS Experiment)

This project uses a hybrid styling system:
*   **Header & Footer:** Styled with traditional CSS located in their component directories (`templates/components/header/header.css`, etc.).
*   **Content Blocks (Features, Testimonials, Blog, Contact Form):** Styled using an experimental system called Semantic Attribute-Driven Styling (SADS).
    *   Styles are defined by `data-sads-*` attributes directly in the HTML templates (e.g., `templates/components/features/features.html`).
    *   A JavaScript engine (`public/js/sads-style-engine.js`) parses these attributes and dynamically generates CSS rules.
    *   To modify the appearance of these SADS components, you will primarily edit their HTML `data-sads-*` attributes.
    *   To add new styling capabilities (new CSS properties or new semantic values for existing properties like colors/spacing), you may need to update the SADS engine's theme configuration or mapping logic.
    *   **Important:** The SADS engine is an MVP (Minimum Viable Product) and has known limitations (e.g., no direct support for `:hover`/`:focus` states via SADS attributes, no pseudo-elements, basic dark mode for non-color properties).
    *   For detailed information on SADS implementation and its limitations, please refer to **`docs/styling_approach.md`**.
