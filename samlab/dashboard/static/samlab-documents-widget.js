// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "lodash",
    "samlab-dashboard",
    "samlab-server",
    "samlab-socket",
    ], function(debug, ko, mapping, lodash, dashboard, server, socket)
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
                });

                component.first_document = function()
                {
                    component.index(0);
                };

                component.last_document = function()
                {
                    if(component.count())
                    {
                        component.index(component.count() - 1);
                    }
                }

                component.load_content = ko.computed(function()
                {
                    if(component.count())
                    {
                        var uri = "/document-collection/" + component.collection() + "/" + component.index();
                        server.get_text(uri, function(text)
                        {
                            log("Updating content.");
                            component.content(text);
                        });
                    }
                });

                component.next_document = function()
                {
                    if(component.count())
                    {
                        component.index((component.index() + 1) % component.count());
                    }
                };

                component.open_document = function()
                {
                    if(component.count())
                    {
                        dashboard.add_widget("samlab-document-widget", {collection: component.collection(), index: component.index()});
                    }
                }

                component.previous_document = function()
                {
                    if(component.count())
                    {
                        component.index((component.index() + component.count() - 1) % component.count());
                    }
                }

                component.random_document = function()
                {
                    if(component.count())
                    {
                        var index = lodash.random(0, component.count() - 1);
                        if(index == component.index())
                            index = (index + 1) % component.count();
                        component.index(index);
                    }
                };

                component.reload = function()
                {
                    log("reload");
                    server.get_json("/document-collection/" + component.collection(),
                    {
                        success: function(data)
                        {
                            // This logic is a little tricky, because
                            // we want to avoid unnecessary updates.
                            if(data.count != component.count())
                            {
                                if(component.index() >= data.count)
                                    component.index(0);
                                component.count(data.count);
                            }
                            else
                            {
                                component.index.valueHasMutated();
                            }
                        },
                    });
                }

                socket.on("service-changed", function(changed)
                {
                    if(changed.service == "document-collection" && changed.name == component.collection())
                    {
                        component.reload();
                    }
                });

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
        widget: { width: 4, height: 12, params: {collection: null, index: 0}},
    };

    return module
});
