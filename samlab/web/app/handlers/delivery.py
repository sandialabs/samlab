# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging
import os

import arrow
import bson
import flask
import pymongo

import samlab.mime


# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs

@application.route("/deliveries")
@require_auth
def get_deliveries():
    require_permissions(["read"])
    deliveries = database.deliveries.find(sort=[("created", pymongo.DESCENDING)])
    deliveries = [delivery for delivery in deliveries if os.path.exists(delivery["directory"])]

    for delivery in deliveries:
        delivery["created"] = arrow.get(delivery["created"]).isoformat()
        delivery.pop("directory")

    return flask.jsonify(deliveries=deliveries)


@application.route("/deliveries/<did>", methods=["DELETE"])
@require_auth
def delete_deliveries_delivery(did):
    if flask.request.method == "DELETE":
        require_permissions(["delete"])
        did = bson.objectid.ObjectId(did)
        result = database.deliveries.delete_one({"_id": did})
        return flask.jsonify(deliveries_deleted=result.deleted_count)


@application.route("/deliveries/<did>/data")
@require_auth
def get_deliveries_delivery_data(did):
    require_permissions(["read"])
    delivery = bson.objectid.ObjectId(did)
    delivery = database.deliveries.find_one({"_id": delivery})

    directory = delivery["directory"]

    for name in os.listdir(directory):
        def stream_contents(path):
            with open(path, "rb") as stream:
                while True:
                    content = stream.read(2 ** 30)
                    if content:
                        yield content
                    else:
                        break

        path = os.path.join(directory, name)

        response = flask.Response(stream_contents(path))
        response.headers["content-type"] = samlab.mime.lookup_type(name)
        response.headers["content-length"] = os.path.getsize(path)
        return response


