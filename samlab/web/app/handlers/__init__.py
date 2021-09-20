# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging
import os

import flask


# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, socketio, require_auth, require_permissions

##################################################################################
# General purpose endpoints

@application.route("/")
@require_auth
def get_index():
    require_permissions(["read"])
    base_dir = os.path.dirname(os.path.realpath(__file__))
    return open(os.path.join(base_dir, "..", "static", "index.html"), "r").read()


@application.route("/database")
@require_auth
def get_database():
    require_permissions(["read"])
    return flask.jsonify(database=application.config["database-name"])


@application.route("/identity")
@require_auth
def get_identity():
    username = "unknown"
    if hasattr(flask.request.authorization, "username"):
        username = flask.request.authorization.username
    return flask.jsonify(username=username)


@application.route("/notify", methods=["POST"])
@require_auth
def post_notify():
    require_permissions(["read"])

    def delayed_emit(delay, params):
        log.info("delayed_emit")
        socketio.sleep(delay)
        socketio.emit("notify", params)

    if "delay" in flask.request.json:
        socketio.start_background_task(delayed_emit, flask.request.json.pop("delay"), flask.request.json)
        return flask.jsonify()

    socketio.emit("notify", flask.request.json)
    return flask.jsonify()


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


