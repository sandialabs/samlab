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
                    outdated: false,
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
                    component.old_load_count();
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
                    component.old_adjust_index();
                });

                component.direction = widget.params.direction;
                component.direction_items =
                [
                    {key: "ascending", label: "Ascending"},
                    {key: "descending", label: "Descending"},
                ];
                component.direction.subscribe(function()
                {
                    component.old_adjust_index();
                });

                component.reload = function()
                {
                    component.outdated(false);
                    component.session(uuidv4());
                    component.old_load_count();
                }

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
                    component.old_lookup_id();
                };

                component.last_observation = function()
                {
                    if(component.count() < 1)
                        return;

                    component.index(component.count() - 1);
                    component.old_lookup_id();
                }

                component.next_observation = function()
                {
                    if(component.count() < 1)
                        return;

                    component.index((component.index() + 1) % component.count());
                    component.old_lookup_id();
                };

                component.previous_observation = function()
                {
                    if(component.count() < 1)
                        return;

                    component.index((component.index() + component.count() - 1) % component.count());
                    component.old_lookup_id();
                }

                component.random_observation = function()
                {
                    if(component.count() < 1)
                        return;

                    component.index(lodash.random(0, component.count()-1));
                    component.old_lookup_id();
                };

                ///////////////////////////////////////////////////////////////////////////////
                // Server communication

                component.old_load_count = function()
                {
                    component.loading(true);
                    object.lookup_count("observations",
                    {
                        session: component.session(),
                        search: component.search(),
                        success: function(data)
                        {
                            log("old_load_count", data);
                            component.count(data.count);
                            component.search_error(false);
                            component.old_adjust_index();
                        },
                        error: function()
                        {
                            component.search_error(true);
                            component.loading(false);
                        },
                    });
                };

                component.old_adjust_index = function()
                {
                    log("old_adjust_index", {id: component.observation.id(), index: component.index()});
                    if(component.count() < 1)
                    {
                        component.index(0);
                    }
                    else
                    {
                        object.lookup_index("observations", component.observation.id(),
                        {
                            session: component.session(),
                            search: component.search(),
                            sort: component.sort(),
                            direction: component.direction(),
                            success: function(data)
                            {
                                log("old_adjust_index", data);
                                //component.observation.id(data.oid);
                                //component.load_observation();
                            },
                            finished: function()
                            {
                                //component.loading(false);
                            },
                        });
                    }

                    component.old_lookup_id();
                }

                component.old_lookup_id = function()
                {
                    component.loading(true);
                    if(component.count() < 1)
                    {
                        component.loading(false);
                        component.observation["attributes-pre"](null);
                        component.observation.content([]);
                        component.observation.created(null);
                        component.observation["modified-by"](null);
                        component.observation.modified(null);
                        component.observation.tags([]);
                        return;
                    }

                    object.lookup_id("observations", component.index(),
                    {
                        session: component.session(),
                        search: component.search(),
                        sort: component.sort(),
                        direction: component.direction(),
                        success: function(data)
                        {
                            log("old_lookup_id", data);
                            component.observation.id(data.oid);
                            component.load_observation();
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
                        component.outdated(true);
                    }
                });

                var observation_changed_subscription = object.changed.subscribe(function(object)
                {
                    if(object.otype == "observations")
                    {
                        component.outdated(true);

                        if(object.oid == component.observation.id())
                        {
                            // Our observation has changed, so reload it.
                            component.load_observation();
                        }
                    }
                });

                var observation_deleted_subscription = object.deleted.subscribe(function(object)
                {
                    if(object.otype == "observations")
                    {
                        component.outdated(true);

                        if(object.oid == component.observation.id())
                        {
                            // Our observation was deleted.  TODO: Do something about it.
                        }
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
                component.old_load_count()

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { width: 6, height: 12, params: {search: "", sort: "_id", direction: "ascending", id: null}},
    };

    return module
});
