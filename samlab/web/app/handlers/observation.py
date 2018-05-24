# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

import arrow
import bson
import flask

import samlab.object
import samlab.observation


# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, socketio, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


@application.route("/observations")
@require_auth
def get_observations():
    require_permissions(["read"])

    search = flask.request.args.get("search", "")
    if search:
        observations = samlab.observation.expand(database, samlab.object.search(database, "observations", search))
    else:
        observations = list(database.observations.find({}))

    sort = flask.request.args.get("sort", "tags")
    if sort == "id":
        observations = sorted(observations, key=lambda o: o["_id"])
    elif sort == "modified":
        observations = sorted(observations, key=lambda o: arrow.get(o["modified"]).isoformat() if "modified" in o else "")[::-1]
    elif sort == "modified-by":
        observations = sorted(observations, key=lambda o: (0, o["modified-by"]) if "modified-by" in o else (1, None))
    elif sort == "original-filename":
        observations = sorted(observations, key=lambda o: [value.get("filename", None) for value in o.get("content", {}).values()])
    elif sort == "tags":
        observations = sorted(observations, key=lambda o: ("label:reviewed" in o["tags"], sorted(o["tags"])))
    else:
        flask.abort(400)
    ids = [str(observation["_id"]) for observation in observations]
    return flask.jsonify(observations=ids)


@application.route("/observations/<exclude(tags):observation>", methods=["GET", "DELETE"])
@require_auth
def get_delete_observations_observation(observation):
    if flask.request.method == "GET":
        require_permissions(["read"])
        observation = bson.objectid.ObjectId(observation)
        observation = database.observations.find_one({"_id": observation})

        if "created" in observation:
            observation["created"] = arrow.get(observation["created"]).isoformat()
        if "modified" in observation:
            observation["modified"] = arrow.get(observation["modified"]).isoformat()

        observation["content"] = [{"role": role, "content-type": spec["content-type"], "filename": spec.get("filename", None)} for role, spec in observation["content"].items()]

        observation["tags"] = sorted(observation.get("tags", []))

        return flask.jsonify(observation=observation)
    elif flask.request.method == "DELETE":
        require_permissions(["delete"])
        observation = bson.objectid.ObjectId(observation)
        samlab.observation.delete(database, fs, observation)
        return flask.jsonify()


