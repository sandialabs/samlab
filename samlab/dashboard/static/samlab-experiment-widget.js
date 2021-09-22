// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-attribute-manager",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-object-manager",
    "samlab-server",
    "samlab-tag-manager",
    "samlab-experiment-manager",
    "samlab-attribute-control",
    "samlab-content-list-control",
    ], function(ko, mapping, attribute_manager, dashboard, dialog, object, server, tag_manager, experiment_manager)
{
    var component_name = "samlab-experiment-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    artifacts: [],
                    selected_option: null,
                    experiment:
                    {
                        "attributes-pre": null,
                        content: [],
                        created: null,
                        id: widget.params.id,
                        artifacts: [],
                        "modified-by": null,
                        modified: null,
                        name: null,
                        tags: [],
                    },
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, "experiments", widget.params.id);
                var experiment_changed_subscription = object.notify_changed("experiments", widget.params.id, function()
                {
                    server.load_json(component, "/experiments/" + component.experiment.id());
                    server.load_json(component, "/experiments/" + component.experiment.id() + "/artifacts");
                });

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    experiment_changed_subscription.dispose();
                    attribute_manager.release("experiments", component.experiment.id);
                    tag_manager.release("experiments", component.experiment.id);
                }

                attribute_manager.manage("experiments", component.experiment.id);
                tag_manager.manage("experiments", component.experiment.id);
                dashboard.active_widget.subscribe(function(active_widget)
                {
                    if(active_widget != widget)
                        return;
                    attribute_manager.manage("experiments", component.experiment.id);
                    tag_manager.manage("experiments", component.experiment.id);
                });

                component.groups =
                [
                    {
                        label: "Visualizations",
                        children:
                        [
                        ],
                    },
                    {
                        label: "Artifacts",
                        children: component.artifacts.map(function(artifact)
                        {
                            return { label: artifact.name, icon: "fa-paper-plane", widget: "samlab-artifact-widget", params: {id: artifact.id}};
                        }),
                    },
                ];

                component.activate_item = function(item)
                {
                    dashboard.add_widget(item.widget, item.params);
                };

                component.manage_attributes = function()
                {
                    dashboard.add_widget("samlab-attribute-widget");
                }

                component.manage_tags = function()
                {
                    dashboard.add_widget("samlab-tag-widget");
                }

                component.delete_experiment = function()
                {
                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                                experiment_manager.delete(component.experiment.id());
                        },
                        message: "This will delete the experiment and its artifacts, and close any related dashboard widgets.",
                        title: "Delete Trial?",
                    });
                };

                component.experiment.created_formatted = ko.pureComputed(function()
                {
                    if(component.experiment.created())
                        return new Date(component.experiment.created()).toLocaleString();
                    return null;
                });

                component.experiment.modified_formatted = ko.pureComputed(function()
                {
                    if(component.experiment.modified())
                        return new Date(component.experiment.modified()).toLocaleString();
                    return null;
                });

                server.load_json(component, "/experiments/" + component.experiment.id());
                server.load_json(component, "/experiments/" + component.experiment.id() + "/artifacts");

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
