# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging
import traceback

import flask

log = logging.getLogger(__name__)

def permit_all():
    """Access control list strategy that allows anyone to do anything.
    """
    def implementation(authorization, requested):
        return True
    return implementation


def forbid_all():
    """Access control list strategy that prevents anyone from doing anything."""
    def implementation(authorization, requested):
        return False
    return implementation


def explicit(**permissions):
    """Access control list strategy based on lists of usernames."""
    def implementation(authorization, requested):
        if authorization is None:
            return False
        for permission in requested:
            if permission not in permissions:
                return False
            if authorization.username not in permissions[permission]:
                return False
        return True
    return implementation
