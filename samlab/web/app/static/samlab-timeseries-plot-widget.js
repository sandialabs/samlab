// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-server",
    "samlab-timeseries",
    ], function(ko, mapping, dashboard, server, timeseries)
{
    var component_name = "samlab-timeseries-plot-widget";

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

                var timeseries_changed_subscription = timeseries.notify_changed(widget.params.key, function()
                {
                    component.load_plot();
                });

                component.dispose = function()
                {
                    timeseries_changed_subscription.dispose();
                }

                component.yscale_items =
                [
                    {key: "linear", label: "Linear"},
                    {key: "log", label: "Log"},
                ];

                component.load_plot = function()
                {
                    server.load_json(component, "/timeseries/plots/auto?key=" + component.timeseries.key() + "&yscale=" + component.yscale() + "&smoothing=" + component.smoothing());
                };

                component.auto_load_plot = ko.computed(function()
                {
                    component.load_plot();
                });

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
