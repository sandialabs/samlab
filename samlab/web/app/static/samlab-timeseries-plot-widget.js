// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "element-resize-event",
    "jquery",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-server",
    "samlab-timeseries",
    ], function(debug, element_resize, jquery, ko, mapping, dashboard, server, timeseries)
{
    var component_name = "samlab-timeseries-plot-widget";

    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var container = jquery(component_info.element.querySelector(".plot"));

                var component = mapping.fromJS(
                {
                    timeseries:
                    {
                        key: widget.params.key,
                    },
                    plot: null,
					smoothing: widget.params.smoothing,
					yscale: widget.params.yscale,
                    width: container.innerWidth(),
                    height: container.innerHeight(),
                });

                component.width.extend({rateLimit: {timeout: 100, method: "notifyWhenChangesStop"}});
                component.height.extend({rateLimit: {timeout: 100, method: "notifyWhenChangesStop"}});

                component.yscale_items =
                [
                    {key: "linear", label: "Linear"},
                    {key: "log", label: "Log"},
                ];

                // Load the plot at startup and anytime there are changes, but limit the rate.
                var load_plot = ko.computed(function()
                {
                    server.load_json(component, "/timeseries/plots/auto?key=" + component.timeseries.key() + "&yscale=" + component.yscale() + "&smoothing=" + component.smoothing() + "&width=" + container.width() + "&height=" + component.height());

                    timeseries.sample.created();
                    timeseries.sample.updated();
                    timeseries.sample.deleted();
                }).extend({rateLimit: {timeout: 500}});

                element_resize(container[0], function()
                {
                    component.width(container.innerWidth());
                    component.height(container.innerHeight());
                });

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {key: "", yscale: "linear", smoothing: 0.0}},
    };

    return module;
});
