// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-object",
    "samlab-server",
    ], function(ko, mapping, dashboard, object, server)
{
    var component_name = "samlab-auto-plot-widget";

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    object:
                    {
                        otype: widget.params.otype,
                        oid: widget.params.oid,
                        name: widget.params.name,
                    },
                    plot: null,
					smoothing: widget.params.smoothing,
					yscale: widget.params.yscale,
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, widget.params.otype, widget.params.oid);
                var object_changed_subscription = object.notify_changed(widget.params.otype, widget.params.oid, function()
                {
                    component.load_plot();
                });

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    object_changed_subscription.dispose();
                }

                component.yscale_items =
                [
                    {key: "linear", label: "Linear"},
                    {key: "log", label: "Log"},
                ];

                component.load_plot = function()
                {
                    server.load_json(component, "/" + component.object.otype() + "/" + component.object.oid() + "/plots/auto?yscale=" + component.yscale() + "&smoothing=" + component.smoothing());
                };

                component.auto_load_plot = ko.computed(function()
                {
                    component.load_plot();
                });

                server.load_json(component, "/" + component.object.otype() + "/" + component.object.oid());

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {yscale: "linear", smoothing: 0.0}},
    };

    return module;
});
