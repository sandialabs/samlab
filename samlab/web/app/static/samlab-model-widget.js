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
    "samlab-model",
    "samlab-object",
    "samlab-permissions",
    "samlab-server",
    "samlab-tag-manager",
    "samlab-content-list-control",
    ], function(ko, mapping, attribute_manager, content, dashboard, dialog, model, object, permissions, server, tag_manager)
{
    var component_name= "samlab-model-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    model:
                    {
                        "attributes-pre": null,
                        content: [],
                        created: null,
                        id: widget.params.id,
                        "modified-by": null,
                        modified: null,
                        name: null,
                        trial: null,
                        tags: [],
                    },
                    permissions: permissions,
                    selected_option: null,
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, "models", widget.params.id);
                var model_changed_subscription = object.notify_changed("models", widget.params.id, function()
                {
                    server.load_json(component, "/models/" + component.model.id());
                });

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    model_changed_subscription.dispose();
                    attribute_manager.release("models", component.model.id);
                    tag_manager.release("models", component.model.id);
                }

                attribute_manager.manage("models", component.model.id);
                tag_manager.manage("models", component.model.id);
                dashboard.active_widget.subscribe(function(active_widget)
                {
                    if(active_widget != widget)
                        return;
                    attribute_manager.manage("models", component.model.id);
                    tag_manager.manage("models", component.model.id);
                });

                component.groups =
                [
                    {
                        label: "Visualizations",
                        children:
                        [
                            {label: "Model attributes", icon: "fa-align-left", widget: "samlab-model-attributes-widget", params: {id: component.model.id}},
                            {label: "Training loss", icon: "fa-line-chart fa-flip-vertical", widget: "samlab-training-loss-widget", params: {id: component.model.id}},
                            {label: "Training accuracy", icon: "fa-line-chart", widget: "samlab-training-accuracy-widget", params: {id: component.model.id}},
                            {label: "Image classification", icon: "fa-picture-o", widget: "samlab-image-classification-widget", params: {id: component.model.id}},
                            {label: "CNN layers", icon: "fa-picture-o", widget: "samlab-cnn-layer-widget", params: {id: component.model.id}},
                        ],
                    },
                    {
                        label: "Parents",
                        children:
                        [
                            { label: "Trial", icon: "fa-address-card", widget: "samlab-trial-widget", params: {id: component.model.trial}},
                        ],
                    },
                ];

                component.view_attributes = function()
                {
                    dashboard.add_widget("samlab-model-attributes-widget", {id: component.model.id});
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

                component.delete_model = function()
                {
                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                                model.delete(component.model.id());
                        },
                        message: "This will delete the model and its data, and close any related dashboard widgets.",
                        title: "Delete Model?",
                    });
                };

                component.model.created_formatted = ko.pureComputed(function()
                {
                    if(component.model.created())
                        return new Date(component.model.created()).toLocaleString();
                    return null;
                });

                component.model.modified_formatted = ko.pureComputed(function()
                {
                    if(component.model.modified())
                        return new Date(component.model.modified()).toLocaleString();
                    return null;
                });

                server.load_json(component, "/models/" + component.model.id());

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
