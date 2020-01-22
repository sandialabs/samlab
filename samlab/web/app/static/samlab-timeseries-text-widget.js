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
                    loading: false,
                    samples: [],
                    timeseries:
                    {
                        key: widget.params.key,
                    },
                });

                component.exclude = timeseries_manager.exclude;

                // Load the plot at startup and anytime there are changes, but limit the rate.
                var load_data = ko.computed(function()
                {
                    if(component.loading())
                        return;

                    component.loading(true);
                    var data = {
                        exclude: mapping.toJS(component.exclude()),
                        key: component.timeseries.key(),
                    }

                    server.post_json("/timeseries/visualization/text", data, {success: function(data)
                    {
                        component.loading(false);
                        mapping.fromJS(data, component);
                    }});

                    timeseries_manager.sample.created();
                    timeseries_manager.sample.updated();
                    timeseries_manager.sample.deleted();
                }).extend({rateLimit: {timeout: 5000}});

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { width: 4, height: 8, params: {key: "", yscale: "linear", smoothing: 0.5}},
    };

    return module;
});
