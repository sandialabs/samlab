# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

import arrow
import flask

import samlab.tasks.generic

# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, socketio, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs

# Setup task queues
generic_queue = samlab.tasks.generic.Queue()


def log_request():
    log.info("socket.io client %s: %s", flask.request.sid, flask.request.event["message"])


def receive_delivery(directory, label):
    document = {
        "created": arrow.utcnow().datetime,
        "directory": directory,
        "label": label,
    }
    did = database.deliveries.insert_one(document).inserted_id
    log.info("Delivery received: %s %s", directory, label)
    socketio.emit("notify", {"icon": "fa fa-truck", "message": "Delivery received: %s" % label, "type": "success", "delay": 0})


##################################################################################
# Asynchronous endpoints

@socketio.on("connect")
@require_auth
def connect():
    require_permissions(["read"])
    log_request()


@socketio.on("cluster-content")
@require_auth
def cluster_content(params):
    require_permissions(["read"])
    log_request()

    sid = flask.request.sid
    database_uri = application.config["database-uri"]
    database_name = application.config["database-name"]
    otype = params["otype"]
    key = params["key"]
    preprocessor = params["preprocessor"]
    algorithm = params["algorithm"]

    assert(otype in ["observations"])


    def implementation(*args, **kwargs):
        task = generic_queue.cluster_content(*args, **kwargs)
        while True:
            try:
                result = task()
            except Exception as e:
                log.debug("%s %s %s", e, e.args, e.metadata)
                result = { "exception": str(eval(e.metadata["error"])) }

            if result is not None:
                result["otype"] = kwargs["otype"]
                result["key"] = kwargs["key"]
                socketio.emit("cluster-content", result, room=sid)
                return
            socketio.sleep(1.0)
    socketio.start_background_task(implementation, database_uri=database_uri, database_name=database_name, otype=otype, key=key, preprocessor=preprocessor, algorithm=algorithm)


@socketio.on("disconnect")
@require_auth
def disconnect():
    log_request()


@socketio.on("export-observations")
@require_auth
def export_observations(params):
    require_permissions(["read"])
    log_request()

    sid = flask.request.sid
    database_uri = application.config["database-uri"]
    database_name = application.config["database-name"]
    search = params["search"]

    def implementation(*args, **kwargs):
        task = generic_queue.export_observations(*args, **kwargs)
        while True:
            result = task()
            if result is not None:
                receive_delivery(result["directory"], "Exported %s observations" % result["count"])
                return
            socketio.sleep(1.0)
    socketio.start_background_task(implementation, database_uri, database_name, search)


@socketio.on("test")
@require_auth
def test():
    require_permissions(["read"])
    log_request()
    socketio.emit("test")


