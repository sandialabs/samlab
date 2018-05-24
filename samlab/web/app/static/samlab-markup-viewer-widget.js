// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "jquery",
    "knockout",
    "knockout.mapping",
    "URI",
    ], function(jquery, ko, mapping, URI)
{
    var component_name = "samlab-markup-viewer-widget";
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
                            jquery(component_info.element).find("a").click(function(event)
                            {
                                console.log("anchor click", URI(event.target.href));
                                if(URI(document.location.href).authority() == URI(event.target.href).authority())
                                {
                                    component.uri(event.target.href);
                                }
                                else
                                {
                                    window.open(event.target.href, "_blank");
                                }
                                return false;
                            });
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
