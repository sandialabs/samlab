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
    var component_name = "samlab-timeseries-widget";
    var log = debug(component_name);

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
                    plot: null,
                    size: [100, 100],
                    smoothing: widget.params.smoothing,
                    yscale: widget.params.yscale,
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
                        var uri = "/timeseries-collection/" + component.collection() + "/" + component.index();
                        var data = {
                            height: component.size()[1] - 100,
                            smoothing: component.smoothing(),
                            width: component.size()[0] - 100,
                            yscale: component.yscale(),
                        };

                        server.post_json(uri, data, {
                            success: function(data)
                            {
                                component.plot(data.plot);
                            },
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
                    server.get_json("/timeseries-collection/" + component.collection(),
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

                component.size.extend({rateLimit: {timeout: 100, method: "notifyWhenChangesStop"}});

                component.yscale_items =
                [
                    {key: "linear", label: "Linear"},
                    {key: "log", label: "Log"},
                ];

                var observer = new ResizeObserver(function(entries, observer)
                {
                    component.size([entries[0].contentRect.width, entries[0].contentRect.height]);
                });
                observer.observe(component_info.element.querySelector(".widget-content"));

                socket.on("service-changed", function(changed)
                {
                    if(changed.service == "timeseries-collection" && changed.name == component.collection())
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
        widget: { width: 4, height: 12, params: {collection: null, index: 0, smoothing: 0.5, yscale: "linear"}},
    };

    return module
});
