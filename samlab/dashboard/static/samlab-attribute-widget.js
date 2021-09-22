// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-attribute-manager",
    "samlab-dashboard",
    ], function(ko, mapping, attribute_manager, dashboard)
{
    var component_name = "samlab-attribute-widget";

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    key: null,
                    value: null,
                });

                component.disabled = ko.pureComputed(function()
                {
                    return attribute_manager.otype() == null || attribute_manager.oid() == null;
                });

                component.keys = attribute_manager.keys;

                component.set_attribute = function()
                {
                    var key = component.key();
                    if(!key)
                    {
                        alert("Cannot set empty attribute key.");
                        return;
                    }

                    var value = JSON.parse(component.value());

                    var attributes = {};
                    attributes[key] = value;

                    attribute_manager.set_attributes(attributes);
                }

                component.set_attribute_key = function(key)
                {
                    component.key(key);
                }

                return component;
            },
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { },
    };

    return module;
});

