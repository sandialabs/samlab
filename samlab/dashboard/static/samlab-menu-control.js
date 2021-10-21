// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    ], function(debug, ko, mapping)
{
    var log = debug("samlab-menu-control");

    var component_name = "samlab-menu-control";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(params, component_info)
            {
                var component = mapping.fromJS({
                    label: params.label || "Menu",
                    disabled: params.disabled || false,
                    items: params.items,
                });

                component.expanded_items = component.items.map(function(item)
                {
                    return {click: item.click, divider: item.divider, heading: item.heading, icon: item.icon || "", key: item.key, label: item.label || "", shortcut: item.shortcut || ""};
                });

                component.select_item = function(item, event)
                {
                    item.click(item, event);
                }

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });
});
