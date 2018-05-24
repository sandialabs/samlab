// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-object",
    "samlab-server",
    ], function(ko, mapping, dashboard, object, server)
{
    var component_name = "samlab-array-image-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    content_type: widget.params["content-type"],
                    label: object.label(widget.params.otype, {singular: true, capitalize: true}) + " Content",
                    metadata: {dtype: null, shape: [], size: null, min: null, mean: null, max: null, sum: null},
                    oid: widget.params.oid,
                    otype: widget.params.otype,
                    role: widget.params.role,
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, widget.params.otype, widget.params.oid);

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                }

                component.colormap = {factory: widget.params.cmap_factory, name: widget.params.cmap_name};

                component.colormaps =
                [
                    {
                        label: "Color Brewer Sequential",
                        children:
                        [
                            {name: "BlueGreen", factory: "brewer"},
                            {name: "BlueGreenYellow", factory: "brewer"},
                            {name: "BluePurple", factory: "brewer"},
                            {name: "Blues", factory: "brewer"},
                            {name: "BrownOrangeYellow", factory: "brewer"},
                            {name: "GreenBlue", factory: "brewer"},
                            {name: "GreenBluePurple", factory: "brewer"},
                            {name: "GreenYellow", factory: "brewer"},
                            {name: "Greens", factory: "brewer"},
                            {name: "Greys", factory: "brewer"},
                            {name: "Oranges", factory: "brewer"},
                            {name: "PurpleBlue", factory: "brewer"},
                            {name: "PurpleRed", factory: "brewer"},
                            {name: "Purples", factory: "brewer"},
                            {name: "RedOrange", factory: "brewer"},
                            {name: "RedOrangeYellow", factory: "brewer"},
                            {name: "RedPurple", factory: "brewer"},
                            {name: "Reds", factory: "brewer"},
                        ],
                    },
                    {
                        label: "Color Brewer Diverging",
                        children:
                        [
                            {name: "BlueGreenBrown", factory: "brewer"},
                            {name: "BlueRed", factory: "brewer"},
                            {name: "BlueYellowRed", factory: "brewer"},
                            {name: "GrayRed", factory: "brewer"},
                            {name: "GreenYellowRed", factory: "brewer"},
                            {name: "PinkGreen", factory: "brewer"},
                            {name: "PurpleGreen", factory: "brewer"},
                            {name: "PurpleOrange", factory: "brewer"},
                            {name: "Spectral", factory: "brewer"},
                        ],
                    },
                    {
                        label: "Linear",
                        children:
                        [
                            {name: "Blackbody", factory: "linear"},
                            {name: "ExtendedBlackbody", factory: "linear"},
                            {name: "Kindlmann", factory: "linear"},
                            {name: "ExtendedKindlmann", factory: "linear"},
                        ],
                    },
                    {
                        label: "Moreland Diverging",
                        children:
                        [
                            {name: "BlueBrown", factory: "diverging"},
                            {name: "BlueRed", factory: "diverging"},
                            {name: "GreenRed", factory: "diverging"},
                            {name: "PurpleGreen", factory: "diverging"},
                            {name: "PurpleOrange", factory: "diverging"},
                        ],
                    },
                ];

                component.set_colormap = function(data)
                {
                    component.colormap.name(data.name);
                    component.colormap.factory(data.factory);
                }

                component.metadata.size_formatted = ko.pureComputed(function()
                {
                    var size = component.metadata.shape()
                    size.reverse();
                    return size.join(" \u00d7 ");
                });

                component.metadata.min_formatted = ko.pureComputed(function()
                {
                    return component.metadata.min() != null ? Number(component.metadata.min()).toPrecision(6) : "";
                });

                component.metadata.mean_formatted = ko.pureComputed(function()
                {
                    return component.metadata.mean() != null ? Number(component.metadata.mean()).toPrecision(6) : "";
                });

                component.metadata.max_formatted = ko.pureComputed(function()
                {
                    return component.metadata.max() != null ? Number(component.metadata.max()).toPrecision(6) : "";
                });

                component.metadata.sum_formatted = ko.pureComputed(function()
                {
                    return component.metadata.sum() != null ? Number(component.metadata.sum()).toPrecision(6) : "";
                });

                component.uri = ko.pureComputed(function()
                {
                    return "/" + component.otype() + "/" + component.oid() + "/content/" + component.role() + "/array/image?cmap-factory=" + component.colormap.factory() + "&cmap-name=" + component.colormap.name();
                });

                server.load_json(component, "/" + component.otype() + "/" + component.oid() + "/content/" + component.role() + "/array/metadata");

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {cmap_factory: "linear", cmap_name: "Blackbody"}},
    };

    return module;
});
