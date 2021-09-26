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
    "samlab-bounding-box-manager",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-notify",
    "samlab-permissions",
    "samlab-server",
    "samlab-socket",
    "samlab-tag-manager",
    "samlab-uuidv4",
    ], function(debug, ko, mapping, lodash, URI, attribute_manager, bounding_box_manager, dashboard, dialog, notify, permissions, server, socket, tag_manager, uuidv4)
{
    var log = debug("samlab-images-widget");

    var component_name = "samlab-images-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    collection: widget.params.collection,
                    count: null,
                    index: widget.params.index,
                    tags: [],
                });

                component.first_image = function()
                {
                    component.index(0);
                };

                component.last_image = function()
                {
                    component.index(component.count() - 1);
                }

                component.load_tags = ko.computed(function()
                {
                    server.get_json("/image-collection/" + component.collection() + "/" + component.index() + "/tags",
                    {
                        success: function(data)
                        {
                            component.tags(data.tags);
                        },
                    });
                });

                component.manage_attributes = function()
                {
                    dashboard.add_widget("samlab-attribute-widget");
                }

                component.manage_tags = function()
                {
                    dashboard.add_widget("samlab-tag-widget");
                }

                component.next_image = function()
                {
                    component.index((component.index() + 1) % component.count());
                };

                component.open_image = function()
                {
                    dashboard.add_widget("samlab-image-widget", {collection: component.collection(), index: component.index()});
                }

                component.previous_image = function()
                {
                    component.index((component.index() + component.count() - 1) % component.count());
                }

                component.random_image = function()
                {
                    var index = lodash.random(0, component.count() - 1);
                    if(index == component.index())
                        index = (index + 1) % component.count();
                    component.index(index);
                };

                component.reload = function()
                {
                    server.get_json("/image-collection/" + component.collection(),
                    {
                        success: function(data)
                        {
                            component.count(data.count);
                            if(component.index() >= data.count)
                                component.index(0);
                        },
                    });
                }

                component.uri = ko.pureComputed(function()
                {
                    return "/image-collection/" + component.collection() + "/" + component.index();
                });


/*
                ////////////////////////////////////////////////////////
                // Search / sort controls

                component.search = widget.params.search;
                component.search.extend({rateLimit: {timeout: 500, method: "notifyWhenChangesStop"}});
                component.search.subscribe(function()
                {
                    component.start_search();
                });

                component.position = ko.pureComputed(function()
                {
                    if(component.state() == "ready")
                        return (component.oindex() + 1) + " of " + component.count();

                    return null;
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
                    component.start_sort();
                });

                component.direction = widget.params.direction;
                component.direction_items =
                [
                    {key: "ascending", label: "Ascending"},
                    {key: "descending", label: "Descending"},
                ];
                component.direction.subscribe(function()
                {
                    component.start_sort();
                });

                component.reload = function()
                {
                    component.outdated(false);
                    component.session(uuidv4());
                    component.start_search();
                }

                /////////////////////////////////////////////////////////////////
                // Operations menu

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

                component.export_observations = function()
                {
                    socket.emit("export-observations", {search: component.search()});
                    notify.local({icon: "fa fa-download", message: "Exporting observations.", type: "success"});
                }

                component.help = function()
                {
                    dashboard.add_widget("samlab-markup-viewer-widget", {uri: "samlab-observations-widget-help.html"});
                }

                ///////////////////////////////////////////////////////////////////////////////
                // State machine

                component.start_search = function()
                {
                    log("state: searching");
                    component.state("searching");
                    object.lookup_count("observations",
                    {
                        session: component.session(),
                        search: component.search(),
                        success: function(data)
                        {
                            component.count(data.count);
                            if(data.count)
                            {
                                var oid = component.observation.id();
                                if(oid != null)
                                {
                                    object.lookup_index("observations", oid,
                                    {
                                        session: component.session(),
                                        search: component.search(),
                                        sort: component.sort(),
                                        direction: component.direction(),
                                        success: function(data)
                                        {
                                            if(data.oindex != null)
                                            {
                                                component.load(data.oindex, data.oid);
                                            }
                                            else
                                            {
                                                component.set_index(0);
                                            }
                                        },
                                    });
                                }
                                else
                                {
                                    component.set_index(0);
                                }
                            }
                            else
                            {
                                component.empty();
                            }
                        },
                        error: function()
                        {
                            component.search_error();
                        }
                    });
                }

                component.search_error = function()
                {
                    log("state: search-error");
                    component.state("search-error");
                }

                component.empty = function()
                {
                    log("state: empty");
                    component.state("empty");

                    component.observation.id(null);
                    component.observation["attributes-pre"](null);
                    component.observation.content([]);
                    component.observation.created(null);
                    component.observation["modified-by"](null);
                    component.observation.modified(null);
                    component.observation.tags([]);
                }

                component.load = function(oindex, oid)
                {
                    log("state: loading", oindex, oid);
                    component.state("loading");

                    component.oindex(oindex);
                    component.observation.id(oid);

                    server.load_json(component, "/observations/" + oid, "GET",
                    {
                        success: function()
                        {
                            component.deleted(false);
                        },
                        error: function()
                        {
                            component.deleted(true);
                        }
                    })
                    server.load_text("/observations/" + oid + "/attributes/summary", function(data)
                    {
                        component.observation["attributes-pre"](data);
                    });

                    attribute_manager.manage("observations", oid);
                    bounding_box_manager.manage("observations", oid, "image");
                    tag_manager.manage("observations", oid);

                    component.ready();
                }

                component.ready = function()
                {
                    log("state: ready");
                    component.state("ready");
                }

                component.set_index = function(oindex)
                {
                    log("set_index:", oindex);

                    // Lookup the id for this index, so we can load it.
                    object.lookup_id("observations", oindex,
                    {
                        session: component.session(),
                        search: component.search(),
                        sort: component.sort(),
                        direction: component.direction(),
                        success: function(data)
                        {
                            component.load(oindex, data.oid);
                        },
                    });
                }

                component.start_sort = function()
                {
                    log("change_sort:", component.sort(), component.direction());

                    // Lookup the index for this id, so we can update the UI.
                    object.lookup_index("observations", component.observation.id(),
                    {
                        session: component.session(),
                        search: component.search(),
                        sort: component.sort(),
                        direction: component.direction(),
                        success: function(data)
                        {
                            component.load(data.oindex, data.oid);
                        },
                    });
                }

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
                    bounding_box_manager.manage("observations", component.observation.id, "image");
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
                            component.load(component.oindex(), component.observation.id());
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
                            log("current observation deleted");
                            component.observation.id(null);
                            component.session(uuidv4());
                            component.start_search();
                        }
                    }
                });

                component.dispose = function()
                {
                    observation_created_subscription.dispose();
                    observation_changed_subscription.dispose();
                    observation_deleted_subscription.dispose();

                    attribute_manager.release("observations", component.observation.id);
                    bounding_box_manager.release("observations", component.observation.id, "image");
                    tag_manager.release("observations", component.observation.id);
                }
*/

                dashboard.bind({widget: widget, keys: "left", callback: component.previous_image});
                dashboard.bind({widget: widget, keys: "right", callback: component.next_image});
                component.reload();

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { width: 6, height: 12, params: {collection: null, index: 0}},
    };

    return module
});
