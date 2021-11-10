import os
import sys
sys.path.insert(0, os.path.abspath('../src/djask'))

project = 'Djask'
copyright = '2021, Andy Zhou'
author = 'Andy Zhou'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    "sphinx_tabs.tabs"
]
templates_path = ['_templates']
exclude_patterns = []
autodoc_typehints = "description"
intersphinx_mapping = {
    "flask": ("https://flask.palletsprojects.com/", None),
}

html_theme = "alabaster"
html_static_path = ['_static']
html_favicon = "_static/djask.ico"
