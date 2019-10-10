// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-object",
    "samlab-server",
    ], function(debug, ko, mapping, dashboard, object, server)
{
    var log = debug("samlab-attributes-widget");

    var component_name = "samlab-attributes-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                log(widget);

                var component = mapping.fromJS(
                {
                    object:
                    {
                        otype: widget.params.otype,
                        oid: widget.params.oid,
                    },
                    attributes_pre: "Loading \u2026",
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, widget.params.otype, widget.params.oid);
                var artifact_changed_subscription = object.notify_changed(widget.params.otype, widget.params.oid, function()
                {
                    server.load_text("/" + component.object.otype() + "/" + component.object.oid() + "/attributes/pre", function(value)
                    {
                        component.attributes_pre(value);
                    });
                });


                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    artifact_changed_subscription.dispose();
                }

                server.load_text("/" + component.object.otype() + "/" + component.object.oid() + "/attributes/pre", function(value)
                {
                    component.attributes_pre(value);
                });

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
