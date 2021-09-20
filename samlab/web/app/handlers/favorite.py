# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import collections
import logging

#import bson
import flask

import samlab.favorite

# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


@application.route("/favorites")
@require_auth
def get_favorites():
    require_permissions(["read"])
    favorites = list(database.favorites.find())
    return flask.jsonify(favorites=favorites)


@application.route("/favorites/<allow(observations,experiments,artifacts,layouts):otype>/<oid>", methods=["PUT", "DELETE"])
@require_auth
def put_delete_favorites_otype_oid(otype, oid):
    if flask.request.method == "PUT":
        require_permissions(["write"])
        name = flask.request.json["name"]
        samlab.favorite.create(database, otype, oid, name)
        return flask.jsonify()

    elif flask.request.method == "DELETE":
        require_permissions(["delete"])
        samlab.favorite.delete(database, otype, oid)
        return flask.jsonify()
