"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import contextlib
import os
import re
import shutil
import sys
from functools import lru_cache

import requests

# pyright: reportMissingImports=false
# pyright: reportMissingTypeStubs=false
from pybtex.database import Entry
from pybtex.plugin import register_plugin
from pybtex.richtext import Tag, Text
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.style.template import (
    FieldIsMissing,
    Node,
    _format_list,  # pyright: ignore[reportPrivateUsage]
    field,
    href,
    join,
    node,
    sentence,
    words,
)

this_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(this_dir))
import _list_technical_reports

_list_technical_reports.main()

# -- Project information -----------------------------------------------------
project = "ComPWA Organization"
REPO_NAME = "compwa-org"
copyright = "2021, ComPWA"
author = "Common Partial Wave Analysis"


# https://docs.readthedocs.io/en/stable/builds.html
def get_branch_name() -> str:
    branch_name = os.environ.get("READTHEDOCS_VERSION", "stable")
    if branch_name == "latest":
        return "main"
    if re.match(r"^\d+$", branch_name):  # PR preview
        return "stable"
    return branch_name


BRANCH = get_branch_name()


# -- Fetch logo --------------------------------------------------------------
def fetch_logo(url: str, output_path: str) -> None:
    if os.path.exists(output_path):
        return
    online_content = requests.get(url, allow_redirects=True)
    with open(output_path, "wb") as stream:
        stream.write(online_content.content)


LOGO_PATH = "_static/logo.svg"
with contextlib.suppress(requests.exceptions.ConnectionError):
    fetch_logo(
        url="https://raw.githubusercontent.com/ComPWA/ComPWA/04e5199/doc/images/logo.svg",
        output_path=LOGO_PATH,
    )

if os.path.exists(LOGO_PATH):
    html_logo = LOGO_PATH

# -- General configuration ---------------------------------------------------
master_doc = "index.md"
source_suffix = {
    ".ipynb": "myst-nb",
    ".md": "myst-nb",
}

# The master toctree document.
master_doc = "index"

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx_codeautolink",
    "sphinx_comments",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_hep_pdgref",
    "sphinx_remove_toctrees",
    "sphinx_thebe",
    "sphinx_togglebutton",
    "sphinxcontrib.bibtex",
]
exclude_patterns = [
    "**.ipynb_checkpoints",
    "*build",
    "*template.md",
    "adr/template.md",
    "tests",
]

# General sphinx settings
add_module_names = False
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "special-members": ", ".join([
        "__call__",
        "__eq__",
    ]),
}
codeautolink_concat_default = True
codeautolink_global_preface = """
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from IPython.display import display
"""
graphviz_output_format = "svg"
html_copy_source = True  # needed for download notebook button
html_favicon = "_static/favicon.ico"
html_js_files = [
    "https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.4/require.min.js",
]
html_last_updated_fmt = "%-d %B %Y"
html_show_copyright = False
html_show_sourcelink = False
html_show_sphinx = False
html_sourcelink_suffix = ""
html_static_path = ["_static"]
html_theme = "sphinx_book_theme"
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/ComPWA",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Zenodo",
            "url": "https://doi.org/10.5281/zenodo.6908149",
            "icon": "https://zenodo.org/badge/DOI/10.5281/zenodo.6908149.svg",
            "type": "url",
        },
    ],
    "logo": {"text": "The ComPWA project"},
    "repository_url": f"https://github.com/ComPWA/{REPO_NAME}",
    "repository_branch": BRANCH,
    "path_to_docs": "docs",
    "use_download_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "use_repository_button": True,
    "launch_buttons": {
        "binderhub_url": "https://mybinder.org",
        "colab_url": "https://colab.research.google.com",
        "notebook_interface": "jupyterlab",
        "thebe": True,
        "thebelab": True,
    },
    "show_toc_level": 2,
}
html_title = "Common Partial Wave Analysis Project"
pygments_style = "sphinx"
remove_from_toctrees = [
    "adr/*",
    "report/*",
]
todo_include_todos = False
viewcode_follow_imported_members = True

# Cross-referencing configuration
default_role = "py:obj"
primary_domain = "py"
nitpicky = True  # warn if cross-references are missing

# Intersphinx settings
version_remapping = {
    "ipython": {
        "8.12.2": "8.12.1",
        "8.12.3": "8.12.1",
    },
    "ipywidgets": {
        "8.0.3": "8.0.5",
        "8.0.4": "8.0.5",
        "8.0.6": "8.0.5",
        "8.1.1": "8.1.2",
    },
    "matplotlib": {"3.5.1": "3.5.0"},
}


def get_version(package_name: str) -> str:
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    constraints_path = f"../.constraints/py{python_version}.txt"
    package_name = package_name.lower()
    with open(constraints_path) as stream:
        constraints = stream.read()
    for line in constraints.split("\n"):
        line = line.split("#")[0]  # remove comments
        line = line.strip()
        line = line.lower()
        if not line.startswith(package_name):
            continue
        if not line:
            continue
        line_segments = tuple(line.split("=="))
        if len(line_segments) != 2:  # noqa: PLR2004
            continue
        _, installed_version, *_ = line_segments
        installed_version = installed_version.strip()
        remapped_versions = version_remapping.get(package_name)
        if remapped_versions is not None:
            existing_version = remapped_versions.get(installed_version)
            if existing_version is not None:
                return existing_version
        return installed_version
    return "stable"


def get_minor_version(package_name: str) -> str:
    installed_version = get_version(package_name)
    if installed_version == "stable":
        return installed_version
    matches = re.match(r"^([0-9]+\.[0-9]+).*$", installed_version)
    if matches is None:
        msg = f"Could not find documentation for {package_name} v{installed_version}"
        raise ValueError(msg)
    return matches[1]


intersphinx_mapping = {
    "IPython": (
        f"https://ipython.readthedocs.io/en/{get_version('IPython')}",
        None,
    ),
    "ampform": ("https://ampform.readthedocs.io/en/stable", None),
    "attrs": (f"https://www.attrs.org/en/{get_version('attrs')}", None),
    "expertsystem": ("https://expertsystem.readthedocs.io/en/stable", None),
    "graphviz": ("https://graphviz.readthedocs.io/en/stable", None),
    "hepstats": ("https://scikit-hep.org/hepstats", None),
    "ipywidgets": (
        f"https://ipywidgets.readthedocs.io/en/{get_version('ipywidgets')}",
        None,
    ),
    "jax": ("https://jax.readthedocs.io/en/latest", None),
    "matplotlib": (
        f"https://matplotlib.org/{get_version('matplotlib')}",
        None,
    ),
    "mpl_interactions": (
        f"https://mpl-interactions.readthedocs.io/en/{get_version('mpl-interactions')}",
        None,
    ),
    "numpy": (f"https://numpy.org/doc/{get_minor_version('numpy')}", None),
    "plotly": ("https://plotly.com/python-api-reference/", None),
    "pwa": ("https://pwa.readthedocs.io", None),
    "python": ("https://docs.python.org/3", None),
    "qrules": ("https://qrules.readthedocs.io/en/stable", None),
    "qrules-0.9.x": ("https://qrules.readthedocs.io/en/0.9.x", None),
    "scipy": ("https://docs.scipy.org/doc/scipy-1.7.0", None),
    "sympy": ("https://docs.sympy.org/latest", None),
    "tensorwaves": ("https://tensorwaves.readthedocs.io/en/stable", None),
    "zfit": ("https://zfit.readthedocs.io/en/latest", None),
}

# Settings for autosectionlabel
autosectionlabel_prefix_document = True

# Settings for bibtex
bibtex_bibfiles = ["bibliography.bib"]
suppress_warnings = [
    "myst.domains",
    "mystnb.unknown_mime_type",
]

# Settings for copybutton
copybutton_prompt_is_regexp = True
copybutton_prompt_text = r">>> |\.\.\. "  # doctest

# Settings for linkcheck
linkcheck_anchors = False
linkcheck_ignore = [
    "http://127.0.0.1:8000",
    "https://atom.io",  # often instable
    "https://doi.org/10.1002/andp.19955070504",  # 403 for onlinelibrary.wiley.com
    "https://github.com/organizations/ComPWA/settings/repository-defaults",  # private
    "https://ieeexplore.ieee.org/document/6312940",  # 401
    "https://open.vscode.dev",
    "https://rosettacode.org",
    "https://via.placeholder.com",  # irregular timeout
    "https://www.andiamo.co.uk/resources/iso-language-codes",  # 443, but works
    r"https://github.com/ComPWA/RUB-EP1-AG/.*",  # private
    r"https://github.com/orgs/ComPWA/projects/\d+",  # private
]


# Settings for myst_nb
def get_execution_mode() -> str:
    if "FORCE_EXECUTE_NB" in os.environ:
        print_once("\033[93;1mWill run ALL Jupyter notebooks!\033[0m")
        return "force"
    if "EXECUTE_NB" in os.environ:
        return "cache"
    return "off"


@lru_cache(maxsize=None)
def print_once(message: str) -> None:
    print(message)


nb_execution_excludepatterns = [
    "adr/001/*",
    "adr/002/*",
    "report/000*",
    "report/001*",
    "report/002*",
    "report/003*",
    "report/005*",
    "report/008*",
    "report/009*",
    "report/01*",
    "report/020*",
    "report/021*",
    "report/022*",
]
nb_execution_mode = get_execution_mode()
nb_execution_show_tb = True
nb_execution_timeout = -1
nb_output_stderr = "remove"

JULIA_NOTEBOOKS = [
    "report/019*",
]
if "READTHEDOCS" not in os.environ and shutil.which("julia") is None:
    nb_execution_excludepatterns.extend(JULIA_NOTEBOOKS)

# Settings for myst-parser
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "dollarmath",
    "smartquotes",
    "substitution",
]
myst_heading_anchors = 4
BINDER_LINK = (
    f"https://mybinder.org/v2/gh/ComPWA/{REPO_NAME}/{BRANCH}?filepath=docs/usage"
)
myst_substitutions = {
    "branch": BRANCH,
    "remark_019": (
        "Notice how a new file [`019/Project.toml`](./019/Project.toml) and "
        " [`019/Manifest.toml`](./019/Manifest.toml) are automatically generated."
        if get_execution_mode() != "off"
        else ""
    ),
    "run_interactive": f"""
```{{margin}}
Run this notebook [on Binder]({BINDER_LINK}) or
{{ref}}`locally on Jupyter Lab <develop:Jupyter Notebooks>` to interactively
modify the parameters.
```
""",
}
myst_update_mathjax = False

# Settings for sphinx_comments
comments_config = {
    "hypothesis": True,
    "utterances": {
        "repo": f"ComPWA/{REPO_NAME}",
        "issue-term": "pathname",
        "label": "📝 Docs",
    },
}

# Settings for Thebe cell output
thebe_config = {
    "repository_url": html_theme_options["repository_url"],
    "repository_branch": html_theme_options["repository_branch"],
}


# Specify bibliography style
@node
def et_al(children, data, sep="", sep2=None, last_sep=None):
    if sep2 is None:
        sep2 = sep
    if last_sep is None:
        last_sep = sep
    parts = [part for part in _format_list(children, data) if part]
    if len(parts) <= 1:
        return Text(*parts)
    if len(parts) == 2:  # noqa: PLR2004
        return Text(sep2).join(parts)
    if len(parts) == 3:  # noqa: PLR2004
        return Text(last_sep).join([Text(sep).join(parts[:-1]), parts[-1]])
    return Text(parts[0], Tag("em", " et al"))


@node
def names(children, context, role, **kwargs):
    """Return formatted names."""
    assert not children
    try:
        persons = context["entry"].persons[role]
    except KeyError:
        raise FieldIsMissing(role, context["entry"]) from None

    style = context["style"]
    formatted_names = [
        style.format_name(person, style.abbreviate_names) for person in persons
    ]
    return et_al(**kwargs)[formatted_names].format_data(context)


class MyStyle(UnsrtStyle):  # type: ignore[reportUntypedBaseClass]
    def __init__(self):
        super().__init__(abbreviate_names=True)

    def format_names(self, role, as_sentence=True) -> Node:
        formatted_names = names(role, sep=", ", sep2=" and ", last_sep=", and ")
        if as_sentence:
            return sentence[formatted_names]
        return formatted_names

    def format_eprint(self, e):  # pyright: ignore[reportIncompatibleMethodOverride]
        if "doi" in e.fields:
            return ""
        return super().format_eprint(e)

    def format_url(self, e: Entry) -> Node:
        if "doi" in e.fields or "eprint" in e.fields:
            return ""
        return words[
            href[
                field("url", raw=True),
                field("url", raw=True, apply_func=remove_http),
            ]
        ]

    def format_isbn(self, e: Entry) -> Node:
        return href[
            join[
                "https://isbnsearch.org/isbn/",
                field("isbn", raw=True, apply_func=remove_dashes_and_spaces),
            ],
            join[
                "ISBN:",
                field("isbn", raw=True),
            ],
        ]


def remove_dashes_and_spaces(isbn: str) -> str:
    to_remove = ["-", " "]
    for remove in to_remove:
        isbn = isbn.replace(remove, "")
    return isbn


def remove_http(input_str: str) -> str:
    to_remove = ["https://", "http://"]
    for remove in to_remove:
        input_str = input_str.replace(remove, "")
    return input_str


register_plugin("pybtex.style.formatting", "unsrt_et_al", MyStyle)
