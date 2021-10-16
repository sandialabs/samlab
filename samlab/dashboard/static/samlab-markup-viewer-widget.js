// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    ], function(debug, ko, mapping)
{
    var component_name = "samlab-markup-viewer-widget";
    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    content: null,
                });

                component.uri = widget.params.uri;

                component.uri.subscribe(function(uri)
                {
                    if(uri)
                    {
                        component.content("<p>Loading content \u2026</p>");
                        require(["text!" + uri], function(content)
                        {
                            component.content(content);
                            for(anchor of component_info.element.querySelectorAll("a"))
                            {
                                anchor.addEventListener("click", function(event)
                                {
                                    window.open(event.target.href, "_blank");
                                    event.preventDefault();
                                });
                            }
                        });
                    }
                });

                component.uri.valueHasMutated();

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {uri: null}},
    };

    return module;
});
