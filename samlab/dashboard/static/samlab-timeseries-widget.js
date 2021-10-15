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
                var plot_widget_element = component_info.element;
                var plot_element = component_info.element.querySelector(".plot");

                var component = mapping.fromJS(
                {
                    collection: widget.params.collection,
                    count: null,
                    grid_height: widget.height,
                    grid_width: widget.width,
                    index: widget.params.index,
                    plot: null,
                    plot_height: plot_element.offsetHeight,
                    plot_width: plot_element.offsetWidth,
                    smoothing: widget.params.smoothing,
                    yscale: widget.params.yscale,
                });

                component.first_document = function()
                {
                    component.index(0);
                };

                component.grid_height.subscribe(function(newValue)
                {
                    var offset = plot_element.getBoundingClientRect().top - plot_widget_element.getBoundingClientRect().top;
                    component.plot_height(plot_widget_element.offsetHeight - offset);
                });

                component.grid_width.subscribe(function(newValue)
                {
                    component.plot_width(plot_element.offsetWidth);
                });

                component.last_document = function()
                {
                    if(component.count())
                    {
                        component.index(component.count() - 1);
                    }
                }

                component.load_content = ko.computed(function()
                {
                    // We want to update automatically whenever the plot size changes.
                    var plot_width = component.plot_width();
                    var plot_height = component.plot_height();

                    if(component.count())
                    {
                        var uri = "/timeseries-collection/" + component.collection() + "/" + component.index();
                        var data = {
                            height: plot_height - 10,
                            smoothing: component.smoothing(),
                            width: plot_width - 10,
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

                component.yscale_items =
                [
                    {key: "linear", label: "Linear"},
                    {key: "log", label: "Log"},
                ];

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
