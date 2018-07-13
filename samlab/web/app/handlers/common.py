# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging
import pprint

import arrow
import bson
import flask
import six

# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, socketio, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


def get_otype_oid(otype, oid):
    assert(isinstance(otype, six.string_types))
    assert(isinstance(oid, bson.objectid.ObjectId))

    require_permissions(["read"])

    obj = database[otype].find_one({"_id": oid})
    if obj is None:
        flask.abort(404)

    obj["name"] = obj.get("name", obj["_id"])

    obj["attributes-pre"] = pprint.pformat(obj["attributes"], depth=1)

    if "created" in obj:
        obj["created"] = arrow.get(obj["created"]).isoformat()
    if "modified" in obj:
        obj["modified"] = arrow.get(obj["modified"]).isoformat()

    content = obj.get("content", {})
    obj["content"] = [{"key": key, "content-type": value["content-type"], "filename": value.get("filename", None)} for key, value in content.items()]

    obj["tags"] = sorted(obj.get("tags", []))

    result = {
        otype[:-1]: obj,
    }

    return flask.jsonify(result)


