// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "lodash",
    "samlab-attribute-manager",
    "samlab-content",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-notify",
    "samlab-object",
    "samlab-observation",
    "samlab-permissions",
    "samlab-server",
    "samlab-socket",
    "samlab-tag-manager",
    "samlab-content-list-control",
    ], function(ko, mapping, lodash, attribute_manager, content, dashboard, dialog, notify, object, observation, permissions, server, socket, tag_manager)
{
    var component_name = "samlab-observations-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    search_error: false,
                    loading: false,
                    observations: [],
                    observation:
                    {
                        "attributes-pre": null,
                        content: [],
                        created: null,
                        "modified-by": null,
                        modified: null,
                        tags: [],
                    },
                    permissions: permissions,
                    sort_keys: ["id", "modified", "modified-by", "original-filename", "tags"],
                });

                component.search = widget.params.search;
                component.search.extend({rateLimit: {timeout: 500, method: "notifyWhenChangesStop"}});

                var sort_labels =
                {
                    "id": "ID",
                    "modified": "Modified",
                    "modified-by": "Modified by",
                    "original-filename": "Original filename",
                    "tags": "Tags",
                };
                component.sort = widget.params.sort;
                component.sort_label = ko.pureComputed(function()
                {
                    return sort_labels[component.sort()];
                });
                component.sort_options = component.sort_keys.map(function(key)
                {
                    return {key: key, label: sort_labels[key]};
                });
                component.set_sort = function(option)
                {
                    component.sort(option.key);
                }

                component.observation.id = widget.params.id;

                component.view_observation = function()
                {
                    dashboard.add_widget("samlab-observation-widget", {id: component.observation.id()});
                }

                component.manage_attributes = function()
                {
                    dashboard.add_widget("samlab-attribute-manager-widget");
                }

                component.manage_tags = function()
                {
                    dashboard.add_widget("samlab-tag-manager-widget");
                }

                component.export_observations = function()
                {
                    socket.emit("export-observations", {search: component.search()});
                    notify.local({icon: "fa fa-download", message: "Exporting observations.", type: "success"});
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
                                observation.delete(component.observation.id());
                        },
                        message: "This will delete the observation and its data, and close any related dashboard widgets.",
                        title: "Delete Observation?",
                    });
                };

                component.help = function()
                {
                    dashboard.add_widget("samlab-markup-viewer-widget", {uri: "samlab-observations-widget-help.html"});
                }

                component.first_observation = function()
                {
                    var observations = component.observations();
                    if(observations.length < 1)
                        return;
                    component.observation.id(observations[0]);
                };

                component.last_observation = function()
                {
                    var observations = component.observations();
                    if(observations.length < 1)
                        return;
                    component.observation.id(observations[observations.length-1]);
                }

                component.random_observation = function()
                {
                    var observations = component.observations();
                    if(observations.length < 1)
                        return;

                    component.observation.id(observations[lodash.random(0, observations.length-1)]);
                };

                component.next_observation = function()
                {
                    var id = component.observation.id();
                    if(id == null)
                        return;

                    var observations = component.observations();
                    var index = observations.indexOf(component.observation.id());
                    component.observation.id(observations[(index + 1) % observations.length]);
                };

                component.previous_observation = function()
                {
                    var id = component.observation.id();
                    if(id == null)
                        return;


                    var observations = component.observations();
                    var index = observations.indexOf(component.observation.id());
                    component.observation.id(observations[(index + observations.length - 1) % observations.length]);
                }

                component.position = ko.pureComputed(function()
                {
                    var index = component.observations.indexOf(component.observation.id());
                    if(index < 0)
                        return null;

                    return (index + 1) + " of " + component.observations().length;
                });

                component.load_observation = ko.computed(function()
                {
                    //var observations = component.observations();
                    var id = component.observation.id();
                    //console.log("load_observation", id);

                    if(id != null)
                    {
                        server.load_json(component, "/observations/" + id);
                        server.load_text("/observations/" + component.observation.id() + "/attributes/pre", function(data)
                        {
                            component.observation["attributes-pre"](data);
                        });
                    }
                    else
                    {
                        //console.log("clear");
                        component.observation["attributes-pre"](null);
                        component.observation.content([]);
                        component.observation.created(null);
                        component.observation["modified-by"](null);
                        component.observation.modified(null);
                        component.observation.tags([]);
                    }

                    attribute_manager.manage("observations", id);
                    tag_manager.manage("observations", id);
                });

                component.observation.created_formatted = ko.pureComputed(function()
                {
                    return component.observation.created() ? new Date(component.observation.created()).toLocaleString() : "";
                });

                component.observation.modified_formatted = ko.pureComputed(function()
                {
                    return new Date(component.observation.modified()).toLocaleString();
                });

                component.observation.images = component.observation.content.filter(function(content)
                {
                    return content["content-type"]().split("/")[0] == "image";
                });

                component.load_observations = ko.computed(function()
                {
                    component.loading(true);
                    server.load_json(component, "/observations?sort=" + component.sort() + "&search=" + component.search(), "GET",
                    {
                        success: function()
                        {
                            component.search_error(false);
                        },
                        error: function()
                        {
                            component.search_error(true);
                        },
                        finished: function()
                        {
                            component.loading(false);
                        },
                    });
                });

                component.observations.subscribe(function(observations)
                {
                    var id = component.observation.id();
                    var index = observations.indexOf(id);
                    if(index < 0)
                    {
                        if(observations.length)
                        {
                            component.observation.id(observations[0]);
                        }
                        else
                        {
                            component.observation.id(null);
                        }
                    }
                });

                dashboard.active_widget.subscribe(function(active_widget)
                {
                    if(active_widget != widget)
                        return;
                    attribute_manager.manage("observations", component.observation.id);
                    tag_manager.manage("observations", component.observation.id);
                });

                var observation_changed_subscription = object.changed.subscribe(function(object)
                {
                    if(object.otype == "observations" && object.oid == component.observation.id())
                    {
                        server.load_json(component, "/observations/" + component.observation.id());
                        server.load_text("/observations/" + component.observation.id() + "/attributes/pre", function(data)
                        {
                            component.observation["attributes-pre"](data);
                        });
                    }
                });

                var observation_deleted_subscription = object.deleted.subscribe(function(object)
                {
                    if(object.otype == "observations")
                    {
                        component.observations.remove(object.oid);
                    }
                });

                component.dispose = function()
                {
                    observation_changed_subscription.dispose();
                    observation_deleted_subscription.dispose();

                    attribute_manager.release("observations", component.observation.id);
                    tag_manager.release("observations", component.observation.id);
                }

                dashboard.bind({widget: widget, keys: "left", callback: component.previous_observation});
                dashboard.bind({widget: widget, keys: "right", callback: component.next_observation});

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { width: 6, height: 12, params: {search: "", sort: "modified", id: null}},
    };

    return module
});
