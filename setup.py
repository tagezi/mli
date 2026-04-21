#!/usr/bin/env python
#     This code is a part of program Manual Lichen identification
#     Copyright (C) 2022 contributors Manual Lichen identification
#     The full list is available at the link
#     https://github.com/tagezi/mli/blob/master/contributors.txt
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""This module contains setup instructions for MIL."""
import codecs
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

with open(os.path.join(here, "mli", "version.py")) as fp:
    exec(fp.read())

setup(
    name="Manua Lichen Identification",
    version=__version__,  # noqa: F821
    author="Valerii Goncharuk",
    author_email="lera.goncharuk@gmail.com",
    packages=["mli"],
    package_data={"": ["LICENSE"]},
    url="https://github.com/tagezi/mli",
    license="GPL 3.0",
    entry_points={
        "console_scripts": [
            "mli = mli:__main__"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GPL 3.0",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: Education",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities",
    ],
    description="Python 3 program for manual lichen identification.",
    include_package_data=True,
    long_description_content_type="text/markdown",
    long_description=long_description,
    zip_safe=True,
    python_requires=">=3.12",
    project_urls={
        "Bug Reports": "https://github.com/tagezi/mli/issues",
        "Read the Docs": "https://github.com/tagezi/mli",
    },
    keywords=["lichen", "identification", "biology", "lichenology", "fungi"],
)
