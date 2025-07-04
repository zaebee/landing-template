# Linter Configuration Notes

This document outlines known linting issues that are best addressed by configuring the linters in the CI environment (e.g., Super-linter setup) rather than by altering the source code in a way that would be functionally incorrect or undesirable.

## HTMLHint: `doctype-first`

- **Issue**: HTMLHint (via Super-linter) reports a `doctype-first` error for all HTML files in the `blocks/` directory (e.g., `blocks/hero.html`, `blocks/features.html`, etc.).
- **Reason**: These files are HTML partials, intended to be included in the main `index.html` by the `build.py` script. As partials, they should not contain a `<!DOCTYPE html>` declaration. The `doctype-first` rule is intended for complete HTML documents.
- **Suggested Solution**: Configure HTMLHint in the CI pipeline to:
  - Ignore the `doctype-first` rule specifically for files within the `blocks/` directory.
  - Alternatively, if HTMLHint is invoked directly, adjust its ruleset (e.g., via an `.htmlhintrc` file if Super-Linter picks it up) to accommodate these partials. For example, exclude the `blocks/` directory from this specific rule or from HTMLHint checks altogether if they are only meant to be validated as part of the assembled `index.html`.

## JSCPD: Duplication Warnings

- **Issue**: JSCPD (JavaScript/JSON Copy Paste Detector, also used for other languages by Super-linter) reports code duplication between the generated `index.html` file and the source HTML block files in the `blocks/` directory.
- **Reason**: The `index.html` file is dynamically generated by the `build.py` script, which concatenates the content of the HTML files from the `blocks/` directory. Therefore, the content of these blocks will naturally be present in both the source partials and the final assembled `index.html`. This is by design and not accidental code duplication that needs refactoring in the traditional sense.
- **Suggested Solution**: Configure JSCPD in the CI pipeline to:
  - Ignore the generated `index.html` file for duplication checks.
  - Alternatively, or in addition, ignore the `blocks/` directory if the primary concern is duplication in non-template/non-partial code.
  - A `.jscpd.json` configuration file might be respected by Super-Linter if placed in the repository root, allowing for more granular control over exclusions and thresholds.

Addressing these issues via linter configuration will lead to a cleaner CI output without compromising the modular structure of the HTML blocks.

---

## CSS Linting (Stylelint)

CSS files (`.css`) are linted using [Stylelint](https://stylelint.io/).

- **Configuration**:
  - Stylelint is configured in `.stylelintrc.json`.
- **Running Linters**:
  - `npm run lint:css` - Runs stylelint to check CSS files.
  - `npm run lint:css:fix` - Runs stylelint and attempts to automatically fix issues.

## Python Linting (Ruff & MyPy)

Python code (`.py` files) is linted using [Ruff](https://beta.ruff.rs/docs/) for formatting and general code quality (style, errors, etc.) and [MyPy](http://mypy-lang.org/) for static type checking.

- **Configuration**:

  - Ruff is configured in `pyproject.toml` under the `[tool.ruff]` and `[tool.ruff.lint]` sections.
  - MyPy is configured in `pyproject.toml` under the `[tool.mypy]` section.
  - Development dependencies, including `ruff` and `mypy`, are listed in `requirements-dev.txt`. Install them using `pip install -r requirements-dev.txt`.

- **Running Linters**:
  - `npm run lint:py` - Runs both Ruff and MyPy to check Python files.
  - `npm run lint:py:fix` - Runs Ruff with autofixing enabled, followed by MyPy.
