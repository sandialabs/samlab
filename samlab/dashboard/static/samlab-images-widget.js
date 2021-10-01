// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "lodash",
    "URI",
    "samlab-bounding-box-manager",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-notify",
    "samlab-permissions",
    "samlab-server",
    "samlab-socket",
    "samlab-tag-manager",
    "samlab-uuidv4",
    ], function(debug, ko, mapping, lodash, URI, bounding_box_manager, dashboard, dialog, notify, permissions, server, socket, tag_manager, uuidv4)
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
                    metadata: null,
                    metaid: "w" + uuidv4(),
                    tags: [],
                    tagid: "w" + uuidv4(),
                    edittagid: "w" + uuidv4(),
                });

                component.first_image = function()
                {
                    component.index(0);
                };

                component.last_image = function()
                {
                    component.index(component.count() - 1);
                }

                component.load_metadata = ko.computed(function()
                {
                    server.get_json("/image-collection/" + component.collection() + "/" + component.index() + "/metadata",
                    {
                        success: function(data)
                        {
                            component.metadata(JSON.stringify(data.metadata, null, 2));
                        },
                    });
                });

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
