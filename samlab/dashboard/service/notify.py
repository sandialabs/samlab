# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import queue

import flask

from samlab.dashboard.server import application, socketio, require_auth, require_permissions


@application.route("/notify", methods=["POST"])
@require_auth
def post_notify():
    require_permissions(["read"])

    def delayed_emit(delay, params):
        socketio.sleep(delay)
        socketio.emit("notify", params)

    if "delay" in flask.request.json:
        socketio.start_background_task(delayed_emit, flask.request.json.pop("delay"), flask.request.json)
        return flask.jsonify()

    socketio.emit("notify", flask.request.json)
    return flask.jsonify()


def emit(message, data=None):
    emit.queue.put((message, data))
emit.queue = queue.Queue()


def emit_loop():
    while True:
        try:
            message, data = emit.queue.get_nowait()
            socketio.emit(message, data)
        except:
            socketio.sleep(0.1)


socketio.start_background_task(emit_loop)

