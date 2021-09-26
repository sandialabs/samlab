# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import os

import flask

from samlab.dashboard import application, socketio, require_auth, require_permissions


@application.route("/")
@require_auth
def get_index():
    require_permissions(["read"])
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "static", "index.html"))
    return flask.send_file(path)


@application.route("/identity")
@require_auth
def get_identity():
    username = "unknown"
    if hasattr(flask.request.authorization, "username"):
        username = flask.request.authorization.username
    return flask.jsonify(username=username)


@application.route("/permissions")
@require_auth
def get_permissions():
    permissions = {
        "delete": application.config["acl"](flask.request.authorization, ["delete"]),
        "developer": application.config["acl"](flask.request.authorization, ["developer"]),
        "read": application.config["acl"](flask.request.authorization, ["read"]),
        "write": application.config["acl"](flask.request.authorization, ["write"]),
    }
    return flask.jsonify(permissions=permissions)


@application.route("/ready")
@require_auth
def get_ready():
    require_permissions(["read"])
    return flask.jsonify(ready=True)


@application.route("/server")
@require_auth
def get_server():
    require_permissions(["read"])
    return flask.jsonify(server={"name": application.config["server-name"], "description": application.config["server-description"]})


