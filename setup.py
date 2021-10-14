# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

from setuptools import setup, find_packages
import re

setup(
    name="samlab",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description="Tools for managing machine learning experiments.",
    install_requires=[
        "arrow",
        "blessings",
        "Flask>=2",
        "flask-socketio",
        "ldap3",
        "requests",
        "watchdog",
    ],
    maintainer="Timothy M. Shead",
    maintainer_email="tshead@sandia.gov",
    packages=find_packages(),
    package_data={
        "samlab.dashboard": [
            "static/*",
            "static/css/*",
            "static/fonts/*",
            ],
        },
    project_urls={
        "Chat": "https://github.com/sandialabs/samlab/discussions",
        "Coverage": "https://coveralls.io/r/sandialabs/samlab",
        "Documentation": "https://samlab.readthedocs.io",
        "Issue Tracker": "https://github.com/sandialabs/samlab/issues",
        "Regression Tests": "https://github.com/sandialabs/samlab/actions",
        "Source": "https://github.com/sandialabs/samlab",
    },
    scripts = [
        "bin/samlab-gputop",
        "bin/samlab-dashboard",
        ],
    version=re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        open(
            "samlab/__init__.py",
            "r").read(),
        re.M).group(1),
)
