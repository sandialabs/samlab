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
    var component_name = "samlab-array-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    content_type: widget.params["content-type"],
                    metadata: {dtype: null, ndim: 0, shape: [], size: null, min: null, mean: null, max: null, sum: null},
                    label: object.label(widget.params.otype, {singular: true, capitalize: true}) + " Content",
                    oid: widget.params.oid,
                    otype: widget.params.otype,
                    key: widget.params.key,
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, widget.params.otype, widget.params.oid);

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                }

                component.colormap = widget.params.colormap;

                component.colormaps =
                [
                    {heading: "Color Brewer Sequential"},
                    {label: "BlueGreen", key: "brewer/BlueGreen"},
                    {label: "BlueGreenYellow", key: "brewer/BlueGreenYellow"},
                    {label: "BluePurple", key: "brewer/BluePurple"},
                    {label: "Blues", key: "brewer/Blues"},
                    {label: "BrownOrangeYellow", key: "brewer/BrownOrangeYellow"},
                    {label: "GreenBlue", key: "brewer/GreenBlue"},
                    {label: "GreenBluePurple", key: "brewer/GreenBluePurple"},
                    {label: "GreenYellow", key: "brewer/GreenYellow"},
                    {label: "Greens", key: "brewer/Greens"},
                    {label: "Greys", key: "brewer/Greys"},
                    {label: "Oranges", key: "brewer/Oranges"},
                    {label: "PurpleBlue", key: "brewer/PurpleBlue"},
                    {label: "PurpleRed", key: "brewer/PurpleRed"},
                    {label: "Purples", key: "brewer/Purples"},
                    {label: "RedOrange", key: "brewer/RedOrange"},
                    {label: "RedOrangeYellow", key: "brewer/RedOrangeYellow"},
                    {label: "RedPurple", key: "brewer/RedPurple"},
                    {label: "Reds", key: "brewer/Reds"},
                    {heading: "Color Brewer Diverging"},
                    {label: "BlueGreenBrown", key: "brewer/BlueGreenBrown"},
                    {label: "BlueRed", key: "brewer/BlueRed"},
                    {label: "BlueYellowRed", key: "brewer/BlueYellowRed"},
                    {label: "GrayRed", key: "brewer/GrayRed"},
                    {label: "GreenYellowRed", key: "brewer/GreenYellowRed"},
                    {label: "PinkGreen", key: "brewer/PinkGreen"},
                    {label: "PurpleGreen", key: "brewer/PurpleGreen"},
                    {label: "PurpleOrange", key: "brewer/PurpleOrange"},
                    {label: "Spectral", key: "brewer/Spectral"},
                    {heading: "Linear"},
                    {label: "Blackbody", key: "linear/Blackbody"},
                    {label: "ExtendedBlackbody", key: "linear/ExtendedBlackbody"},
                    {label: "Kindlmann", key: "linear/Kindlmann"},
                    {label: "ExtendedKindlmann", key: "linear/ExtendedKindlmann"},
                    {heading: "Moreland Diverging"},
                    {label: "BlueBrown", key: "diverging/BlueBrown"},
                    {label: "BlueRed", key: "diverging/BlueRed"},
                    {label: "GreenRed", key: "diverging/GreenRed"},
                    {label: "PurpleGreen", key: "diverging/PurpleGreen"},
                    {label: "PurpleOrange", key: "diverging/PurpleOrange"},
                ];

                component.metadata.image_size_formatted = ko.pureComputed(function()
                {
                    var size = component.metadata.shape()
                    size.reverse();
                    return size.join(" \u00d7 ");
                });

                component.metadata.shape_formatted = ko.pureComputed(function()
                {
                    return component.metadata.shape().join(" \u00d7 ");
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

                component.image_uri = ko.pureComputed(function()
                {
                    return "/" + component.otype() + "/" + component.oid() + "/content/" + component.key() + "/array/image?colormap=" + component.colormap();
                });

                server.load_json(component, "/" + component.otype() + "/" + component.oid() + "/content/" + component.key() + "/array/metadata");

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { height: 12, params: {colormap: "linear/Blackbody"}},
    };

    return module;
});
