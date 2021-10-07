# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask
import toyplot.svg
import xml.etree

from samlab.dashboard import application, require_auth, require_permissions
from samlab.dashboard.service import require_backend


@application.route("/timeseries-collection/<name>")
@require_auth
def get_timeseries_count(name):
    require_permissions(["read"])
    timeseries_collection = require_backend("timeseries-collection", name)
    return flask.jsonify(count=len(timeseries_collection))


@application.route("/timeseries-collection/<name>/<int:index>")
@require_auth
def get_timeseries(name, index):
    require_permissions(["read"])
    timeseries_collection = require_backend("timeseries-collection", name)
    timeseries = timeseries_collection.get(index)
    canvas, axes, mark = toyplot.plot(timeseries)
    svg = toyplot.svg.render(canvas)
    return flask.Response(xml.etree.ElementTree.tostring(svg, encoding="utf8", method="xml"), mimetype="image/svg+xml")

