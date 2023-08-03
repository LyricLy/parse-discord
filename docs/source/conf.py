import sys

# make sure viewcode can see the module
sys.path.insert(1, "..")

project = "parse-discord"
copyright = "2023 LyricLy"
author = "Christina Hanson"
release = "0.1.0"

html_theme = "furo"
extensions = ["myst_parser", "sphinx_search.extension", "autodoc2", "sphinx.ext.viewcode", "sphinx.ext.intersphinx"]

myst_enable_extensions = ["fieldlist"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

autodoc2_packages = ["../../parse_discord"]
autodoc2_hidden_objects = ["dunder", "private", "undoc"]
autodoc2_class_docstring = "both"
autodoc2_render_plugin = "myst"
autodoc2_module_all_regexes = [r".*\..*"]
