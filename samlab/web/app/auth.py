# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

import flask

log = logging.getLogger(__name__)

def basic(realm):
    """Tell clients to provide basic authentication."""
    def implementation():
        log.info("Requesting basic authentication for realm: %s", realm)
        return flask.Response("Password required.", 401, {"WWW-Authenticate": 'Basic realm="%s"' % realm})
    return implementation

def none():
    def implementation():
        raise NotImplementedError("This should never be called.")
    return implementation
