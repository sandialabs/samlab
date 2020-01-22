# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import collections
import functools
import hashlib
import logging
import re
import xml.etree.ElementTree as xml

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

    keys = collections.defaultdict(set)
    for item in database.timeseries.aggregate([{"$group": {"_id": {"experiment": "$experiment", "trial": "$trial", "key": "$key", "content-type": "$content-type"}}}]):
        item = item["_id"]
        try:
            keys[item["key"]].add(item["content-type"])
        except Exception as e:
            log.error(e)

    result["keys"] = [{"key": key, "content-types": content_types} for key, content_types in sorted(keys.items())]

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


def _get_samples(key, include_content_types, include, exclude):
    # Use-cases
    #
    # * Include content-type(s)
    # * Exclude experiment(s)
    # * Exclude trial(s)

    exclude_experiments = set()
    exclude_trials = set()

    for item in exclude:
        if "experiment" in item and "trial" not in item:
            exclude_experiments.add(item["experiment"])

    for item in exclude:
        if "experiment" in item and "trial" in item:
            exclude_trials.add((item["experiment"], item["trial"]))

    query = {
        "key": key,
        "experiment": {"$nin": list(exclude_experiments)},
        "content-type": {"$in": list(include_content_types)},
        }

    #log.debug(f"query: {query} exclude_trials: {exclude_trials}")

    samples = []
    for sample in database.timeseries.find(query):
        if (sample["experiment"], sample["trial"]) in exclude_trials:
            continue
        samples.append(sample)
    return samples


class Reservoir(object):
    def __init__(self, size, seed=1234):
        self._storage = []
        self._size = size
        self._count = 0
        self._generator = numpy.random.RandomState(seed=seed)

    def __len__(self):
        return self._storage.__len__()

    def __getitem__(self, key):
        return self._storage.__getitem__(key)

    def append(self, item):
        self._count += 1
        if len(self._storage) < self._size:
            self._storage.append(item)
        else:
            index = self._generator.choice(self._count)
            if index < self._size:
                self._storage[index] = item


@application.route("/timeseries/visualization/plot", methods=["POST"])
@require_auth
def post_timeseries_visualization_plot():
    require_permissions(["read"])

    exclude = flask.request.json.get("exclude", [])
    height = int(float(flask.request.json.get("height", 500)))
    include = flask.request.json.get("include", [])
    key = flask.request.json.get("key")
    max_samples = int(float(flask.request.json.get("max_samples", 1000)))
    smoothing = float(flask.request.json.get("smoothing", "0"))
    width = int(float(flask.request.json.get("width", 500)))
    yscale = flask.request.json.get("yscale", "linear")

    sample_reservoir = functools.partial(Reservoir, size=max_samples, seed=1234)

    steps = collections.defaultdict(sample_reservoir)
    values = collections.defaultdict(sample_reservoir)
    timestamps = collections.defaultdict(sample_reservoir)

    generator = numpy.random.RandomState(seed=1234)
    samples = _get_samples(key, ["application/x-scalar"], include, exclude)
    for sample in samples:
        series = (sample["experiment"], sample["trial"])
        steps[series].append(sample["step"])
        values[series].append(sample["value"])
        timestamps[series].append(sample["timestamp"])

    for series in steps.keys():
        sort_order = numpy.argsort(steps[series])
        steps[series] = numpy.array(steps[series])[sort_order]
        values[series] = numpy.array(values[series])[sort_order]
        timestamps[series] = numpy.array(timestamps[series])[sort_order]

    # Create the plot.
    canvas = toyplot.Canvas(width=width, height=height)
    axes = canvas.cartesian(xlabel="Step", yscale=yscale)

    for index, series in enumerate(steps.keys()):
        experiment, trial = series
        color = _get_color(experiment, trial)

        # Display smoothed data.
        if smoothing:
            smoothed = []
            last = values[series][0]
            for value in values[series]:
                smoothed_val = last * smoothing + (1 - smoothing) * value
                smoothed.append(smoothed_val)
                last = smoothed_val

            title = "{} / {}".format(experiment, trial)
            axes.plot(steps[series], values[series], color=color, opacity=0.25, style={"stroke-width":1}, title=title)

            title = "{} / {} (smoothed)".format(experiment, trial)
            axes.plot(steps[series], smoothed, color=color, opacity=1, style={"stroke-width":2}, title=title)
        # Just display the data
        else:
            title = "{} / {}".format(experiment, trial)
            axes.plot(steps[series], values[series], color=color, opacity=1, style={"stroke-width":2}, title=title)

    return flask.jsonify({"plot": toyplot.html.tostring(canvas)})

@application.route("/timeseries/visualization/text", methods=["POST"])
@require_auth
def post_timeseries_visualization_text():
    require_permissions(["read"])

    exclude = flask.request.json.get("exclude", [])
    include = flask.request.json.get("include", [])
    key = flask.request.json.get("key")

    samples = _get_samples(key, ["text/plain"], include, exclude)
    for sample in samples:
        sample["color"] = toyplot.color.to_css(_get_color(sample["experiment"], sample["trial"]))
    return flask.jsonify({"samples": samples})


