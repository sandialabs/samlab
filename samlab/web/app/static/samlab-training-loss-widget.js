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
    var component_name = "samlab-training-loss-widget";

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    minimum_test_loss: null,
                    minimum_training_loss: null,
                    minimum_validation_loss: null,
                    model:
                    {
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

                component.show_model = function()
                {
                    dashboard.add_widget("samlab-model-widget", {id: widget.params.id});
                };

                component.minimum_training_loss_formatted = ko.pureComputed(function()
                {
                    return component.minimum_training_loss() != null ? Number(component.minimum_training_loss()).toPrecision(4) : "";
                });

                component.minimum_validation_loss_formatted = ko.pureComputed(function()
                {
                    return component.minimum_validation_loss() != null ? Number(component.minimum_validation_loss()).toPrecision(4) : "";
                });

                component.minimum_test_loss_formatted = ko.pureComputed(function()
                {
                    return component.minimum_test_loss() != null ? Number(component.minimum_test_loss()).toPrecision(4) : "";
                });

                component.scale = widget.params.scale;

                component.scale_items =
                [
                    {key: "linear", label: "Linear"},
                    {key: "log", label: "Log"},
                ];

                component.show_training = widget.params.show_training != null ? widget.params.show_training : true;
                component.show_validation = widget.params.show_validation != null ? widget.params.show_validation : true;
                component.show_test = widget.params.show_test != null ? widget.params.show_test : true;

                component.load_plot = ko.computed(function()
                {
                    server.load_json(component, "/models/" + component.model.id() + "/plots/training-loss?scale=" + component.scale() + "&training=" + component.show_training() + "&validation=" + component.show_validation() + "&test=" + component.show_test());
                });

                server.load_json(component, "/models/" + component.model.id());

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {scale: "linear", show_training: true, show_validation: true, show_test: true}},
    };

    return module;
});
