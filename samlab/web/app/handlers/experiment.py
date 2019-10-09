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
import samlab.experiment

# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


@application.route("/experiments")
@require_auth
def get_experiments():
    require_permissions(["read"])

    experiments = list(database.experiments.find())

    sort = flask.request.args.get("sort", "tags")
    if sort == "id":
        experiments = sorted(experiments, key=lambda o: o["_id"])
    elif sort == "created":
        experiments = sorted(experiments, key=lambda o: arrow.get(o["created"]).isoformat() if "created" in o else None)[::-1]
    elif sort == "modified":
        experiments = sorted(experiments, key=lambda o: arrow.get(o["modified"]).isoformat() if "modified" in o else None)[::-1]
    elif sort == "modified-by":
        experiments = sorted(experiments, key=lambda o: (0, o["modified-by"]) if "modified-by" in o else (1, None))
    elif sort == "original-filename":
        experiments = sorted(experiments, key=lambda o: o.get("content", {}).get("original", {}).get("filename", None))
    elif sort == "tags":
        experiments = sorted(experiments, key=lambda o: ("label:reviewed" in o["tags"], sorted(o["tags"])))
    else:
        flask.abort(400, description="Unknown sort type.")

    experiments = [{"id": str(experiment["_id"]), "name": experiment.get("name", str(experiment["_id"]))} for experiment in experiments]

    return flask.jsonify(experiments=experiments)


@application.route("/experiments/<exclude(count,tags):oid>", methods=["GET", "DELETE"])
@require_auth
def get_delete_experiments_experiment(oid):
    oid = bson.objectid.ObjectId(oid)

    if flask.request.method == "GET":
        return samlab.web.app.handlers.common.get_otype_oid("experiments", oid)
    elif flask.request.method == "DELETE":
        require_permissions(["delete"])
        samlab.experiment.delete(database, fs, oid)
        return flask.jsonify()


@application.route("/experiments/<experiment>/artifacts")
@require_auth
def get_experiments_experiment_artifacts(experiment):
    require_permissions(["read"])
    experiment = bson.objectid.ObjectId(experiment)
    artifacts = database.artifacts.find(filter={"experiment": experiment}, sort=[("created", pymongo.ASCENDING)])
    artifacts = [{"id": str(artifact["_id"]), "name": artifact.get("name", str(artifact["_id"]))} for artifact in artifacts]
    return flask.jsonify(artifacts=artifacts)


