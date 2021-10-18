# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import functools
import os
import uuid

import arrow
import flask
import flask_socketio
import werkzeug.routing


# Setup the web server.
application = flask.Flask(__name__)
application.secret_key = os.urandom(24)
socketio = flask_socketio.SocketIO(application, json=flask.json)

class AllowConverter(werkzeug.routing.BaseConverter):
    def __init__(self, map, *items):
        werkzeug.routing.BaseConverter.__init__(self, map)
        self.items = items

    def to_python(self, value):
        if value not in self.items:
            raise werkzeug.routing.ValidationError()
        return value
application.url_map.converters["allow"] = AllowConverter

class ExcludeConverter(werkzeug.routing.BaseConverter):
    def __init__(self, map, *items):
        werkzeug.routing.BaseConverter.__init__(self, map)
        self.items = items

    def to_python(self, value):
        if value in self.items:
            raise werkzeug.routing.ValidationError()
        return value
application.url_map.converters["exclude"] = ExcludeConverter


##################################################################################
# Authentication and permissions

sessions = {}

def require_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # Validate an existing session.
        if "sid" in flask.session:
            sid = flask.session["sid"]
            if sid in sessions:
                session = sessions[sid]
                if session["remote-ip"] == flask.request.remote_addr:
                    elapsed = arrow.utcnow() - session["last-request"]
                    if elapsed.total_seconds() < application.config["session-timeout"]:
                        session["last-request"] = arrow.utcnow()
                        # Handle the request
                        return f(*args, **kwargs)
                del sessions[sid]
            del flask.session["sid"]
        # No existing session, so authenticate the user.
        if application.config["credentials"](flask.request.authorization):
            # Create a new session.
            flask.session["sid"] = uuid.uuid4()
            sessions[flask.session["sid"]] = {
                "last-request": arrow.utcnow(),
                "remote-ip": flask.request.remote_addr,
                }
            # Handle the request
            return f(*args, **kwargs)
        # Prompt the user for their credentials.
        return application.config["authentication"]()
    return decorated


def require_permissions(permissions):
    if not application.config["acl"](flask.request.authorization, permissions):
        flask.abort(403)

