import sphinx_bootstrap_theme

html_css_files = [
    "https://cdn.jsdelivr.net/gh/ickc/markdown-latex-css/css/_table.min.css",
    "https://cdn.jsdelivr.net/gh/ickc/markdown-latex-css/fonts/fonts.min.css",
]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinxcontrib.apidoc",
]
source_suffix = ".rst"
master_doc = "index"
project = "pantable"
year = "2016-2020"
author = "Kolen Cheung"
copyright = f"{year}, {author}"
version = release = "0.13.3"

pygments_style = "solarizedlight"
html_theme = "bootstrap"
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
html_theme_options = {
    "navbar_links": [("GitHub", "https://github.com/ickc/pantable/", True,)],
    "source_link_position": None,
    "bootswatch_theme": "readable",
    "bootstrap_version": "3",
}

html_use_smartypants = True
html_last_updated_fmt = "%b %d, %Y"
html_split_index = False
html_short_title = f"{project}-{version}"

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False

# sphinxcontrib.apidoc
apidoc_module_dir = '../src/pantable'
apidoc_separate_modules = True
apidoc_module_first = True
