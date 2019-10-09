# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import bson
import flask

import samlab.artifact
import samlab.web.app.handlers.common

# Get the web server.
from samlab.web.app import application, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


@application.route("/artifacts/<exclude(count,tags):oid>", methods=["GET", "DELETE"])
@require_auth
def get_delete_artifacts_artifact(oid):
    oid = bson.objectid.ObjectId(oid)

    if flask.request.method == "GET":
        return samlab.web.app.handlers.common.get_otype_oid("artifacts", oid)

    elif flask.request.method == "DELETE":
        require_permissions(["delete"])
        samlab.artifact.delete(database, fs, oid)
        return flask.jsonify()


