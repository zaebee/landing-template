"""
The `build_protocols` package defines interfaces and implementations for various
components of the static site generation process.

This includes protocols and classes for:
- Configuration management
- Data loading and caching
- HTML block generation
- Page assembly
- Translation services

This __init__.py file marks the directory as a Python package.
It currently does not export any symbols directly; modules within this
package are intended to be imported explicitly by other parts of the application,
for example: `from build_protocols.translation import DefaultTranslationProvider`.
"""

# The primary purpose of this __init__.py is to mark the 'build_protocols'
# directory as a package, allowing its modules (like translation.py,
# data_loading.py, etc.) to be imported using dot notation.

# Example of how symbols could be exposed directly from the package if desired:
# from .interfaces import TranslationProvider
# from .translation import DefaultTranslationProvider

# However, for this project, explicit imports from submodules are preferred
# as seen in build.py (e.g., from build_protocols.config_management import ...).
# This keeps the namespace cleaner and dependencies more obvious.
