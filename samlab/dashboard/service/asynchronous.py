# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

import flask

from samlab.dashboard.server import socketio, require_auth, require_permissions
from samlab.dashboard.service.notify import emit


log = logging.getLogger(__name__)


def _log_request():
    log.info("socket.io client %s: %s", flask.request.sid, flask.request.event["message"])


@socketio.on("connect")
@require_auth
def connect():
    require_permissions(["read"])
    _log_request()


@socketio.on("disconnect")
@require_auth
def disconnect():
    _log_request()


@socketio.on("test")
@require_auth
def test():
    require_permissions(["read"])
    _log_request()
    emit("test")


