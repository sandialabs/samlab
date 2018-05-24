// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-object",
    "samlab-server",
    ], function(ko, dashboard, object, server)
{
    var component_name = "samlab-training-accuracy-widget";

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    maximum_test_accuracy: null,
                    maximum_training_accuracy: null,
                    maximum_validation_accuracy: null,
                    model: {
                        id: widget.params.id,
                        name: null,
                    },
                    plot: null,
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, "models", widget.params.id);

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                }

                server.load_json(component, "/models/" + component.model.id());
                server.load_json(component, "/models/" + component.model.id() + "/plots/training-accuracy");

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
