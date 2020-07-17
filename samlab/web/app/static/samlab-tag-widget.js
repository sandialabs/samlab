// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-tag-manager",
    "samlab-dashboard",
    ], function(ko, mapping, tag_manager, dashboard)
{
    var component_name = "samlab-tag-widget";

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    new_tag: null,
                });

                component.disabled = ko.pureComputed(function()
                {
                    return tag_manager.otype() == null || tag_manager.oid() == null;
                });

                component.tags = ko.pureComputed(function()
                {
                    var result = [];

                    var tags = tag_manager.tags();
                    for(var index = 0; index != tags.length; ++index)
                    {
                        var tag = tags[index];
                        var shortcut = null;
                        if(index < 10)
                        {
                            shortcut = "" + ((index+1) % 10)
                        }
                        if(10 <= index && index < 36)
                        {
                            shortcut = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[index - 10];
                        }
                        result.push({tag: tag, shortcut: shortcut});
                    }

                    return result;
                });

                component.set_shortcuts = ko.computed(function()
                {
                    dashboard.unbind({widget: widget});
                    for(let tag of component.tags())
                    {
                        if(tag.shortcut)
                        {
                            dashboard.bind(
                            {
                                widget: widget,
                                keys: tag.shortcut,
                                callback: function()
                                {
                                    tag_manager.toggle_tag(tag.tag);
                                },
                            });
                        }
                    }
                });


                component.toggle_tag = function(item)
                {
                    tag_manager.toggle_tag(ko.utils.unwrapObservable(item.tag));
                }

                component.add_tag = function()
                {
                    tag_manager.add_tag(component.new_tag());
                }

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

