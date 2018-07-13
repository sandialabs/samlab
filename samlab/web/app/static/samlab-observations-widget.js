// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "lodash",
    "URI",
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
    "samlab-uuidv4",
    "samlab-content-list-control",
    ], function(debug, ko, mapping, lodash, URI, attribute_manager, content, dashboard, dialog, notify, object, observation, permissions, server, socket, tag_manager, uuidv4)
{
    var log = debug("samlab-observations-widget");

    var component_name = "samlab-observations-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                //////////////////////////////////////////////////////
                // Data model

                var component = mapping.fromJS(
                {
                    count: 0,
                    index: 0,
                    loading: false,
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
                    search_error: false,
                    session: uuidv4(),
                });

                component.observation.id = widget.params.id;

                ////////////////////////////////////////////////////////
                // Search / sort controls

                component.search = widget.params.search;
                component.search.extend({rateLimit: {timeout: 500, method: "notifyWhenChangesStop"}});
                component.search.subscribe(function()
                {
                    component.load_count();
                });

                component.position = ko.pureComputed(function()
                {
                    if(component.count() < 1)
                        return null;

                    return (component.index() + 1) + " of " + component.count();
                });

                component.sort = widget.params.sort;
                component.sort_items =
                [
                    {key: "_id", label: "ID"},
                    {key: "created", label: "Created"},
                    {key: "modified", label: "Modified"},
                    {key: "modified-by", label: "Modified by"},
                    {key: "tags", label: "Tags"},
                ];
                component.sort.subscribe(function()
                {
                    component.adjust_index();
                });

                /////////////////////////////////////////////////////////////////
                // Operations menu
/*
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
*/

                component.export_observations = function()
                {
                    socket.emit("export-observations", {search: component.search()});
                    notify.local({icon: "fa fa-download", message: "Exporting observations.", type: "success"});
                }

                component.help = function()
                {
                    dashboard.add_widget("samlab-markup-viewer-widget", {uri: "samlab-observations-widget-help.html"});
                }

                component.manage_attributes = function()
                {
                    dashboard.add_widget("samlab-attribute-manager-widget");
                }

                component.manage_tags = function()
                {
                    dashboard.add_widget("samlab-tag-manager-widget");
                }

                component.view_observation = function()
                {
                    dashboard.add_widget("samlab-observation-widget", {id: component.observation.id()});
                }

                /////////////////////////////////////////////////////////////////
                // Navigation controls

                component.first_observation = function()
                {
                    if(component.count() < 1)
                        return;
                    component.index(0);
                    component.lookup_id();
                };

                component.last_observation = function()
                {
                    if(component.count() < 1)
                        return;

                    component.index(component.count() - 1);
                    component.lookup_id();
                }

                component.next_observation = function()
                {
                    if(component.count() < 1)
                        return;

                    component.index((component.index() + 1) % component.count());
                    component.lookup_id();
                };

                component.previous_observation = function()
                {
                    if(component.count() < 1)
                        return;

                    component.index((component.index() + component.count() - 1) % component.count());
                    component.lookup_id();
                }

                component.random_observation = function()
                {
                    if(component.count() < 1)
                        return;

                    component.index(lodash.random(0, component.count()-1));
                    component.lookup_id();
                };

                ///////////////////////////////////////////////////////////////////////////////
                // Server communication

                component.load_count = function()
                {
                    log("load_count");
                    component.loading(true);
                    var session = component.session();
                    var search = component.search();
                    var uri = URI("/observations/count").setQuery({session: session, search: search})
                    server.get_json(uri,
                    {
                        success: function(data)
                        {
                            component.count(data.count);
                            component.search_error(false);
                            component.adjust_index();
                        },
                        error: function()
                        {
                            component.search_error(true);
                            component.loading(false);
                        },
                        finished: function()
                        {
                            component.loading(false);
                        },
                    });
                };

                component.adjust_index = function()
                {
                    log("adjust_index");

                    if(component.count() < 1)
                    {
                        component.index(0);
                    }
                    else
                    {
                        if(component.index() >= component.count())
                        {
                            component.index(component.count()-1)
                        }
                    }

                    component.lookup_id();
                }

                component.lookup_id = function()
                {
                    log("lookup_id");
                    if(component.count() < 1)
                    {
                        component.observation["attributes-pre"](null);
                        component.observation.content([]);
                        component.observation.created(null);
                        component.observation["modified-by"](null);
                        component.observation.modified(null);
                        component.observation.tags([]);
                        return;
                    }

                    component.loading(true);
                    var session = component.session();
                    var search = component.search();
                    var sort = component.sort();
                    var direction = "ascending";
                    var index = component.index();

                    var uri = URI("/observations/index/" + index).setQuery({session: session, search: search, sort: sort, direction: direction})
                    server.get_json(uri,
                    {
                        success: function(data)
                        {
                            component.observation.id(data.oid);
                            component.load_observation();
                        },
                        error: function()
                        {
                            component.loading(false);
                        },
                        finished: function()
                        {
                            component.loading(false);
                        },
                    });
                };

                component.load_observation = function()
                {
                    log("load_observation");

                    var id = component.observation.id();
                    server.load_json(component, "/observations/" + id);
                    server.load_text("/observations/" + id + "/attributes/pre", function(data)
                    {
                        component.observation["attributes-pre"](data);
                    });

                    attribute_manager.manage("observations", id);
                    tag_manager.manage("observations", id);
                };

                /////////////////////////////////////////////////////////////////////
                // Display formatting

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

                /////////////////////////////////////////////////////////////////////////
                // External event handling

                dashboard.active_widget.subscribe(function(active_widget)
                {
                    if(active_widget != widget)
                        return;
                    attribute_manager.manage("observations", component.observation.id);
                    tag_manager.manage("observations", component.observation.id);
                });

                var observation_created_subscription = object.created.subscribe(function(object)
                {
                    if(object.otype == "observations")
                    {
/*
                        component.load_count();
*/
                    }
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
/*
                        component.load_count();
*/
                    }
                });

                component.dispose = function()
                {
                    observation_created_subscription.dispose();
                    observation_changed_subscription.dispose();
                    observation_deleted_subscription.dispose();

                    attribute_manager.release("observations", component.observation.id);
                    tag_manager.release("observations", component.observation.id);
                }

                dashboard.bind({widget: widget, keys: "left", callback: component.previous_observation});
                dashboard.bind({widget: widget, keys: "right", callback: component.next_observation});

                // Start running
                component.load_count()

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { width: 6, height: 12, params: {search: "", sort: "_id", id: null}},
    };

    return module
});
