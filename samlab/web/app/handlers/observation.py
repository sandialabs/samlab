# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

import arrow
import bson
import flask

import samlab.object
import samlab.observation
import samlab.web.app.handlers.common


# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


@application.route("/observations/<exclude(count,tags):oid>", methods=["GET", "DELETE"])
@require_auth
def get_delete_observations_observation(oid):
    oid = bson.objectid.ObjectId(oid)
    if flask.request.method == "GET":
        return samlab.web.app.handlers.common.get_otype_oid("observations", oid)
    elif flask.request.method == "DELETE":
        require_permissions(["delete"])
        samlab.observation.delete(database, fs, oid)
        return flask.jsonify()


