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
    "URI",
    ], function(debug, element_resize, jquery, ko, mapping, dashboard, server, timeseries, URI)
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
                    exclusions: widget.params.exclusions,
                    height: container.innerHeight(),
                    plot: null,
					smoothing: widget.params.smoothing,
                    timeseries:
                    {
                        key: widget.params.key,
                    },
                    version: widget.params.version,
                    width: container.innerWidth(),
					yscale: widget.params.yscale,
                });

                component.height.extend({rateLimit: {timeout: 100, method: "notifyWhenChangesStop"}});
                component.width.extend({rateLimit: {timeout: 100, method: "notifyWhenChangesStop"}});

                component.yscale_items =
                [
                    {key: "linear", label: "Linear"},
                    {key: "log", label: "Log"},
                ];

                // Load the plot at startup and anytime there are changes, but limit the rate.
                var load_plot = ko.computed(function()
                {
                    var data = {
                        exclusions: component.exclusions(),
                        height: component.height(),
                        key: component.timeseries.key(),
                        smoothing: component.smoothing(),
                        width: component.width(),
                        yscale: component.yscale(),
                    }

                    server.post_json("/timeseries/plots/auto", data, {success: function(data)
                    {
                        component.plot(data.plot);
                    }});

                    timeseries.sample.created();
                    timeseries.sample.updated();
                    timeseries.sample.deleted();
                }).extend({rateLimit: {timeout: 500}});

                element_resize(container[0], function()
                {
                    component.width(container.innerWidth());
                    component.height(container.innerHeight());
                });

                var on_show = timeseries.on_show.subscribe(function(params)
                {
                    component.exclusions.remove(function(item)
                    {
                        return item.experiment == params.experiment && item.trial == params.trial;
                    });
                    component.version(component.version() + 1);
                });

                var on_hide = timeseries.on_hide.subscribe(function(params)
                {
                    component.exclusions.remove(function(item)
                    {
                        return item.experiment == params.experiment && item.trial == params.trial;
                    });
                    component.exclusions.push(params);
                    component.version(component.version() + 1);
                });

                component.dispose = function()
                {
                    on_show.dispose();
                    on_hide.dispose();
                }

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { width: 4, height: 8, params: {key: "", yscale: "linear", smoothing: 0.5, exclusions: [], version: 0}},
    };

    return module;
});