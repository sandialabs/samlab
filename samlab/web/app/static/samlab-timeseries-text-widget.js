// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "jquery",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-server",
    "samlab-timeseries-manager",
    "URI",
    ], function(debug, jquery, ko, mapping, dashboard, server, timeseries_manager, URI)
{
    var component_name = "samlab-timeseries-text-widget";

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
                    samples: [],
                    timeseries:
                    {
                        key: widget.params.key,
                    },
                    version: widget.params.version,
                });

                // Load the plot at startup and anytime there are changes, but limit the rate.
                var load_data = ko.computed(function()
                {
                    var data = {
                        exclusions: component.exclusions(),
                        key: component.timeseries.key(),
                        'content-type': "text/plain",
                    }

                    server.post_json("/timeseries/samples", data, {success: function(data)
                    {
                        mapping.fromJS(container, data);
                    }});

                    timeseries_manager.sample.created();
                    timeseries_manager.sample.updated();
                    timeseries_manager.sample.deleted();
                }).extend({rateLimit: {timeout: 500}});

/*
                var on_show = timeseries_manager.on_show.subscribe(function(params)
                {
                    component.exclusions.remove(function(item)
                    {
                        return item.experiment == params.experiment && item.trial == params.trial;
                    });
                    component.version(component.version() + 1);
                });

                var on_hide = timeseries_manager.on_hide.subscribe(function(params)
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
*/

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
