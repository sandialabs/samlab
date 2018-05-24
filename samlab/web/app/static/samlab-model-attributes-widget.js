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
    var component_name = "samlab-model-attributes-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    model:
                    {
                        id: widget.params.id,
                    },
                    model_attributes_pre: "Loading \u2026",
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, "models", widget.params.id);
                var model_changed_subscription = object.notify_changed("models", widget.params.id, function()
                {
                    server.load_text("/models/" + component.model.id() + "/attributes/pre", function(value)
                    {
                        component.model_attributes_pre(value);
                    });
                });


                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    model_changed_subscription.dispose();
                }

                server.load_text("/models/" + component.model.id() + "/attributes/pre", function(value)
                {
                    component.model_attributes_pre(value);
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
