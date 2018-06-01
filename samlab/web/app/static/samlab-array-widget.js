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
                    metadata: {dtype: null, shape: [], size: null, min: null, mean: null, max: null, sum: null},
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

                component.view_as_image = function()
                {
                    dashboard.add_widget("samlab-array-image-widget", {otype: component.otype, oid: component.oid, key: component.key, "content-type": component.content_type});
                }

                server.load_json(component, "/" + component.otype() + "/" + component.oid() + "/content/" + component.key() + "/array/metadata");

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: {},
    };

    return module;
});
