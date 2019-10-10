// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-server",
    "samlab-timeseries",
    ], function(debug, ko, mapping, dashboard, server, timeseries)
{
    var component_name = "samlab-timeseries-plot-widget";

    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    timeseries:
                    {
                        key: widget.params.key,
                    },
                    plot: null,
					smoothing: widget.params.smoothing,
					yscale: widget.params.yscale,
                });

                component.yscale_items =
                [
                    {key: "linear", label: "Linear"},
                    {key: "log", label: "Log"},
                ];

                // Load the plot at startup and anytime there are changes, but limit the rate.
                var load_plot = ko.computed(function()
                {
                    server.load_json(component, "/timeseries/plots/auto?key=" + component.timeseries.key() + "&yscale=" + component.yscale() + "&smoothing=" + component.smoothing());

                    timeseries.sample.created();
                    timeseries.sample.updated();
                    timeseries.sample.deleted();
                }).extend({rateLimit: {timeout: 500}});

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {key: "foo/bar/baz", yscale: "linear", smoothing: 0.0}},
    };

    return module;
});
