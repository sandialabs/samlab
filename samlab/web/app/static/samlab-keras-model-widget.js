// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-object",
    "samlab-server",
    "samlab-socket",
    ], function(ko, mapping, dashboard, object, server, socket)
{
    var component_name = "samlab-keras-model-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    content_type: widget.params["content-type"],
                    label: object.label(widget.params.otype, {singular: true, capitalize: true}) + " Content",
                    oid: widget.params.oid,
                    otype: widget.params.otype,
                    key: widget.params.key,
                    summary: { layers: [] },
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, widget.params.otype, widget.params.oid);

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    socket.off("keras-model-summary", component.keras_model_summary_ready);
                }

                component.loading = ko.pureComputed(function()
                {
                    return component.summary.layers().length == 0 ? true : false;
                })

                component.keras_model_summary_ready = function(summary)
                {
                    if(summary.otype == component.otype() && summary.oid == component.oid() && summary.key == component.key())
                    {
                        mapping.fromJS({summary: summary.summary}, component);
                    }
                }

                socket.on("keras-model-summary", component.keras_model_summary_ready);
                socket.emit("keras-model-summary", {otype: component.otype(), oid: component.oid(), key: component.key()});

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { },
    };

    return module;
});
