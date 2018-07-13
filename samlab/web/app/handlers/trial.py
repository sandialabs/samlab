# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging
import pprint

import arrow
import bson
import flask
import pymongo

import samlab.web.app.handlers.common
import samlab.trial

# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, socketio, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


@application.route("/trials")
@require_auth
def get_trials():
    require_permissions(["read"])

    trials = list(database.trials.find())

    sort = flask.request.args.get("sort", "tags")
    if sort == "id":
        trials = sorted(trials, key=lambda o: o["_id"])
    elif sort == "created":
        trials = sorted(trials, key=lambda o: arrow.get(o["created"]).isoformat() if "created" in o else None)[::-1]
    elif sort == "modified":
        trials = sorted(trials, key=lambda o: arrow.get(o["modified"]).isoformat() if "modified" in o else None)[::-1]
    elif sort == "modified-by":
        trials = sorted(trials, key=lambda o: (0, o["modified-by"]) if "modified-by" in o else (1, None))
    elif sort == "original-filename":
        trials = sorted(trials, key=lambda o: o.get("content", {}).get("original", {}).get("filename", None))
    elif sort == "tags":
        trials = sorted(trials, key=lambda o: ("label:reviewed" in o["tags"], sorted(o["tags"])))
    else:
        flask.abort(400, description="Unknown sort type.")

    trials = [{"id": str(trial["_id"]), "name": trial.get("name", str(trial["_id"]))} for trial in trials]

    return flask.jsonify(trials=trials)


@application.route("/trials/<exclude(count,tags):oid>", methods=["GET", "DELETE"])
@require_auth
def get_delete_trials_trial(oid):
    oid = bson.objectid.ObjectId(oid)

    if flask.request.method == "GET":
        return samlab.web.app.handlers.common.get_otype_oid("trials", oid)
    elif flask.request.method == "DELETE":
        require_permissions(["delete"])
        samlab.trial.delete(database, fs, oid)
        return flask.jsonify()


@application.route("/trials/<trial>/models")
@require_auth
def get_trials_trial_models(trial):
    require_permissions(["read"])
    trial = bson.objectid.ObjectId(trial)
    models = database.models.find(filter={"trial": trial}, sort=[("created", pymongo.ASCENDING)])
    models = [{"id": str(model["_id"]), "name": model.get("name", str(model["_id"]))} for model in models]
    return flask.jsonify(models=models)


