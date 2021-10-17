// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-server",
    "samlab-socket",
    ], function(debug, ko, mapping, dashboard, server, socket)
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
                    grid_height: widget.height,
                    grid_width: widget.width,
                    keys: [],
                    pattern: widget.params.pattern,
                    plot: null,
                    plot_height: plot_element.offsetHeight,
                    plot_width: plot_element.offsetWidth,
                    smoothing: widget.params.smoothing,
                    yscale: widget.params.yscale,
                });

                component.compiled_pattern = ko.computed(function()
                {
                    return new RegExp(component.pattern());
                });

                component.grid_height.subscribe(function(newValue)
                {
                    var offset = plot_element.getBoundingClientRect().top - plot_widget_element.getBoundingClientRect().top;
                    component.plot_height(plot_widget_element.offsetHeight - offset);
                });

                component.grid_width.subscribe(function(newValue)
                {
                    component.plot_width(plot_element.offsetWidth);
                });

                component.reload = function()
                {
                    server.get_json("/timeseries-collection/" + component.collection(),
                    {
                        success: function(data)
                        {
                            component.keys(data.keys);
                            component.keys.valueHasMutated();
                        },
                    });
                }

                component.selected_keys = component.keys.filter(function(key)
                {
                    return component.compiled_pattern().test(key);
                });

                component.select_timeseries = function(key)
                {
                    component.pattern(key);
                }

                component.sync_content = ko.computed(function()
                {
                    var uri = "/timeseries-collection/" + component.collection() + "/plot";
                    var data = {
                        height: component.plot_height() - 10,
                        keys: component.selected_keys(),
                        smoothing: component.smoothing(),
                        width: component.plot_width() - 10,
                        yscale: component.yscale(),
                    };

                    server.post_json(uri, data, {
                        success: function(data)
                        {
                            component.plot(data.plot);
                        },
                    });
                });

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
        widget: { width: 4, height: 12, params: {collection: null, pattern: ".*", smoothing: 0.5, yscale: "linear"}},
    };

    return module
});
