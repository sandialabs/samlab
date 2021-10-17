# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import flask
import scipy.signal
import toyplot.html
import xml.etree

from samlab.dashboard import application, require_auth, require_permissions
from samlab.dashboard.service import require_backend


@application.route("/timeseries-collection/<name>")
@require_auth
def get_timeseries(name):
    require_permissions(["read"])
    timeseries_collection = require_backend("timeseries-collection", name)
    count = len(timeseries_collection)
    keys = list(timeseries_collection.keys())
    return flask.jsonify(count=count, keys=keys)


@application.route("/timeseries-collection/<name>/plot", methods=["POST"])
@require_auth
def post_timeseries_plot(name):
    require_permissions(["read"])
    timeseries_collection = require_backend("timeseries-collection", name)

    timeseries = [timeseries_collection.get(key) for key in sorted(flask.request.json.get("keys", []))]

    height = int(float(flask.request.json.get("height", 500)))
    max_samples = int(float(flask.request.json.get("max_samples", 1000)))
    smoothing = float(flask.request.json.get("smoothing", "0"))
    width = int(float(flask.request.json.get("width", 500)))
    yscale = flask.request.json.get("yscale", "linear")

    canvas = toyplot.Canvas(width=width, height=height)
    axes = canvas.cartesian(xlabel="Step", yscale=yscale)

    palette = toyplot.color.brewer.palette("Set2")
    for index, columns in enumerate(timeseries):
        color = palette[index]

        if columns.shape[1] == 1:
            x = numpy.arange(columns.shape[0])
            y = columns[:,0]
        elif columns.shape[1] == 2:
            x = columns[:,0]
            y = columns[:,1]
        if columns.shape[1] == 3:
            x = columns[:,0]
            y = columns[:,2]

        if smoothing:
            alpha = 1 - smoothing
            b = [alpha]
            a = [1, alpha-1]
            zi = scipy.signal.lfiltic(b, a, y[0:1], [0])
            ys = scipy.signal.lfilter(b, a, y, zi=zi)[0]
            axes.plot(x, y, color=color, opacity=0.25)
            axes.plot(x, ys, color=color)
        else:
            axes.plot(x, y, color=color)
    return flask.jsonify({"plot": toyplot.html.tostring(canvas)})

