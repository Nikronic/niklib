# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import datetime
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'niklib'
copyright = f'{datetime.datetime.now().year}, Nikan Doosti'
author = 'Nikan Doosti'

# The full version, including alpha/beta/rc tags
VERSION: dict = {}
with open('../../niklib/version.py', 'r') as version_file:
    exec(version_file.read(), VERSION)
release = VERSION['VERSION']

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.autosummary',
    'sphinx_autodoc_typehints',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosectionlabel',
    'sphinx_copybutton',
]

napoleon_use_ivar = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    'niklib.version',
    '_build'
]

autosummary_generate = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Default options to an ..autoXXX directive.
autodoc_default_options = {
    "special-members": "__init__,__call__",
    "undoc-members": True,
    "show-inheritance": True,
    "inherited-members": False,
    "private-members": True,
}

# Subclasses should show parent classes docstrings if they don't override them.
autodoc_inherit_docstrings = True

# sort docs based on source code
autodoc_member_order = 'bysource'

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'snorkel': ('https://snorkel.readthedocs.io/en/latest/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),    
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None),
    'lightgbm': ('https://lightgbm.readthedocs.io/en/latest/', None),
    'xgboost': ('https://xgboost.readthedocs.io/en/stable/', None),
    'mlflow': ('https://mlflow.org/docs/latest/', None)
}

# This value contains a list of modules to be mocked up
autodoc_mock_imports = [
    # 'numpy',
    # 'matplotlib',
    'typing',
    # 'sklearn',
    # 'mlflow',
    'flaml',
    # 'snorkel',
    'dvc',
    # 'xgboost',
    'catboost'
]
