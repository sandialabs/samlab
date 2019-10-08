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
    var component_name = "samlab-artifact-attributes-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    artifact:
                    {
                        id: widget.params.id,
                    },
                    artifact_attributes_pre: "Loading \u2026",
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, "artifacts", widget.params.id);
                var artifact_changed_subscription = object.notify_changed("artifacts", widget.params.id, function()
                {
                    server.load_text("/artifacts/" + component.artifact.id() + "/attributes/pre", function(value)
                    {
                        component.artifact_attributes_pre(value);
                    });
                });


                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    artifact_changed_subscription.dispose();
                }

                server.load_text("/artifacts/" + component.artifact.id() + "/attributes/pre", function(value)
                {
                    component.artifact_attributes_pre(value);
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
