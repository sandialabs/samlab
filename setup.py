# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

from setuptools import setup, find_packages
import re

setup(
    name="samlab",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Other Environment",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
    description="Tools for managing machine learning experiments.",
    install_requires=[
        "arrow",
        "blessings",
        "Flask",
        "flask-socketio",
        "ldap3",
        "requests",
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
