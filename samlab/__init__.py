# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Tools for managing machine learning experiments."""

__version__ = "0.2.0"

import logging
import warnings

import arrow

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class DeprecationWarning(Warning):
    pass


def deprecated(message):
    warnings.warn(message, DeprecationWarning, stacklevel=3)


from threading import Timer


