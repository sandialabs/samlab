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
    "samlab-observation-manager",
    "samlab-permissions",
    "samlab-server",
    "samlab-tag-manager",
    "samlab-attribute-control",
    "samlab-content-list-control",
    ], function(ko, mapping, attribute_manager, dashboard, dialog, object, observation_manager, permissions, server, tag_manager)
{
    var component_name = "samlab-observation-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    observation: {
                        content: [],
                        created: null,
                        id: widget.params.id,
                        "modified-by": null,
                        modified: null,
                        tags: [],
                        },
                    permissions: permissions,
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, "observations", widget.params.id);
                var observation_changed_subscription = object.notify_changed("observations", widget.params.id, function()
                {
                    server.load_json(component, "/observations/" + component.observation.id());
                });



                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    observation_changed_subscription.dispose();
                    attribute_manager.release("observations", component.observation.id);
                    tag_manager.release("observations", component.observation.id);
                };

                attribute_manager.manage("observations", component.observation.id);
                tag_manager.manage("observations", component.observation.id);
                dashboard.active_widget.subscribe(function(active_widget)
                {
                    if(active_widget != widget)
                        return;
                    attribute_manager.manage("observations", component.observation.id);
                    tag_manager.manage("observations", component.observation.id);
                });

                component.show_observations = function()
                {
                    dashboard.add_widget("samlab-observations-widget");
                }

                component.manage_attributes = function()
                {
                    dashboard.add_widget("samlab-attribute-widget");
                }

                component.manage_tags = function()
                {
                    dashboard.add_widget("samlab-tag-widget");
                }

                component.delete_observation = function()
                {
                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                                observation_manager.delete(component.observation.id());
                        },
                        message: "This will delete the observation and its data, and close any related dashboard widgets.",
                        title: "Delete Observation?",
                    });
                };

                component.observation.name = ko.pureComputed(function()
                {
                    return "Observation-" + component.observation.id().substring(16);
                });

                component.observation.created_formatted = ko.pureComputed(function()
                {
                    return new Date(component.observation.created()).toLocaleString();
                });

                component.observation.modified_formatted = ko.pureComputed(function()
                {
                    return new Date(component.observation.modified()).toLocaleString();
                });

                component.observation.images = component.observation.content.filter(function(content)
                {
                    return content["content-type"]().split("/")[0] == "image";
                });

                server.load_json(component, "/observations/" + component.observation.id());

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { width: 6, height: 12 },
    };

    return module;
});
