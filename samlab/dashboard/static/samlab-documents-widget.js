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
    "samlab-attribute-control",
    "samlab-content-list-control",
    ], function(debug, ko, mapping, lodash, URI, attribute_manager, bounding_box_manager, dashboard, dialog, notify, permissions, server, socket, tag_manager, uuidv4)
{
    var log = debug("samlab-documents-widget");

    var component_name = "samlab-documents-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    collection: widget.params.collection,
                    content: null,
                    count: null,
                    index: widget.params.index,
                    tags: [],
                });

                component.first_document = function()
                {
                    component.index(0);
                };

                component.last_document = function()
                {
                    component.index(component.count() - 1);
                }

                component.load_content = ko.computed(function()
                {
                    var uri = "/document-collection/" + component.collection() + "/" + component.index();
                    require(["text!" + uri], function(content)
                    {
                        component.content(content);
                    });
                });

                component.load_tags = ko.computed(function()
                {
                    server.get_json("/document-collection/" + component.collection() + "/" + component.index() + "/tags",
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

                component.next_document = function()
                {
                    component.index((component.index() + 1) % component.count());
                };

                component.open_document = function()
                {
                    dashboard.add_widget("samlab-document-widget", {collection: component.collection(), index: component.index()});
                }

                component.previous_document = function()
                {
                    component.index((component.index() + component.count() - 1) % component.count());
                }

                component.random_document = function()
                {
                    var index = lodash.random(0, component.count() - 1);
                    if(index == component.index())
                        index = (index + 1) % component.count();
                    component.index(index);
                };

                component.reload = function()
                {
                    server.get_json("/document-collection/" + component.collection(),
                    {
                        success: function(data)
                        {
                            component.count(data.count);
                            if(component.index() >= data.count)
                                component.index(0);
                        },
                    });
                }

                dashboard.bind({widget: widget, keys: "left", callback: component.previous_document});
                dashboard.bind({widget: widget, keys: "right", callback: component.next_document});
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
