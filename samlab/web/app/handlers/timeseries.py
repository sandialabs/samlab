# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import collections
import hashlib
import logging
import re

import flask
import numpy
import toyplot.bitmap
import toyplot.color
import toyplot.html

import samlab.timeseries

# Setup logging.
log = logging.getLogger(__name__)

# Get the web server.
from samlab.web.app import application, require_auth, require_permissions

# Get the database.
from samlab.web.app.database import database, fs


def _get_color(experiment, trial):
    index = int(hashlib.sha1((experiment + trial).encode("utf8")).hexdigest(), 16) % len(_get_color.palette)
    return _get_color.palette[index]
_get_color.palette = toyplot.color.brewer.palette("Set2")

@application.route("/timeseries/metadata")
@require_auth
def get_timeseries_metadata():
    require_permissions(["read"])

    experiments = set()
    keys = set()

    experiment_trials = collections.defaultdict(set)
    experiment_keys = collections.defaultdict(set)
    key_experiments = collections.defaultdict(set)
    key_trials = collections.defaultdict(set)

    for item in database.timeseries.aggregate([{"$group": {"_id": {"experiment": "$experiment", "trial": "$trial", "key": "$key"}}}]):
        experiment = item["_id"]["experiment"]
        trial = item["_id"]["trial"]
        key = item["_id"]["key"]

        experiments.add(experiment)
        keys.add(key)

        experiment_trials[experiment].add(trial)
        experiment_keys[experiment].add(key)
        key_experiments[key].add(experiment)
        key_trials[key].add(trial)

    result = {"experiments": [], "keys": []}

    for experiment in sorted(experiments):
        result["experiments"].append({
            "experiment": experiment,
            "keys": sorted(experiment_keys[experiment]),
            "trials": [{
                "trial": trial,
                "color": toyplot.color.to_css(_get_color(experiment, trial)),
                } for trial in sorted(experiment_trials[experiment])],
            })

    for key in sorted(keys):
        result["keys"].append({
            "key":key,
            "experiments": sorted(key_experiments[key]),
            "trials": sorted(key_trials[key]),
            })

    return flask.jsonify(result)


@application.route("/timeseries/plots/auto")
@require_auth
def get_timeseries_plots_auto():
    require_permissions(["read"])

    experiment = flask.request.args.get("experiment")
    height = int(float(flask.request.args.get("height", 500)))
    key = flask.request.args.get("key")
    smoothing = float(flask.request.args.get("smoothing", "0"))
    width = int(float(flask.request.args.get("width", 500)))
    yscale = flask.request.args.get("yscale", "linear")

    canvas = toyplot.Canvas(width=width, height=height)
    axes = canvas.cartesian(xlabel="Step", yscale=yscale)

    steps = collections.defaultdict(list)
    values = collections.defaultdict(list)
    timestamps = collections.defaultdict(list)

    for sample in database.timeseries.find({"experiment": experiment, "key": key}):
        series = sample.get("trial")
        step = sample["step"]
        value = sample["value"]
        timestamp = sample["timestamp"]
        steps[series].append(step)
        values[series].append(value)
        timestamps[series].append(timestamp)

    for series in steps:
        steps[series] = numpy.array(steps[series])
        values[series] = numpy.array(values[series])
        timestamps[series] = numpy.array(timestamps[series])

    for index, series in enumerate(steps):
        color = _get_color(experiment, series)

        # Display smoothed data.
        if smoothing:
            smoothed = []
            last = values[series][0]
            for value in values[series]:
                smoothed_val = last * smoothing + (1 - smoothing) * value
                smoothed.append(smoothed_val)
                last = smoothed_val
            axes.plot(steps[series], values[series], color=color, opacity=0.3, style={"stroke-width":1}, title=series)
            axes.plot(steps[series], smoothed, color=color, opacity=1, style={"stroke-width":2}, title="{} (smoothed)".format(series))
        # Just display the data
        else:
            axes.plot(steps[series], values[series], color=color, opacity=1, style={"stroke-width":2}, title=series)

    result = {}
    result["plot"] = toyplot.html.tostring(canvas)

    return flask.jsonify(result)


@application.route("/timeseries/samples", methods=["DELETE"])
@require_auth
def delete_timeseries_samples():
    require_permissions(["delete"])

    experiment = flask.request.args.get("experiment", None)
    trial = flask.request.args.get("trial", None)
    key = flask.request.args.get("key", None)

    samlab.timeseries.delete(database, fs, experiment=experiment, trial=trial, key=key)

    return flask.jsonify()


