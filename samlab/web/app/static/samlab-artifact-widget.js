// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-attribute-manager",
    "samlab-content",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-artifact",
    "samlab-object",
    "samlab-permissions",
    "samlab-server",
    "samlab-tag-manager",
    "samlab-content-list-control",
    ], function(ko, mapping, attribute_manager, content, dashboard, dialog, artifact, object, permissions, server, tag_manager)
{
    var component_name= "samlab-artifact-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    artifact:
                    {
                        "attributes-pre": null,
                        content: [],
                        created: null,
                        id: widget.params.id,
                        "modified-by": null,
                        modified: null,
                        name: null,
                        experiment: null,
                        tags: [],
                    },
                    permissions: permissions,
                    selected_option: null,
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, "artifacts", widget.params.id);
                var artifact_changed_subscription = object.notify_changed("artifacts", widget.params.id, function()
                {
                    server.load_json(component, "/artifacts/" + component.artifact.id());
                });

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    artifact_changed_subscription.dispose();
                    attribute_manager.release("artifacts", component.artifact.id);
                    tag_manager.release("artifacts", component.artifact.id);
                }

                attribute_manager.manage("artifacts", component.artifact.id);
                tag_manager.manage("artifacts", component.artifact.id);
                dashboard.active_widget.subscribe(function(active_widget)
                {
                    if(active_widget != widget)
                        return;
                    attribute_manager.manage("artifacts", component.artifact.id);
                    tag_manager.manage("artifacts", component.artifact.id);
                });

                component.groups =
                [
                    {
                        label: "Visualizations",
                        children:
                        [
                            {label: "Attributes", icon: "fa-align-left", widget: "samlab-attributes-widget", params: {otype: "artifacts", oid: component.artifact.id}},
                            {label: "Auto Plot", icon: "fa-line-chart", widget: "samlab-auto-plot-widget", params: {otype: "artifacts", oid: component.artifact.id, name: component.artifact.name}},
                        ],
                    },
                    {
                        label: "Parents",
                        children:
                        [
                            { label: "Experiment", icon: "fa-address-card", widget: "samlab-experiment-widget", params: {id: component.artifact.experiment}},
                        ],
                    },
                ];

                component.view_attributes = function()
                {
                    dashboard.add_widget("samlab-attributes-widget", {otype: "artifacts", oid: component.artifact.id});
                }

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

                component.delete_artifact = function()
                {
                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                                artifact.delete(component.artifact.id());
                        },
                        message: "This will delete the artifact and its data, and close any related dashboard widgets.",
                        title: "Delete Model?",
                    });
                };

                component.artifact.created_formatted = ko.pureComputed(function()
                {
                    if(component.artifact.created())
                        return new Date(component.artifact.created()).toLocaleString();
                    return null;
                });

                component.artifact.modified_formatted = ko.pureComputed(function()
                {
                    if(component.artifact.modified())
                        return new Date(component.artifact.modified()).toLocaleString();
                    return null;
                });

                server.load_json(component, "/artifacts/" + component.artifact.id());

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
