"""
pyregularexpression – public API façade
=======================================

• Dynamically imports every first–level sub-module that is **not** private
  (doesn’t start with “_”) and re-exports all of its public symbols.

• A symbol is considered public if the sub-module defines ``__all__``; if
  that list is absent, every attribute whose name does **not** start with an
  underscore is exported.

This lets callers write, e.g.::

    from pyregularexpression import (
        find_medical_code_v1,
        find_algorithm_validation_v1,
        split_text_by_filter,   #  ← new helper
    )

without having to remember internal module paths.
"""
from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType
from typing import List

__all__: List[str] = []

# ────────────────────────────────────────────────────────────────
# 1.  Dynamically pull in every immediate child module
# ────────────────────────────────────────────────────────────────
for _finder, _mod_name, _is_pkg in pkgutil.iter_modules(__path__):
    if _mod_name.startswith("_"):
        continue  # skip private helpers like _version.py
    try:
        _module: ModuleType = importlib.import_module(f".{_mod_name}", __name__)
    except ModuleNotFoundError as e:
        if e.name == "pyspark":
            continue
        raise

    _exports = getattr(_module, "__all__", None)

    if _exports is None:  # fall back to “everything that isn’t private”
        _exports = [name for name in dir(_module) if not name.startswith("_")]

    for _sym in _exports:
        globals()[_sym] = getattr(_module, _sym)

    __all__.extend(_exports)

# ────────────────────────────────────────────────────────────────
# 2.  Explicit eager import of split_text_filter
#    (makes sure it’s available even if users pin __all__ manually)
# ────────────────────────────────────────────────────────────────
try:
    from . import split_text_filter as _stf

    globals()["split_text_by_filter"] = _stf.split_text_by_filter
    __all__.append("split_text_by_filter")
except ModuleNotFoundError:
    # If the file isn’t present in the build (old wheel), just ignore.
    pass

# Deduplicate while preserving order
__all__ = list(dict.fromkeys(__all__))

# ────────────────────────────────────────────────────────────────
# 3.  Expose the package version (wheel installs only)
# ────────────────────────────────────────────────────────────────
try:
    from importlib.metadata import version as _pkg_version  # Python ≥3.8
except ImportError:  # pragma: no cover  –  Py<3.8 fallback
    from importlib_metadata import version as _pkg_version  # type: ignore

try:
    __version__: str = _pkg_version(__name__)
except Exception:  # pragma: no cover  –  editable install / runtime path
    __version__ = "0.0.0.dev0"

# ────────────────────────────────────────────────────────────────
# 4.  Clean up internal names from the namespace
# ────────────────────────────────────────────────────────────────
for _name in (
    "importlib",
    "pkgutil",
    "ModuleType",
    "List",
    "_finder",
    "_mod_name",
    "_is_pkg",
    "_module",
    "_exports",
    "_sym",
    "_pkg_version",
    "_stf",
):
    globals().pop(_name, None)
