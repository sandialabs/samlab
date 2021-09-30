// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    ], function(ko, mapping)
{
    var component_name = "samlab-image-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    collection: widget.params.collection,
                    index: widget.params.index,
                    uri: widget.params.uri,
                });

                component.display_uri = ko.pureComputed(function()
                {
                    return component.uri() || "/image-collection/" + component.collection() + "/" + component.index();
                });

                component.title = ko.pureComputed(function()
                {
                    return component.uri() || component.collection() + "/" + (component.index() + 1);
                });

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { },
    };

    return module;
});
