# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging
import pprint

import arrow
import bson
import flask
import pymongo

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


@application.route("/trials/<exclude(tags):trial>", methods=["GET", "DELETE"])
@require_auth
def get_delete_trials_trial(trial):
    if flask.request.method == "GET":
        require_permissions(["read"])
        trial = bson.objectid.ObjectId(trial)
        trial = database.trials.find_one({"_id": trial})

        if trial is None:
            flask.abort(404)

        if "created" in trial:
            trial["created"] = arrow.get(trial["created"]).isoformat()
        if "modified" in trial:
            trial["modified"] = arrow.get(trial["modified"]).isoformat()
        trial["name"] = trial.get("name", trial["_id"])

        trial["attributes-pre"] = pprint.pformat(trial["attributes"], depth=1)

        if "content" in trial:
            trial["content"] = [{"key": key, "content-type": value["content-type"], "filename": value.get("filename", None)} for key, value in sorted(trial["content"].items())]
        else:
            trial["content"] = []

        return flask.jsonify(trial=trial)

    elif flask.request.method == "DELETE":
        require_permissions(["delete"])
        trial = bson.objectid.ObjectId(trial)
        samlab.trial.delete(database, fs, trial)
        return flask.jsonify()


@application.route("/trials/<trial>/models")
@require_auth
def get_trials_trial_models(trial):
    require_permissions(["read"])
    trial = bson.objectid.ObjectId(trial)
    models = database.models.find(filter={"trial": trial}, sort=[("created", pymongo.ASCENDING)])
    models = [{"id": str(model["_id"]), "name": model.get("name", str(model["_id"]))} for model in models]
    return flask.jsonify(models=models)


