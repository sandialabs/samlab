# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import io
import logging
import pprint

import arrow
import bson
import flask
import toyplot.bitmap
import toyplot.color
import toyplot.html

import samlab.deserialize
import samlab.object

# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, socketio, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


@application.route("/<allow(observations,models):otype>/<oid>/content/<role>", methods=["DELETE"])
@require_auth
def delete_otype_oid_content_role(otype, oid, role):
    require_permissions(["delete"])
    oid = bson.objectid.ObjectId(oid)
    try:
        samlab.object.delete_content(database, fs, otype, oid, role)
    except KeyError:
        flask.abort(404)
    return flask.jsonify()


@application.route("/<allow(observations,trials,models):otype>/attributes/keys")
@require_auth
def get_otype_attributes_keys(otype):
    require_permissions(["read"])

    keys = set()
    for owner in database[otype].find(projection={"attributes":True, "_id": False}):
        keys.update(owner["attributes"].keys())

    return flask.jsonify(keys=sorted(keys))


@application.route("/<allow(observations,trials,models):otype>/<oid>/attributes/pre")
@require_auth
def get_otype_oid_attributes_pre(otype, oid):
    require_permissions(["read"])
    owner = bson.objectid.ObjectId(oid)
    owner = database[otype].find_one({"_id": owner})

    response = flask.make_response(pprint.pformat(owner["attributes"]))
    response.headers["content-type"] = "text/plain"
    return response


@application.route("/<allow(observations,trials,models):otype>/content/roles")
@require_auth
def get_otype_content_roles(otype):
    require_permissions(["read"])

    roles = set()
    for o in database[otype].find(projection={"content": True, "_id": False}):
        roles.update(o["content"].keys())

    return flask.jsonify(roles=sorted(roles))


@application.route("/<allow(observations,trials,models):otype>/<oid>/content/<role>/data")
@require_auth
def get_otype_oid_content_role_data(otype, oid, role):
    require_permissions(["read"])
    owner = bson.objectid.ObjectId(oid)
    owner = database[otype].find_one({"_id": owner})

    if role not in owner["content"]:
        flask.abort(404)

    content = fs.get(owner["content"][role]["data"])

    response = flask.make_response(content.read())
    response.headers["content-type"] = content.content_type
    response.cache_control.max_age = "300"
    response.cache_control.public = True
    return response


@application.route("/<allow(observations,trials,models):otype>/<oid>/content/<role>/array/image")
@require_auth
def get_otype_oid_content_role_array_image(otype, oid, role):
    require_permissions(["read"])

    owner = bson.objectid.ObjectId(oid)
    owner = database[otype].find_one({"_id": owner})

    if not role in owner["content"]:
        flask.abort(404)

    if owner["content"][role]["content-type"] != "application/x-numpy-array":
        flask.abort(400)

    data = samlab.deserialize.array(fs, owner["content"][role])

    cmap_factory = flask.request.args.get("cmap-factory", "linear")
    if cmap_factory == "brewer":
        cmap_factory = toyplot.color.brewer
        cmap_name = "BlueRed"
    elif cmap_factory == "linear":
        cmap_factory = toyplot.color.linear
        cmap_name = "Blackbody"
    elif cmap_factory == "diverging":
        cmap_factory = toyplot.color.diverging
        cmap_name = "BlueRed"
    else:
        flask.abort(400)

    cmap_name = flask.request.args.get("cmap-name", cmap_name)
    try:
        colormap = cmap_factory.map(cmap_name)
    except:
        flask.abort(400)

    data = colormap.colors(data)

    stream = io.BytesIO()
    toyplot.bitmap.to_png(data, stream)

    response = flask.make_response(stream.getvalue())
    response.headers["content-type"] = "image/png"
    return response


@application.route("/<allow(observations,trials,models):otype>/<oid>/content/<role>/array/metadata")
@require_auth
def get_otype_oid_content_role_array_metadata(otype, oid, role):
    require_permissions(["read"])

    owner = bson.objectid.ObjectId(oid)
    owner = database[otype].find_one({"_id": owner})

    if not role in owner["content"]:
        flask.abort(404)

    if owner["content"][role]["content-type"] != "application/x-numpy-array":
        flask.abort(400)

    array = samlab.deserialize.array(fs, owner["content"][role])

    metadata = {
        "dtype": array.dtype.name,
        "shape": array.shape,
        "size": array.size,
        "min": array.min() if array.size else None,
        "mean": array.mean() if array.size else None,
        "max": array.max() if array.size else None,
        "sum": array.sum() if array.size else None,
        }
    return flask.jsonify(metadata=metadata)


@application.route("/<allow(observations,trials,models):otype>/<oid>/content/<role>/image/metadata")
@require_auth
def get_otype_oid_content_role_image_metadata(otype, oid, role):
    require_permissions(["read"])

    owner = bson.objectid.ObjectId(oid)
    owner = database[otype].find_one({"_id": owner})

    if not role in owner["content"]:
        flask.abort(404)

    if owner["content"][role]["content-type"] not in ["image/jpeg", "image/png"]:
        flask.abort(400)

    image = samlab.deserialize.image(fs, owner["content"][role])

    return flask.jsonify(metadata={"size": image.size})


@application.route("/<allow(observations,trials,models):otype>/tags")
@require_auth
def get_otype_tags(otype):
    require_permissions(["read"])

    tags = set()
    for owner in database[otype].find(projection={"tags":True, "_id": False}):
        tags.update(owner["tags"])

    return flask.jsonify(tags=sorted(tags))


@application.route("/<allow(observations,trials,models):otype>/<oid>/attributes", methods=["PUT"])
@require_auth
def put_otype_oid_attributes(otype, oid):
    require_permissions(["write"])
    owner = bson.objectid.ObjectId(oid)
    owner = database[otype].find_one({"_id": owner})

    attributes = owner["attributes"]
    attributes.update(flask.request.json)

    database[otype].update_one(
        {"_id": owner["_id"]},
        {"$set": {"attributes": attributes, "modified-by": flask.request.authorization.username, "modified": arrow.utcnow().datetime}}
        )

    socketio.emit("attribute-keys-changed", otype) # TODO: Handle this in samlab.web.app.watch_database

    return flask.jsonify()


@application.route("/<allow(observations,trials,models):otype>/<oid>/tags", methods=["PUT"])
@require_auth
def put_otype_oid_tags(otype, oid):
    require_permissions(["write"])
    owner = bson.objectid.ObjectId(oid)
    owner = database[otype].find_one({"_id": owner})

    add = flask.request.json["add"]
    remove = flask.request.json["remove"]
    toggle = flask.request.json["toggle"]

    tags = set(owner["tags"])
    for tag in add:
        tags.add(tag)
    for tag in remove:
        tags.discard(tag)
    for tag in toggle:
        if tag in tags:
            tags.discard(tag)
        else:
            tags.add(tag)
    tags = list(tags)

    database[otype].update_one(
        {"_id": owner["_id"]},
        {"$set": {"tags": tags, "modified-by": flask.request.authorization.username, "modified": arrow.utcnow().datetime}}
        )

    socketio.emit("tags-changed", otype) # TODO: Handle this in samlab.web.app.watch_database

    return flask.jsonify()


