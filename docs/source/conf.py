import os
import sys

import tomli

sys.path.insert(0, os.path.abspath("../../src/djask"))

project = "Djask"
copyright = "2022, Andy Zhou"
author = "Andy Zhou"
pyproject_file = open("../../pyproject.toml", "rb")
release = tomli.load(pyproject_file)["project"]["version"]
pyproject_file.close()

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_tabs.tabs",
    "pallets_sphinx_themes",
]
templates_path = ["_templates"]
exclude_patterns = []
autodoc_typehints = "description"
intersphinx_mapping = {
    "flask": ("https://flask.palletsprojects.com/", None),
}

html_theme = "flask"
html_static_path = ["_static"]
html_favicon = "_static/djask.ico"
