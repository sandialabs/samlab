// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-attribute-manager",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-object",
    "samlab-server",
    "samlab-tag-manager",
    "samlab-trial",
    "samlab-content-list-control",
    ], function(ko, mapping, attribute_manager, dashboard, dialog, object, server, tag_manager, trial)
{
    var component_name = "samlab-trial-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    models: [],
                    selected_option: null,
                    trial:
                    {
                        "attributes-pre": null,
                        content: [],
                        created: null,
                        id: widget.params.id,
                        models: [],
                        "modified-by": null,
                        modified: null,
                        name: null,
                        tags: [],
                    },
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, "trials", widget.params.id);
                var trial_changed_subscription = object.notify_changed("trials", widget.params.id, function()
                {
                    server.load_json(component, "/trials/" + component.trial.id());
                    server.load_json(component, "/trials/" + component.trial.id() + "/models");
                });

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    trial_changed_subscription.dispose();
                    attribute_manager.release("trials", component.trial.id);
                    tag_manager.release("trials", component.trial.id);
                }

                attribute_manager.manage("trials", component.trial.id);
                tag_manager.manage("trials", component.trial.id);
                dashboard.active_widget.subscribe(function(active_widget)
                {
                    if(active_widget != widget)
                        return;
                    attribute_manager.manage("trials", component.trial.id);
                    tag_manager.manage("trials", component.trial.id);
                });

                component.groups =
                [
                    {
                        label: "Models",
                        children: component.models.map(function(model)
                        {
                            return { label: model.name, icon: "fa-paper-plane", widget: "samlab-model-widget", params: {id: model.id}};
                        }),
                    },
                ];

                component.activate_item = function(item)
                {
                    dashboard.add_widget(item.widget, item.params);
                };

                component.manage_attributes = function()
                {
                    dashboard.add_widget("samlab-attribute-manager-widget");
                }

                component.manage_tags = function()
                {
                    dashboard.add_widget("samlab-tag-manager-widget");
                }

                component.delete_trial = function()
                {
                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                                trial.delete(component.trial.id());
                        },
                        message: "This will delete the trial and its models, and close any related dashboard widgets.",
                        title: "Delete Trial?",
                    });
                };

                component.trial.created_formatted = ko.pureComputed(function()
                {
                    if(component.trial.created())
                        return new Date(component.trial.created()).toLocaleString();
                    return null;
                });

                component.trial.modified_formatted = ko.pureComputed(function()
                {
                    if(component.trial.modified())
                        return new Date(component.trial.modified()).toLocaleString();
                    return null;
                });

                server.load_json(component, "/trials/" + component.trial.id());
                server.load_json(component, "/trials/" + component.trial.id() + "/models");

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
