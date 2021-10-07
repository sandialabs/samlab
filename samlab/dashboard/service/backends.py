# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask

from samlab.dashboard import application, require_auth, require_permissions
from samlab.dashboard.service import _backends


@application.route("/backends")
@require_auth
def get_backends():
    require_permissions(["read"])
    backends = [{"service": service, "name": name} for service in _backends for name in _backends[service]]
    return flask.jsonify(backends=backends)


