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

    experiment_trials = collections.defaultdict(set)

    for item in database.timeseries.aggregate([{"$group": {"_id": {"experiment": "$experiment", "trial": "$trial"}}}]):
        experiment = item["_id"]["experiment"]
        trial = item["_id"]["trial"]
        experiment_trials[experiment].add(trial)

    result = {"experiments": []}

    for experiment in sorted(experiment_trials.keys()):
        result["experiments"].append({
            "experiment": experiment,
            "trials": [{
                "trial": trial,
                "color": toyplot.color.to_css(_get_color(experiment, trial)),
                } for trial in sorted(experiment_trials[experiment])],
            })

    result["keys"] = database.timeseries.distinct("key")

    return flask.jsonify(result)


@application.route("/timeseries/plots/auto", methods=["POST"])
@require_auth
def post_timeseries_plots_auto():
    require_permissions(["read"])

    experiments = flask.request.json.get("experiments", [])
    height = int(float(flask.request.json.get("height", 500)))
    key = flask.request.json.get("key")
    smoothing = float(flask.request.json.get("smoothing", "0"))
    trials = flask.request.json.get("trials", [])
    width = int(float(flask.request.json.get("width", 500)))
    yscale = flask.request.json.get("yscale", "linear")

    log.debug("experiments: {}".format(experiments))
    log.debug("trials: {}".format(trials))

    canvas = toyplot.Canvas(width=width, height=height)
    axes = canvas.cartesian(xlabel="Step", yscale=yscale)

    steps = collections.defaultdict(list)
    values = collections.defaultdict(list)
    timestamps = collections.defaultdict(list)

    query = {"key": key, "experiment": {"$nin": experiments.get("exclude", [])}}
    log.debug("query: {}".format(query))

    for sample in database.timeseries.find(query):
        experiment = sample.get("experiment")
        trial = sample.get("trial")
        step = sample["step"]
        value = sample["value"]
        timestamp = sample["timestamp"]
        steps[(experiment, trial)].append(step)
        values[(experiment, trial)].append(value)
        timestamps[(experiment, trial)].append(timestamp)

    for item in steps:
        steps[item] = numpy.array(steps[item])
        values[item] = numpy.array(values[item])
        timestamps[item] = numpy.array(timestamps[item])

    for index, item in enumerate(steps):
        experiment, trial = item
        color = _get_color(experiment, trial)

        # Display smoothed data.
        if smoothing:
            smoothed = []
            last = values[item][0]
            for value in values[item]:
                smoothed_val = last * smoothing + (1 - smoothing) * value
                smoothed.append(smoothed_val)
                last = smoothed_val

            title = "{} / {}".format(experiment, trial)
            axes.plot(steps[item], values[item], color=color, opacity=0.25, style={"stroke-width":1}, title=title)

            title = "{} / {} (smoothed)".format(experiment, trial)
            axes.plot(steps[item], smoothed, color=color, opacity=1, style={"stroke-width":2}, title=title)
        # Just display the data
        else:
            title = "{} / {}".format(experiment, trial)
            axes.plot(steps[item], values[item], color=color, opacity=1, style={"stroke-width":2}, title=title)

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


