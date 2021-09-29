# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

import flask

log = logging.getLogger(__name__)


class Basic(object):
    """Instruct clients to provide basic authentication."""
    def __init__(self, realm):
        self.realm = realm


    def __call__(self):
        log.info("Requesting basic authentication for realm: %s", self.realm)
        return flask.Response("Password required.", 401, {"WWW-Authenticate": 'Basic realm="%s"' % self.realm})


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(realm={self.realm!r})"


class Null(object):
    def __call__(self):
        raise NotImplementedError("This should never be called.")


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}()"

