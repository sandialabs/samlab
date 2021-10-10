# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.dashboard import application, require_auth, require_permissions
from samlab.dashboard.service import require_backend


@application.route("/document-collection/<name>")
@require_auth
def get_document_count(name):
    require_permissions(["read"])
    document_collection = require_backend("document-collection", name)
    return flask.jsonify(count=len(document_collection))


@application.route("/document-collection/<name>/<int:index>")
@require_auth
def get_document(name, index):
    require_permissions(["read"])
    document_collection = require_backend("document-collection", name)
    document = document_collection.get(index)
    if isinstance(document, str):
        return flask.send_file(document)
    else:
        raise RuntimeError(f"Unknown document type: {type(document)}")


