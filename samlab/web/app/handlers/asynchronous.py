# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

import flask

from samlab.web.app import socketio, require_auth, require_permissions


log = logging.getLogger(__name__)


def log_request():
    log.info("socket.io client %s: %s", flask.request.sid, flask.request.event["message"])


##################################################################################
# Asynchronous endpoints

@socketio.on("connect")
@require_auth
def connect():
    require_permissions(["read"])
    log_request()


@socketio.on("disconnect")
@require_auth
def disconnect():
    log_request()


@socketio.on("test")
@require_auth
def test():
    require_permissions(["read"])
    log_request()
    socketio.emit("test")


