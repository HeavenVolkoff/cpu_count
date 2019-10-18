#!/usr/bin/env python3

"""Entrypoint for setuptools package installation.
    isort:skip_file
"""

import sys

if sys.version_info <= (3, 3):
    raise RuntimeError("Only Python >= 3.4 supported")

from os import path, chdir
from shlex import quote
from distutils.errors import DistutilsOptionError

try:
    import pkg_resources
    from setuptools import setup, find_namespace_packages
    from setuptools.config import read_configuration
except ImportError:
    raise RuntimeError(
        "The setuptools package is missing or broken. To (re)install it run:\n"
        "{} -m pip install -U setuptools".format(sys.executable)
    )


def has_requirement(req):
    try:
        pkg_resources.require(req)
    except pkg_resources.ResolutionError:
        return False
    else:
        return True


if __name__ == "__main__":
    # Allow setup.py to run from another directory
    chdir(path.dirname(__file__) or ".")

    SETUP_CONFIG = "setup.cfg"

    if not path.isfile(SETUP_CONFIG):
        raise RuntimeError("Unsupported package structure, a setup.cfg file is required")

    config = read_configuration(SETUP_CONFIG)
    options = config.get("options", {})
    metadata = config.get("metadata", {})
    missing_install_requires = tuple(
        filter(lambda req: not has_requirement(req), options.get("setup_requires", []))
    )

    if missing_install_requires:
        raise RuntimeError(
            "Missing dependencies to install {}. To fix run:\n{} -m pip install {}".format(
                metadata.get("name", "this package"),
                sys.executable,
                " ".join(map(quote, missing_install_requires)),
            )
        )

    try:
        setup()
    except DistutilsOptionError:
        raise RuntimeError(
            "Perhaps your setuptools package is too old. To update it run:\n"
            "{} -m pip install -U setuptools",
            sys.executable,
        )
